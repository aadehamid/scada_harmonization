"""Seeded OT extras — valves, states, counters, modes, plus controlled messiness.

Same seed → same extras. TEP/IIoT native rows are copied (not aliased) unchanged.
Lots, work-order, and material IDs stay Phase 5.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from scada_harmonizer.datagen.records import (
    DEFAULT_SEED,
    L0Record,
    Quality,
    SourceDataset,
)


class ExtraKind(StrEnum):
    VALVE = "valve"
    STATE = "state"
    COUNTER = "counter"
    MODE = "mode"
    GAP = "gap"
    SPIKE = "spike"
    FLATLINE = "flatline"


class ExtraSpec(BaseModel):
    """Declared schema for one extra signal. Kind decides how values are generated."""

    model_config = ConfigDict(extra="forbid")

    friendly_name: str
    kind: ExtraKind


DEFAULT_EXTRAS: tuple[ExtraSpec, ...] = (
    ExtraSpec(friendly_name="xv_feed", kind=ExtraKind.VALVE),
    ExtraSpec(friendly_name="machine_state", kind=ExtraKind.STATE),
    ExtraSpec(friendly_name="cycle_count", kind=ExtraKind.COUNTER),
    ExtraSpec(friendly_name="ctrl_mode", kind=ExtraKind.MODE),
    ExtraSpec(friendly_name="comm_gap", kind=ExtraKind.GAP),
    ExtraSpec(friendly_name="noise_spike", kind=ExtraKind.SPIKE),
    ExtraSpec(friendly_name="stuck_pv", kind=ExtraKind.FLATLINE),
)


def _row(
    spec: ExtraSpec,
    ts: datetime,
    value: bool | int | float,
    quality: Quality,
    reason: str | None,
    dataset: SourceDataset,
) -> L0Record:
    return L0Record(
        ts_utc=ts,
        friendly_name=spec.friendly_name,
        source_column=spec.friendly_name,
        source_dataset=dataset,
        value=value,
        quality=quality,
        quality_reason=reason,
    )


def _generate_extra(
    spec: ExtraSpec,
    timestamps: Sequence[datetime],
    dataset: SourceDataset,
    rng: random.Random,
) -> list[L0Record]:
    rows: list[L0Record] = []
    n = len(timestamps)
    if spec.kind is ExtraKind.VALVE:
        for ts in timestamps:
            rows.append(_row(spec, ts, bool(rng.randrange(2)), Quality.GOOD, None, dataset))
        return rows
    if spec.kind is ExtraKind.STATE:
        for ts in timestamps:
            rows.append(_row(spec, ts, rng.randrange(3), Quality.GOOD, None, dataset))
        return rows
    if spec.kind is ExtraKind.COUNTER:
        start = rng.randrange(0, 10)
        for i, ts in enumerate(timestamps):
            rows.append(_row(spec, ts, start + i, Quality.GOOD, None, dataset))
        return rows
    if spec.kind is ExtraKind.MODE:
        auto = bool(rng.randrange(2))
        for ts in timestamps:
            if rng.random() < 0.25:
                auto = not auto
            rows.append(_row(spec, ts, auto, Quality.GOOD, None, dataset))
        return rows
    if spec.kind is ExtraKind.GAP:
        base = rng.uniform(0.5, 1.5)
        for i, ts in enumerate(timestamps):
            # Sample 0 stays Good so a time-ordered identity list can start Good.
            is_gap = i > 0 and rng.random() < 0.35
            quality = Quality.BAD if is_gap else Quality.GOOD
            reason = "gap" if is_gap else None
            rows.append(_row(spec, ts, float(base), quality, reason, dataset))
        return rows
    if spec.kind is ExtraKind.SPIKE:
        base = rng.uniform(40.0, 60.0)
        for i, ts in enumerate(timestamps):
            spiked = i > 0 and rng.random() < 0.25
            value = float(base + 900.0) if spiked else float(base)
            reason = "spike" if spiked else None
            quality = Quality.UNCERTAIN if spiked else Quality.GOOD
            rows.append(_row(spec, ts, value, quality, reason, dataset))
        return rows
    if spec.kind is ExtraKind.FLATLINE:
        current = rng.uniform(10.0, 20.0)
        hold_from = max(1, n // 2)
        for i, ts in enumerate(timestamps):
            if i < hold_from:
                current = rng.uniform(10.0, 20.0)
            reason = "flatline" if i >= hold_from else None
            quality = Quality.STALE if i >= hold_from else Quality.GOOD
            rows.append(_row(spec, ts, float(current), quality, reason, dataset))
        return rows
    raise ValueError(f"unknown extra kind: {spec.kind}")


def augment(
    records: Sequence[L0Record],
    *,
    seed: int = DEFAULT_SEED,
    extras: Sequence[ExtraSpec] | None = None,
) -> list[L0Record]:
    """Append extras. Native rows are copied first, in the same order."""
    specs = list(DEFAULT_EXTRAS if extras is None else extras)
    natives = [row.model_copy() for row in records]
    if not natives:
        return []
    dataset = natives[0].source_dataset
    timestamps = sorted({row.ts_utc for row in natives})
    rng = random.Random(seed)
    extra_rows: list[L0Record] = []
    for spec in specs:
        extra_rows.extend(_generate_extra(spec, timestamps, dataset, rng))
    return natives + extra_rows
