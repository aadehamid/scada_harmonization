"""Seeded 1 s rotating-equipment stream (charter §14 N8 fast class).

Writes a wide Polars frame: native UTC + string machine identity + numeric
PVs. ``ingest_iiot`` melts it. Machine identity is stream metadata, not an
L0 PV. Kaggle stays a snapshot. TEP stays 180 s.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

import polars as pl
from pydantic import BaseModel, ConfigDict

from scada_harmonizer.datagen.records import DEFAULT_SEED, parse_utc_z

MACHINE_STREAM_PERIOD_S = 1.0
# Name + gauss sigma. Order is the RNG order — do not reshuffle (golden pin).
_PV_NOISE: tuple[tuple[str, float], ...] = (
    ("vibration_rms", 0.04),
    ("motor_current_a", 0.15),
    ("shaft_speed_rpm", 2.5),
)
MACHINE_STREAM_PVS: tuple[str, ...] = tuple(name for name, _ in _PV_NOISE)
DEFAULT_N_MACHINES = 2
DEFAULT_N_SECONDS = 20
DEFAULT_START = datetime(2026, 1, 1, tzinfo=UTC)
_WIDE_SCHEMA = {
    "ts_utc": pl.Datetime(time_zone="UTC"),
    "machine_id": pl.String,
    "machine_type": pl.String,
    **{name: pl.Float64 for name, _ in _PV_NOISE},
}


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
    if not 1 <= n_machines <= len(DEFAULT_MACHINES):
        raise ValueError(f"n_machines must be 1..{len(DEFAULT_MACHINES)}")
    return DEFAULT_MACHINES[:n_machines]


def generate_machine_stream(
    *,
    seed: int = DEFAULT_SEED,
    n_machines: int = DEFAULT_N_MACHINES,
    n_seconds: int = DEFAULT_N_SECONDS,
    start: datetime | None = None,
) -> pl.DataFrame:
    """Wide IIoT frame at native 1 s UTC. Same seed → identical frame.

    ``n_machines`` is 1..``len(DEFAULT_MACHINES)`` (currently 2). ``start``
    must be timezone-aware UTC.
    """
    if n_seconds < 2:
        raise ValueError("n_seconds must be >= 2 so cadence deltas exist")
    origin = DEFAULT_START if start is None else parse_utc_z(start)
    roster = _machines(n_machines)
    rng = random.Random(seed)
    period = timedelta(seconds=MACHINE_STREAM_PERIOD_S)
    rows: list[dict[str, object]] = []
    for tick in range(n_seconds):
        ts = origin + tick * period
        for spec in roster:
            row: dict[str, object] = {
                "ts_utc": ts,
                "machine_id": spec.machine_id,
                "machine_type": spec.machine_type,
            }
            for name, sigma in _PV_NOISE:
                row[name] = round(getattr(spec, name) + rng.gauss(0.0, sigma), 6)
            rows.append(row)
    return pl.DataFrame(rows, schema=_WIDE_SCHEMA)


def write_machine_stream_csv(frame: pl.DataFrame, path: Path) -> Path:
    """Write a wide CSV ``ingest_iiot_csv`` can melt. ``ts_utc`` is ISO-8601 Z."""
    if "ts_utc" not in frame.columns:
        raise ValueError("machine stream CSV requires a ts_utc column")
    path.parent.mkdir(parents=True, exist_ok=True)
    if frame.schema["ts_utc"] != pl.String:
        frame = frame.with_columns(
            pl.col("ts_utc").dt.convert_time_zone("UTC").dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
    frame.write_csv(path)
    return path
