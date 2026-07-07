# ingestion (pipeline layer 1 — Phase 1)

Loads the benchmark datasets (TEP, Industrial IoT, optional NAB), validates schema,
standardizes timestamps, and caches normalized forms into `data/cache/` for deterministic
replay. No code until Phase 1.
