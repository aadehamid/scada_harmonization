"""Tiny in-memory / on-disk frames for Phase 1 tests. No network, no full datasets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

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
    """2 samples × 2 value columns with native UTC timestamps."""
    return pd.DataFrame(
        {
            "timestamp": ["2024-01-01T00:00:00Z", "2024-01-01T00:00:01Z"],
            "temperature": [70.1, 70.2],
            "vibration": [0.11, 0.12],
        }
    )


def write_tiny_tep_csv(path: Path) -> Path:
    tiny_tep_wide().to_csv(path, index=False)
    return path
