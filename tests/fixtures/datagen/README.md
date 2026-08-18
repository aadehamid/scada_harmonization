# tests/fixtures/datagen

Legal home for the Phase 1 golden slice. `data/**` is gitignored except READMEs, so
committed JSONL cannot live there.

- `golden_l0_slice.jsonl` — 2 TEP samples × 2 columns, canonical L0 JSONL
  (`design/PHASE1_L0_CONTRACT.md`). CI hashes these records, not raw downloads.
- `tiny_tep.csv` — the matching wide TEP input (offline; not a dataset download).
- `golden_machine_stream_l0_slice.jsonl` — 2 machines × 20 s × 3 PVs at native
  1 s UTC, natives only, seed 42. Generated; not a Kaggle snapshot.

Hashes are SHA-256 of the UTF-8 golden files. Pinned as `GOLDEN_SHA256` and
`MACHINE_STREAM_GOLDEN_SHA256` in `tests/datagen/factories.py`.
