"""Wide benchmark tables → long L0 rows.

TEP arrives wide. ``n_long = n_samples * n_value_columns``. Each TEP sample
``i`` gets sim-time ``1970-01-01T00:00:00Z + i * 180s``. IIoT uses a native
UTC column when present.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

import polars as pl

from scada_harmonizer.datagen.records import L0Record, Quality, SourceDataset, parse_utc_z
from scada_harmonizer.datagen.timebase import iiot_fallback_sim_time, tep_sim_time

INDEX_COLUMNS = frozenset({"sample", "sample_index"})
TIME_COLUMNS = frozenset({"timestamp", "ts", "ts_utc", "time"})


def _is_value_dtype(dtype: pl.DataType) -> bool:
    return dtype == pl.Boolean or dtype.is_numeric()


def _value_columns(frame: pl.DataFrame) -> list[str]:
    names: list[str] = []
    for name in frame.columns:
        if name in INDEX_COLUMNS or name in TIME_COLUMNS:
            continue
        if _is_value_dtype(frame.schema[name]):
            names.append(name)
    if not names:
        raise ValueError("no numeric/bool value columns to melt")
    return names


def _sample_index(frame: pl.DataFrame) -> list[int]:
    for name in frame.columns:
        if name in INDEX_COLUMNS:
            return [int(value) for value in frame.get_column(name).to_list()]
    return list(range(frame.height))


def _unwrap_scalar(value: object) -> object:
    """Pull a Python scalar out of a numpy/polars cell."""
    item = getattr(value, "item", None)
    if callable(item):
        return item()
    return value


def _reject_missing(number: object) -> object:
    """Gaps are quality codes, not null cells."""
    if number is None or (isinstance(number, float) and number != number):
        raise ValueError("L0 value cannot be null; encode gaps as quality, not NaN")
    return number


def _as_float(value: object) -> float:
    """TEP is analog process data — store natives as float, not int."""
    number = _reject_missing(_unwrap_scalar(value))
    if isinstance(number, bool) or not isinstance(number, int | float):
        raise TypeError(f"cannot coerce {type(number).__name__} to float")
    return float(number)


def _as_python_value(value: object) -> bool | int | float:
    number = _reject_missing(_unwrap_scalar(value))
    if isinstance(number, bool):
        return number
    if isinstance(number, int):
        return int(number)
    if isinstance(number, float):
        return float(number)
    raise TypeError(f"cannot coerce {type(number).__name__} to an L0 value")


def _melt(
    frame: pl.DataFrame,
    *,
    timestamps: Sequence[datetime],
    source_dataset: SourceDataset,
    coerce_float: bool,
) -> list[L0Record]:
    if frame.is_empty():
        raise ValueError(f"{source_dataset.value} frame is empty")
    if len(timestamps) != frame.height:
        raise ValueError("timestamp count must match sample count")
    value_columns = _value_columns(frame)
    records: list[L0Record] = []
    for ts, row in zip(timestamps, frame.iter_rows(named=True), strict=True):
        for column in value_columns:
            raw = row[column]
            value = _as_float(raw) if coerce_float else _as_python_value(raw)
            records.append(
                L0Record(
                    ts_utc=ts,
                    friendly_name=column,
                    source_column=column,
                    source_dataset=source_dataset,
                    value=value,
                    quality=Quality.GOOD,
                    quality_reason=None,
                )
            )
    return records


def ingest_tep(wide: pl.DataFrame) -> list[L0Record]:
    """Melt a wide TEP table to long L0. Clean benchmark rows are Good."""
    indexes = _sample_index(wide)
    timestamps = [tep_sim_time(index) for index in indexes]
    return _melt(wide, timestamps=timestamps, source_dataset=SourceDataset.TEP, coerce_float=True)


def ingest_iiot(wide: pl.DataFrame) -> list[L0Record]:
    """Melt a wide IIoT table. Native UTC wins; otherwise epoch + i * 1s."""
    timestamps = _iiot_timestamps(wide)
    return _melt(wide, timestamps=timestamps, source_dataset=SourceDataset.IIOT, coerce_float=False)


def _iiot_timestamps(frame: pl.DataFrame) -> list[datetime]:
    for name in frame.columns:
        if name not in TIME_COLUMNS:
            continue
        stamps: list[datetime] = []
        for value in frame.get_column(name).to_list():
            if isinstance(value, datetime):
                stamps.append(parse_utc_z(value))
            else:
                stamps.append(parse_utc_z(str(value)))
        return stamps
    return [iiot_fallback_sim_time(index) for index in range(frame.height)]


def ingest_tep_csv(path: Path) -> list[L0Record]:
    return ingest_tep(pl.read_csv(path))


def ingest_iiot_csv(path: Path) -> list[L0Record]:
    return ingest_iiot(pl.read_csv(path))
