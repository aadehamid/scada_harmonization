"""1 s machine stream — N8 fast class (Hamid lock).

Generate → ingest as SourceDataset.IIOT → cache JSONL → augment → replay.
Kaggle stays a snapshot. TEP stays 180 s. No network, no full dataset.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from scada_harmonizer.datagen.augmentation import DEFAULT_EXTRAS, ExtraKind, augment
from scada_harmonizer.datagen.generation import (
    MACHINE_STREAM_PERIOD_S,
    MACHINE_STREAM_PVS,
    generate_machine_stream,
    write_machine_stream_csv,
)
from scada_harmonizer.datagen.ingestion import (
    ingest_iiot,
    ingest_iiot_csv,
    ingest_tep,
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
from scada_harmonizer.datagen.replay import MixedCadenceError, ReplayStream, identity_list
from tests.datagen.factories import (
    FORBIDDEN_BUSINESS_NAMES,
    GOLDEN_SHA256,
    GOLDEN_SLICE,
    IDENTITY_COLUMN_NAMES,
    MACHINE_STREAM_GOLDEN_SHA256,
    MACHINE_STREAM_GOLDEN_SLICE,
    TINY_TEP_CSV,
    assert_tep_cadence_180s,
    assert_unique_same_name_cadence_seconds,
    tiny_iiot_wide,
    tiny_iiot_wide_no_time,
    tiny_tep_wide,
)


def _assert_schema(rows: list[L0Record]) -> None:
    assert rows
    for row in rows:
        dumped = row.to_canonical_dict()
        assert list(dumped.keys()) == list(CANONICAL_FIELDS)
        assert dumped["quality"] is not None
        assert "seed" not in dumped
        assert row.quality is not None


def _identity_names(rows: list[L0Record]) -> set[str]:
    names = {row.friendly_name for row in rows} | {row.source_column for row in rows}
    return {name for name in names if name in IDENTITY_COLUMN_NAMES}


def _extra_names() -> set[str]:
    return {spec.friendly_name for spec in DEFAULT_EXTRAS}


def test_machine_stream_generate_ingest_cache_augment_replay(tmp_path: Path) -> None:
    wide = generate_machine_stream(seed=DEFAULT_SEED)
    assert isinstance(wide, pl.DataFrame)
    assert wide.height == 2 * 20
    assert "ts_utc" in wide.columns
    assert "machine_id" in wide.columns
    assert wide.schema["machine_id"] == pl.String
    assert set(MACHINE_STREAM_PVS).issubset(set(wide.columns))
    assert MACHINE_STREAM_PERIOD_S == 1.0

    natives = ingest_iiot(wide)
    _assert_schema(natives)
    assert all(row.source_dataset is SourceDataset.IIOT for row in natives)
    assert all(row.quality is Quality.GOOD for row in natives)
    assert _identity_names(natives) == set()
    assert_unique_same_name_cadence_seconds(natives, 1.0)
    assert len(natives) == 2 * 20 * len(MACHINE_STREAM_PVS)

    csv_path = tmp_path / "machine_stream.csv"
    write_machine_stream_csv(wide, csv_path)
    from_csv = ingest_iiot_csv(csv_path)
    assert [row.to_canonical_dict() for row in from_csv] == [
        row.to_canonical_dict() for row in natives
    ]

    cache = tmp_path / "cache" / "machine_natives.jsonl"
    native_hash = write_l0_jsonl(natives, cache)
    assert native_hash == MACHINE_STREAM_GOLDEN_SHA256
    assert sha256_file(MACHINE_STREAM_GOLDEN_SLICE) == MACHINE_STREAM_GOLDEN_SHA256
    assert sha256_file(GOLDEN_SLICE) == GOLDEN_SHA256
    assert native_hash != GOLDEN_SHA256

    pin_hash = write_l0_jsonl(natives, tmp_path / "natives_pin.jsonl")
    assert pin_hash == MACHINE_STREAM_GOLDEN_SHA256

    extra_names = _extra_names()
    native_names = {row.friendly_name for row in natives}
    assert native_names.isdisjoint(extra_names)
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

    augmented = augment(natives, seed=DEFAULT_SEED)
    _assert_schema(augmented)
    assert_unique_same_name_cadence_seconds(augmented, 1.0)
    native_after = [row for row in augmented if row.friendly_name in native_names]
    assert write_l0_jsonl(native_after, tmp_path / "natives_after.jsonl") == pin_hash
    assert all(before is not after for before, after in zip(natives, native_after, strict=True))
    extras = [row for row in augmented if row.friendly_name in extra_names]
    assert extras
    qualities = {row.quality for row in extras}
    reasons = {row.quality_reason for row in extras if row.quality_reason is not None}
    assert Quality.GOOD in qualities
    assert Quality.BAD in qualities
    assert Quality.UNCERTAIN in qualities
    assert Quality.STALE in qualities
    assert reasons == {"gap", "spike", "flatline"}
    for row in augmented:
        assert row.friendly_name.lower() not in FORBIDDEN_BUSINESS_NAMES
        assert _identity_names([row]) == set()

    again = augment(natives, seed=DEFAULT_SEED)
    assert [row.to_canonical_dict() for row in augmented] == [
        row.to_canonical_dict() for row in again
    ]
    other = augment(natives, seed=7)
    extra_default = [row.to_canonical_dict() for row in extras]
    extra_other = [row.to_canonical_dict() for row in other if row.friendly_name in extra_names]
    assert extra_default != extra_other

    identities = identity_list(augmented)
    replayed = identity_list(augment(read_l0_jsonl(cache), seed=DEFAULT_SEED))
    assert identities == replayed
    assert identities
    assert all(len(row) == 4 for row in identities)
    pipeline_csv = tmp_path / "pipeline.csv"
    write_machine_stream_csv(wide, pipeline_csv)
    extras_hash = materialize_cache(
        pipeline_csv,
        tmp_path / "cache" / "machine_plus_extras.jsonl",
        source_dataset=SourceDataset.IIOT,
        seed=DEFAULT_SEED,
        include_extras=True,
    )
    assert extras_hash != MACHINE_STREAM_GOLDEN_SHA256
    assert identity_list(read_l0_jsonl(tmp_path / "cache" / "machine_plus_extras.jsonl")) == (
        identities
    )
    assert ReplayStream(augmented).identity_list() == identities

    tep = ingest_tep(tiny_tep_wide())
    assert_tep_cadence_180s(tep)
    with pytest.raises(MixedCadenceError):
        identity_list(tep + natives)
    with pytest.raises(MixedCadenceError):
        ReplayStream(tep + natives)
    with pytest.raises(MixedCadenceError):
        augment(tep + natives)


def test_machine_stream_seed_determinism() -> None:
    first = generate_machine_stream(seed=DEFAULT_SEED)
    second = generate_machine_stream(seed=DEFAULT_SEED)
    assert first.equals(second)
    other = generate_machine_stream(seed=7)
    assert not first.equals(other)
    extras_a = augment(ingest_iiot(first), seed=DEFAULT_SEED)
    extras_b = augment(ingest_iiot(second), seed=DEFAULT_SEED)
    assert [row.to_canonical_dict() for row in extras_a] == [
        row.to_canonical_dict() for row in extras_b
    ]


def test_machine_identity_is_not_an_l0_pv() -> None:
    natives = ingest_iiot(generate_machine_stream(seed=DEFAULT_SEED))
    assert _identity_names(natives) == set()
    assert {row.friendly_name for row in natives} == set(MACHINE_STREAM_PVS)
    assert {row.source_column for row in natives} == set(MACHINE_STREAM_PVS)


def test_numeric_machine_id_is_not_melted() -> None:
    wide = pl.DataFrame(
        {
            "ts_utc": ["2026-01-01T00:00:00Z", "2026-01-01T00:00:01Z"],
            "Machine_ID": [101, 101],
            "machine_type": ["pump", "pump"],
            "vibration_rms": [2.4, 2.5],
        }
    )
    records = ingest_iiot(wide)
    assert _identity_names(records) == set()
    assert {row.friendly_name for row in records} == {"vibration_rms"}
    assert len(records) == 2


def test_tep_metadata_columns_are_not_melted() -> None:
    wide = pl.DataFrame(
        {
            "faultNumber": [0, 0],
            "simulationRun": [1, 1],
            "sample": [0, 1],
            "xmeas_1": [0.25, 0.26],
        }
    )
    records = ingest_tep(wide)
    assert _identity_names(records) == set()
    assert {row.friendly_name for row in records} == {"xmeas_1"}
    assert len(records) == 2
    assert_tep_cadence_180s(records)


def test_machine_stream_golden_sha256_is_stable(tmp_path: Path) -> None:
    from_file = sha256_file(MACHINE_STREAM_GOLDEN_SLICE)
    assert from_file == MACHINE_STREAM_GOLDEN_SHA256
    records = read_l0_jsonl(MACHINE_STREAM_GOLDEN_SLICE)
    rewritten = write_l0_jsonl(records, tmp_path / "machine_rewrite.jsonl")
    assert rewritten == MACHINE_STREAM_GOLDEN_SHA256
    generated = write_l0_jsonl(
        ingest_iiot(generate_machine_stream(seed=DEFAULT_SEED)),
        tmp_path / "from_generator.jsonl",
    )
    assert generated == MACHINE_STREAM_GOLDEN_SHA256
    assert sha256_file(GOLDEN_SLICE) == GOLDEN_SHA256
    assert ingest_tep(tiny_tep_wide())
    assert_tep_cadence_180s(ingest_tep(tiny_tep_wide()))


def test_existing_iiot_snapshot_and_tep_paths_stay_green() -> None:
    snapshot = ingest_iiot(tiny_iiot_wide())
    fallback = ingest_iiot(tiny_iiot_wide_no_time())
    tep = ingest_tep(tiny_tep_wide())
    assert {row.source_dataset for row in snapshot} == {SourceDataset.IIOT}
    assert {row.source_dataset for row in fallback} == {SourceDataset.IIOT}
    assert {row.source_dataset for row in tep} == {SourceDataset.TEP}
    assert_tep_cadence_180s(tep)
    from tests.datagen.factories import assert_same_name_cadence_seconds

    assert_same_name_cadence_seconds(snapshot, 1.0)
    assert_same_name_cadence_seconds(fallback, 1.0)
    assert sha256_file(GOLDEN_SLICE) == GOLDEN_SHA256
    assert TINY_TEP_CSV.is_file()
