"""Blocking Phase 1 L0 tests. Contract: design/PHASE1_L0_CONTRACT.md.

These tests are written first (Hamid TDD lock). They import the public datagen API
and must stay green without network or full-dataset downloads.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import threading
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from scada_harmonizer.datagen.augmentation import DEFAULT_EXTRAS, ExtraKind, augment
from scada_harmonizer.datagen.ingestion import (
    ingest_iiot,
    ingest_tep,
    ingest_tep_csv,
    read_l0_jsonl,
    sha256_file,
    write_l0_jsonl,
)
from scada_harmonizer.datagen.records import (
    CANONICAL_FIELDS,
    DEFAULT_SEED,
    L0Record,
    Quality,
    SourceDataset,
)
from scada_harmonizer.datagen.replay import (
    MixedCadenceError,
    ReplayEvent,
    ReplayIdentity,
    ReplayMode,
    ReplaySettings,
    ReplayStream,
    identity_list,
)
from tests.datagen.factories import (
    GOLDEN_SHA256,
    GOLDEN_SLICE,
    TINY_TEP_CSV,
    assert_same_name_cadence_seconds,
    assert_tep_cadence_180s,
    tiny_iiot_wide,
    tiny_iiot_wide_no_time,
    tiny_tep_wide,
    tiny_tep_wide_n,
    write_tiny_tep_csv,
)

FORBIDDEN_BUSINESS_NAMES = {
    "lot",
    "lot_id",
    "work_order",
    "wo_id",
    "workorder",
    "material",
    "material_id",
}


class FakeWallClock:
    """Injectable wall clock so live replay tests never sleep on a real clock."""

    def __init__(self, start: datetime) -> None:
        self._now = start
        self.slept: list[float] = []

    def now(self) -> datetime:
        return self._now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self._now = self._now + timedelta(seconds=seconds)


def _sim_deltas_ms(identities: Sequence[ReplayIdentity], friendly_name: str) -> list[int]:
    times = [row.sim_time_utc_ms for row in identities if row.friendly_name == friendly_name]
    return [b - a for a, b in zip(times, times[1:], strict=False)]


# --- L0 schema -----------------------------------------------------------------


def test_l0_required_fields_present_and_ordered() -> None:
    rec = L0Record(
        ts_utc=datetime(1970, 1, 1, tzinfo=UTC),
        friendly_name="xmeas_1",
        source_column="xmeas_1",
        source_dataset=SourceDataset.TEP,
        value=0.25,
        quality=Quality.GOOD,
        quality_reason=None,
    )
    dumped = rec.to_canonical_dict()
    assert list(dumped.keys()) == list(CANONICAL_FIELDS)
    assert "seed" not in dumped
    assert dumped["quality"] == "Good"
    assert dumped["quality_reason"] is None
    assert DEFAULT_SEED == 42


def test_l0_record_is_frozen() -> None:
    rec = L0Record(
        ts_utc=datetime(1970, 1, 1, tzinfo=UTC),
        friendly_name="xmeas_1",
        source_column="xmeas_1",
        source_dataset=SourceDataset.TEP,
        value=0.25,
        quality=Quality.GOOD,
        quality_reason=None,
    )
    with pytest.raises(ValidationError):
        type(rec).__setattr__(rec, "value", 9.99)
    with pytest.raises(ValidationError):
        type(rec).__setattr__(rec, "quality", Quality.BAD)


def test_l0_quality_always_present() -> None:
    with pytest.raises(ValidationError):
        L0Record.model_validate(
            {
                "ts_utc": datetime(1970, 1, 1, tzinfo=UTC),
                "friendly_name": "xmeas_1",
                "source_column": "xmeas_1",
                "source_dataset": SourceDataset.TEP,
                "value": 0.25,
            }
        )
    records = ingest_tep(tiny_tep_wide())
    assert records
    assert all(row.quality is not None for row in records)
    assert all(row.quality == Quality.GOOD for row in records)


# --- TEP cadence + melt --------------------------------------------------------


def test_tep_cadence_same_name_deltas_are_180s() -> None:
    records = ingest_tep(tiny_tep_wide_n(n_samples=4, n_value_columns=3))
    assert_tep_cadence_180s(records)


def test_melt_wide_shape_maps_to_long_row_count() -> None:
    n_samples, n_value_columns = 5, 4
    wide = tiny_tep_wide_n(n_samples=n_samples, n_value_columns=n_value_columns)
    records = ingest_tep(wide)
    assert len(records) == n_samples * n_value_columns
    assert {row.source_dataset for row in records} == {SourceDataset.TEP}
    assert all(row.friendly_name == row.source_column for row in records)


# --- Golden slice + two-process ------------------------------------------------


def test_golden_slice_sha256_is_stable(tmp_path: Path) -> None:
    from_file = sha256_file(GOLDEN_SLICE)
    assert from_file == GOLDEN_SHA256
    records = read_l0_jsonl(GOLDEN_SLICE)
    rewritten = tmp_path / "golden_rewrite.jsonl"
    from_rewrite = write_l0_jsonl(records, rewritten)
    assert from_rewrite == GOLDEN_SHA256
    ingested = ingest_tep_csv(TINY_TEP_CSV)
    from_ingest = write_l0_jsonl(ingested, tmp_path / "from_tiny_tep.jsonl")
    assert from_ingest == GOLDEN_SHA256


def test_two_process_same_raw_and_seed_same_cache_hash(tmp_path: Path) -> None:
    raw = write_tiny_tep_csv(tmp_path / "raw.csv")
    cache_a = tmp_path / "a" / "cache.jsonl"
    cache_b = tmp_path / "b" / "cache.jsonl"
    script = (
        "from pathlib import Path\n"
        "from scada_harmonizer.datagen.pipeline import materialize_cache\n"
        "from scada_harmonizer.datagen.records import SourceDataset\n"
        "print(materialize_cache(Path({raw!r}), Path({cache!r}), "
        "source_dataset=SourceDataset.TEP, seed=42))\n"
    )
    hashes: list[str] = []
    for cache in (cache_a, cache_b):
        cache.parent.mkdir(parents=True)
        result = subprocess.run(
            [sys.executable, "-c", script.format(raw=str(raw), cache=str(cache))],
            check=True,
            capture_output=True,
            text=True,
        )
        hashes.append(result.stdout.strip())
    assert hashes[0]
    assert hashes[0] == hashes[1]
    assert hashes[0] == hashlib.sha256(cache_a.read_bytes()).hexdigest()


# --- Augmentation --------------------------------------------------------------


def test_augmentation_declared_schema_seed_and_natives_unchanged(tmp_path: Path) -> None:
    kinds = {spec.kind for spec in DEFAULT_EXTRAS}
    assert kinds == {
        ExtraKind.VALVE,
        ExtraKind.STATE,
        ExtraKind.COUNTER,
        ExtraKind.MODE,
        ExtraKind.GAP,
        ExtraKind.SPIKE,
        ExtraKind.FLATLINE,
    }
    assert all(spec.friendly_name for spec in DEFAULT_EXTRAS)

    natives = ingest_tep(tiny_tep_wide())
    extra_names = {spec.friendly_name for spec in DEFAULT_EXTRAS}
    native_names = {row.friendly_name for row in natives}
    assert native_names.isdisjoint(extra_names)

    # Pin the ingested natives *before* augment. A post-augment snapshot of the
    # same L0Record instances would still match after in-place value/quality mutation.
    hash_before = write_l0_jsonl(natives, tmp_path / "natives_before.jsonl")

    first = augment(natives, seed=DEFAULT_SEED)
    second = augment(natives, seed=DEFAULT_SEED)
    assert [row.to_canonical_dict() for row in first] == [row.to_canonical_dict() for row in second]

    other_seed = augment(natives, seed=7)
    extra_first = [row.to_canonical_dict() for row in first if row.friendly_name in extra_names]
    extra_other = [
        row.to_canonical_dict() for row in other_seed if row.friendly_name in extra_names
    ]
    assert extra_first
    assert extra_first != extra_other

    native_after = [row for row in first if row.friendly_name in native_names]
    hash_after = write_l0_jsonl(native_after, tmp_path / "natives_after.jsonl")
    assert hash_before == hash_after
    assert all(before is not after for before, after in zip(natives, native_after, strict=True))

    for row in first:
        assert row.friendly_name.lower() not in FORBIDDEN_BUSINESS_NAMES
        assert list(row.to_canonical_dict()) == list(CANONICAL_FIELDS)


# --- Replay --------------------------------------------------------------------


def test_iiot_without_time_column_uses_epoch_plus_i_seconds() -> None:
    records = ingest_iiot(tiny_iiot_wide_no_time())
    temps = [row for row in records if row.friendly_name == "temperature"]
    assert len(temps) == 3
    assert temps[0].ts_utc == datetime(1970, 1, 1, tzinfo=UTC)
    assert temps[1].ts_utc == datetime(1970, 1, 1, 0, 0, 1, tzinfo=UTC)
    assert temps[2].ts_utc == datetime(1970, 1, 1, 0, 0, 2, tzinfo=UTC)
    assert_same_name_cadence_seconds(records, 1.0)


def test_iiot_native_utc_same_name_deltas_are_1s() -> None:
    records = ingest_iiot(tiny_iiot_wide())
    temps = [row for row in records if row.friendly_name == "temperature"]
    assert temps[0].ts_utc == datetime(2024, 1, 1, tzinfo=UTC)
    assert_same_name_cadence_seconds(records, 1.0)
    assert_tep_cadence_180s(ingest_tep(tiny_tep_wide_n(n_samples=3, n_value_columns=2)))


def test_mixed_cadence_tep_and_iiot_on_one_stream_fails() -> None:
    mixed = ingest_tep(tiny_tep_wide()) + ingest_iiot(tiny_iiot_wide())
    with pytest.raises(MixedCadenceError):
        identity_list(mixed)
    with pytest.raises(MixedCadenceError):
        ReplayStream(mixed)
    with pytest.raises(MixedCadenceError):
        augment(mixed)


def test_replay_same_seed_identical_identity_list() -> None:
    natives = ingest_tep(tiny_tep_wide())
    a = identity_list(augment(natives, seed=DEFAULT_SEED))
    b = identity_list(augment(natives, seed=DEFAULT_SEED))
    assert a == b
    assert a
    assert all(len(row) == 4 for row in a)
    first = a[0]
    assert first.sim_time_utc_ms == 0
    assert first.quality == Quality.GOOD


def test_speed_pause_resume_rebase_do_not_change_identity_or_sim_deltas() -> None:
    records = ingest_tep(tiny_tep_wide_n(n_samples=3, n_value_columns=2))
    base = identity_list(records)
    expected_sim_deltas = [180_000, 180_000]
    origin = datetime(2026, 8, 18, 12, 0, tzinfo=UTC)

    fast_clock = FakeWallClock(origin)
    fast_stream = ReplayStream(
        records,
        settings=ReplaySettings(mode=ReplayMode.LIVE, speed_factor=10.0, rebase_origin=origin),
        clock=fast_clock,
    )
    fast_events = list(fast_stream.emit())
    fast_ids = [event.identity for event in fast_events]
    assert fast_ids == base
    assert _sim_deltas_ms(fast_ids, "xmeas_1") == expected_sim_deltas
    fast_walls = [
        event.wall_time for event in fast_events if event.identity.friendly_name == "xmeas_1"
    ]
    wall_deltas = [
        (b - a).total_seconds() for a, b in zip(fast_walls, fast_walls[1:], strict=False)
    ]
    assert wall_deltas == [18.0, 18.0]

    rebase_origin = datetime(2026, 1, 1, tzinfo=UTC)
    rebase_clock = FakeWallClock(rebase_origin)
    rebase_stream = ReplayStream(
        records,
        settings=ReplaySettings(
            mode=ReplayMode.LIVE, speed_factor=1.0, rebase_origin=rebase_origin
        ),
        clock=rebase_clock,
    )
    rebase_events = list(rebase_stream.emit())
    rebase_ids = [event.identity for event in rebase_events]
    assert rebase_ids == base
    assert _sim_deltas_ms(rebase_ids, "xmeas_1") == expected_sim_deltas
    assert rebase_events[0].wall_time == rebase_origin
    assert rebase_events[0].identity.sim_time_utc_ms == 0


def test_live_emit_while_paused_then_resume_keeps_identity() -> None:
    """emit() blocks while paused; resume() is cross-thread. Identity unchanged."""
    records = ingest_tep(tiny_tep_wide_n(n_samples=3, n_value_columns=2))
    base = identity_list(records)
    origin = datetime(2026, 8, 18, 12, 0, tzinfo=UTC)
    clock = FakeWallClock(origin)
    stream = ReplayStream(
        records,
        settings=ReplaySettings(mode=ReplayMode.LIVE, speed_factor=1.0, rebase_origin=origin),
        clock=clock,
    )
    stream.pause()
    collected: list[ReplayEvent] = []
    finished = threading.Event()

    def _emit() -> None:
        try:
            collected.extend(stream.emit())
        finally:
            finished.set()

    worker = threading.Thread(target=_emit, name="replay-emit")
    worker.start()
    try:
        worker.join(timeout=0.2)
        assert worker.is_alive()
        assert collected == []
        assert clock.slept == []
        stream.resume()
        assert finished.wait(timeout=2.0)
        worker.join(timeout=2.0)
        assert not worker.is_alive()
    finally:
        stream.resume()
        worker.join(timeout=2.0)
    ids = [event.identity for event in collected]
    assert ids == base
    assert _sim_deltas_ms(ids, "xmeas_1") == [180_000, 180_000]


def test_backfill_vs_live_same_identity_backfill_is_not_live() -> None:
    records = ingest_tep(tiny_tep_wide())
    settings_backfill = ReplaySettings(mode=ReplayMode.BACKFILL)
    settings_live = ReplaySettings(
        mode=ReplayMode.LIVE,
        rebase_origin=datetime(2026, 8, 18, 12, 0, tzinfo=UTC),
        speed_factor=100.0,
    )
    clock = FakeWallClock(datetime(2026, 8, 18, 12, 0, tzinfo=UTC))
    backfill = ReplayStream(records, settings=settings_backfill, clock=clock)
    live = ReplayStream(
        records,
        settings=settings_live,
        clock=FakeWallClock(datetime(2026, 8, 18, 12, 0, tzinfo=UTC)),
    )

    assert backfill.mode is ReplayMode.BACKFILL
    assert live.mode is ReplayMode.LIVE
    assert backfill.is_live is False
    assert live.is_live is True
    assert identity_list(records, settings=settings_backfill) == identity_list(
        records, settings=settings_live
    )

    backfill_events = list(backfill.emit())
    live_events = list(live.emit())
    assert [event.identity for event in backfill_events] == [
        event.identity for event in live_events
    ]
    assert all(event.is_live is False for event in backfill_events)
    assert all(event.is_live is True for event in live_events)
    assert clock.slept == []


def test_backfill_wall_time_is_historical_sim_time_regardless_of_speed() -> None:
    records = ingest_tep(tiny_tep_wide_n(n_samples=3, n_value_columns=2))
    clock = FakeWallClock(datetime(2026, 8, 18, 12, 0, tzinfo=UTC))
    stream = ReplayStream(
        records,
        settings=ReplaySettings(mode=ReplayMode.BACKFILL, speed_factor=50.0),
        clock=clock,
    )
    events = list(stream.emit())
    assert events
    assert all(event.is_live is False for event in events)
    assert all(event.wall_time == event.record.ts_utc for event in events)
    assert [event.identity for event in events] == identity_list(records)
    assert events[0].identity.sim_time_utc_ms == 0
    assert _sim_deltas_ms([event.identity for event in events], "xmeas_1") == [180_000, 180_000]
    assert clock.slept == []
