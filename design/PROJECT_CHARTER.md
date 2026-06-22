# Project Charter — Industrial Data Harmonization & Contextualization Home Lab

**Status:** Authoritative project definition. Supersedes scattered framing in the superseded
source docs now under `reference/` (`reference/docs/` and
`reference/engineering_drawing_business_case/`); `README.md` and `AGENTS.md` are aligned to it.

**Last updated:** 2026-06-21

---

## 1. Purpose

Build a **home lab that simulates a multi-site manufacturing enterprise** in which similar
operational realities are represented differently across sites, then:

1. **Harmonize** those disparate OT representations into a common enterprise language through
   a Sparkplug B / MQTT **Unified Namespace (UNS)**; and
2. **Contextualize** the harmonized data — tie it to assets, lines, sites, events, work orders,
   materials, and engineering topology — so it is meaningful to OT, IT, analytics, ML, ERP, and
   graph-based reasoning systems.

This is a **learning environment and architecture prototype**, not a product and not a
consulting deliverable. The explicit goal is to understand every layer of a modern industrial
data architecture at the bare-metal level *before* adopting enterprise-grade software that
abstracts those layers away.

### Guiding principle

> Only **Level 0 (the physical world)** is synthetic. Everything above it — PLC-facing
> structures, messaging, historian, analytics, ERP, knowledge graph, cloud — behaves like a
> real OT/IT stack assembled from open-source or free/community software.

---

## 2. The problem being simulated

The core problem is **not** collecting plant telemetry. It is that different sites, lines, and
machines represent the *same underlying reality* in different ways — because of local PLC naming
conventions, controller memory structures, brownfield integrations, differing tag taxonomies,
uneven operational modeling, and even **different system integrators contracted per project** — so
tag modeling diverges not only site-to-site but *within* a single site. What should be
enterprise-comparable data arrives as site-specific, cryptic, inconsistent signals.

The consequences are operational, not cosmetic. When every plant organizes data differently and
there is **no standardized contextualization**, analytics data can take **days to assemble by hand**
(engineers pull historian extracts manually), real-time plant data stays **fragmented and "owned" by
individual sites**, and ML/analytics cannot scale across the enterprise. The lab deliberately
manufactures this mess (same reality, different names per site), then proves it can be conformed to
one namespace, **governed as a reusable data product**, and enriched into connected context.

The same fragmentation spans **three source domains** — the classic IT/OT/ET integration problem —
and each contributes a distinct kind of mess:

| Source domain | Where it lives in the lab | The mess it brings |
|---------------|---------------------------|--------------------|
| **OT** — operational telemetry | SCADA / PLC tags → UNS | cryptic, inconsistent, machine-unreadable tags |
| **IT** — business-transactional | on-prem relational systems (Postgres: MES/LIMS/CMMS/quality) | own business keys (batch/material/work-order/asset IDs) that don't align to OT identities |
| **ET** — engineering context | asset topology / drawings | relationships trapped in static documents/silos |

The three recurring challenges across these domains:

- **Harmonization** — cryptic OT tag → semantic metric (Plane 1).
- **Identity reconciliation** — stitching IT business keys, OT asset identities, and ET topology
  references together so they describe one asset/batch/event (the heart of Plane 3).
- **Governance & reuse** — once harmonized, the canonical definitions must be *owned, documented, and
  discoverable* so the same signal is reusable by every business and technical consumer without
  re-interpretation. The three-stage mapping table doubles as a **governed data-product catalog** with
  named owners ("data creators as gatekeepers") and per-field lineage — the lab's lightweight answer to
  "a unified approach for contextualizing *and governing* data, reusable for all users" (see §4).

Clean operational data **plus** reconciled transactional records **plus** accurate engineering
context = a complete foundation for industrial AI. None is useful at full scale without the others.

### Grounded in real industry discovery

The simulated problem is not invented — it mirrors what real process and CPG manufacturers report in
digital-transformation discovery. Two representative inputs are folded in as problem *patterns* (not
client/sales framing — consistent with how the `reference/` material is treated):

- **A global specialty-chemicals manufacturer:** "Every plant organizes data differently
  (different tags, names, descriptions); real-time plant data is fragmented and often considered owned
  by the sites." "We pull historian data manually, sometimes it takes days." "No standardized
  contextualization; tag modeling varies site by site, and at times within sites depending on the
  integrator." *Aspirations:* automate end-to-end pipelines from historians **and labs** to the cloud;
  enable ML/analytics at scale serving **global and local** requirements; a unified approach for
  contextualizing **and governing** data, reusable by all users; a **data-marketplace model where data
  creators are gatekeepers**; blend **edge + historian + SAP**.
- **A global packaged-foods (CPG) manufacturer:** drivers include **M&A reshaping the manufacturing
  footprint** and an **ongoing SAP ECC → S/4 transformation**; the ask is a unified, near-real-time
  data foundation feeding **yield-improvement** feedback loops, **root-cause analysis**, and
  **edge-executed, human-in-the-loop** actions, with **governance that preserves operator control while
  enabling autonomy** across a **variable plant footprint**.

These map onto the lab without changing the thesis — they sharpen *why* it matters:

| Real-world signal | Where it lives in the lab |
|---|---|
| same reality / different names; site & integrator variance | Plane 1 harmonization · `DOMAIN.md` divergence roster |
| fragmented, site-"owned" data; govern + reuse; data-marketplace/gatekeepers | governed data-product catalog — `metric_registry` (§4) |
| days-to-data, manual historian pulls | automated pipelines (Phases 1–5) — the cost of *not* harmonizing |
| M&A footprint; ongoing SAP migration | acquisition backstory (`DOMAIN.md`); ERP-in-flux realism |
| global **and** local requirements | two-tier broker — local site autonomy + central enterprise UNS (§4) |
| yield improvement / production-leakage; edge + human-in-the-loop feedback | Plane 4 Track A flagship use case (§3, §6, §8) |
| blend edge + historian + SAP; labs feed predictive models | IT/OT/ET fusion; LIMS as the lab leg of the IT source |

---

## 3. The three planes

