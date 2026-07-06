# Learning Log — Industrial Data Harmonization Home Lab

Durable concepts, gotchas, and glossary entries captured as the lab is designed and built.
Per the build cadence (AGENTS.md → "How we work"), when a component's teaching scaffolding is
pruned, the durable learning lands **here** so nothing is lost.

**How to use:** add entries as concepts appear (walkthroughs, build sessions, debugging).
One `##` section per component/theme; glossary at the bottom, alphabetized, plain-language.

---

## Concepts (per component)

*(seeded empty — filled during the Diagram 1 walkthrough and each build phase)*

## Gotchas

- **Eraser MCP:** the AI edit path (`update_diagram`) tends to reverse connection arrow
  directions — use `manually_update_diagram` (verbatim DSL) when direction matters.

---

## Glossary

- **CDC (change data capture)** — capturing inserts/updates/deletes from a database as an event
  stream; *log-based* CDC (Debezium reading the Postgres WAL) catches deletes and ordering that
  *poll-based* CDC misses.
- **Historian** — the OT time-series database of record for telemetry (here: TimescaleDB
  hypertables); stores value + timestamp + quality per sample.
- **Hypertable** — TimescaleDB's abstraction that auto-partitions a Postgres table by time into
  chunks, enabling compression, retention, and continuous aggregates.
- **iDMZ (industrial DMZ, "Level 3.5")** — the buffer zone between OT (Purdue Levels 0–3) and
  IT/enterprise (Levels 4–5); all cross-boundary traffic terminates there, and no IT-side system
  initiates connections into OT.
- **ISA-95** — the enterprise–control-system integration standard; source of the
  equipment hierarchy (enterprise → site → area → production unit → equipment) and the Level 0–4
  functional model.
- **NBIRTH / DBIRTH / NDATA / DDATA / NDEATH** — Sparkplug B message types: node/device birth
  certificates (declare all metrics + aliases), node/device data (changes only, by exception), and
  node death (via MQTT Last-Will). Consumers rebuild state from births — Sparkplug messages are
  *never* MQTT-retained.
- **OLTP / OLAP** — transactional workloads (many small concurrent writes; Postgres) vs analytical
  workloads (large read-heavy scans; DuckDB/lakehouse). One engine per concern.
- **Purdue model** — the classic OT network reference architecture (Levels 0–5) that the lab's
  OT / iDMZ / IT zoning follows (charter §13.8).
- **RBE (report by exception)** — publishing only when a value changes beyond a deadband, instead
  of on every scan; saves bandwidth but makes the historian store irregular, change-only samples
  (queries must gap-fill).
- **Sparkplug B** — an MQTT topic + protobuf payload specification (ISO/IEC 20237:2023) adding
  birth/death lifecycle, metric aliases, datatypes, and command semantics (NCMD/DCMD) on top of
  plain MQTT.
- **UNS (Unified Namespace)** — the single, hierarchically-organized, semantically-named event
  namespace through which all OT/IT systems publish and consume current plant state.
- **WAL (write-ahead log)** — Postgres's durability log; logical decoding of the WAL is what
  Debezium reads for CDC (a replication slot pins WAL until the connector consumes it).
