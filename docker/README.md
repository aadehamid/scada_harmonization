# docker — infrastructure as a learning artifact

Compose files + per-service config land here **one service at a time**, each explained, as
its phase begins (first: per-site Mosquitto, Phase 2). The wiring is half the lesson —
nothing is pre-scaffolded (AGENTS.md learning practice #2).

Planned conventions (charter §8.2 RAM risk + §13 L1.3):
- **compose profiles per phase** — `ot-core` / `streaming` / `analytics` / `enterprise` / `ml`
  so only the active phase's services run (full stack is realistically 16–24 GB).
- **Docker-network IT/OT segmentation** — separate edge-per-site vs central/cloud networks;
  only the site-forwarder bridges (the logical iDMZ, charter §13.8).
- per-service `mem_limit`; secrets via `.env` + Docker secrets (§13 L7.2).