```
  SOURCES        OT: SCADA/PLC tags   IT: Postgres OLTP   ET: asset topology
                        │                    │                   │
                        └────────────────────┼───────────────────┘
                                             ↓
┌────────────────────────────────────────────────────────────────────────┐
│ PLANE 1 — HARMONIZE (OT)                                                 │
│   synthetic Level 0 → PLC-world disguise → Sparkplug B → UNS             │
│   units / status / timestamp normalization · per-field lineage           │
│   reference design: reference/docs/ (ISHE patterns)                      │
├────────────────────────────────────────────────────────────────────────┤
│ PLANE 2 — RECORD (Enterprise)                                            │
│   curated operational events → ERPNext (SAP-like)                        │
│   work orders · production confirmations · maintenance · inventory       │
├────────────────────────────────────────────────────────────────────────┤
│ PLANE 3 — CONTEXTUALIZE (Knowledge)                                      │
│   UNS + IT transactional + ERP + asset topology                         │
│     → identity reconciliation → Neo4j knowledge graph → GraphRAG         │
│   ISO 15926 / DEXPI-aligned ontology · traversal & reasoning queries     │
│   reference design: reference/engineering_drawing_business_case/         │
├────────────────────────────────────────────────────────────────────────┤
│ PLANE 4 — APPLY (Intelligence)  — consumes Planes 1–3; the payoff         │
│   Track A · Traditional ML   → predictive maintenance, anomaly detection, │
│     time-series forecasting, soft sensors; predictions published back to  │
│     the UNS (closes the OT→IT→OT loop). [build Phase 6]                    │
│   Track B · LLM / GenAI      → information retrieval, NL query, summaries, │
│     operator/engineer copilot, grounded by GraphRAG over Neo4j. [Phase 7] │
└────────────────────────────────────────────────────────────────────────┘
```

IT business-transactional data (Postgres) is both a **source** to reconcile (left) and, optionally,
a **derived operational data store** populated *by* the pipeline (see §4).

**Plane 4 (Apply)** is the intelligence layer the foundation exists for — two tracks that *consume* the
harmonized + contextualized data: **traditional ML** on the time-series/operational side (predictive
maintenance, anomaly detection, forecasting, soft sensors — scoring back into the UNS) and **LLM/GenAI**
on the knowledge side (retrieval, understanding, copilots via GraphRAG). The **flagship Track-A use case
is yield improvement / "production-leakage" detection** — a concrete business KPI computable from the TEP
product streams — delivered as **action-ready, human-in-the-loop recommendations executed at the edge**
(the OT→IT→OT loop made operator-governed). Tooling and specifics are **deferred** — captured here so the
foundation is built to feed both; details when we reach Phases 6–7.

---

## 4. Layered technical architecture (ISA-95 view)

| Level | Role | Implementation |
|-------|------|----------------|
| **L0** | Synthetic & benchmark process reality | Python replay of benchmark datasets + generated signals |
| **L1/2** | PLC-world representation (brownfield realism) — **hybrid** | Python-modeled cryptic tags (`N7:20`, `MW100`, `FIC101_PV`) at Rotterdam + Corpus Christi. **Two** real protocol sites: **OpenPLC** over **Modbus TCP** (Beaumont) + an **OPC-UA** server (`asyncua`, Geismar) — both polled into Sparkplug (§13 L1.1) |
| **L3 — transport/UNS** | Harmonization backbone (two-tier) | **Mosquitto** per-site edge broker (local autonomy) + **EMQX OSS** central UNS broker; connected by a **Python site-forwarder** (not a raw broker bridge). **Sparkplug B** throughout |
| **L3 — OT consumers** | SCADA / storage / dashboards | Ignition Maker Edition, **TimescaleDB** historian (hypertables), Grafana |
| **L3 — relational store (OLTP)** | Transactional **system of record** (role A) + derived **operational data store / ODS** (role B) | **PostgreSQL** — role A: independent MES/LIMS/CMMS/quality source systems (CDC-captured); role B: ODS co-located in the TimescaleDB instance |
| **L3/4 — analytics (OLAP)** | Streaming & analytical path | Kafka → **medallion lakehouse** (Bronze/Silver/Gold, Parquet/object store) via **Spark ETL** → **DuckDB** (interactive OLAP query — distinct from Postgres OLTP); plus a **batch/file-drop** ingestion path (§13 L4) |
| **L4 — IT/cloud** | Cloud-shaped landing zone | floci (local AWS emulation: S3, Lambda, Kinesis, Glue, Athena, RDS, …) |
| **Cross-cutting — enterprise** | SAP-like business records | ERPNext (runs on its own MariaDB — not the Postgres ODS) |
| **Cross-cutting — knowledge** | Connected-context graph + reasoning | Neo4j + GraphRAG |
| **Cross-cutting — glue** | All custom logic | **Python** managed with **`uv`** (Paho MQTT, PySparkplug, pandas, Pydantic, Neo4j driver) |
| **Cross-cutting — observability** | Pipeline/infra monitoring | **Prometheus + Grafana** — container health, message rates, CDC lag, dead-letter counts, broker state (§13 L7.1) |

### Storage concern separation (no overlap)

Each engine owns one concern; nothing duplicates another:

| Engine | Concern | Shape |
|--------|---------|-------|
| **TimescaleDB** (historian) | high-frequency **time-series** telemetry | hypertables, append-only, time-indexed |
| **PostgreSQL** | **relational/transactional** (OLTP) — source-of-record + ODS | concurrent writes, current-state, business keys |
| **DuckDB** + Parquet/floci-S3 | **analytical** (OLAP) — batch, ML features | columnar, read-heavy |
| Neo4j | **relationships / connected context** | graph |
| ERPNext (on MariaDB) | **enterprise business records** | relational, owned by ERPNext |

> TimescaleDB *is* Postgres, so historian and the role-B ODS share one instance (separate schemas);
> the role-A source systems stay in a **separate** Postgres home (see database topology below).

