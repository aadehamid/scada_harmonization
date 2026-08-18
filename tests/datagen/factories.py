"""Tiny in-memory / on-disk frames for Phase 1 tests. No network, no full datasets."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

import pandas as pd

from scada_harmonizer.datagen.records import L0Record

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "datagen"
GOLDEN_SLICE = FIXTURES / "golden_l0_slice.jsonl"
TINY_TEP_CSV = FIXTURES / "tiny_tep.csv"
# SHA-256 of golden_l0_slice.jsonl (canonical JSONL bytes).
GOLDEN_SHA256 = "f5b9d1cfdaf9f298d9cdcbcb926bc3486dfdac1cccff7816b34ac290e6d33516"


def tiny_tep_wide() -> pd.DataFrame:
    """2 samples × 2 value columns. Matches tests/fixtures/datagen/tiny_tep.csv."""
    return pd.DataFrame(
        {
            "xmeas_1": [0.25, 0.26],
            "xmeas_2": [3664.0, 3665.0],
        }
    )


def tiny_tep_wide_n(n_samples: int, n_value_columns: int) -> pd.DataFrame:
    """Deterministic wide TEP frame for melt/cadence tests."""
    data = {
        f"xmeas_{j}": [float(i * 10 + j) for i in range(n_samples)]
        for j in range(1, n_value_columns + 1)
    }
    return pd.DataFrame(data)


def tiny_iiot_wide() -> pd.DataFrame:
    """3 samples × 2 value columns with native UTC timestamps (1s cadence)."""
    return pd.DataFrame(
        {
            "timestamp": [
                "2024-01-01T00:00:00Z",
                "2024-01-01T00:00:01Z",
                "2024-01-01T00:00:02Z",
            ],
            "temperature": [70.1, 70.2, 70.3],
            "vibration": [0.11, 0.12, 0.13],
        }
    )


def tiny_iiot_wide_no_time() -> pd.DataFrame:
    """IIoT wide frame with no timestamp column — fallback epoch + i * 1s."""
    return pd.DataFrame(
        {
            "temperature": [70.1, 70.2, 70.3],
            "vibration": [0.11, 0.12, 0.13],
        }
    )


def write_tiny_tep_csv(path: Path) -> Path:
    tiny_tep_wide().to_csv(path, index=False)
    return path


def assert_same_name_cadence_seconds(rows: Sequence[L0Record], expected_seconds: float) -> None:
    """Consecutive same-name sim-time deltas match the dataset cadence."""
    by_name: dict[str, list[datetime]] = defaultdict(list)
    for row in rows:
        by_name[row.friendly_name].append(row.ts_utc)
    assert by_name
    for times in by_name.values():
        times.sort()
        deltas = [(b - a).total_seconds() for a, b in zip(times, times[1:], strict=False)]
        assert deltas
        assert all(delta == expected_seconds for delta in deltas)


def assert_tep_cadence_180s(rows: Sequence[L0Record]) -> None:
    """Consecutive same-name sim-time deltas are 180s (TEP contract)."""
    assert_same_name_cadence_seconds(rows, 180.0)
