# Learning Log — Industrial Data Harmonization Home Lab

Durable concepts, gotchas, and glossary entries captured as the lab is designed and built.
Per the build cadence (AGENTS.md → "How we work"), when a component's teaching scaffolding is
pruned, the durable learning lands **here** so nothing is lost.

**How to use:** add entries as concepts appear (walkthroughs, build sessions, debugging).
One `##` section per component/theme; glossary at the bottom, alphabetized, plain-language.

---

## Concepts (per component)

### E2E walkthrough §0.1 — ISA-95 / IEC 62264 (the function & data lens; the lab's spine)

*Captured 2026-07-11 during the Diagram 1 v2 walkthrough opener (E2E_WALKTHROUGH.md §0.1).*

**What it is / isn't.** ISA-95 (US) = IEC 62264 (international twin, identical content) is the
**enterprise–control-system integration standard**: a *functional and data* model for how business
systems and plant-floor systems exchange information. **It is NOT a network architecture and NOT a
security standard** — that is the single most common misconception. Networks = Purdue; security =
IEC 62443. ISA-95 only says *what functions exist and what data flows between them.*

**Two hierarchies:**
1. **Functional hierarchy (Levels 0–4)** — L0 physical process · L1 sensing/actuation · L2 supervisory
   control · **L3 Manufacturing Operations Management (MOM)** — MES/LIMS/CMMS/Quality · L4 business
   planning (ERP). *Level 3 is the hinge*: business tempo above (orders, months, money), process tempo
   below (ms, sensors, physics). Every hard integration problem lives at the L3↔L4 seam — which is
   exactly where identity reconciliation bites (ERP order ID ≠ MES key).
