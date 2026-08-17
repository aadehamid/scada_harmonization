# augmentation (pipeline layer 2, Phase 1)

Adds the OT extras the benchmark datasets lack: synthetic analog/discrete signals
(valves, states, counters), operational modes, and controlled messiness (gaps,
spikes, flatlines). Deterministic and seeded: same input, same output. Lots,
work-order, and material IDs stay Phase 5 (`context_export`). No code until
Phase 1 for these OT extras.