**Postgres wears two hats:**
- **Role A — source-of-record OLTP:** stands in for on-prem plant transactional systems
  (MES, LIMS, CMMS, quality, batch records, downtime/shift logs). A *source* to reconcile — it has
  its own business keys that don't align to OT/ISA-95 identities. This is the IT leg of IT/OT/ET.
- **Role B — derived ODS:** the pipeline's relational integration/staging store — current harmonized
  state (a SQL-queryable mirror of UNS retained state), the asset/equipment master, the semantic
  mapping registry (the grown-up home of the three-stage mapping table once it outgrows YAML — a
  **governed data-product catalog**: every metric carries an owner/"gatekeeper", a human definition,
  and lineage, so harmonized signals are discoverable and reusable without re-interpretation),
  curated events, and per-field lineage / dead-letter log.

Run the two roles as **separate databases/schemas** so the "system of record vs. integration copy"
boundary stays explicit. Postgres also appears as floci's **RDS** target for cloud-pattern emulation
— keep that as a separate "what it'd look like in AWS" demo, not the lab's primary ODS.

### Broker topology & the two-step harmonization model (DECIDED)

The UNS uses a **two-tier broker topology** mirroring real edge/hub plant patterns (local autonomy +
enterprise harmonization):

```
  SITE A                         SITE B
  edge: Mosquitto                edge: Mosquitto
   ↑ local Sparkplug              ↑ local Sparkplug
   │ (site A's own namespace)     │ (site B's own namespace)
   └─── Python site-forwarder ────┴─── Python site-forwarder ───┐
        (cross-site conforming)                                 ↓
                                            CENTRAL: EMQX OSS  — enterprise UNS
                                            (one harmonized namespace; rule engine,
                                             Kafka/Postgres bridges, fan-out to IT)
```

- **Mosquitto (per-site edge):** lightweight local broker; the site keeps exchanging OT data even if
  the WAN/central system is down. Holds the site's *own* (still-divergent) Sparkplug namespace.
- **EMQX OSS (central):** the enterprise UNS broker — cross-site harmonization target, IT
  integrations, fan-out. Justified centrally by its rule engine, native data bridges, and clustering.
- **Connection = a Python site-forwarder, NOT a raw broker bridge.** Sparkplug B is stateful (death
  certificates via LWT, primary-host `STATE`); a naive `spBv1.0/#` broker bridge breaks that coherence
  across tiers and gives no control over what forwards. A site-forwarder subscribes locally and
  re-publishes a curated stream upward — preserving per-tier Sparkplug state and controlling exactly
  which topics leave the site.

This makes harmonization a **two-step** process, each with a physical home:

1. **Local mapping (edge):** PLC tag → Sparkplug metric, in each site's own namespace → site Mosquitto.
2. **Cross-site conforming (forwarder → EMQX):** each site's divergent representation is reconciled to
   the **one enterprise UNS namespace**. This is where "same reality, different names" becomes "one
   namespace" — the proof of harmonization.

### Database topology (DECIDED)

**Historian = TimescaleDB.** Chosen over InfluxDB/QuestDB so the whole stack speaks one query
language (SQL) — InfluxDB's Flux/InfluxQL would add cognitive surface that teaches nothing the lab
doesn't already get from SQL, and the lab's bottleneck is modeling/integration, not raw ingest rate
(QuestDB's edge). Timescale also integrates cleanly with Python (psycopg/SQLAlchemy), Grafana, and BI.

Three relational domains across **two Postgres homes** (both Postgres — same tooling):

| Home | Schemas | Owner | Role |
|------|---------|-------|------|
| **TimescaleDB instance** | `ts_historian.*` (hypertables) + `ods_core.*`, `erp_shadow.*` | pipeline | historian + derived ODS (role B) |
| **Separate Postgres** (own instance, or own DB in the cluster) | `mes.*`, `lims.*`, `cmms.*`, `quality.*` | the "plant" | source-of-record OLTP (role A) — what CDC reads |

Rationale: historian and ODS are both **pipeline-owned sinks** → co-locate (consolidation win). The
role-A systems are **independent foreign sources to reconcile** → keep separate, so CDC genuinely
captures from another system and the IT/OT/ET source boundary stays physical, not just logical.
ERPNext keeps its own MariaDB; `erp_shadow` is only an ODS convenience copy for SQL joins.

> In production you'd physically split historian from OLTP for workload isolation (heavy ingest vs.
> transactions). One Timescale instance for historian+ODS is fine for the lab — splitting later is
> part of the upgrade-friendly story.

### Relational schema layout (DECIDED)

**Home 1 — TimescaleDB instance (pipeline-owned):**

| Schema | Purpose | Sample tables |
|--------|---------|---------------|
| `ts_historian` | Time-series telemetry (hypertables) | `telemetry` (ts, metric_id, value, quality), `events` (alarms/faults/downtime) |
| `ods_core` | Derived ODS: current state + master data + **governed registry** + reconciliation | `asset_master` (ISA-95 hierarchy), `metric_registry` (the 3-stage mapping table as a **governed data product** — each metric has an owner/"gatekeeper", definition, and lineage), `current_state` (last value per metric), `identity_map`, `lineage`, `dead_letter` |
| `erp_shadow` | Read-only convenience copy of ERP rows for SQL joins | `work_order_shadow`, `material_shadow` |

**Home 2 — separate Postgres (the "plant" source-of-record, CDC-captured):**

| Schema | Stands in for | Sample tables |
|--------|---------------|---------------|
| `mes` | Manufacturing execution | `production_order`, `batch`, `batch_step` |
| `lims` | Lab / quality | `sample`, `lab_result`, `disposition` |
| `cmms` | Maintenance | `work_order`, `asset_condition` |
| `quality` | Quality events | `nonconformance`, `inspection` |

**Boundary rules — what makes the separation *mean* something:**

1. **No cross-home foreign keys.** Source systems (`mes`/`lims`/…) never FK into `ods_core`; they carry
   their *own* business keys (`batch_id='B-2207'`, `asset_id='EQ-4471'`).
