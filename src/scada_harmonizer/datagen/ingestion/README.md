# ingestion (pipeline layer 1, Phase 1)

Loads the benchmark datasets (TEP, Industrial IoT, optional NAB), validates schema,
standardizes timestamps, and caches normalized forms into `data/cache/` for deterministic
replay. The L0 record, TEP melt, sim-time rule, and cache hash are defined in
`design/PHASE1_L0_CONTRACT.md`. NAB is optional and not required for Phase 1 exit.
No code until Phase 1.
