"""1 s machine stream — N8 fast class (Hamid lock).

Generate → ingest as SourceDataset.IIOT → cache JSONL → augment → replay.
Kaggle stays a snapshot. TEP stays 180 s. No network, no full dataset.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import polars as pl
import pytest

from scada_harmonizer.datagen.augmentation import DEFAULT_EXTRAS, ExtraKind, augment
from scada_harmonizer.datagen.generation import (
    DEFAULT_N_MACHINES,
    DEFAULT_N_SECONDS,
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
    assert_tep_cadence_180s,
    assert_unique_same_name_cadence_seconds,
    tiny_tep_wide,
)

_EXTRA_NAMES = {spec.friendly_name for spec in DEFAULT_EXTRAS}


def _canonical(rows: Sequence[L0Record]) -> list[dict[str, object]]:
    return [row.to_canonical_dict() for row in rows]


def _assert_schema(rows: Sequence[L0Record]) -> None:
    assert rows
    for row in rows:
        dumped = row.to_canonical_dict()
        assert list(dumped.keys()) == list(CANONICAL_FIELDS)
        assert dumped["quality"] is not None
        assert "seed" not in dumped
        assert row.quality is not None


def _identity_names(rows: Sequence[L0Record]) -> set[str]:
    names = {row.friendly_name for row in rows} | {row.source_column for row in rows}
    return names & IDENTITY_COLUMN_NAMES


def test_machine_stream_generate_ingest_cache_augment_replay(tmp_path: Path) -> None:
    wide = generate_machine_stream(seed=DEFAULT_SEED)
    n_native = DEFAULT_N_MACHINES * DEFAULT_N_SECONDS * len(MACHINE_STREAM_PVS)
    assert wide.height == DEFAULT_N_MACHINES * DEFAULT_N_SECONDS
    assert wide.schema["machine_id"] == pl.String
    assert set(MACHINE_STREAM_PVS).issubset(wide.columns)
    assert MACHINE_STREAM_PERIOD_S == 1.0

    natives = ingest_iiot(wide)
    _assert_schema(natives)
    assert {row.source_dataset for row in natives} == {SourceDataset.IIOT}
    assert all(row.quality is Quality.GOOD for row in natives)
    assert _identity_names(natives) == set()
    assert_unique_same_name_cadence_seconds(natives, 1.0)
    assert len(natives) == n_native

    csv_path = tmp_path / "machine_stream.csv"
    write_machine_stream_csv(wide, csv_path)
    assert _canonical(ingest_iiot_csv(csv_path)) == _canonical(natives)

    cache = tmp_path / "cache" / "machine_natives.jsonl"
    native_hash = write_l0_jsonl(natives, cache)
    assert native_hash == MACHINE_STREAM_GOLDEN_SHA256 == sha256_file(MACHINE_STREAM_GOLDEN_SLICE)
    assert sha256_file(GOLDEN_SLICE) == GOLDEN_SHA256 != native_hash
    assert write_l0_jsonl(natives, tmp_path / "natives_pin.jsonl") == native_hash

    native_names = {row.friendly_name for row in natives}
    assert native_names.isdisjoint(_EXTRA_NAMES)
    assert {spec.kind for spec in DEFAULT_EXTRAS} == set(ExtraKind)

    augmented = augment(natives, seed=DEFAULT_SEED)
    _assert_schema(augmented)
    assert_unique_same_name_cadence_seconds(augmented, 1.0)
    native_after = [row for row in augmented if row.friendly_name in native_names]
    assert write_l0_jsonl(native_after, tmp_path / "natives_after.jsonl") == native_hash
    assert all(before is not after for before, after in zip(natives, native_after, strict=True))

    extras = [row for row in augmented if row.friendly_name in _EXTRA_NAMES]
    assert extras
    assert {row.quality for row in extras} >= {
        Quality.GOOD,
        Quality.BAD,
        Quality.UNCERTAIN,
        Quality.STALE,
    }
    assert {row.quality_reason for row in extras if row.quality_reason} == {
        "gap",
        "spike",
        "flatline",
    }
    assert _identity_names(augmented) == set()
    assert all(row.friendly_name.lower() not in FORBIDDEN_BUSINESS_NAMES for row in augmented)
    assert _canonical(augmented) == _canonical(augment(natives, seed=DEFAULT_SEED))
    assert _canonical(extras) != _canonical(
        [row for row in augment(natives, seed=7) if row.friendly_name in _EXTRA_NAMES]
    )

    identities = identity_list(augmented)
    assert identities == identity_list(augment(read_l0_jsonl(cache), seed=DEFAULT_SEED))
    assert identities and all(len(row) == 4 for row in identities)

    extras_cache = tmp_path / "cache" / "machine_plus_extras.jsonl"
    extras_hash = materialize_cache(
        csv_path,
        extras_cache,
        source_dataset=SourceDataset.IIOT,
        seed=DEFAULT_SEED,
        include_extras=True,
    )
    assert extras_hash != MACHINE_STREAM_GOLDEN_SHA256
    assert identity_list(read_l0_jsonl(extras_cache)) == identities
    assert ReplayStream(augmented).identity_list() == identities

    tep = ingest_tep(tiny_tep_wide())
    assert_tep_cadence_180s(tep)
    mixed = tep + natives
    with pytest.raises(MixedCadenceError):
        identity_list(mixed)
    with pytest.raises(MixedCadenceError):
        ReplayStream(mixed)
    with pytest.raises(MixedCadenceError):
        augment(mixed)


def test_machine_stream_seed_determinism() -> None:
    first = generate_machine_stream(seed=DEFAULT_SEED)
    second = generate_machine_stream(seed=DEFAULT_SEED)
    assert first.equals(second)
    assert not first.equals(generate_machine_stream(seed=7))
    assert _canonical(augment(ingest_iiot(first), seed=DEFAULT_SEED)) == _canonical(
        augment(ingest_iiot(second), seed=DEFAULT_SEED)
    )


def test_machine_identity_is_not_an_l0_pv() -> None:
    natives = ingest_iiot(generate_machine_stream(seed=DEFAULT_SEED))
    assert _identity_names(natives) == set()
    assert {row.friendly_name for row in natives} == set(MACHINE_STREAM_PVS)
    assert {row.source_column for row in natives} == set(MACHINE_STREAM_PVS)


def test_numeric_machine_id_is_not_melted() -> None:
    records = ingest_iiot(
        pl.DataFrame(
            {
                "ts_utc": ["2026-01-01T00:00:00Z", "2026-01-01T00:00:01Z"],
                "Machine_ID": [101, 101],
                "machine_type": ["pump", "pump"],
                "vibration_rms": [2.4, 2.5],
            }
        )
    )
    assert _identity_names(records) == set()
    assert {row.friendly_name for row in records} == {"vibration_rms"}
    assert len(records) == 2


def test_tep_metadata_columns_are_not_melted() -> None:
    records = ingest_tep(
        pl.DataFrame(
            {
                "faultNumber": [0, 0],
                "simulationRun": [1, 1],
                "sample": [0, 1],
                "xmeas_1": [0.25, 0.26],
            }
        )
    )
    assert _identity_names(records) == set()
    assert {row.friendly_name for row in records} == {"xmeas_1"}
    assert len(records) == 2
    assert_tep_cadence_180s(records)


def test_machine_stream_golden_sha256_is_stable(tmp_path: Path) -> None:
    assert sha256_file(MACHINE_STREAM_GOLDEN_SLICE) == MACHINE_STREAM_GOLDEN_SHA256
    records = read_l0_jsonl(MACHINE_STREAM_GOLDEN_SLICE)
    assert write_l0_jsonl(records, tmp_path / "rewrite.jsonl") == MACHINE_STREAM_GOLDEN_SHA256
    assert (
        write_l0_jsonl(
            ingest_iiot(generate_machine_stream(seed=DEFAULT_SEED)),
            tmp_path / "from_generator.jsonl",
        )
        == MACHINE_STREAM_GOLDEN_SHA256
    )
    assert sha256_file(GOLDEN_SLICE) == GOLDEN_SHA256
    assert_tep_cadence_180s(ingest_tep(tiny_tep_wide()))