2. **Reconciliation lives in `ods_core.identity_map`** — `(source_system, source_key) → canonical_identity`,
   the explicit stitch between IT keys, OT/ISA-95 identities, and (later) ET topology. This *is* the
   artifact Plane 3 produces.
3. **Lane discipline:** the historian never holds business keys; the source systems never hold telemetry.
4. **Neo4j reads from the harmonized/reconciled side** (`ods_core` + UNS), not from the raw source schemas.

---

## 5. Implementation approach

The three architecture notes (`hand_built`, `umh_anchored`, `python_centric`) are **not three
competing projects**. They are phases / styles of the *same* architecture:

- **Build & learn phase → Hand-built + Python-centric.**
  Assemble every component explicitly so each boundary (where harmonization happens, what owns
  history vs. streaming, how OT and IT consume the same signal) is visible and testable. Python
  is the default implementation language and a *first-class UNS participant* (virtual sensors,
  Sparkplug publishers, enrichment nodes, inference services), not just glue.

- **Abstraction phase → UMH-anchored (later).**
  Once the internals are understood, United Manufacturing Hub Community can replace the
  hand-wired MQTT/Kafka/historian/modeling bundle. This is the "graduate to enterprise tooling"
  step — adopted *after* understanding what it abstracts.

Every component is chosen to be **upgrade-friendly**: OSS brokers → EMQX Enterprise/HiveMQ;
Ignition Maker → licensed Ignition; floci → real AWS; Python replay → real gateways — all without
invalidating the design.

---

## 6. Data strategy

### Domain (DECIDED)

The simulated enterprise is a **multi-site process / specialty-chemicals manufacturer**. The
domain is **data-driven, not dictated** — it is whatever the two anchor benchmark datasets can
believably represent, so realistic data is always available without fabrication:

- **Continuous process units** (reactors, columns, utility loops) ← **Tennessee Eastman Process**
  (a chemical-plant benchmark: 52 variables — flow/pressure/temperature/level/composition —
  correlated, multivariate, 21 fault scenarios).
- **Rotating machines** (pumps, compressors, motors, conveyors) attached to those units ←
  **Industrial IoT Dataset (Synthetic)** (machine sensor + failure data: temperature, pressure,
  vibration, humidity, power — domain-agnostic equipment monitoring).

The same TEP process unit and the same IIoT machine type are **cloned across ≥2 sites with
deliberately divergent PLC naming and conventions** — which *is* the harmonization problem the lab
exists to prove. Physical meaning is **assigned** at the mapping stage (a TEP variable becomes a
reactor inlet temperature; an IIoT signal becomes a compressor motor current), so the data's
statistical shape — not its original labels — is the only real constraint.

### Sites & ISA-95 identity (DECIDED)

**Enterprise:** Lagos Specialty Chemicals · **UNS/topic root:** `lagos-chem` (the ISA-95 `enterprise`
level and the root of every UNS topic, e.g. `lagos-chem/beaumont/...`).

> **Backstory:** see [`DOMAIN.md`](DOMAIN.md) — a Lagos-HQ specialty-chemicals firm that grew by
> acquisition, which is *why* each site runs a different SCADA lineage. The narrative makes every
> technical quirk below trace to a business event.

**4 sites**, each running the *same* TEP process unit + IIoT machines but representing them
differently — so the lab exercises every harmonization dimension at once:

| Site (`site`) | Heritage / SCADA | Divergence flavor | PLC realism |
|---|---|---|---|
| **Beaumont** (TX) | Legacy brownfield, **Allen-Bradley** | Cryptic AB register tags (`N7:20`, `FIC101_PV`); imperial units; short status codes | **Real OpenPLC** (Modbus TCP) |
| **Geismar** (LA) | Acquired, **Siemens** | Siemens addresses (`DB10.DBD4`, `MW100`); metric units | Python-modeled |
| **Rotterdam** (NL) | Newer European, **Ignition/MQTT-style** | Verbose semi-semantic nested names; metric units; different status vocabulary | Python-modeled |
| **Corpus Christi** (TX) | Acquired O&G/midstream, **CygNet** | Compound flat tags that *encode* hierarchy (`CC_NORTH_U12_FIC101`); mixed units | Python-modeled |

Spans register-address vs. compound-name vs. verbose-semantic naming · imperial vs. metric · 4 SCADA
lineages · real vs. modeled PLC. Maps onto the three ISHE source archetypes (CygNet compound /
discrete-field / nested-topic), so those extracted patterns transfer directly. Full ISA-95 path:
`enterprise (lagos-chem) → site → area → line/cell → equipment-class → equipment-id`.

### Synthetic data is layered, not random

Benchmark datasets supply realistic multivariate dynamics; Python fills operational/enterprise
context and intentional messiness.

**Base datasets to replay:**
- **Industrial IoT Dataset (Synthetic)** — machine/equipment behavior (motors, pumps, conveyors)
- **Tennessee Eastman Process (TEP)** — continuous multivariable process behavior + faults
- **Numenta Anomaly Benchmark (optional)** — extra anomaly-rich streams

**The three-stage name mapping table is the spine of the whole lab:**

| Stage | Example | Lives where |
|-------|---------|-------------|
| 1. Friendly source variable | `reactor1_feed_flow` | dataset / generator |
| 2. Site-specific PLC tag | `FIC101_PV` / `N7:20` (differs per site) | PLC-world layer |
| 3. Sparkplug metric + asset path | `Reactor1/FeedFlow` | UNS / harmonization |

This table also carries unit, range, cadence, asset class, site context, the
work-order/batch/material/graph-entity IDs that later feed ERPNext and Neo4j, and **governance
metadata — each metric's owner ("gatekeeper"), human-readable definition, and lineage** — so it
doubles as a governed data-product catalog (its grown-up home is `ods_core.metric_registry`, §4).
**Build this table well and the rest is plumbing.**

**Six implementation layers** (from `synthetic_data_generation_notes.md`):
1. Ingestion · 2. Augmentation · 3. PLC mapping · 4. Sparkplug · 5. Context export · 6. Replay/orchestration

### Synthetic transactional data (the IT leg)

