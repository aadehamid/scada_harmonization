"""Wide benchmark tables → long L0 rows.

TEP arrives wide. ``n_long = n_samples * n_value_columns``. Each TEP sample
``i`` gets sim-time ``1970-01-01T00:00:00Z + i * 180s``. IIoT uses a native
UTC column when present.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

import pandas as pd

from scada_harmonizer.datagen.records import L0Record, Quality, SourceDataset
from scada_harmonizer.datagen.timebase import iiot_fallback_sim_time, tep_sim_time

INDEX_COLUMNS = frozenset({"sample", "sample_index"})
TIME_COLUMNS = frozenset({"timestamp", "ts", "ts_utc", "time"})


def _value_columns(frame: pd.DataFrame) -> list[str]:
    names: list[str] = []
    for raw in frame.columns:
        name = str(raw)
        if name in INDEX_COLUMNS or name in TIME_COLUMNS:
            continue
        series = frame[raw]
        if pd.api.types.is_bool_dtype(series) or pd.api.types.is_numeric_dtype(series):
            names.append(name)
    if not names:
        raise ValueError("no numeric/bool value columns to melt")
    return names


def _sample_index(frame: pd.DataFrame) -> list[int]:
    for raw in frame.columns:
        if str(raw) in INDEX_COLUMNS:
            return [int(value) for value in frame[raw].tolist()]
    return list(range(len(frame)))


def _as_float(value: object) -> float:
    """TEP is analog process data — store natives as float, not int."""
    if pd.isna(value):
        raise ValueError("L0 value cannot be null; encode gaps as quality, not NaN")
    return float(value)  # type: ignore[arg-type]


def _as_python_value(value: object) -> bool | int | float:
    if pd.isna(value):
        raise ValueError("L0 value cannot be null; encode gaps as quality, not NaN")
    if isinstance(value, bool):
        return value
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return int(value)
    return float(value)  # type: ignore[arg-type]


def _melt(
    frame: pd.DataFrame,
    *,
    timestamps: Sequence[datetime],
    source_dataset: SourceDataset,
    coerce_float: bool,
) -> list[L0Record]:
    if frame.empty:
        raise ValueError(f"{source_dataset.value} frame is empty")
    if len(timestamps) != len(frame):
        raise ValueError("timestamp count must match sample count")
    value_columns = _value_columns(frame)
    records: list[L0Record] = []
    for row_i in range(len(frame)):
        ts = timestamps[row_i]
        row = frame.iloc[row_i]
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


def ingest_tep(wide: pd.DataFrame) -> list[L0Record]:
    """Melt a wide TEP table to long L0. Clean benchmark rows are Good."""
    indexes = _sample_index(wide)
    timestamps = [tep_sim_time(index) for index in indexes]
    return _melt(wide, timestamps=timestamps, source_dataset=SourceDataset.TEP, coerce_float=True)


def ingest_iiot(wide: pd.DataFrame) -> list[L0Record]:
    """Melt a wide IIoT table. Native UTC wins; otherwise epoch + i * 1s."""
    timestamps = _iiot_timestamps(wide)
    return _melt(wide, timestamps=timestamps, source_dataset=SourceDataset.IIOT, coerce_float=False)


def _iiot_timestamps(frame: pd.DataFrame) -> list[datetime]:
    for raw in frame.columns:
        if str(raw) not in TIME_COLUMNS:
            continue
        series = pd.to_datetime(frame[raw], utc=True)
        return [stamp.to_pydatetime() for stamp in series]
    return [iiot_fallback_sim_time(index) for index in range(len(frame))]


def ingest_tep_csv(path: Path) -> list[L0Record]:
    return ingest_tep(pd.read_csv(path))


def ingest_iiot_csv(path: Path) -> list[L0Record]:
    return ingest_iiot(pd.read_csv(path))
