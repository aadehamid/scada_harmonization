# data — local-only payloads (gitignored)

Contents are never committed; only this structure (via READMEs) is tracked.
Hamid's persist rules: keep raw; cache is regenerable and may be deleted; do not
write Full Faulty Testing as L0. Record: `design/PHASE1_SYNTHETIC_DATA.md`.

| Folder | Contents |
|--------|----------|
| `raw/` | benchmark dataset downloads — TEP, Industrial IoT (Synthetic), optional NAB (links: `design/synthetic_data_generation_notes.md`). **1.35 GiB kept** (18 Aug 2026). |
| `cache/` | normalized replay forms produced by the ingestion layer — deterministic, regenerable. Full L0 cache (330,920,000 rows, 54.63 GiB) was written then deleted 18 Aug 2026. |

Later-phase stores do **not** live here: the medallion lakehouse (Bronze/Silver/Gold
Parquet) belongs to MinIO volumes (Phase 6), and databases own their own Docker volumes.
