# data — local-only payloads (gitignored)

Contents are never committed; only this structure (via READMEs) is tracked.

| Folder | Contents |
|--------|----------|
| `raw/` | benchmark dataset downloads — TEP, Industrial IoT (Synthetic), optional NAB (links: `design/synthetic_data_generation_notes.md`) |
| `cache/` | normalized replay forms produced by the ingestion layer — deterministic, regenerable |

Later-phase stores do **not** live here: the medallion lakehouse (Bronze/Silver/Gold
Parquet) belongs to MinIO volumes (Phase 6), and databases own their own Docker volumes.