Beyond OT telemetry, the data-generation layer also produces **synthetic relational tables** seeded
into PostgreSQL (role A) to represent plant business-transactional systems:

- **MES** — production/work orders, batch genealogy
- **LIMS / quality** — sample results, dispositions
- **CMMS** — maintenance work orders, asset condition
- **Operational logs** — downtime tickets, shift logs

Critically, these tables carry their **own business keys** (e.g. batch `B-2207`, asset `EQ-4471`)
that are **deliberately not aligned** to the OT asset identities (`site-a/line-2/reactor-1`) or the
ET topology references. This extends the lab's "same reality, different representation" principle
from *tags* to *transactional records*, and creates the **identity-reconciliation** problem that is
the core of Plane 3: stitching IT keys ↔ OT identities ↔ ET topology so they describe one
asset/batch/event. Reconciled records are what give the Neo4j graph its cross-domain value
(genealogy, root-cause: *which batch ran on which reactor during which fault, against which work
order, with which lab result*).

**Integration pattern:** Postgres OLTP → **CDC** (change-data-capture, e.g. Debezium) → Kafka →
canonical-identity mapping → UNS events and/or Neo4j. This reuses the existing Kafka layer rather
than adding a new path.

---

## 7. Design assets extracted from the archived docs

These patterns are **kept** and migrated into the home-lab design. The business/sales framing
around them is **discarded**.

### From `reference/docs/` (ISHE — operational harmonization)

- **Canonical Pydantic model hierarchy** — `CanonicalTelemetry` → equipment-class submodels,
  `DataQuality`, `FieldLineage`, `DeadLetterEntry`, `UNSEnvelope`, `BirthCertificate`. This is the
  semantic target (stage 3) of the mapping table.
- **ISA-95 identity model** — Enterprise→Site→Area→Cell→EquipmentClass→EquipmentID.
  *Generalize* from O&G Well/ESP to the manufacturing Site/Area/Line/Cell/Asset hierarchy.
- **Per-field lineage discipline + config-driven YAML mapping** — direct implementation of the
  three-stage mapping table with provenance.
- **Transform primitives** — unit conversion, status normalization (unmapped → `Unknown`),
  timestamp coercion to UTC, cross-field data-quality flagging.
- **UNS semantics as a reference spec** — retained state, report-by-exception, birth certificates,
  wildcard matching, topic sanitization. ISHE implemented these *in-memory*; the home lab does the
  *real* version over MQTT/Sparkplug B, and uses ISHE's behavior as the **test oracle**.
- **Contract-first milestone discipline** — model → adapters → errors → transforms → pipeline → UNS.

### From `reference/engineering_drawing_business_case/` (EngiGraph — engineering context)

- **Ontology foundation: ISO 15926 / DEXPI** — a standards-based process-plant ontology for the
  Neo4j model instead of an ad-hoc schema. (Highest-value extract for Plane 3.)
- **Multi-level ontology architecture** — Core Equipment → Process System → Facility → Cross-Facility;
  matches the "start simple, extend" philosophy.
- **Node/edge vocabulary** — Equipment, Instrument, Valve, Pipe, Control System /
  `connects-to`, `controls`, `isolates`, `inspects`, `belongs-to` — merged with the design notes'
  `PART_OF` / `HAS_METRIC` / `GENERATED_EVENT` / `FULFILLS_WORK_ORDER` / `CONSUMED_MATERIAL`.
- **GraphRAG pattern** — query the graph first; the LLM composes from retrieved graph data, not
  training data. Blueprint for the operator/engineer copilot.
- **Graph-algorithm use cases** — shortest-path (isolation routing), centrality (critical nodes),
  impact analysis. These are the demo queries that prove the graph is worth building.
- **Digital-thread framing** — topology ↔ SCADA tag ↔ ERP FLOC ↔ work order linkage.

### Deliberately NOT extracted

- All market sizing, revenue/TAM projections, persona pain tables, competitor matrices, named
  clients, and ER&I-challenge framing.
- The narrow O&G-only scope (Well/ESP; CygNet/Wonderware/Ignition specifics) — keep the *patterns*,
  swap the *examples* for manufacturing/multi-site assets.
- EngiGraph's CV/VLM P&ID-extraction pipeline (symbol detection, OCR, VLM). The home lab
  *synthesizes* graph topology directly, so it keeps only EngiGraph's **ontology + graph + query**
  layers, not the document-extraction layers.

---

## 8. Proposed build sequence

| Phase | Goal | Deliverable |
|-------|------|-------------|
| **0** | Skeleton | Repo layout, `pyproject.toml`, the 3-stage mapping table as config, one asset |
| **1** | Level 0 replay | Ingestion + augmentation over TEP / Industrial IoT, replay in time order |
| **2** | PLC disguise + Sparkplug (edge) | **Python-modeled** cryptic tags → mapping + Sparkplug publisher → site **Mosquitto**; verify NBIRTH/DBIRTH/NDATA locally |
| **3** | OT consume | **TimescaleDB** historian (hypertables) + Grafana; optionally Ignition Maker as SCADA consumer; (optional) stand up `ods_core` ODS (role B) in the same instance for current-state mirror; **real-time alerting node** (UNS → rules → alerts, §13 L2.1); introduce **Prometheus + Grafana** observability (§13 L7.1) |
| **4** | Multi-site + central UNS | Clone asset template with *different* site tags; stand up **one real OpenPLC site** (Beaumont, Modbus TCP → Sparkplug) **and one real OPC-UA site** (Geismar, `asyncua` → Sparkplug, §13 L1.1); **Python site-forwarders** (with **store-and-forward** buffer, §13 L1.2) conform each site → central **EMQX** enterprise UNS → prove cross-site harmonization; **Docker-network IT/OT segmentation** (§13 L1.3); one **historian-less site** (§13 L1.4) |
| **5a** | IT transactional source | Seed synthetic MES/LIMS/CMMS tables into Postgres (role A); CDC → Kafka; reconcile IT keys ↔ OT/ISA-95 identities (CDC milestone below) |
| **5b** | Context | Context-export → ERPNext events + Neo4j graph (asset↔tag↔event↔work-order↔batch↔lab-result) |
| **6** | Loop closure — **Plane 4 Track A (ML)** | Stand up the **medallion lakehouse** (Bronze/Silver/Gold) via **Spark ETL** + **batch/file-drop ingestion** (§13 L4); traditional ML (predictive maintenance / anomaly / forecasting; **flagship: yield-improvement / production-leakage detection** over TEP product streams) over historian + gold features; **MLflow** registry/tracking (§13 L6.1); **offline (gold) + online (Redis) feature store** (§13 L6.2); **human-in-the-loop, edge-executed** predictions published back into Sparkplug; floci cloud landing |
| **7** | Reasoning — **Plane 4 Track B (LLM)** | LLM/GenAI: GraphRAG over Neo4j for retrieval / troubleshooting / lineage / impact / genealogy; operator-engineer copilot |
| **Later** | Abstraction | Re-platform L3 backbone onto UMH Community |

