# augmentation (pipeline layer 2, Phase 1)

Adds the OT extras the benchmark datasets lack: valves, states, counters, modes, and
controlled messiness (gaps, spikes, flatlines). Deterministic and seeded: same input,
same extras. Native TEP/IIoT columns are not mutated. Lots, work-order, and material
IDs stay Phase 5 (`context_export`).
