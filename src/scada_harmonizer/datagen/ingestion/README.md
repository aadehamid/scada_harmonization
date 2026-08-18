# ingestion (pipeline layer 1, Phase 1)

Loads local TEP / IIoT CSVs (no downloaders), validates schema, melts wide tables to
long L0 rows, and writes canonical JSONL. TEP sim-time is epoch + `i * 180s`. IIoT
uses native UTC when present (generated 1 s machine stream, or a snapshot file).
Identity columns stay metadata. Cache hash is SHA-256 of that UTF-8 file. Full
caches go in `data/cache/` (gitignored); CI uses `tests/fixtures/datagen/`.
See `design/PHASE1_L0_CONTRACT.md`.
