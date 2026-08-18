# tests/fixtures/datagen

Legal home for the Phase 1 golden slice. `data/**` is gitignored except READMEs, so
committed JSONL cannot live there.

- `golden_l0_slice.jsonl` — 2 TEP samples × 2 columns, canonical L0 JSONL
  (`design/PHASE1_L0_CONTRACT.md`). CI hashes these records, not raw downloads.
- `tiny_tep.csv` — the matching wide TEP input (offline; not a dataset download).

Hash is SHA-256 of the UTF-8 golden file. Pinned in `tests/test_phase1_l0_contract.py`.
