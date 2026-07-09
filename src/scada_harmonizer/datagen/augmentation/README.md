# augmentation (pipeline layer 2 — Phase 1)

Adds what the benchmark datasets lack: synthetic analog/discrete signals (valves, states,
counters), operational modes, controlled messiness (gaps, spikes, flatlines), and
enterprise-relevant context (work orders, lots, material IDs). Deterministic — seeded
randomness, same input → same output. No code until Phase 1.
