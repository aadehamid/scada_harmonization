# notebooks — the learning surface

**Marimo** notebooks, one per component (AGENTS.md "Medium"): rich explanations,
experiments, run-and-observe. When a component is done, its teaching scaffolding is pruned —
clean code graduates to `src/scada_harmonizer/` (the source of truth), durable concepts go
to `design/LEARNING_LOG.md`, and the notebook keeps a slim demo or retires.

Notebooks talk to infrastructure (brokers, TimescaleDB, Neo4j, …) as clients; the services
themselves run via `docker/`.