Phases 0–4 are the core harmonization proof. Phases 5–7 are the contextualization story (now
spanning OT + IT + ET).

**CDC learning milestone (within Phase 5a):**

- **5a.1 — Python poll:** watermark-based polling of the role-A schemas, publishing **Debezium-shaped**
  change events to Kafka — envelope `{before, after, op (c/u/d/r), ts_ms, source}`, topic
  `{server}.{schema}.{table}` (e.g. `lagoschem.mes.work_order`).
- **5a.2 — Debezium sandbox (one table):** stand up **Kafka Connect + Debezium Postgres connector**
  (`wal_level=logical`) on a single table (e.g. `mes.work_order`); compare topic naming + payload vs.
  the Python events. Both producers normalize into one canonical **`ChangeEvent`** Pydantic model via
  a small adapter (the swap seam). Learn the **replication-slot / WAL-retention** behavior.
- **5a.3 — Swap one full source:** replace Python CDC with Debezium for one source (MES); others stay
  on Python; migrate the rest later. The payoff: see firsthand why log-based CDC (catches deletes +
  ordered changes + initial snapshot `op:r`) beats poll-based (misses hard deletes and intra-interval
  changes).

---

## 9. Design principles

- **Only Level 0 is synthetic** — everything above behaves like real software.
- **Preserve the PLC-world boundary** — never publish clean semantic names straight from Python;
  the cryptic → harmonized transition is the whole point.
- **Pydantic-first** — every data boundary is a validated model; no raw dicts cross layers.
- **Deterministic, reproducible transforms** — same input → same output.
- **Cross-source equivalence** — the same physical event represented differently across sites must
  produce identical harmonized output. This is the proof of harmonization.
- **Sparkplug B as the contract** — not plain JSON-over-MQTT; births, aliases, datatypes, lifecycle.
- **Harmonize before contextualize** — Neo4j/ERP consume the *harmonized* side, not raw values.
- **Reconcile identities; preserve system-of-record authority** — IT/OT/ET keys are stitched into one
  identity, but each source system stays authoritative for its own domain; the ODS is a derived copy.
- **Right store for the shape** — time-series→historian, relational/transactional→Postgres (OLTP),
  analytical→DuckDB (OLAP), relationships→Neo4j. No engine duplicates another's concern.
- **Govern what you harmonize** — every canonical metric has an owner ("gatekeeper"), a definition, and
  lineage, so harmonized data is a *reusable, discoverable data product*, not just a clean signal. Local
  site autonomy and central enterprise standards coexist (serve *global and local* at once).
- **Config over code** — site mappings, status maps, unit factors, ontology are data.
- **Upgrade-friendly** — every OSS component has a credible paid/enterprise replacement path.
- **Python as a first-class participant** — not just glue; a native UNS node.

---

## 10. Scope

**In scope:** synthetic multi-site data (OT telemetry + IT transactional tables); PLC-world disguise;
Sparkplug B/MQTT UNS; historian + dashboards; PostgreSQL relational store (transactional source-of-record
+ derived ODS); CDC → Kafka; identity reconciliation across IT/OT/ET; ERPNext enterprise integration;
Neo4j knowledge graph + GraphRAG; floci cloud emulation; **Plane 4 intelligence — traditional ML
(predictive maintenance, anomaly, forecasting) with predictions scored back to the UNS, and LLM/GenAI
(retrieval, copilot) grounded by GraphRAG**.

**Out of scope (for now):** real PLC/field hardware; live SCADA connections; document/P&ID
CV-VLM extraction; production security hardening; real cloud accounts; real ERP deployments
beyond ERPNext community.

---

## 11. Document map

| Document | Role |
|----------|------|
| `design/PROJECT_CHARTER.md` | **This file — authoritative project definition** |
| `design/DOMAIN.md` | Domain narrative — Lagos Specialty Chemicals backstory (why the sites diverge) |
| `design/uns_home_lab_notes.md` | Vision & high-level scope |
| `design/hand_built_sparkplug_uns_notes.md` | Architecture option: hand-built |
| `design/umh_anchored_sparkplug_uns_notes.md` | Architecture option: UMH-anchored (abstraction phase) |
| `design/python_centric_uns_notes.md` | Implementation philosophy: Python-centric |
| `design/synthetic_data_generation_notes.md` | Data strategy & the 6-layer pipeline |
| `reference/docs/` *(local-only ref)* | Reference: ISHE harmonization patterns (Plane 1) |
| `reference/engineering_drawing_business_case/` *(local-only ref)* | Reference: EngiGraph ontology/graph patterns (Plane 3) |
| `reference/README.md` | Index of reference material & what to consult each for |

---

## 12. Open decisions

1. ~~Manufacturing domain & asset roster~~ — **DECIDED (2026-05-29):** multi-site process /
   specialty-chemicals plant; TEP process units + Industrial-IoT rotating machines, cloned across
   ≥2 sites with divergent naming. See §6.
2. ~~Broker choice~~ — **DECIDED (2026-05-30):** two-tier — **Mosquitto** per-site edge (local
   autonomy) + **EMQX OSS** central UNS, connected by a **Python site-forwarder** (not a raw broker
   bridge, to preserve Sparkplug state). Harmonization becomes two-step (local mapping → cross-site
   conforming). See §4.
