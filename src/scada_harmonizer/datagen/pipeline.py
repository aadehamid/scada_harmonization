"""Phase 1 entry point: local raw file + seed → canonical cache JSONL.

No downloads. Full caches belong in ``data/cache/`` (gitignored). CI uses the
committed golden slice under ``tests/fixtures/datagen/``.
"""

from __future__ import annotations

from pathlib import Path

from scada_harmonizer.datagen.augmentation import augment
from scada_harmonizer.datagen.ingestion import ingest_iiot_csv, ingest_tep_csv, write_l0_jsonl
from scada_harmonizer.datagen.records import DEFAULT_SEED, SourceDataset


def materialize_cache(
    raw_path: Path,
    cache_path: Path,
    *,
    source_dataset: SourceDataset,
    seed: int = DEFAULT_SEED,
    include_extras: bool = True,
) -> str:
    """Ingest a local CSV, optionally augment, write JSONL, return SHA-256."""
    if source_dataset is SourceDataset.TEP:
        records = ingest_tep_csv(raw_path)
    elif source_dataset is SourceDataset.IIOT:
        records = ingest_iiot_csv(raw_path)
    else:
        raise ValueError(f"unsupported source_dataset: {source_dataset}")
    if include_extras:
        records = augment(records, seed=seed)
    return write_l0_jsonl(records, cache_path)
