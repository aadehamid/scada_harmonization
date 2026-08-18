"""Seeded 1 s rotating-equipment stream (charter §14 N8 fast class).

Writes a wide Polars frame: native UTC + string machine identity + numeric
PVs. ``ingest_iiot`` melts it. Machine identity is stream metadata, not an
L0 PV. Kaggle stays a snapshot. TEP stays 180 s.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path

import polars as pl
from pydantic import BaseModel, ConfigDict

from scada_harmonizer.datagen.records import DEFAULT_SEED, format_utc_z

MACHINE_STREAM_PERIOD_S = 1.0
MACHINE_STREAM_PVS: tuple[str, ...] = (
    "vibration_rms",
    "motor_current_a",
    "shaft_speed_rpm",
)
DEFAULT_N_MACHINES = 2
DEFAULT_N_SECONDS = 20
DEFAULT_START = datetime(2026, 1, 1, tzinfo=UTC)


class MachineSpec(BaseModel):
    """One rotating asset. Identity stays on the wide frame."""

    model_config = ConfigDict(extra="forbid")

    machine_id: str
    machine_type: str
    vibration_rms: float
    motor_current_a: float
    shaft_speed_rpm: float


DEFAULT_MACHINES: tuple[MachineSpec, ...] = (
    MachineSpec(
        machine_id="P-101",
        machine_type="centrifugal_pump",
        vibration_rms=2.4,
        motor_current_a=18.5,
        shaft_speed_rpm=1780.0,
    ),
    MachineSpec(
        machine_id="K-201",
        machine_type="process_compressor",
        vibration_rms=3.1,
        motor_current_a=42.0,
        shaft_speed_rpm=3550.0,
    ),
)


def _machines(n_machines: int) -> tuple[MachineSpec, ...]:
    if n_machines < 1:
        raise ValueError("n_machines must be >= 1")
    if n_machines <= len(DEFAULT_MACHINES):
        return DEFAULT_MACHINES[:n_machines]
    extra: list[MachineSpec] = []
    for index in range(len(DEFAULT_MACHINES), n_machines):
        extra.append(
            MachineSpec(
                machine_id=f"M-{301 + (index - len(DEFAULT_MACHINES)) * 100}",
                machine_type="motor",
                vibration_rms=2.0 + index * 0.1,
                motor_current_a=15.0 + index,
                shaft_speed_rpm=1750.0 + index * 10.0,
            )
        )
    return DEFAULT_MACHINES + tuple(extra)


def generate_machine_stream(
    *,
    seed: int = DEFAULT_SEED,
    n_machines: int = DEFAULT_N_MACHINES,
    n_seconds: int = DEFAULT_N_SECONDS,
    start: datetime | None = None,
    machines: Sequence[MachineSpec] | None = None,
) -> pl.DataFrame:
    """Wide IIoT frame at native 1 s UTC. Same seed → identical frame."""
    if n_seconds < 2:
        raise ValueError("n_seconds must be >= 2 so cadence deltas exist")
    origin = DEFAULT_START if start is None else start
    if origin.tzinfo is None:
        raise ValueError("start must be timezone-aware UTC")
    roster = tuple(machines) if machines is not None else _machines(n_machines)
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []
    period = timedelta(seconds=MACHINE_STREAM_PERIOD_S)
    for tick in range(n_seconds):
        ts = origin + tick * period
        for spec in roster:
            rows.append(
                {
                    "ts_utc": ts,
                    "machine_id": spec.machine_id,
                    "machine_type": spec.machine_type,
                    "vibration_rms": round(spec.vibration_rms + rng.gauss(0.0, 0.04), 6),
                    "motor_current_a": round(spec.motor_current_a + rng.gauss(0.0, 0.15), 6),
                    "shaft_speed_rpm": round(spec.shaft_speed_rpm + rng.gauss(0.0, 2.5), 6),
                }
            )
    return pl.DataFrame(
        rows,
        schema={
            "ts_utc": pl.Datetime(time_zone="UTC"),
            "machine_id": pl.String,
            "machine_type": pl.String,
            "vibration_rms": pl.Float64,
            "motor_current_a": pl.Float64,
            "shaft_speed_rpm": pl.Float64,
        },
    )


def write_machine_stream_csv(frame: pl.DataFrame, path: Path) -> Path:
    """Write a wide CSV ``ingest_iiot_csv`` can melt. ``ts_utc`` is ISO-8601 Z."""
    if "ts_utc" not in frame.columns:
        raise ValueError("machine stream CSV requires a ts_utc column")
    path.parent.mkdir(parents=True, exist_ok=True)
    stamps = []
    for value in frame.get_column("ts_utc").to_list():
        if isinstance(value, datetime):
            stamps.append(format_utc_z(value))
        else:
            stamps.append(str(value))
    frame.with_columns(pl.Series("ts_utc", stamps, dtype=pl.String)).write_csv(path)
    return path