3. ~~Historian choice~~ — **DECIDED (2026-05-30):** **TimescaleDB** (SQL everywhere; modeling, not
   ingest rate, is the bottleneck). See §4 database topology.
4. ~~How literal the PLC layer is~~ — **DECIDED (2026-05-30):** **hybrid** — most sites Python-modeled
   cryptic tags; **one** site runs a real **OpenPLC** runtime over **Modbus TCP** (the realism lesson
   once, without taxing every site). Start Python-modeled in Phase 2; add the OpenPLC site in Phase 4.
5. **When ERPNext and Neo4j enter** — Phase 5 as planned, or earlier stubs.
9. **API / backend framework** — **FastAPI** is the *intended* choice for the Plane 3 query / GraphRAG /
   copilot API (and any HTTP service interface). Not needed until that layer (~Phase 5b/7); intent
   recorded, decide concretely then. The core pipeline needs no HTTP backend.

10. **Plane 4 ML tooling** *(deferred to ~Phase 6)* — traditional ML stack (e.g. scikit-learn /
    statsmodels / streaming libs), feature sourcing from TimescaleDB + DuckDB, model packaging, and how
    predictions are published back to the UNS as Sparkplug metrics.
11. **Plane 4 LLM/GenAI tooling** *(deferred to ~Phase 7)* — GraphRAG framework (e.g. neo4j-graphrag),
    embedding/vector store, and LLM provider (Claude per house default). Both tracks captured now so the
    foundation feeds them; specifics decided when we get there.
12. **Redis (open source)** *(deferred, optional Plane 4)* — **NOT in the foundation** (Planes 1–3); must
    not duplicate MQTT-retained / Timescale `current_state` (current state), Kafka (streaming), or Neo4j
    native vector index (GraphRAG). **Learning Redis IS a goal** → scheduled as a deliberate hands-on
    milestone (same pattern as Debezium), most naturally the **online feature store in Phase 6** (teaches
    the online/offline feature-store split). Candidate secondary roles: LLM semantic/response cache +
    copilot session memory (Phase 7), API cache/rate-limit (if FastAPI). Evaluate at Phases 6–7.

**Tooling (DECIDED 2026-05-30):** **`uv`** is the package/project manager for everything — `uv add` /
`uv sync` / `uv run`, `pyproject.toml` + committed `uv.lock`, uv-pinned Python version. No pip/poetry.

**Diagrams (DECIDED 2026-06-21):** all project diagrams are created with the **Eraser MCP** and saved
to the Eraser workspace/folder **`scada_harmonization`**; each architecture view / implementation type
(§5) gets its own diagram there, linked from the relevant design doc. See AGENTS.md → "Diagrams".
6. ~~Number & identity of sites~~ — **DECIDED (2026-05-30):** enterprise **Lagos Specialty Chemicals**
   (root `lagos-chem`); **4 sites** — Beaumont (AB, real OpenPLC), Geismar (Siemens), Rotterdam
   (Ignition-style), Corpus Christi (CygNet). See §6.
7. ~~Postgres deployment~~ — **DECIDED (2026-05-30):** **consolidate historian + role-B ODS in the
   TimescaleDB instance** (separate schemas: `ts_historian` / `ods_core` / `erp_shadow`); keep the
   **role-A source systems** (`mes`/`lims`/`cmms`/`quality`) in a **separate** Postgres home so CDC
   captures from a foreign system. floci-RDS remains a separate cloud-pattern demo. See §4.
8. ~~CDC mechanism~~ — **DECIDED (2026-05-30):** **start Python poll, design for Debezium** — with an
   explicit hands-on Debezium learning milestone (goal is to *learn* Debezium, not avoid it). Three
   steps inside build Phase 5a — see §8.
13. ~~Governance / data-product framing~~ — **DECIDED (2026-06-21):** adopt a **lightweight governed
    catalog** — the three-stage mapping table / `metric_registry` is a governed data product (owner/
    "gatekeeper" + definition + lineage). **Not** a full data-mesh pillar; no separate governance build
    phase. Folds the specialty-chemicals discovery "govern + reuse / data-marketplace,
    creators-as-gatekeepers" pattern into
    what we already build. See §2, §4, §6, §9.
14. ~~Plane 4 flagship use case~~ — **DECIDED (2026-06-21):** **yield improvement / production-leakage**
    is the named flagship Track-A use case (generic ML methods retained), delivered as human-in-the-loop,
    edge-executed recommendations. **No** lab→pilot→plant tier added — LIMS covers the lab leg. Folds the
    CPG discovery yield / edge-feedback / HITL pattern. See §3, §6, §8.
15. ~~Reference-architecture review~~ — **DECIDED (2026-06-21):** benchmarked the design layer-by-layer
    against a real industrial-products target architecture; resolved all adds/keeps-out. See **§13**.

---

## 13. Reference-architecture review & implementation variants (DECIDED 2026-06-21)

The design was benchmarked, **layer by layer**, against a **real industrial-products company's target
architecture** (an AWS-native OT/IT/lab data platform). The review **validated the thesis** and
resolved, per layer, what the lab adds vs. keeps out. The reference is essentially our **cloud-native
variant** (what `floci` emulates); the hand-built design realizes the same capabilities with
self-hosted OSS.

### 13.1 Decision ledger

