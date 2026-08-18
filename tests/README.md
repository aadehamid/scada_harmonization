# tests — executable understanding

Small, targeted pytest suites that encode what was learned and can't go stale (AGENTS.md
learning practice #4). The centerpiece arrives at Phase 4a: the **cross-source equivalence
suite** — the same physical event replayed through ≥2 divergent sites must yield identical
canonical UNS output.

Phase 1 blocking unit tests live in `tests/test_phase1_l0_contract.py` (schema, melt,
cadence, golden-slice hash, two-process, augmentation, mixed cadence, replay identity /
clock). The Hamid-lock end-to-end path is `tests/test_phase1_e2e.py`: ingest the
committed wide slice → cache JSONL → augment (seed 42) → replay identity, in one test.
Both use `tests/fixtures/datagen/` — no network, no full-dataset CI.

Run with `uv run pytest`.
