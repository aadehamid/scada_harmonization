"""L0 measurement record — the Phase 1 contract type.

One row per measurement (long form). Seed is run metadata (default 42), not a
column. Physical meaning waits for the mapping table.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

CANONICAL_FIELDS: tuple[str, ...] = (
    "ts_utc",
    "friendly_name",
    "source_column",
    "source_dataset",
    "value",
    "quality",
    "quality_reason",
)
DEFAULT_SEED = 42


class Quality(StrEnum):
    """Canonical quality (charter §14 N10). Always present on an L0 row."""

    GOOD = "Good"
    UNCERTAIN = "Uncertain"
    BAD = "Bad"
    STALE = "Stale"


class SourceDataset(StrEnum):
    TEP = "tep"
    IIOT = "iiot"


def format_utc_z(dt: datetime) -> str:
    """ISO-8601 with a ``Z`` suffix. Naive datetimes are rejected."""
    if dt.tzinfo is None:
        raise ValueError("ts_utc must be timezone-aware UTC")
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def parse_utc_z(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        text = value[:-1] + "+00:00" if value.endswith("Z") else value
        dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError("ts_utc must be timezone-aware UTC")
    return dt.astimezone(UTC)


class L0Record(BaseModel):
    """Long-form L0 row. Field declaration order is the canonical JSONL order."""

    model_config = ConfigDict(extra="forbid")

    ts_utc: datetime
    friendly_name: str
    source_column: str
    source_dataset: SourceDataset
    value: bool | int | float
    quality: Quality
    quality_reason: str | None = None

    @field_validator("ts_utc", mode="before")
    @classmethod
    def _utc_only(cls, value: datetime | str) -> datetime:
        return parse_utc_z(value)

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "ts_utc": format_utc_z(self.ts_utc),
            "friendly_name": self.friendly_name,
            "source_column": self.source_column,
            "source_dataset": self.source_dataset.value,
            "value": self.value,
            "quality": self.quality.value,
            "quality_reason": self.quality_reason,
        }


def records_to_jsonl(records: Sequence[L0Record]) -> str:
    """Canonical JSONL: one object per line, keys in contract order, UTF-8."""
    return "".join(json.dumps(row.to_canonical_dict()) + "\n" for row in records)


def write_l0_jsonl(records: Sequence[L0Record], path: Path) -> str:
    """Write canonical JSONL and return the SHA-256 hex digest of the file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = records_to_jsonl(records)
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_l0_jsonl(path: Path) -> list[L0Record]:
    records: list[L0Record] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(L0Record.model_validate_json(line))
    return records


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