| # | Layer | Decision |
|---|-------|----------|
| L1.1 | OT edge | **Add OPC-UA** — Python `asyncua` server at **Geismar (Siemens)** → polled into Sparkplug. Two *real* protocols: Modbus/OpenPLC (Beaumont) + OPC-UA (Geismar); Rotterdam + Corpus Christi stay Python-modeled |
| L1.2 | OT edge | **Edge store-and-forward** — site-forwarder buffers + replays on reconnect (local autonomy when WAN/central down) |
| L1.3 | OT edge | **IT/OT boundary = logical** via separate Docker networks (edge-per-site vs central/cloud); only the forwarder bridges. No real firewall/SD-WAN |
| L1.4 | OT edge | One **historian-less site** (history only via central TimescaleDB); skip "4G sensors" |
| L2.1 | UNS/stream | **Add real-time alerting node** (UNS → rule thresholds → alert events back to UNS/Kafka), Phase 3–4 |
| L2.2 | UNS/stream | **No separate hot store** — TimescaleDB + MQTT-retained covers near-real-time |
| L3.1 | IT/ET sources | **No CRM, no separate MDM** — `ods_core` (asset_master + identity_map + governed `metric_registry`) is the lab's MDM analog |
| L3.2 | IT/ET sources | **LIMS only** lab system; skip ELN / instrument / chem-inventory / Protec |
| L4.1 | Storage/lake | **Medallion lakehouse** (Bronze/Silver/Gold, Parquet/object store) via **real Spark ETL**; DuckDB stays the interactive OLAP query engine |
| L4.2 | Storage/lake | **Add batch/file-drop ingestion** → bronze (historian/instrument extracts) alongside CDC/streaming |
| L5.1 | Context | Neo4j ontology **starts minimal, extends** (ISO 15926/DEXPI-aligned core vocab) |
| L5.2 | Context | GraphRAG embeddings in **Neo4j native vector index** (no separate vector DB) |
| L6.1 | ML | **MLflow** (tracking + registry + publish→score) in hand-built design; SageMaker + dataiku in cloud-native; algorithms still deferred to Phase 6 |
| L6.2 | ML | Feature store = **offline gold medallion + online Redis** (online/offline split) |
| L7.1 | Cross-cutting | **Prometheus + Grafana** pipeline/infra observability |
| L7.2 | Cross-cutting | **Lightweight secrets/access** — `.env` + Docker secrets, per-service auth, catalog gatekeepers; Vault + IAM/RBAC = enterprise upgrade path |
| L8.1 | Delivery | **Three architecture diagrams** (§13.4) |
| L8.2 | Delivery | Cloud-native variant targets **floci-emulated AWS** (real AWS = production upgrade) |

### 13.2 New components & learning milestones

**Net-new components** (beyond pre-review charter): OPC-UA server (Geismar) · edge store-and-forward ·
Docker-network segmentation · historian-less site · real-time alerting node · medallion lakehouse +
Spark ETL · batch/file-drop ingestion · MLflow · online/offline feature store · Prometheus+Grafana
observability · `ods_core` named the MDM analog.

**New hands-on learning milestones** (join Debezium + Redis): **OPC-UA · Spark · observability
(Prometheus) · MLflow.**

### 13.3 Deliberately out of scope

CRM/Salesforce · separate MDM platform · extra lab systems (ELN/instrument/chem/Protec) · pilot
plants · EDMS (ET topology is synthesized) · separate real-time "hot" store · Power BI (Grafana +
DuckDB/notebooks; Superset/Metabase = OSS-BI upgrade) · separate vector DB · Vault/IAM now · real AWS now.

### 13.4 The three implementation variants (architecture diagrams)

The three architecture notes (§5) are realized as **three full architecture diagrams**, all saved to
the project's Eraser folder **"SCADA Harmonization"** (= the convention's `scada_harmonization`), each
delivering the *same* capability set:

1. **Hand-built / Python-centric** — self-hosted OSS, every boundary explicit; the learning
   architecture built across Phases 0–7 (EMQX, Kafka, TimescaleDB, Spark, DuckDB, Neo4j, MLflow,
   Prometheus, Python forwarder/enrichment/alerting).
2. **UMH-anchored** — United Manufacturing Hub Community collapses the L3 ingestion/streaming/
   historian/modeling backbone into one platform; the abstraction phase (§5).
3. **Cloud-native (floci → AWS)** — the same design mapped onto floci-emulated AWS (IoT Core,
   Kinesis, Glue/Spark, Athena, S3 medallion, RDS, SageMaker, KMS/IAM/CloudWatch) ≈ the reference
   target architecture; real AWS is the production upgrade.

> Where the lab **exceeds** the reference: Sparkplug-B contract · two-tier broker + Python
> site-forwarder (the harmonization point) · Neo4j + ISO 15926/DEXPI ontology · GraphRAG/GenAI ·
> first-class identity reconciliation · the governed data-product catalog.

**Status (2026-06-22):** Diagram 1 (Hand-built / Python-centric) is **in progress / under review**
([Eraser link](https://app.eraser.io/workspace/6Ng61sTaot9VjtU87bEY?diagram=vheRVPpajwodCEDwqnBZ&layout=canvas));
Diagrams 2–3 (UMH-anchored, cloud-native) not yet started. *Tooling note:* Eraser's AI edit path
(`update_diagram`) tends to reverse connection arrow directions — use `manually_update_diagram`
(verbatim DSL) when direction matters.

### 13.5 Plane 4 — edge/cloud ML execution & closed-loop control (DECIDED 2026-06-22)

How models run and how their output becomes control action (refines §3 / §13 L6):

| # | Decision | Resolution |
|---|----------|-----------|
| L6.3 | ML execution tiers | **Per-site edge inference** (true edge — low latency, survives WAN loss, scores live OT off the local Mosquitto) **+ cloud/central** for training and batch serving. |
| L6.4 | Feature planes & deploy | Models consume **three planes**: **OT** (historian / live UNS), **IT** (`ods_core` / CDC), and **harmonized OT/IT** (gold features + graph context — the *premium* source). **MLflow** registry deploys the *same* model to **both** edge and cloud; **online (Redis) / offline (gold)** feature split. |
| L6.5 | Closed-loop control + HITL | Model (edge or cloud) → **HITL Operator Console** (approve / edit / reject) → approved command published to the **UNS as a Sparkplug setpoint/command topic** → site edge → **controller writeback** (OpenPLC register / OPC-UA write) → actuators. The **model never actuates directly**; the **controller executes**, the **human gates**, and all writeback flows through the single auditable **UNS command path** (no direct edge→PLC bypass). |

This makes "edge-executed, human-in-the-loop" concrete and closes the OT→IT→OT loop with a human gate.
