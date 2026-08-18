"""End-to-end Phase 1 path (Hamid lock).

Ingest a committed wide slice → write cache JSONL → augment (seed 42) →
replay identity. One test asserts the full chain. No network, no full dataset.
Contract unit tests in test_phase1_l0_contract.py stay blocking.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from scada_harmonizer.datagen.augmentation import augment
from scada_harmonizer.datagen.ingestion import (
    ingest_iiot_csv,
    read_l0_jsonl,
    sha256_file,
    write_l0_jsonl,
)
from scada_harmonizer.datagen.pipeline import materialize_cache
from scada_harmonizer.datagen.records import (
    CANONICAL_FIELDS,
    DEFAULT_SEED,
    L0Record,
    Quality,
    SourceDataset,
)
from scada_harmonizer.datagen.replay import (
    MixedCadenceError,
    ReplayMode,
    ReplaySettings,
    ReplayStream,
    identity_list,
)
from tests.datagen.factories import (
    GOLDEN_SHA256,
    GOLDEN_SLICE,
    TINY_TEP_CSV,
    assert_tep_cadence_180s,
    tiny_iiot_wide,
)


def _assert_schema(rows: list[L0Record]) -> None:
    assert rows
    for row in rows:
        dumped = row.to_canonical_dict()
        assert list(dumped.keys()) == list(CANONICAL_FIELDS)
        assert dumped["quality"] is not None
        assert "seed" not in dumped
        assert row.quality is not None


def _materialize_tep(cache_path: Path, *, extras: bool) -> str:
    return materialize_cache(
        TINY_TEP_CSV,
        cache_path,
        source_dataset=SourceDataset.TEP,
        seed=DEFAULT_SEED,
        include_extras=extras,
    )


def test_phase1_e2e_ingest_cache_augment_replay(tmp_path: Path) -> None:
    cache = tmp_path / "cache" / "tep_natives.jsonl"

    native_hash = _materialize_tep(cache, extras=False)
    assert native_hash == GOLDEN_SHA256
    assert sha256_file(cache) == GOLDEN_SHA256
    assert sha256_file(GOLDEN_SLICE) == GOLDEN_SHA256
    natives = read_l0_jsonl(cache)
    assert (
        _materialize_tep(tmp_path / "cache" / "tep_natives_again.jsonl", extras=False)
        == native_hash
    )

    _assert_schema(natives)
    assert all(row.source_dataset is SourceDataset.TEP for row in natives)
    assert all(row.quality is Quality.GOOD for row in natives)
    assert_tep_cadence_180s(natives)

    # Pin ingested natives before augment — not the same objects after mutation.
    pin_hash = write_l0_jsonl(natives, tmp_path / "natives_pin.jsonl")
    assert pin_hash == GOLDEN_SHA256

    augmented = augment(natives, seed=DEFAULT_SEED)
    _assert_schema(augmented)
    assert_tep_cadence_180s(augmented)
    native_names = {row.friendly_name for row in natives}
    native_after = [row for row in augmented if row.friendly_name in native_names]
    assert write_l0_jsonl(native_after, tmp_path / "natives_after.jsonl") == pin_hash
    assert all(before is not after for before, after in zip(natives, native_after, strict=True))

    identities = identity_list(augmented)
    again = identity_list(augment(read_l0_jsonl(cache), seed=DEFAULT_SEED))
    assert identities == again
    assert identities
    assert all(len(row) == 4 for row in identities)
    assert identities[0].sim_time_utc_ms == 0
    assert {row.sim_time_utc_ms for row in identities} == {0, 180_000}

    extras_cache = tmp_path / "cache" / "tep_plus_extras.jsonl"
    extras_hash = _materialize_tep(extras_cache, extras=True)
    assert extras_hash != GOLDEN_SHA256
    one_shot = identity_list(read_l0_jsonl(extras_cache))
    assert one_shot == identities

    backfill = ReplayStream(augmented, settings=ReplaySettings(mode=ReplayMode.BACKFILL))
    live = ReplayStream(
        augmented,
        settings=ReplaySettings(
            mode=ReplayMode.LIVE,
            rebase_origin=datetime(2026, 8, 18, 12, 0, tzinfo=UTC),
            speed_factor=50.0,
        ),
    )
    assert [event.identity for event in backfill.emit()] == identities
    assert live.identity_list() == identities
    assert backfill.is_live is False
    assert live.is_live is True

    iiot_csv = tmp_path / "tiny_iiot.csv"
    tiny_iiot_wide().to_csv(iiot_csv, index=False)
    iiot = ingest_iiot_csv(iiot_csv)
    _assert_schema(iiot)
    with pytest.raises(MixedCadenceError):
        identity_list(natives + iiot)
    with pytest.raises(MixedCadenceError):
        ReplayStream(read_l0_jsonl(cache) + iiot)