2. **Equipment hierarchy** — `Enterprise → Site → Area → Production Unit → Equipment`. This *is* the
   lab's UNS topic path `lagos-chem/<site>/<area>/<production-unit>/…` (§14 N19) and the `asset_master`
   shape. ISA-95 splits the bottom into **Production Unit** (continuous — the lab's branch) vs
   **Line/Work Cell** (discrete) vs **Process Cell/Unit** (batch).

**Part 2 object models** (the standardized nouns): **material** (definition vs lot → N14
`material_definition`/`material_lot`), **equipment** (class vs instance → P6 templates; *"Centrifugal
Pump"* = class, *"P-101 at Beaumont"* = instance — harmonization = every site's instances conform to
shared classes), **personnel**, **process segments**.

**L3↔L4 exchange pattern — "schedule down, performance up."** Orders/targets flow down, actuals/
performance flow up, reconciled periodically. XML binding = **B2MML** (MESA's ready-made ISA-95 XML
schemas; the model can also be JSON / OPC-UA information models). In the lab this pattern *is* the
order-to-cash conduit **C6 down** + production confirmations up (§12 #18).

**Where the lab aligns / diverges (web-checked):** industry increasingly says **"MOM"** for L3, not
just "MES" (MES is the software, MOM is the ISA-95 function) — the lab's L3 breadth
(MES+LIMS+CMMS+Quality) is the standards-correct MOM scope. "Schedule down/performance up with periodic
reconciliation" is the documented real-world process/O&G pattern. **Deliberate divergence:** classic
ISA-95 integration is point-to-point B2MML (ERP↔MES); the lab keeps the ISA-95 *object model + hierarchy*
but routes telemetry through a **UNS** (broker-as-hub) instead — same nouns, modern plumbing. Adoption
in the wild is uneven/partial, so "we modeled the equipment hierarchy end-to-end" is a genuine strength.

**Sidebar — ISA-88 vs ISA-106:** because LSC is a *continuous* process, production is modeled as
**lots** (ISA-106 continuous ops), not **batches** (ISA-88) → table is `production_lot`, not `batch`
(§14 N13).

**Teach-back:** *"ISA-95 is the function-and-data standard: a 5-level functional hierarchy (physical
process → ERP) and a 5-tier equipment hierarchy (enterprise → equipment); my UNS topic path IS that
equipment hierarchy. It says what runs where and what crosses the L3↔L4 seam (schedule down,
performance up) — nothing about networks or security; those are Purdue and 62443."*

**Sources:** [Siemens ISA-95 framework](https://www.siemens.com/en-us/technology/isa-95-framework-layers/) ·
[Symestic — ISA-95 for MES/ERP](https://www.symestic.com/en-us/blog/mes/isa95) ·
[Process Control Guide — ISA-95 enterprise integration](https://processcontrolguide.com/isa-95-enterprise-integration/) ·
[ISA.org — ISA-95 standard](https://www.isa.org/standards-and-publications/isa-standards/isa-95-standard).

### Phase 1 L0 — melt, cache, persist (2026-08-18)

*Captured after PRs #28 (`8564fed`), #29 (`3039710`), #30, and #31 (`7da1621`).
Full write-up: `design/PHASE1_SYNTHETIC_DATA.md`. Datasheet:
`design/PHASE1_DATASHEET.md`. Contract: `design/PHASE1_L0_CONTRACT.md`.*

**What landed.** Polars melts wide Parquet on read into long L0 rows. pydantic
freezes the L0 boundary. Replay identity is
`(sim_time_utc_ms, friendly_name, value, quality)`. 21 golden-slice tests. No
network in CI.

**Persist (Hamid).** Warehouse is wide Parquet on R2 `lagos-chem-l0` (ENAM, zstd),
including the 9,600,000-row Faulty Testing native. Raw stays on R2
(1,419,880,076 bytes, no csv). Local `data/raw/` and `data/cache/` are not
durable. History JSONL 330,920,000 rows / 58,661,861,866 bytes was written then
deleted. 96 GiB was an estimate, never the warehouse. Golden SHA-256
`f5b9d1cfdaf9f298d9cdcbcb926bc3486dfdac1cccff7816b34ac290e6d33516`.

**IIoT correction.** The Kaggle file is snapshot-per-machine (500,000 × 18 in the
warehouse), not a 1 s historian stream. The contract's `epoch + i * 1s` path is a
melt fallback. N8 is not rewritten.

**Addendum (2026-08-19).** `#33` landed the 1 s machine stream
(`generate_machine_stream`, P-101 / K-201). `friendly_name` is
`{machine_id}/{pv}`; identity is not an L0 PV. `uv run pytest` is 41 after the
Unit 100 one-pager. TEP golden SHA unchanged. Machine-stream golden
`84b9f088…2159f0`. Unit 100 P&ID Rev B one-pager + 59-name tag list:
`design/UNIT100_PID.md`. Walkthrough is parallel and does not gate build.

**Teach-back:** *"Phase 1 stores wide natives on R2 and melts them on read with
Polars. The 1 s class is a generated machine stream. Hamid persists raw and
warehouse on R2. Local disks are scratch. The mapping table still assigns
meaning."*

**Hamid lock (2026-08-18, via Chief Architect):** Diagram 1 v2 L0 cuts are packed in `HANDOFF.md` §2, not drawn. The N8 fast-class hole landed as `#33`. N8 is not rewritten.

## Gotchas

- **Eraser MCP:** the AI edit path (`update_diagram`) tends to reverse connection arrow
  directions — use `manually_update_diagram` (verbatim DSL) when direction matters.
- **IIoT Kaggle file is not 1 Hz.** Snapshot per machine. Do not replay it as TEP's
  fast-class twin. Do not mix TEP and IIoT on one stream. The ~1 s class is
  `generate_machine_stream` (P-101 / K-201), ingested as `iiot`. TEP stays 180 s.

---

## Glossary

- **B2MML (Business To Manufacturing Markup Language)** — MESA's ready-made XML schema binding of the
  ISA-95 object model (production schedules, work orders, performance, material definitions); the usual
  wire format for L3↔L4 integration. The same model can also be JSON or an OPC-UA information model.
- **CDC (change data capture)** — capturing inserts/updates/deletes from a database as an event
  stream; *log-based* CDC (Debezium reading the Postgres WAL) catches deletes and ordering that
  *poll-based* CDC misses.
- **Equipment class vs instance (ISA-95 Part 2)** — a *class* is a reusable template (e.g. "Centrifugal
  Pump" with a shared tag schema); an *instance* is a specific asset ("Pump P-101 at Beaumont").
  Harmonization = every site's instances conform to shared classes (lab: P6 equipment templates).
- **Golden slice** — the tiny committed L0 JSONL under `tests/fixtures/datagen/` whose
  SHA-256 pins replay identity in CI. Not a raw download. Phase 1 pin:
  `f5b9d1cfdaf9f298d9cdcbcb926bc3486dfdac1cccff7816b34ac290e6d33516`.
- **Historian** — the OT time-series database of record for telemetry (here: TimescaleDB
  hypertables); stores value + timestamp + quality per sample.
- **Hypertable** — TimescaleDB's abstraction that auto-partitions a Postgres table by time into
  chunks, enabling compression, retention, and continuous aggregates.
- **iDMZ (industrial DMZ, "Level 3.5")** — the buffer zone between OT (Purdue Levels 0–3) and
  IT/enterprise (Levels 4–5); all cross-boundary traffic terminates there, and no IT-side system
  initiates connections into OT.
- **IEC 62264** — the international designation of **ISA-95** (identical content); see ISA-95.
- **IIoT snapshot (this lab's Kaggle file)** — one row per machine, not a 1-second
  time series. Warehouse object `iiot` is 500,000 × 18. Distinct from TEP.
- **ISA-88 / ISA-106** — process-modeling standards: ISA-88 (= IEC 61512) is *batch* control;
  ISA-106 is *continuous* operations. LSC is continuous → production modeled as **lots** (ISA-106),
  not **batches** (ISA-88); hence `production_lot`, not `batch` (§14 N13).
- **ISA-95 (= IEC 62264)** — the enterprise–control-system integration standard: a *functional and
  data* model (NOT a network or security standard). Gives the Level 0–4 **functional** hierarchy
  (physical process → L3 MOM → L4 ERP) and the **equipment** hierarchy (enterprise → site → area →
  production unit → equipment — the lab's UNS topic path). Defines Part 2 object models (material,
  equipment, personnel, process segments) and the L3↔L4 "schedule down, performance up" exchange.
- **L0 record** — long-form Phase 1 measurement row: `ts_utc`, `friendly_name`,
  `source_column`, `source_dataset`, `value`, `quality`, `quality_reason`. Seed is
  run metadata (default 42), not a column.
- **Melt** — wide table to long rows. One output row per (sample, value column).
  `n_long = n_samples * n_value_columns`.
- **MOM (Manufacturing Operations Management)** — the ISA-95 term for the **Level 3** *function*
  (production, quality, maintenance, inventory operations). "MES" is a common software name for it;
  MOM is the broader standards term. The lab's L3 = MES + LIMS + CMMS + Quality.
- **NBIRTH / DBIRTH / NDATA / DDATA / NDEATH** — Sparkplug B message types: node/device birth
  certificates (declare all metrics + aliases), node/device data (changes only, by exception), and
  node death (via MQTT Last-Will). Consumers rebuild state from births — Sparkplug messages are
  *never* MQTT-retained.
- **OLTP / OLAP** — transactional workloads (many small concurrent writes; Postgres) vs analytical
  workloads (large read-heavy scans; DuckDB/lakehouse). One engine per concern.
- **Production unit** — the lowest tier of the ISA-95 equipment hierarchy on the *continuous-process*
  branch (the discrete branch uses line/work cell; the batch branch uses process cell/unit). LSC's
  reactors/columns are production units — the `<production-unit>` segment of the UNS topic path.
- **Purdue model** — the classic OT network reference architecture (Levels 0–5) that the lab's
  OT / iDMZ / IT zoning follows (charter §13.8).
- **RBE (report by exception)** — publishing only when a value changes beyond a deadband, instead
  of on every scan; saves bandwidth but makes the historian store irregular, change-only samples
  (queries must gap-fill).
- **Schedule down / performance up** — the ISA-95 L3↔L4 exchange pattern: schedules/orders/targets
  flow *down* from ERP (L4) to operations (L3); actuals/performance flow *up*; reconciled periodically.
  Lab: order-to-cash conduit C6 down + production confirmations up (§12 #18).
- **Sim-time** — the simulated clock on an L0 row, not wall-clock. TEP sample `i` is
  `1970-01-01T00:00:00Z + i * 180s`. Speed/pause/rebase change wall spacing only.
- **Sparkplug B** — an MQTT topic + protobuf payload specification (ISO/IEC 20237:2023) adding
  birth/death lifecycle, metric aliases, datatypes, and command semantics (NCMD/DCMD) on top of
  plain MQTT.
- **UNS (Unified Namespace)** — the single, hierarchically-organized, semantically-named event
  namespace through which all OT/IT systems publish and consume current plant state.
- **WAL (write-ahead log)** — Postgres's durability log; logical decoding of the WAL is what
  Debezium reads for CDC (a replication slot pins WAL until the connector consumes it).
