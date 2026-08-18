"""Replay identity: ordered (sim_time_utc_ms, friendly_name, value, quality).

Clock settings (speed, pause, rebase) change wall-clock only. Mixing TEP and
IIoT on one stream is a contract error.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from enum import StrEnum
from typing import NamedTuple

from pydantic import BaseModel, ConfigDict, field_validator

from scada_harmonizer.datagen.records import DEFAULT_SEED, L0Record, Quality, SourceDataset


class MixedCadenceError(ValueError):
    """TEP and IIoT cannot share one replay stream."""


class ReplayMode(StrEnum):
    LIVE = "live"
    BACKFILL = "backfill"


class ReplayIdentity(NamedTuple):
    sim_time_utc_ms: int
    friendly_name: str
    value: bool | int | float
    quality: Quality


class ReplaySettings(BaseModel):
    """Clock knobs. They do not appear on the identity list."""

    model_config = ConfigDict(extra="forbid")

    seed: int = DEFAULT_SEED
    speed_factor: float = 1.0
    rebase_origin: datetime | None = None
    mode: ReplayMode = ReplayMode.LIVE

    @field_validator("speed_factor")
    @classmethod
    def _positive_speed(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("speed_factor must be > 0")
        return value


def assert_single_dataset(records: Sequence[L0Record]) -> SourceDataset:
    datasets = {row.source_dataset for row in records}
    if len(datasets) > 1:
        names = ", ".join(sorted(dataset.value for dataset in datasets))
        raise MixedCadenceError(f"do not mix TEP and IIoT on one stream; got {names}")
    if not datasets:
        raise ValueError("cannot replay an empty record list")
    return next(iter(datasets))


def sort_records(records: Sequence[L0Record]) -> list[L0Record]:
    return sorted(records, key=lambda row: (row.ts_utc, row.friendly_name, row.source_column))


def sim_time_utc_ms(ts: datetime) -> int:
    return int(ts.astimezone(UTC).timestamp() * 1000)


def to_identity(record: L0Record) -> ReplayIdentity:
    return ReplayIdentity(
        sim_time_utc_ms=sim_time_utc_ms(record.ts_utc),
        friendly_name=record.friendly_name,
        value=record.value,
        quality=record.quality,
    )


def identity_list(
    records: Sequence[L0Record],
    settings: ReplaySettings | None = None,
) -> list[ReplayIdentity]:
    """Time-ordered identity. ``settings`` is accepted and ignored for the list."""
    _ = settings
    assert_single_dataset(records)
    return [to_identity(row) for row in sort_records(records)]
