# replay (pipeline layer 6, Phase 1)

Time-ordered emission of L0 rows. Identity is
`(sim_time_utc_ms, friendly_name, value, quality)`. Simulated clock with N8 rebase,
speed factor, pause/resume, backfill vs live. Mixing TEP and IIoT on one stream
fails. See `docs/LSC-004_Level_0_Contract.md`.
