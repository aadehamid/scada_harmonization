# replay (pipeline layer 6, Phase 1)

Orchestrates replay: time-ordered emission, simulated clock with rebasing (charter §14 N8),
speed factor, pause/resume, backfill vs live mode. Deterministic: same seed → identical
sequence (Phase 1 exit criterion). Replay identity, N8 rebase, speed/pause, and
backfill-vs-live are defined in `design/PHASE1_L0_CONTRACT.md`. No code until Phase 1.
