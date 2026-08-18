# data/cache — normalized replay forms (gitignored)

Output of the ingestion layer: schema-validated, timestamp-standardized replay inputs.
Deterministic and regenerable from `data/raw/` — **safe to delete**.

Hamid deleted the full L0 JSONL on 18 Aug 2026 after it was written (330,920,000 rows,
54.63 GiB). Full Faulty Testing was never written (~96 GiB at 200 B/rec). CI uses the
committed golden slice under `tests/fixtures/datagen/`, not this folder. See
`design/PHASE1_SYNTHETIC_DATA.md`.
