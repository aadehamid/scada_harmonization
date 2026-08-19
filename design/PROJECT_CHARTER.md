# Project Charter — Industrial Data Harmonization & Contextualization Home Lab

**Status:** Authoritative project definition. Supersedes scattered framing in the superseded
source docs now under `reference/` (`reference/docs/` and
`reference/engineering_drawing_business_case/`); `README.md` and `AGENTS.md` are aligned to it.

**Last updated:** 2026-08-17 (Phase 1 exit lock: replay-only; decisions otherwise unchanged since 2026-07-06)

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
| **IT** — business-transactional | on-prem relational systems (Postgres: MES/LIMS/CMMS/quality) | own business keys (lot/material/work-order/asset IDs) that don't align to OT identities |
| **ET** — engineering context | asset topology / drawings | relationships trapped in static documents/silos |

The three recurring challenges across these domains:

- **Harmonization** — cryptic OT tag → semantic metric (Plane 1).
- **Identity reconciliation** — stitching IT business keys, OT asset identities, and ET topology
  references together so they describe one asset/lot/event (the heart of Plane 3).
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

## 3. The four planes

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
| **L3 — transport/UNS** | Harmonization backbone (two-tier) | **Mosquitto 2.0.x** per-site edge broker (local autonomy) + **EMQX ≥5.9** (BSL 1.1, **single node**) central UNS broker; connected by a **Python site-forwarder** (not a raw broker bridge). **Sparkplug B 3.0** throughout |
| **L3 — OT consumers** | SCADA / storage / dashboards | Ignition Maker Edition, **TimescaleDB** historian (hypertables), Grafana |
| **L3/L4 — relational store (OLTP)** | Transactional **system of record** (role A) + derived **operational data store / ODS** (role B) | **PostgreSQL** — role A: independent MES/LIMS/CMMS/quality source systems (OT-side, CDC-captured); role B: derived ODS in an **IT-side Postgres** (zone split — §14 N16) |
| **L3/4 — analytics (OLAP)** | Streaming & analytical path | Kafka → **medallion lakehouse** (Bronze/Silver/Gold, Parquet/object store) via **Spark ETL** → **DuckDB** (interactive OLAP query — distinct from Postgres OLTP); plus a **batch/file-drop** ingestion path (§13 L4) |
| **L4 — IT/cloud** | Cloud-shaped landing zone | floci (local AWS emulation: S3, Lambda, Kinesis, Glue, Athena, RDS, …) |
| **Cross-cutting — enterprise** | SAP-like business records | ERPNext (runs on its own MariaDB — not the Postgres ODS) |
| **Cross-cutting — knowledge** | Connected-context graph + reasoning | Neo4j + GraphRAG |
| **Cross-cutting — glue** | All custom logic | **Python** managed with **`uv`** (paho-mqtt ≥2.x, pysparkplug 0.6.x *candidate — see §4.1*, Polars, Pydantic v2, Neo4j driver) |
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

> All three relational homes speak Postgres — one tooling story. The historian keeps its own OT-side
> Timescale instance; the role-B ODS lives in an **IT-side** Postgres (zone split, §14 N16); the
> role-A source systems stay in their own OT-side plant Postgres (see database topology below).

**Postgres wears two hats:**
- **Role A — source-of-record OLTP:** stands in for on-prem plant transactional systems
  (MES, LIMS, CMMS, quality, production-lot records, downtime/shift logs). A *source* to reconcile — it has
  its own business keys that don't align to OT/ISA-95 identities. This is the IT leg of IT/OT/ET.
- **Role B — derived ODS:** the pipeline's relational integration/staging store — current harmonized
  state (a SQL-queryable mirror of the retained enterprise UNS topics, §14 N1/N2), the asset/equipment master, the semantic
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
                                            CENTRAL: EMQX ≥5.9 (single node) — enterprise UNS
                                            (one harmonized namespace; rule engine,
                                             Kafka/Postgres bridges, fan-out to IT)
```

- **Mosquitto (per-site edge):** lightweight local broker; the site keeps exchanging OT data even if
  the WAN/central system is down. Holds the site's *own* (still-divergent) Sparkplug namespace.
- **EMQX ≥5.9 (central, single node):** the enterprise UNS broker — cross-site harmonization target,
  IT integrations, fan-out. **Licensing reality (verified 2026-07-06):** from v5.9 EMQX ships as one
  unified edition under **BSL 1.1** — all former Enterprise features (rule engine, native
  Kafka/Postgres data integrations) included, and **free in production on a single node only**;
  clustering requires a paid license, and each version reverts to Apache-2.0 after 4 years. (The
  older Apache-2.0 "EMQX OSS" 5.x editions had *no* Kafka/Postgres bridges — MQTT/HTTP sinks only —
  so the original "rule engine + native bridges + clustering" justification never held for any free
  edition.) The lab runs **one EMQX node** (no broker HA needed); a licensed EMQX cluster or HiveMQ
  is the enterprise upgrade path. The UNS→Kafka bridge is **custom Python** in the learning phase
  (§14 N6 — the bare-metal lesson); EMQX's native Kafka sink is the "graduate-to" comparison.
  **Network placement: in the iDMZ (Level 3.5)** as the controlled OT/IT conduit — see §13.8 Z2.
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

Three relational domains across **three Postgres homes** (all Postgres — same tooling; zone
placement per §13.8 and §14 N16):

| Home | Zone | Schemas | Owner | Role |
|------|------|---------|-------|------|
| **TimescaleDB instance** | OT (L3, per Z4) | `ts_historian.*` (hypertables) | pipeline | historian |
| **IT-side Postgres** | IT (L4) | `ods_core.*`, `erp_shadow.*` | pipeline | derived ODS (role B) |
| **Plant Postgres** (own instance) | OT (L3, per Z3) | `mes.*`, `lims.*`, `cmms.*`, `quality.*` | the "plant" | source-of-record OLTP (role A) — what CDC reads |

Rationale: the role-A systems are **independent foreign sources to reconcile** → keep separate, so CDC
genuinely captures from another system and the IT/OT/ET source boundary stays physical, not just
logical. The historian is a classic **OT-side** system (Z4), while `ods_core`/`erp_shadow` are read by
**IT-side** consumers (Neo4j, Spark, the lakehouse) — co-locating them made one instance straddle the
iDMZ (an undeclared crossing), so the ODS moved to its own IT-side home, fed by the Kafka/CDC conduits
that already cross the boundary (§14 N16; amends §12 #7). ERPNext keeps its own MariaDB; `erp_shadow`
is only an ODS convenience copy for SQL joins.

> In production you'd also split historian from OLTP for workload isolation (heavy ingest vs.
> transactions) — the zone-driven split delivers that seam early instead of "later".

### Relational schema layout (DECIDED)

**Home 1 — TimescaleDB instance (pipeline-owned, OT zone):**

| Schema | Purpose | Sample tables |
|--------|---------|---------------|
| `ts_historian` | Time-series telemetry (hypertables) | `telemetry` (ts, metric_id, value, quality — `UNIQUE (ts, metric_id)` + `ON CONFLICT DO NOTHING` for idempotent replay, §14 N9; quality enum §14 N10), `events` (alarms/faults/downtime + ISA-18.2 priority/state/ack, §14 N20) |

**Home 2 — IT-side Postgres (pipeline-owned, IT zone — §14 N16):**

| Schema | Purpose | Sample tables |
|--------|---------|---------------|
| `ods_core` | Derived ODS: current state + master data + **governed registry** + reconciliation + audit | `asset_master` (ISA-95 hierarchy), `metric_registry` (the 3-stage mapping table as a **governed data product** — owner/"gatekeeper", definition, lineage, plus per-metric `raw_min/raw_max/eu_min/eu_max` scaling §14 N17, quality mapping §14 N10, `source_cadence` §14 N8, `interpolation_type` §14 N11, UNECE Rec 20 unit codes §14 N18), `current_state` (last value per metric — mirrors the retained enterprise UNS topics), `identity_map` (+ match/survivorship/steward columns §14 N15), `lineage`, `dead_letter` (capture **and redrive** schema §14 N28), `command_audit` (§14 N24) |
| `erp_shadow` | Read-only convenience copy of ERP rows for SQL joins | `work_order_shadow`, `material_shadow` |

**Home 3 — separate plant Postgres (the "plant" source-of-record, CDC-captured, OT zone):**

| Schema | Stands in for | Sample tables |
|--------|---------------|---------------|
| `mes` | Manufacturing execution | `production_order`, `production_lot`, `lot_step` (lot-based — continuous process, §14 N13), `material_definition`, `material_lot` (§14 N14) |
| `lims` | Lab / quality | `sample`, `lab_result`, `disposition` |
| `cmms` | Maintenance | `work_order`, `asset_condition` |
| `quality` | Quality events | `nonconformance`, `inspection` |

**Boundary rules — what makes the separation *mean* something:**

1. **No cross-home foreign keys.** Source systems (`mes`/`lims`/…) never FK into `ods_core`; they carry
   their *own* business keys (`lot_id='B-2207'`, `asset_id='EQ-4471'`).
2. **Reconciliation lives in `ods_core.identity_map`** — `(source_system, source_key) → canonical_identity`,
   the explicit stitch between IT keys, OT/ISA-95 identities, and (later) ET topology. This *is* the
   artifact Plane 3 produces.
3. **Lane discipline:** the historian never holds business keys; the source systems never hold telemetry.
4. **Neo4j reads from the harmonized/reconciled side** (`ods_core` + UNS), not from the raw source schemas.

### 4.1 Pinned stack (tool names, versions, editions — verified 2026-07-06)

Version **floors** and editions/licenses the design assumes. Exact pins land in `uv.lock` /
`docker-compose.yml` as each phase starts — re-verify a row when its phase begins.

| Tool | Version / edition (floor) | License | Role (build phase) |
|------|---------------------------|---------|--------------------|
| Python + `uv` | Python ≥3.12, uv-pinned; `uv.lock` committed | PSF / MIT+Apache | all custom logic (0+) |
| paho-mqtt | ≥2.1 | EPL-2.0/EDL | MQTT transport (2+) |
| pysparkplug | 0.6.x — **candidate, not decided** (PyPI dev status: *Pre-Alpha*; Sparkplug 3.0 conformance undocumented) | Apache-2.0 | Sparkplug payloads (2+). Phase 2 acceptance test = spec behavior (NBIRTH-before-NDATA, seq 0–255 wraparound, alias resolution, NCMD Rebirth, LWT NDEATH) observed via a compliant consumer. Fallbacks: hand-rolled `spBv1.0` protobuf over paho-mqtt (also the raw-mechanism lesson), Eclipse Tahu, `mqtt-spb-wrapper` |
| Sparkplug B | spec **3.0** (= ISO/IEC 20237:2023) | — | the wire contract (2+) |
| Mosquitto | 2.0.x | EPL-2.0 | per-site edge broker ×4 (2+) |
| EMQX | **≥5.9, single node** (BSL grant covers one production node; each version → Apache-2.0 after 4 yrs) | BSL 1.1 | central enterprise UNS broker in the iDMZ (4+) |
| OpenPLC Runtime | v3 | GPLv3 | Beaumont real PLC, Modbus TCP :502 (4) |
| asyncua (opcua-asyncio) | ≥1.1 | LGPL-3.0 | Geismar real OPC-UA server (4) |
| Ignition | **Maker Edition 8.3.x** (8.1.x fallback) — free personal/non-commercial, online *leased* activation, 10k tags, 10 Perspective sessions | proprietary (free tier) | SCADA consumer (3+). Use Maker-compatible **Cirrus Link MQTT Engine** builds; in Docker do **not** set `GATEWAY_MODULES_ENABLED` (known Maker license conflict). Licensed Ignition = upgrade path |
| TimescaleDB | **Community Edition ≥2.26** on PostgreSQL ≥17.2 (compression + continuous aggregates are Community/TSL features; Apache-2.0 edition lacks them). Vendor renamed **TigerData**, 2025 | TSL (free self-hosted) | historian (3+) |
| PostgreSQL | ≥17.2 | PostgreSQL License | role-A plant OLTP + IT-side ODS home (5a+) |
| Apache Kafka | ≥4.0 (KRaft — no ZooKeeper) | Apache-2.0 | IT streaming backbone (4+) |
| Kafka Connect + Debezium | Debezium ≥3.4 | Apache-2.0 | log-based CDC milestone (5a.2) |
| Apicurio Registry | 3.x | Apache-2.0 | Kafka schema registry, Avro + compatibility rules (5a.2, §14 N26) |
| Apache Spark | ≥4.0 | Apache-2.0 | medallion ETL (6) |
| DuckDB | ≥1.2 | MIT | interactive OLAP over Parquet (3+) |
| MinIO | latest stable | AGPLv3 | hand-built S3-compatible object store for the medallion Parquet (6); floci-S3 stays the cloud-pattern demo |
| Neo4j | **Community 2025.x** (CalVer since Jan 2025; native vector index included) + `neo4j-graphrag` | GPLv3 / Apache-2.0 | knowledge graph + GraphRAG (5b, 7) |
| ERPNext | **v15 LTS or v16** (v16 GA Dec 2025) on MariaDB 10.x — Postgres unsupported | GPLv3 | enterprise business records (5b) |
| Grafana | OSS ≥11 | AGPLv3 | dashboards + observability UI (3+) |
| Prometheus | ≥3.0 | Apache-2.0 | pipeline/infra metrics (3+) |
| MLflow | ≥3.0 | Apache-2.0 | model tracking/registry (6) |
| Redis | ≥8.0 — **AGPLv3, genuinely open source again since May 2025**; Valkey ≥8.0 (BSD) = drop-in fallback | AGPLv3 | online feature store (6) |
| floci | 0.x — young project (public 2025/2026) | MIT | local AWS emulation (6+). Fallback: LocalStack **Community** for S3/Lambda/Kinesis + DuckDB in place of Glue/Athena (LocalStack gates those behind Pro) |
| UMH | **UMH Core** (`benthos-umh` + embedded Redpanda) — **adopted** abstraction target, §12 #16 | Apache-2.0 (umh-core + benthos-umh); embedded Redpanda = Redpanda Community License (source-available, free self-host); Management Console = optional SaaS | abstraction phase (Later) |
| Databricks | Free Edition (serverless, non-commercial; Unity Catalog, MLflow) | proprietary (free tier) | graduate-to managed lakehouse (§13.6, post-6) |

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
  Once the internals are understood, United Manufacturing Hub can replace the
  hand-wired MQTT/Kafka/historian/modeling bundle. This is the "graduate to enterprise tooling"
  step — adopted *after* understanding what it abstracts. **Target (DECIDED 2026-07-06, §12 #16):
  UMH Core** (single container, `benthos-umh` + embedded Redpanda, Apache-2.0, run standalone) —
  it replaces the forwarders/bridges/streaming leg; TimescaleDB + Grafana stay hand-built.

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
level and the root of every UNS topic, e.g. `lagos-chem/beaumont/...`). **Encoding (§14 N1):** these
ISA-95 topics exist on the **enterprise tier as retained plain-MQTT republish**; on the wire the site
tier is pure Sparkplug (`spBv1.0/...`, `group_id = lagos-chem:<site>`) — Sparkplug's fixed topic
namespace cannot carry `lagos-chem/...` directly.

> **Backstory:** see [`DOMAIN.md`](DOMAIN.md) — a Lagos-HQ specialty-chemicals firm that grew by
> acquisition, which is *why* each site runs a different SCADA lineage. The narrative makes every
> technical quirk below trace to a business event.

**4 sites**, each running the *same* TEP process unit + IIoT machines but representing them
differently — so the lab exercises every harmonization dimension at once:

| Site (`site`) | Heritage / SCADA | Divergence flavor | PLC realism |
|---|---|---|---|
| **Beaumont** (TX) | Legacy brownfield, **Allen-Bradley** | Cryptic AB register tags (`N7:20`, `FIC101_PV`); imperial units; short status codes | **Real OpenPLC** (Modbus TCP) |
| **Geismar** (LA) | Acquired, **Siemens** | Siemens addresses (`DB10.DBD4`, `MW100`); metric units | **Real OPC-UA** (`asyncua`, §13 L1.1) |
| **Rotterdam** (NL) | Newer European, **Ignition/MQTT-style** | Verbose semi-semantic nested names; metric units; different status vocabulary | Python-modeled |
| **Corpus Christi** (TX) | Acquired O&G/midstream, **CygNet** | Compound flat tags that *encode* hierarchy (`CC_NORTH_U12_FIC101`); mixed units | Python-modeled |

Spans register-address vs. compound-name vs. verbose-semantic naming · imperial vs. metric · **raw
integer counts vs. scaled floats** (Beaumont publishes raw ADC counts — §14 N17) · **four quality
dialects** (§14 N10) · 4 SCADA lineages · real vs. modeled PLC. Maps onto the three ISHE source
archetypes (CygNet compound / discrete-field / nested-topic), so those extracted patterns transfer
directly. Full ISA-95 path:
`enterprise (lagos-chem) → site → area → production-unit → equipment-class → equipment-id`
(*production unit* is ISA-95's continuous-process work-center level — not "line/cell", the discrete
branch; `equipment-class` in the topic path is a deliberate navigability convention while
`asset_master` keeps class as an instance attribute — §14 N19).

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
work-order/lot/material/graph-entity IDs that later feed ERPNext and Neo4j, and **governance
metadata — each metric's owner ("gatekeeper"), human-readable definition, and lineage** — so it
doubles as a governed data-product catalog (its grown-up home is `ods_core.metric_registry`, §4).
Per **§14** it additionally carries, per metric: **raw→EU scaling** (`raw_min/raw_max/eu_min/eu_max`,
N17), a **per-site quality mapping** (N10), **`source_cadence`** (N8), **`interpolation_type`**
(step | linear, N11), and **UNECE Rec 20 unit codes** (N18) — all frozen into the Phase 0 schema.
**Build this table well and the rest is plumbing.**

**Six implementation layers** (from `synthetic_data_generation_notes.md`):
1. Ingestion · 2. Augmentation · 3. PLC mapping · 4. Sparkplug · 5. Context export · 6. Replay/orchestration

### Synthetic transactional data (the IT leg)

Beyond OT telemetry, the data-generation layer also produces **synthetic relational tables** seeded
into PostgreSQL (role A) to represent plant business-transactional systems:

- **MES** — production/work orders, **lot genealogy** (lot-based, not batch — continuous process, §14 N13) + material definitions/lots (§14 N14)
- **LIMS / quality** — sample results, dispositions
- **CMMS** — maintenance work orders, asset condition
- **Operational logs** — downtime tickets, shift logs

Critically, these tables carry their **own business keys** (e.g. lot `B-2207`, asset `EQ-4471`)
that are **deliberately not aligned** to the OT asset identities (`site-a/line-2/reactor-1`) or the
ET topology references. This extends the lab's "same reality, different representation" principle
from *tags* to *transactional records*, and creates the **identity-reconciliation** problem that is
the core of Plane 3: stitching IT keys ↔ OT identities ↔ ET topology so they describe one
asset/lot/event. Reconciled records are what give the Neo4j graph its cross-domain value
(genealogy, root-cause: *which production lot ran on which reactor during which fault, against which
work order, with which lab result* — and, with the §14 N14 material model, *which finished lots
contain feedstock lot X*).

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
| **3** | OT consume | **TimescaleDB** historian (hypertables) + Grafana; optionally Ignition Maker as SCADA consumer; **real-time alerting node** (UNS → rules → alerts, §13 L2.1); introduce **Prometheus + Grafana** observability (§13 L7.1). Role-B `ods_core` is **IT-side Postgres** (§14 N16) — not this phase. |
| **4a** | Harmonization proof — the thesis (all-Python, low integration risk) | Clone the asset template to **≥2 Python-modeled sites** with *different* site tags; **Python site-forwarders** (Sparkplug session contract §14 N3; Primary-Host STATE §14 N4) conform each site → central **EMQX** enterprise UNS + retained ISA-95 republish (§14 N1); broker authn/ACLs (§14 N22) + TLS on forwarder→EMQX (§14 N23); **cross-source equivalence test suite green** |
| **4b** | Real protocols + full roster | Swap in the **real OpenPLC site** (Beaumont, Modbus TCP → Sparkplug, publishing **raw counts** scaled via §14 N17) and the **real OPC-UA site** (Geismar, `asyncua` → Sparkplug, §13 L1.1) behind the already-proven forwarder seam; add sites 3–4 |
| **4c** | Resilience & zoning | **Store-and-forward** buffer + outage drill (§13 L1.2, §14 N12); **Docker-network IT/OT segmentation** with zone labels + conduit inventory (§13 L1.3, §14 N21); one **historian-less site** (§13 L1.4); deliberate clock-skew site exercise (§14 N9) |
| **5a** | IT transactional source | Seed synthetic MES/LIMS/CMMS tables into Postgres (role A); CDC → Kafka; reconcile IT keys ↔ OT/ISA-95 identities (CDC milestone below) |
| **5b** | Context | Context-export → ERPNext events + Neo4j graph (asset↔tag↔event↔work-order↔lot↔material↔lab-result); **order-to-cash thin thread** (Sales Order → MRP → Work Order → `production_lot` → Delivery Note + Invoice, §12 #18) |
| **6** | Loop closure — **Plane 4 Track A (ML)** | Stand up the **medallion lakehouse** (Bronze/Silver/Gold) via **Spark ETL** + **batch/file-drop ingestion** (§13 L4); traditional ML (predictive maintenance / anomaly / forecasting; **flagship: yield-improvement / production-leakage detection** over TEP product streams) over historian + gold features; **MLflow** registry/tracking (§13 L6.1); **offline (gold) + online (Redis) feature store** (§13 L6.2); **human-in-the-loop, edge-executed** predictions published back into Sparkplug; floci cloud landing |
| **7** | Reasoning — **Plane 4 Track B (LLM)** | LLM/GenAI: GraphRAG over Neo4j for retrieval / troubleshooting / lineage / impact / genealogy; operator-engineer copilot |
| **Later** | Abstraction | Re-platform the forwarder/bridge/streaming leg onto **UMH Core** (§12 #16); Timescale + Grafana stay |

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

**Sequencing (amended 2026-08-17):** Phase 0 *skeleton* (uv project + directory structure) is
diagram-independent and already landed (PR #22). The *substantive* Phase 0 exit — the three-stage
mapping table — **remains gated on the Diagram 1 walkthrough lock**. Diagrams 2–3 are drawn
**just-in-time** (Diagram 2 — target decided: UMH Core, §12 #16 — before the "Later" re-platform;
Diagram 3 before the Phase 6 floci work) — neither informs the mapping table.

**Reality note (2026-07-27, still current):** Phase 0 was **split in practice**. Its *skeleton* half
— uv project (Python 3.13, ruff + pytest, no runtime deps) + the full README-only directory
structure — landed early, **before** the Diagram 1 lock (PR #22, 2026-07-07). Its *substantive* half
— the **three-stage mapping table** (`config/mappings/`, still an empty reserved folder) — **remains
gated on the Diagram 1 walkthrough**, since the walkthrough is what validates the §14 columns the
table must carry. §8.1's Phase-0 exit criterion is therefore **not met**: Phase 0 is open until that
table validates.

Phase 1 may close in parallel with the walkthrough. Its exit is replay-only (deterministic sequence + N8 clock). It does not require the mapping table or a `source_cadence` column. The Phase 1 L0 record and replay identity live in design/PHASE1_L0_CONTRACT.md.

**Reality note (2026-08-19):** Phase 1 L0 code is on `main` at `7b6cdd5` (PR #28 wiring; #29 generators; #31 Polars; #33 1 s machine stream). Runtime deps are polars + pydantic (Hamid lock: Polars replaces pandas for every tabular job). A full L0 cache (330,920,000 rows, 54.63 GiB) was written and then deleted the same day, per Hamid. Raw downloads (1.35 GiB) stay. Full Faulty Testing was never written. The Kaggle IIoT file is snapshot-per-machine, not a 1 s time series; the ~1 s class is the generated P-101 / K-201 stream. Land record: `design/PHASE1_SYNTHETIC_DATA.md`. The 2026-07-27 Phase 0 split note above remains current: the mapping table is still gated. Unit 100 P&ID Rev B is not in the repo. This note does not rewrite N8.

### 8.1 Exit criteria (definition of done, per phase)

| Phase | Done when |
|-------|-----------|
| **0** | Mapping-table YAML validates via Pydantic **including the §14 columns** (scaling N17, quality N10, `source_cadence` N8, `interpolation_type` N11, UNECE units N18); one measurement defined across all 4 sites; `LEARNING_LOG.md` growing |
| **1** | Deterministic replay (same seed → identical sequence); §14 N8 clock (simulated clock, speed factor, rebasing). L0 cache stores the friendly name (`source_column` is side metadata). Physical meaning and mapping-table `source_cadence` stay on Phase 0. |
| **2** | `mosquitto_sub` shows NBIRTH/DBIRTH/NDATA matching the mapping table; Sparkplug library verified against spec behaviors incl. Templates (§4.1, §14 N7); Mosquitto authn + ACL enforced (a mis-scoped publish is rejected — §14 N22) |
| **3** | Telemetry lands in the hypertable **idempotently** (double-replay proves no duplicates, §14 N9); Grafana reads continuous-aggregate rollups (§14 N11); alerting node implements the ISA-18.2 state machine and a TEP fault demonstrates a flood + shelving (§14 N20); Prometheus scraping the OT zone |
| **4a** | **The same physical event replayed through ≥2 sites yields identical canonical UNS output** (pytest cross-source equivalence suite); an unmapped tag lands in `dead_letter`, not silence; a late subscriber sees retained enterprise-UNS state instantly (§14 N2 demo) |
| **4b** | All 4 sites conformed, including both real-protocol sites; Beaumont raw counts scale correctly end-to-end (§14 N17) |
| **4c** | Kill EMQX/WAN for N minutes → the site keeps operating locally; on reconnect the forwarder backfills with `is_historical`, **no gaps and no duplicates** in Timescale, rollups correct (§14 N11/N12); the skewed-clock site is detected and corrected (§14 N9) |
| **5a** | Python CDC and Debezium emit `ChangeEvent`s passing the **same contract tests**, including a hard-delete case the Python poller provably misses; Apicurio schema-evolution exercise done (§14 N26/N29) |
| **5b** | The genealogy query answers *"which finished lots contain feedstock lot X?"* (§14 N13/N14); one survivorship-conflict demo resolves per policy (§14 N15); ERPNext receives curated confirmations; **the order-to-cash thread closes end-to-end** — Sales Order → plan → work order → lot → Delivery Note → Invoice, with genealogy linking every hop (§12 #18) |
| **6** | A model climbs L0→L1 through defined gates (§14 N30); one recommendation with SHAP + TTL is approved in the console → DCMD → clamped write → DDATA read-back → `command_audit` row (§14 N5/N24/N32); drift dashboard live (§14 N31); T²/SPE catches a TEP fault univariate EWMA misses (§14 N33) |
| **7** | The copilot answers a cross-domain question (fault → lot → work order → lab result) grounded in graph citations |

### 8.2 Top risks (reviewed at each phase boundary)

| Risk | Signal | Mitigation |
|------|--------|------------|
| **Single-host RAM exhaustion** — the full Phase-6 stack (EMQX + Kafka + Connect + Spark + Neo4j + ERPNext + Timescale + 2× Postgres + Ignition + MLflow + Redis + floci + 4 site stacks) is realistically **16–24 GB+** of containers | compose up fails; swapping | **docker compose profiles per phase** (`ot-core` / `streaming` / `analytics` / `enterprise` / `ml`) so only the active phase's services run; per-service `mem_limit`; stated host assumption (32 GB comfortable; 16 GB = strict profiles) |
| **Diagram/analysis perfectionism** delaying running code | days pass with no runnable artifact | Diagram 1 walkthrough timeboxed; mapping-table spine gated on Diagram-1 lock (sequencing note above); Diagrams 2–3 just-in-time |
| **Scope breadth** (~25 technologies, 8 phases, solo learner) | a phase drags far past estimate | §8.1 exit criteria as gates; YAGNI (AGENTS.md); 4a/4b/4c split front-loads the thesis, defers integration risk |
| **Library immaturity** (pysparkplug Pre-Alpha; floci young) | Phase 2/6 blockers | fallbacks pre-recorded in §4.1 (hand-rolled `spBv1.0` protobuf; LocalStack + DuckDB) |
| **License / product drift** (EMQX BSL, UMH Core pivot, Redis relicensing) | upgrade surprises | versions/editions pinned in §4.1; re-verify at each phase start; §12 #16 |

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
- **Event time at the source; idempotent sinks everywhere** — timestamps are assigned at the edge
  publisher (UTC ms); transport is at-least-once and every sink dedups (§14 N9).
- **Quality is first-class** — every sample carries Good/Uncertain/Bad/Stale; real-time and ML
  consumers act on it (SPC/ML use Good only; STALE-on-NDEATH) (§14 N10).
- **Enforce the namespace** — broker authentication + per-branch topic ACLs make topic ownership a
  technical property, not an aspiration; only the console identity may command (§14 N22).
- **No IT-initiated connections into OT** — every cross-zone flow terminates in the iDMZ; conduits
  are documented and OT always dials out (§14 N21).

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
| `design/LEARNING_LOG.md` | Learning log & glossary — durable concepts land here when teaching scaffolding is pruned |
| `design/PHASE1_L0_CONTRACT.md` | Phase 1 L0 record + replay identity (authoritative for ingest/augment/replay) |
| `design/PHASE1_SYNTHETIC_DATA.md` | Phase 1 land / persist / disk record (HTML twin + assets) |
| `design/E2E_WALKTHROUGH.md` | End-to-end walkthrough guide — three threads (order · telemetry · control-back), deck coverage, describe-anyway list for consciously-omitted systems |
| `design/WALKTHROUGH_PROGRESS.md` | Live walkthrough cursor — per-step status + resume prompt (not a design source) |
| `design/uns_home_lab_notes.md` | Vision & high-level scope *(archived vision note — superseded on decided items; see §4/§12/§13)* |
| `design/hand_built_sparkplug_uns_notes.md` | Architecture option: hand-built *(archived — superseded on decided items)* |
| `design/umh_anchored_sparkplug_uns_notes.md` | Architecture option: UMH-anchored (abstraction phase) *(archived — describes UMH Classic; adopted target = UMH Core, §12 #16)* |
| `design/python_centric_uns_notes.md` | Implementation philosophy: Python-centric *(archived — superseded on decided items)* |
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
   autonomy) + **EMQX** central UNS, connected by a **Python site-forwarder** (not a raw broker
   bridge, to preserve Sparkplug state). Harmonization becomes two-step (local mapping → cross-site
   conforming). See §4. **Amended (2026-07-06):** pinned **EMQX ≥5.9, single node, BSL 1.1** — the
   pre-5.9 "OSS" edition had no Kafka/Postgres bridges and the BSL grant covers one production node;
   see §4 licensing reality + §4.1 pinned stack.
3. ~~Historian choice~~ — **DECIDED (2026-05-30):** **TimescaleDB** (SQL everywhere; modeling, not
   ingest rate, is the bottleneck). See §4 database topology. **Amended (2026-07-06):** pinned
   **TimescaleDB Community Edition ≥2.26** (TSL license, free self-hosted — **compression +
   continuous aggregates required**, and the Apache-2.0 edition lacks them) on **PostgreSQL ≥17.2**;
   vendor renamed **TigerData** (2025). See §4.1.
4. ~~How literal the PLC layer is~~ — **DECIDED (2026-05-30):** **hybrid** — most sites Python-modeled
   cryptic tags; **one** site runs a real **OpenPLC** runtime over **Modbus TCP** (the realism lesson
   once, without taxing every site). Start Python-modeled in Phase 2; add the OpenPLC site in Phase 4.
   **Amended (2026-06-21, §13 L1.1):** now **two** real-protocol sites — OpenPLC/Modbus (Beaumont) **+**
   a real **OPC-UA** server (`asyncua`, Geismar); Rotterdam & Corpus Christi stay Python-modeled.
5. **When ERPNext and Neo4j enter** — Phase 5 as planned, or earlier stubs.
6. ~~Number & identity of sites~~ — **DECIDED (2026-05-30):** enterprise **Lagos Specialty Chemicals**
   (root `lagos-chem`); **4 sites** — Beaumont (AB, real OpenPLC/Modbus), Geismar (Siemens, **real
   OPC-UA** per §13 L1.1), Rotterdam (Ignition-style, Python-modeled), Corpus Christi (CygNet,
   Python-modeled). See §6.
7. ~~Postgres deployment~~ — **DECIDED (2026-05-30):** **consolidate historian + role-B ODS in the
   TimescaleDB instance** (separate schemas: `ts_historian` / `ods_core` / `erp_shadow`); keep the
   **role-A source systems** (`mes`/`lims`/`cmms`/`quality`) in a **separate** Postgres home so CDC
   captures from a foreign system. floci-RDS remains a separate cloud-pattern demo. See §4.
   **Amended (2026-07-06, §14 N16):** the consolidation straddled the iDMZ (the historian is OT-side
   per Z4, but `ods_core` is read by IT-side consumers) — `ods_core` + `erp_shadow` now live in their
   own **IT-side Postgres**; three Postgres homes total. See §4.
8. ~~CDC mechanism~~ — **DECIDED (2026-05-30):** **start Python poll, design for Debezium** — with an
   explicit hands-on Debezium learning milestone (goal is to *learn* Debezium, not avoid it). Three
   steps inside build Phase 5a — see §8.
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
    not duplicate the retained enterprise UNS topics (§14 N2) / Timescale `current_state` (current state),
    Kafka (streaming), or Neo4j native vector index (GraphRAG). **Learning Redis IS a goal** → scheduled as a deliberate hands-on
    milestone (same pattern as Debezium), most naturally the **online feature store in Phase 6** (teaches
    the online/offline feature-store split). Candidate secondary roles: LLM semantic/response cache +
    copilot session memory (Phase 7), API cache/rate-limit (if FastAPI). Evaluate at Phases 6–7.
    **License note (2026-07-06):** Redis 8 returned to genuine open source (**AGPLv3**, May 2025), so
    "Redis (open source)" is accurate again; **Valkey** (BSD, CNCF) is the drop-in fallback if AGPL
    ever matters.
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
16. ~~UMH abstraction target: Core vs Classic~~ — **DECIDED (2026-07-06): adopt UMH Core** as the
    abstraction-phase target. **Licensing verified:** `umh-core` and `benthos-umh` are **Apache-2.0**
    (genuinely open source); the embedded **Redpanda** broker is source-available (Redpanda Community
    License — free to self-host); the cloud **Management Console is an optional SaaS** — the lab runs
    Core **standalone via YAML config** to stay fully self-hosted. **What it abstracts:** UMH Core
    replaces the Python site-forwarders / protocol converters and the hand-wired UNS→Kafka bridge
    (benthos-umh Data Flow Components: Modbus, OPC-UA, and stateful **Sparkplug B inputs** — tracks
    births/aliases/seq — plus Kafka/UNS outputs) and the Kafka leg (embedded Redpanda). **What stays
    hand-built:** TimescaleDB + Grafana (Core does not bundle the Classic historian/visualization
    stack). Diagram 2 (§13.4 #2) depicts UMH Core. The UMH-anchored note describes the legacy Classic
    bundle — kept for background only.
17. **IT/OT best-practice review adoptions** — **DECIDED (2026-07-06):** see **§14** (N1–N35 ledger:
    Sparkplug namespace encoding, forwarder session contract, primary hosts, DCMD command path,
    replay clock, time/quality/historian semantics, lot-based production model, conduit inventory +
    broker auth/TLS/audit, functional-safety correction, and the Plane-4 MLOps additions).
18. **Order-to-cash thin thread** — **DECIDED (2026-07-06):** Plane 2 gains the **demand→floor
    direction** (previously only confirmations-up): one **ERPNext Sales Order → MRP/Production Plan →
    Work Order**, synced into `mes.production_order` (the plant's own key space — still deliberately
    misaligned), driving one `production_lot`; the thread closes with an ERPNext **Delivery Note +
    Sales Invoice**. Gives the lab all ten handoffs of the industry order thread (Thread A,
    `design/E2E_WALKTHROUGH.md`) and makes ISA-95 L3↔L4 *schedule-down + performance-up*. Phase 5b
    scope (ERPNext-native, ~a day); §8.1 exit criteria updated. CRM stays out — the Sales Order is
    the lab's entry point.
19. **No separate WMS** — **DECIDED (2026-07-06):** warehouse semantics are represented as **ERPNext
    stock movements + `mes.material_lot` staging/consumption events**, not a WMS system. A real WMS
    (bins, waves, pick paths, dock scheduling) is *described* in walkthroughs at its proper place
    (Thread A steps 3 & 9, `design/E2E_WALKTHROUGH.md`) but adds no harmonization/contextualization
    lesson the lab doesn't already teach. Joins the §13.3 conscious-out list.

**Tooling (DECIDED 2026-05-30):** **`uv`** is the package/project manager for everything — `uv add` /
`uv sync` / `uv run`, `pyproject.toml` + committed `uv.lock`, uv-pinned Python version. No pip/poetry.

**Diagrams (DECIDED 2026-06-21):** all project diagrams are created with the **Eraser MCP** and saved
to the Eraser workspace/folder **`scada_harmonization`**; each architecture view / implementation type
(§5) gets its own diagram there, linked from the relevant design doc. See AGENTS.md → "Diagrams".

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
| L2.2 | UNS/stream | **No separate hot store** — TimescaleDB + the **retained enterprise-tier UNS topics** (§14 N1/N2; Sparkplug operational messages themselves are never MQTT-retained) cover near-real-time |
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
(Prometheus) · MLflow.** Optional *later* "graduate-to / explore" milestones (§13.6):
**Databricks Free Edition** (managed lakehouse) · **Apache Iggy** (alternative streaming).

### 13.3 Deliberately out of scope

CRM/Salesforce · **separate WMS** (ERPNext stock moves + `material_lot` events cover the warehouse
semantics — §12 #19) · separate MDM platform · extra lab systems (ELN/instrument/chem/Protec) · pilot
plants · EDMS (ET topology is synthesized) · separate real-time "hot" store · Power BI (Grafana +
DuckDB/notebooks; Superset/Metabase = OSS-BI upgrade) · separate vector DB · Vault/IAM now · real AWS now.

### 13.4 The three implementation variants (architecture diagrams)

The three architecture notes (§5) are realized as **three full architecture diagrams**, all saved to
the project's Eraser folder **"SCADA Harmonization"** (= the convention's `scada_harmonization`), each
delivering the *same* capability set:

1. **Hand-built / Python-centric** — self-hosted OSS, every boundary explicit; the learning
   architecture built across Phases 0–7 (EMQX, Kafka, TimescaleDB, Spark, DuckDB, Neo4j, MLflow,
   Prometheus, Python forwarder/enrichment/alerting).
2. **UMH-anchored** — United Manufacturing Hub collapses the L3 ingestion/streaming
   backbone into one platform; the abstraction phase (§5). **Target: UMH Core (§12 #16, DECIDED)** —
   the diagram depicts Core (benthos-umh DFCs + embedded Redpanda; TimescaleDB/Grafana remain the
   lab's own).
3. **Cloud-native (floci → AWS)** — the same design mapped onto floci-emulated AWS (IoT Core,
   Kinesis, Glue/Spark, Athena, S3 medallion, RDS, SageMaker, KMS/IAM/CloudWatch) ≈ the reference
   target architecture; real AWS is the production upgrade.

> Where the lab **exceeds** the reference: Sparkplug-B contract · two-tier broker + Python
> site-forwarder (the harmonization point) · Neo4j + ISO 15926/DEXPI ontology · GraphRAG/GenAI ·
> first-class identity reconciliation · the governed data-product catalog.

**Status (2026-07-06): Diagram 1 v2 is the working diagram.** The full §14-aligned redraw
(28 review findings applied: single-node EMQX + retained ISA-95 UNS, DCMD writeback + DDATA read-back
+ command_audit, per-site alerting/Redis, per-zone Prometheus, edge-pull model staging, conduits
C1–C6, UNS→Kafka bridge, Ignition, ET-topology leg, lot-based MES, order-to-cash) lives at
[Diagram 1 v2 (2026-07-06)](https://app.eraser.io/workspace/MgnB91QGOhX8xWiKeaAK?diagram=133RhOiN_-G6Ko5kaTj8&layout=canvas)
in the "SCADA Harmonization" Eraser folder. The
[2026-06-23 original](https://app.eraser.io/workspace/6Ng61sTaot9VjtU87bEY?diagram=vheRVPpajwodCEDwqnBZ&layout=canvas)
is kept for history. The teaching walkthrough and the "lock" target v2. Diagrams 2–3 are drawn
**just-in-time** (see §8 sequencing note) — Phase 0 no longer waits on them. Diagram 2's target is
decided: **UMH Core** (§12 #16). *Tooling note:* Eraser's AI edit path
(`update_diagram`) tends to reverse connection arrow directions — use `manually_update_diagram`
(verbatim DSL) when direction matters.

### 13.5 Plane 4 — edge/cloud ML execution & closed-loop control (DECIDED 2026-06-22)

How models run and how their output becomes control action (refines §3 / §13 L6):

| # | Decision | Resolution |
|---|----------|-----------|
| L6.3 | ML execution tiers | **Per-site edge inference** (true edge — low latency, survives WAN loss, scores live OT off the local Mosquitto) **+ cloud/central** for training and batch serving. |
| L6.4 | Feature planes & deploy | Models consume **three planes**: **OT** (historian / live UNS), **IT** (`ods_core` / CDC), and **harmonized OT/IT** (gold features + graph context — the *premium* source). **MLflow** registry deploys the *same* model to **both** edge and cloud; **online (Redis) / offline (gold)** feature split. **Sourcing rule (2026-07-06, Diagram-1 v2 review):** *cloud* training sources the OT-historian plane **from the lakehouse copy** (Bronze/Silver — that data already crossed via conduit C2); it never opens a direct read into the OT-zone historian. *Edge* inference scores the live plane off the local site broker, with online features **computed at the edge** from the single-sourced definitions (§14 N35) — no Gold→edge materialization push. |
| L6.5 | Closed-loop control + HITL | Model (edge or cloud) → **HITL Operator Console** (approve / edit / reject) → approved command delivered as a **Sparkplug DCMD message** — the recommendation event flows down through the iDMZ EMQX, and the **site-forwarder (acting as the site's host application) issues the DCMD on the site Mosquitto** where the target Edge Node's session lives (Sparkplug has no free-form "setpoint topics"; §14 N5) → **controller writeback** (clamped OpenPLC register / OPC-UA write) → actuators; the **DDATA read-back confirms** the write and feeds the audit trail (§14 N24). The **model never actuates directly**; the **controller executes**, the **human gates**, and all writeback flows through the single auditable **UNS command path** (no direct edge→PLC bypass). *Refined by §13.7:* HITL is **graded** (L0 shadow / L1 alert / L2 recommend / L3 closed-loop, P3 + §14 N30) and guarded by **defense-in-depth safety layers** (P2); recommendations carry **explainability** (P4) and a **validity TTL** (§14 N32). |

This makes "edge-executed, human-in-the-loop" concrete and closes the OT→IT→OT loop with a human gate.

### 13.6 Optional "graduate-to" / explore components (DECIDED 2026-06-22)

Two free tools evaluated and slotted as **post-hand-built options** (the upgrade-friendly / abstraction
pattern — **neither changes the hand-built core**):

| Component | Decision | Where it fits |
|-----------|----------|---------------|
| **Databricks Free Edition** — managed cloud lakehouse (Delta Lake, **Unity Catalog**, Spark/Photon, MLflow, Genie AI/BI, Lakeflow; free, non-commercial, serverless) | **Adopt as a "graduate-to managed lakehouse" learning milestone + the managed-lakehouse option in the cloud-native variant.** Build the medallion + Spark + MLflow **by hand first** (the learning), then mirror Bronze/Silver/Gold onto Databricks to learn **Delta Lake**, **Unity Catalog** (fills the lab's lake-catalog/governance gap), Lakeflow, and Genie. **Not** in the hand-built core (cloud-hosted; would abstract the bare-metal lesson). Low lock-in (Delta + Unity Catalog are open source). | §13 L4 analytics layer → Databricks; cloud-native variant (§13.4 #3) may use Databricks in place of raw Glue/Athena/SageMaker. |
| **Apache Iggy** — Rust single-binary ultra-high-throughput persistent streaming (incubating) | **Keep Kafka as the backbone; add Iggy as an *optional explore milestone*** on a **non-Debezium** stream (e.g. UNS→analytics fan-out or alerting) to learn it and compare hands-on. **Do not replace Kafka:** it would break the **Debezium CDC milestone** (Iggy has no Kafka-Connect/Debezium/Schema-Registry ecosystem), the lab's bottleneck is **modeling, not ingest rate**, and Iggy is **not production-ready**. | Streaming layer (§4) — Kafka default; Iggy a swap-seam experiment (Phase 6+/later). |

### 13.7 Patterns adopted from the reference-architecture audit (DECIDED 2026-06-23)

A detailed external reference (a CPG yield-intelligence / autonomous-yield-management architecture —
local-only `design/SAMPLE_*`) was audited pattern-by-pattern. The design was validated; the items below
are **adopted to close real gaps** (CPG specifics dropped — general industrial-AI patterns kept). They
refine, not replace, prior decisions.

**Tier 1 — clear gaps now closed:**

| # | Pattern | How it lands in the lab |
|---|---------|-------------------------|
| P1 | **Scan-rate strategy tied to process physics** + **deadband/compression** + cascade check | Formalize the mapping table's `cadence` into an explicit **scan rate + RBE deadband per metric**, classed by physics: **fast process vars ~1 s · supporting ~5 s · environmental ~30 s · state = on-change**. The rate must hold across every link (replay → PLC/poll → Sparkplug RBE → historian); deadband too wide *hides* slow drift. "Scan rate decides whether the model can even *see* the problem." |
| P2 | **Defense-in-depth safety for closed-loop** (not just a human gate) | Three independent layers guard any setpoint writeback: (1) **model safety-envelope** — recommendations clamped to a safe range in the serving layer; (2) **PLC/edge-side limits** — the writeback validates & **rejects/clamps** unsafe setpoints (hardcoded bounds, independent of the model); (3) an **independent safety-check service** *not on the model write path* — an independent **BPCS-level guard, NOT an SIS** (a real plant would have a separate certified SIS below all three layers; the lab consciously does not model one — §14 N25). The model can never drive the process unsafe even if a human approves a bad value. Extends §13.5 L6.5. |
| P3 | **Graded HITL maturity** (replaces single-mode HITL) | **L0 Shadow** (score live data, surface nothing — every model starts here; §14 N30) → **L1 Alert** (notify, operator acts) → **L2 Recommend** (specific setpoint + confidence, operator accepts/edits) → **L3 Closed-loop** (auto-write with override + the P2 safety layers). Climb the ladder only where feedback is fast and stakes low, gated by explicit promotion criteria with automatic demotion (§14 N30); **some metrics stay L1-only**. Refines §13.5 L6.5. |
| P4 | **Explainability as a required ML output** | Every alert/recommendation (edge **and** cloud) must carry a **feature attribution** (SHAP for tabular; saliency/Grad-CAM where applicable) — "top factor: reactor feed-temp +4 °C (SHAP 0.47)". The HITL console renders the *why*; without it operators can't trust or act. Hard requirement on the model-serving contract. |
| P5 | **SPC / adaptive control charts** as the detection method | Frame Track-A yield/quality detection as **statistical process control** — **EWMA / CUSUM / adaptive limits** — with ML **adjusting the chart parameters from covariates** ("dynamic SPC"), not generic "anomaly detection." This is the established, explainable yield method and the bare-metal mechanic the lab should teach. **Extended (§14 N33):** two-level SPC — univariate EWMA/CUSUM on named yield metrics **plus PCA-based Hotelling T²/SPE with contribution plots** across the correlated TEP metric set (several TEP faults shift correlation structure without moving any single mean — invisible to univariate charts). |

**Tier 2 — strengtheners (we had analogs; now explicit):**

| # | Pattern | How it lands |
|---|---------|--------------|
| P6 | **Equipment-type templates** (UDT analog) | Define an **equipment class once** (its metric set + units + ranges + scan/deadband + alarm limits) as a Pydantic type; **instantiate per site/asset** binding only the site-specific PLC tag. This is *how harmonization scales* to N sites consistently — the spine's type system. |
| P7 | **Bronze-layer schema validation** | **All data lands in Bronze as-is** (immutable raw + ingest metadata); validation against the governed `metric_registry` runs at the **Bronze→Silver promotion** — **missing / unexpected / schema-drifted** metrics are recorded in `dead_letter` *with a pointer back to the Bronze record* (never dropped from Bronze, so rejects stay reprocessable — §14 N27/N28); only conforming data advances to Silver. Makes the registry an *enforced* contract, not just documentation. |
| P8 | **Business data joins downstream, not in the UNS** (explicit principle) | The **UNS/Sparkplug carries OT real-time only**; IT/business records (CDC) join OT **downstream** in `ods_core` / lakehouse / Neo4j — they run on different timescales (min/hr vs ms) and must not flow through the MQTT broker. (We already do this; now stated as a principle.) |
| P9 | **Golden-batch / golden-run reference** | Persist the best-performing historical reference; models (and operators) compare the live run against it for drift and yield. **For the continuous TEP process this is a *golden operating window* per (asset, operating mode / product grade)** — steady-state statistics + the PCA baseline from §14 N33, not a time-aligned batch profile (an ISA-88 concept with no trajectory to align here; §14 N13). Batch-style golden profiles can still be demonstrated on IIoT machine run cycles. |

**Tier 3 — conscious scope decisions (noted, not adopted):**
- **Machine vision / CNN modality** — *out* (charter §7 already dropped CV/VLM); our anchors are time-series.
- **Connected-worker / manual-operation digitization** (pick-to-light, AR, connected-worker apps) — *out* (no human operators in a synthetic lab); transferable bit kept: **operator/shift/lot as ML covariates**.
- **Broker topology divergence** — the reference uses **no central broker** (per-plant brokers → cloud gateway); we **keep the central EMQX UNS cluster** as a *conscious* choice (the "central UNS broker" school; richer for the cross-site harmonization thesis). Both are valid.

### 13.8 OT/IT network zoning & the iDMZ (DECIDED 2026-06-23)

Resolved while refining the hand-built architecture diagram (Diagram 1), grounded in Purdue/ISA-95 +
IEC 62443 and UNS best-practice research. These fix *where the OT/IT air gap sits* and *what lives on
each side* — a network-zone question distinct from the data-domain (IT/OT/ET) framing of §2.

**Two distinct axes (don't conflate them):**
- **Data domain** (§2 IT/OT/ET) — *what kind* of data: OT telemetry vs IT transactional vs ET topology.
- **Network zone** (Purdue / the diagram's zones) — *where on the network*: OT Levels 0–3 vs the **iDMZ
  (Level 3.5)** vs IT/Enterprise Levels 4–5. The iDMZ is the IT/OT boundary; all cross-boundary traffic
  terminates there.

| # | Decision | Rationale |
|---|----------|-----------|
| Z1 | **The iDMZ (Level 3.5) is the OT/IT air gap.** OT zone = Levels 0–3 (operational/real-time); IT/Enterprise/Cloud zone = Levels 4–5. | Purdue/IEC 62443: only enterprise (L4–5) sits above the iDMZ; everything operational is below it. |
| Z2 | **The central EMQX enterprise UNS broker sits *in* the iDMZ (Level 3.5)** as the controlled OT/IT conduit — *not* purely OT, *not* IT. Per-site **Mosquitto edge brokers stay OT** (Levels 2–3, local autonomy). | Documented best practice: site/edge brokers buffer in OT; the **enterprise broker is the DMZ conduit** (HiveMQ/Siemens "broker-as-DMZ-gateway"). Forwarders publish up to it; OT historian/dashboards/console subscribe down; IT analytics bridge across. |
| Z3 | **MES, LIMS, CMMS, Quality + the plant Postgres are OT-side (ISA-95 Level 3)** — even though they are "IT data-domain." **ERPNext (Level 4) stays IT-side.** | ISA-95: MES/LIMS/CMMS/WMS/historian are Level 3 (below the iDMZ); only ERP/enterprise is Level 4. Their **CDC (Debezium) is an iDMZ crossing** carrying transactional data *up* to IT analytics — reinforces §13.7 P8. |
| Z4 | **TimescaleDB historian + Grafana + the HITL operator console + safety layers are OT-side (Level 3).** | Historians and SCADA dashboards are classic OT systems; control/HITL must stay operational. The earlier draft wrongly stranded them above the gap. |

**The iDMZ is crossed by exactly three flows** (everything else is zone-internal): harmonized telemetry
**up** (EMQX → Kafka), transactional data **up** (plant Postgres → Debezium → Kafka), and cloud-ML
recommendations **down** (Model Serving → EMQX → operator console). Model/feature deployment to the edge
also transits the iDMZ. The closed-loop **command path is mediated by the iDMZ UNS broker** but control
execution stays OT-internal (broker → forwarder → PLC-clamp → controller). *The three flows are realized
as five documented conduits with an explicit connection-initiation rule — see §14 N21.*

---

## 14. IT/OT best-practice review adoptions (DECIDED 2026-07-06)

A multi-lens best-practice review (UNS/Sparkplug contract · IEC 62443/Purdue zoning · ISA-95/-88
modeling · streaming & lakehouse engineering · historian operations · industrial-ML safety · tool
fact-check · plan integrity) was run against current industry sources. It **validated the
architecture-level design** — forwarder-not-bridge, EMQX-in-iDMZ, MES/LIMS at Level 3, P8
business-joins-downstream, graded HITL, and SPC-first all match or exceed documented practice — and
surfaced gaps concentrated one layer down, at the **protocol/semantics level**. The ledger below
closes them. Anchoring standards: **Sparkplug 3.0** (ISO/IEC 20237:2023), **IEC 62443** + **NIST SP
800-82r3**, **ISA-95 Parts 1–2**, **ISA-106** (continuous-process automation), **ISA-18.2/IEC 62682**
(alarm management), **IEC 61511** (functional safety), **OPC UA/IEC 62541** (quality codes),
**UNECE Rec 20** (units of measure).

### 14.1 UNS & Sparkplug contract

| # | Decision | Resolution |
|---|----------|-----------|
| N1 | **Namespace encoding — Sparkplug at the edge, retained ISA-95 UNS at the enterprise** | Sparkplug B fixes topics to `spBv1.0/{group_id}/{msg_type}/{edge_node_id}/[{device_id}]` — a literal `lagos-chem/...` topic cannot exist in a pure Sparkplug system, so §6's "topic root" needed an encoding decision. **Site tier = pure Sparkplug:** `group_id = lagos-chem:<site>` (Parris-style delimiter encoding), `edge_node_id` = data collector per area/production-unit, `device_id` = equipment. **Enterprise tier:** the site-forwarder (or an EMQX-side republisher) decodes Sparkplug and *also* publishes canonical JSON onto **plain-MQTT retained ISA-95 topics** `lagos-chem/<site>/<area>/<production-unit>/<equipment-class>/<equipment-id>/<metric>` on EMQX. Teaches both schools: Sparkplug state management at the edge, a browsable retained UNS at the enterprise. |
| N2 | **Retained-state semantics corrected** | Sparkplug operational messages (BIRTH/DATA/DEATH) are **never MQTT-retained**; last-known-value lives in consuming hosts' BIRTH-seeded state. The N1 enterprise republish topics **are** the lab's retained UNS state — `ods_core.current_state` mirrors *those* (L2.2 and §12 #12 wording amended). Live demo: a late-joining `mosquitto_sub` sees the retained enterprise topics instantly but nothing on `spBv1.0/#` until a rebirth. |
| N3 | **Forwarder Sparkplug session contract** | The forwarder is a **compliant Sparkplug Edge Node per site** on EMQX: its own MQTT session with Will-based NDEATH (bdSeq), its own NBIRTH declaring every conformed metric, per-session `seq` 0–255, and its **own alias space** remapped via `metric_registry` (raw pass-through of site payload bytes is invalid — aliases/seq are session-scoped to the site broker). It implements the one mandatory command, **NCMD "Node Control/Rebirth"**, translating central rebirth requests into local rebirths when stale. Store-and-forward flush on reconnect = fresh NBIRTH (incremented bdSeq) **first**, then buffered values with `is_historical=true` + original timestamps, in order. This contract doubles as the Phase 4 test list. |
| N4 | **Primary Host Application per tier** | Site tier: the **site-forwarder is the site's Primary Host** (publishes retained `STATE` on the site Mosquitto; local publishers buffer while it is OFFLINE). Central tier: the **historian/Kafka-ingest service is Primary Host on EMQX** (forwarders buffer and flush on its `STATE` ONLINE — L1.2 implemented the standard Sparkplug way instead of ad hoc). |
| N5 | **Commands are NCMD/DCMD messages, not a "setpoint topic"** | Sparkplug has no free-form command topics. Path: HITL console approval → recommendation event down through iDMZ EMQX → **site-forwarder (acting as the site's host application) issues DCMD** to the target Edge Node *on the site Mosquitto where that node's session lives* → clamped OpenPLC/OPC-UA write → **DDATA read-back = the confirmation and the audit record** (console shows commanded-vs-confirmed). §13.5 L6.5 amended. |
| N6 | **Sparkplug decode point + Kafka topic/key design** | One Python **UNS→Kafka bridge** on the IT side: subscribes to EMQX, holds BIRTH state (stateful alias resolution — *the* lesson about Sparkplug consumers), decodes protobuf, validates into Pydantic `CanonicalTelemetry`, publishes JSON to Kafka. **Kafka carries harmonized records, never Sparkplug bytes.** Topics: `uns.telemetry.<site>` (4) + `uns.events` + `uns.commands`; record **key = canonical asset path** so one asset's metrics stay ordered on one partition (1:1 MQTT→Kafka topic mapping is a topic-explosion anti-pattern). EMQX's native Kafka sink = the graduate-to comparison. |
| N7 | **Sparkplug Templates (UDTs) on the wire** | Each P6 equipment class is *also* emitted as a Sparkplug **Template definition** in NBIRTH with template instances per device (≥1 class, e.g. pumps). Ignition MQTT Engine materializes these as UDT definitions/instances automatically — P6's lesson moved from Python-internal to the actual contract layer. Verify Template support in the Sparkplug library early in Phase 2 (feeds the §4.1 pysparkplug decision). |

### 14.2 Time, quality & historian semantics

| # | Decision | Resolution |
|---|----------|-----------|
| N8 | **Replay clock & cadence** (unblocks Phase 1) | One orchestrator-owned **simulated clock**: dataset timestamps rebased to wall-clock-now at replay start, single configurable speed factor; the Sparkplug payload timestamp = simulated event time (UTC ms). **TEP's native cadence is 3 minutes** (Rieth et al. dataset), so TEP-sourced metrics are honestly re-classed into the slower P1 scan classes (30 s–3 min); the ~1 s "fast" class is carried by the IIoT machine dataset + Python generators — no interpolated pseudo-dynamics for SPC to "detect". (Optional later: re-run an open TEP simulator, e.g. `tep2py`, at a finer step.) The mapping table gains a **`source_cadence`** column so replay cadence vs scan class is a per-metric contract. Accelerated backfill writes historical timestamps and never feeds the live alerting path. |
| N9 | **Time & delivery semantics** | Timestamps are assigned **at the edge publisher** (UTC ms); brokers/historian never re-stamp. Pipeline stance: **at-least-once transport + idempotent sinks everywhere** — `ts_historian.telemetry` gets `UNIQUE (ts, metric_id)` + `ON CONFLICT DO NOTHING` (hypertable unique keys must include time; decided now because it is hard to retrofit); the Phase 6 Spark milestone explicitly includes event-time watermarks + dedup. Real-time consumers (alerting, `current_state`) **skip `is_historical` data**. Teaching milestone: one site (Corpus Christi) replays with a deliberately skewed, drifting clock (+90 s) that the conforming step must detect and correct; Prometheus tracks per-site timestamp lag (the lab analog of NTP monitoring). |
| N10 | **Quality-code model** (the *fifth* divergence dimension) | Canonical enum **Good / Uncertain / Bad / Stale (+ reason)** on `CanonicalTelemetry`, mapped **per site**: Geismar = real OPC UA StatusCodes; Sparkplug "Quality" metric property (0=BAD/192=GOOD/500=STALE convention) where used; Beaumont/Modbus = comms-inferred only (Modbus has no quality). Consuming hosts mark all of a node's metrics **STALE on NDEATH** (Sparkplug rule). Downstream: SPC/ML consume Good samples only (a stale flatline fed to EWMA suppresses exactly the drift the yield use case must detect); dashboards render non-Good distinctly; Bad routes to events/dead-letter. |
| N11 | **Historian lifecycle** (named now, tuned in Phase 3) | Five explicit decisions when built: chunk interval; **compression policy with delay > the longest planned outage drill**; retention + **continuous aggregates** per metric class (e.g. raw 90 d, 1-min rollup 1 yr — dashboards/SPC query rollups, not raw); per-metric **`interpolation_type` (step \| linear)** column in `metric_registry` consumed by a documented `time_bucket_gapfill()`/`locf()`/`interpolate()` query pattern (RBE data is change-only — every analytics query needs gap-fill semantics). Phase 4 run-and-observe: backfill an outage, verify rollups + compressed-chunk behavior. |
| N12 | **Store-and-forward semantics** (completes L1.2/L1.4) | Buffer = **24 h at rated scan rates**, on-disk (SQLite/file queue — itself a bare-metal lesson); overflow evicts **oldest**; replayed messages carry original timestamps + `is_historical` (N3). Historian backfills normally (see N11 compression delay); alerting/`current_state` ignore replays. **L1.4 corollary:** the buffer duration *is* the historian-less site's maximum history-loss budget — verified by an outage drill. |

### 14.3 Data modeling & the IT leg

| # | Decision | Resolution |
|---|----------|-----------|
| N13 | **Continuous process ⇒ lot-based accounting** (ISA-88 out, ISA-106 in) | LSC/TEP is a **continuous** process — there are no physical batches, and ISA-88's recipe/phase model does not apply (ISA-106 is the continuous-process counterpart). `mes.batch`/`batch_step` are reframed as **`mes.production_lot`** (+ `lot_step` if needed) with explicit `start_ts`/`end_ts` and product grade; a "lot" = a defined production time window / grade campaign. **Genealogy = time-window joins** (lot ↔ telemetry ↔ consumed material lots), not batch-record joins. P9's reference becomes a **golden operating window** per (asset, operating mode/grade) — steady-state statistics + the N33 PCA baseline; batch-style golden profiles can still be demonstrated on IIoT machine run cycles. |
| N14 | **Material model** (ISA-95 Part 2) | Add **`mes.material_definition`** (product/feedstock catalog) and **`mes.material_lot`** (lot_id, definition, quantity, produced-by / consumed-by production run, timestamps). Genealogy is definitionally consumed-lot → produced-lot; `CONSUMED_MATERIAL` graph edges now have source tables, and the recall-scoping query ("which finished lots contain feedstock lot X?") becomes the Plane 3 flagship demo. |
| N15 | **`identity_map` upgraded to a real MDM analog** | Add `match_rule`, `match_confidence`, `valid_from`/`valid_to`, `steward` columns; write a one-page **survivorship policy** per attribute domain (nameplate attributes: ET topology wins; maintenance status: CMMS wins; financial: ERP wins), enforced by the Python reconciliation service; seed **one deliberate fuzzy-match case** in the synthetic data (`P-101A` vs `EQ-4471` vs "Feed Pump A") so probabilistic matching is exercised. Keeps the L3.1 no-platform decision; makes the "MDM analog" claim true. |
| N16 | **`ods_core` zone placement — split along the zone line** (amends §12 #7) | The consolidated Timescale instance straddled the iDMZ: §13.8 Z4 puts the historian OT-side while Neo4j/Spark/lakehouse (IT-side) read `ods_core` — an undeclared crossing. Resolution: **`ts_historian` stays in the OT-side Timescale instance; `ods_core` + `erp_shadow` move to an IT-side Postgres**, fed via the Kafka/CDC conduits that already cross the iDMZ. This accelerates the "split later" seam §4 already promised; §4 database topology updated. |
| N17 | **Raw-counts → engineering-units scaling** (a missing divergence dimension) | Real AB integer files hold **raw ADC counts** (e.g. 4–20 mA → 6208–31208), not scaled floats. **Beaumont publishes raw integer counts** for its analog tags; the mapping table gains **`raw_min` / `raw_max` / `eu_min` / `eu_max`** columns and a **`scale_linear`** transform primitive joins §7's set. Must land **before Phase 0 freezes the mapping-table schema** — it deepens exactly the lesson Beaumont exists to teach. |
| N18 | **Units-of-measure governance** | **UNECE Rec 20** codes are the canonical `unit` values in `metric_registry`, backed by a small units dimension table (code, display symbol, dimension, conversion-to-canonical factor) as Phase 0 YAML — otherwise free-text units (`degF`/`°F`/`DEG F`) recreate the divergence problem *inside* the registry. Clean hook for QUDT-style unit nodes in Neo4j later. |
| N19 | **ISA-95 vocabulary fixes** | The work-center level is a **production unit** (ISA-95's continuous-process branch), not "line/cell" (the discrete branch — the one branch LSC is *not*). Full path: `enterprise → site → area → production-unit → equipment-class → equipment-id`. `equipment-class` appears in the topic path as a **deliberate navigability convention**, while `asset_master` keeps class as an attribute of the equipment instance per ISA-95 (type vs instance stated, not conflated). |
| N20 | **ISA-18.2 alarm model** (upgrades L2.1) | The alerting node implements a minimal **ISA-18.2/IEC 62682** shape: Pydantic `AlarmEvent` with the alarm state machine (Normal → Unack-Alarm → Acked → RTN-Unack), 3–4 priorities, ack/shelve, and a chattering guard (deadband + on/off-delay). `ts_historian.events` gains priority/state/source-rule columns; the HITL console gets ack/shelve; one Grafana panel shows EEMUA-191 alarm-rate KPIs (flood = >10 alarms/10 min). **Placement: per-site edge** (survives WAN loss, minimal latency — consistent with Z4); central EMQX gets only a thin cross-site notification consumer. Replaying a TEP fault then demonstrates a *real* alarm flood — the reason rationalization/shelving exist. |

### 14.4 Security & zoning (completes §13.8)

| # | Decision | Resolution |
|---|----------|-----------|
| N21 | **Connection-initiation rule + conduit inventory** | Explicit rule (NIST SP 800-82r3): **no IT-side system ever initiates a connection into the OT zone**; every crossing terminates in the iDMZ. The §13.8 flows are realized as six conduits: **C1** telemetry up — site forwarder (OT) → EMQX (iDMZ), OT-initiated outbound, MQTT/TLS :8883, Phase 4. **C2** telemetry into IT — UNS→Kafka bridge (IT) → EMQX (iDMZ), IT-initiated *into the iDMZ only*, Phase 4+. **C3** CDC — **Kafka Connect/Debezium runs as a dual-homed iDMZ container** (attached to both the OT-source and IT Docker networks — it *is* the conduit, like a DMZ historian relay), Phase 5a. **C4** recommendations down — model serving (IT) → EMQX (iDMZ) → forwarder consumes (OT-initiated), Phase 6. **C5** model/feature deploy — **edge pulls outbound** from an iDMZ staging point (MLflow artifact mirror or EMQX model topic), Phase 6. **C6** order-to-cash schedule-down *(added 2026-07-06 — the Diagram-1 v2 review caught that §12 #18's ERPNext-work-order→plant-MES leg is a crossing N21 had not declared)* — an **order-integration service in the iDMZ** (or an OT-side MES-sync that pulls outbound from ERPNext's API) carries work orders down; in the lab the synthetic generator may play this role, but the conduit is declared, Phase 5b. Placements fixed accordingly: **online Redis = per-site, OT-side** (edge inference scores off the local Mosquitto); **Prometheus = one per zone, federated** to central Grafana (a central Prometheus scraping into OT would violate the rule). Every service carries a `lab.zone` Docker label; the compose files are the living zone/asset inventory (IEC 62443-3-2). |
| N22 | **Broker authentication + per-branch topic ACLs** (extends L7.2) | Every MQTT client authenticates with unique credentials. Phase 2: Mosquitto `password_file` + `acl_file` (a site publisher may publish only its own Sparkplug group). Phase 4: EMQX authn + authz — each site-forwarder may publish only its own namespace (Beaumont → `lagos-chem/beaumont/#` + its `spBv1.0` group), IT consumers are subscribe-only, and **only the HITL console identity may publish command topics**. This is the governed-namespace thesis made *enforceable* — a mis-scoped publish is rejected live, which is itself the governance demo. Pure config + a handful of credentials. |
| N23 | **TLS on the WAN-representing conduit** | The forwarder→EMQX link plays the inter-site WAN, and Sparkplug defers all transport security to MQTT/TLS. Lab CA (one openssl script); EMQX TLS listener :8883; the four site-forwarders + the UNS→Kafka bridge connect over TLS (server-auth; mTLS optional stretch). Per-site Mosquitto stays plaintext — recorded as a deliberate asymmetry (zone-internal; §10's hardening exclusion covers the rest). |
| N24 | **Command-path audit** (makes L6.5's "auditable" true) | New **`command_audit`** table (IT-side ODS): recommendation id, model + MLflow version, SHAP summary, proposed vs approved setpoint, approver, HITL level, safety-layer verdicts (envelope / PLC-clamp / independent check), and per-hop timestamps (console publish → forwarder receipt → writeback result → DDATA read-back); plus a small archiver subscribed to the command topic. Broker authz (N22) restricts who may command at all. For a simulated chemicals plant, the setpoint-change audit trail is the signature compliance artifact (21 CFR Part 11-style). |
| N25 | **Functional-safety concept corrected** (amends §13.7 P2) | The "independent safety-check service" is a **BPCS-level guard — NOT an SIS**, and the "GuardLogix analog" label is dropped (GuardLogix is a SIL 3-certified safety controller; under **IEC 61511** an SIS is a separate, functionally independent, certified protection layer that a Python service on shared broker fabric cannot claim). LOPA onion mapped for the lab: process design → **BPCS control (all three P2 layers live here)** → alarms + operator (N20/P3) → *SIS trip — consciously **not** modeled (a real plant would have one below all of this)* → relief/physical → emergency response. Optional Phase 6 teaching artifact: a hard-trip in Beaumont's OpenPLC ladder logic at a TEP shutdown constraint, clearly labeled "uncertified SIS stand-in", independent of model, broker, and config. |

### 14.5 Streaming & lakehouse

| # | Decision | Resolution |
|---|----------|-----------|
| N26 | **Kafka wire contract + schema registry** | Phase 5a.1 (Python poll): JSON + the Pydantic `ChangeEvent` is the contract. Phase 5a.2 (Debezium milestone) adds **Apicurio Registry** (one container) with **Avro converters + a compatibility mode** on the one Debezium table — records carry a schema id instead of Debezium's verbose embedded-schema JSON default. Exercise schema evolution deliberately: `ALTER TABLE ADD COLUMN` and observe converter/registry behavior. (Nuance to teach correctly: under BACKWARD compatibility, *removing* a field is the allowed change; *adding a mandatory field without a default* is what gets rejected.) A new hands-on learning milestone in the existing Debezium slot. |
| N27 | **Bronze is immutable raw** (amends §13.7 P7) | **All** data lands in Bronze as-is (immutable, with ingest metadata); `metric_registry` validation runs at the **Bronze→Silver promotion**, not at ingest; failures are recorded in `dead_letter` **with a pointer back to the Bronze record** and are never dropped from Bronze — so rejected data stays reprocessable after a registry fix. |
| N28 | **Dead-letter redrive** (completes the DLQ pattern) | `dead_letter` schema fixed now: id, ingested_at, source (site/topic/offset), `raw_payload` (full original bytes), `error_category` (unknown_metric \| schema_drift \| validation \| transform), error_detail, retry_count, status (open \| redriven \| discarded). A ~50-line redrive script (Phase 4/6 deliverable) re-feeds open rows through the harmonization entry point — idempotent because sinks are (N9) — and marks them redriven. **The governance demo loop:** unknown tag → dead-lettered → gatekeeper adds it to `metric_registry` → redrive → flows through. |
| N29 | **CDC operational specifics** (extends milestone 5a.2) | Four checklist additions: set `max_slot_wal_keep_size` on the role-A Postgres + Debezium heartbeat (an idle replication slot pins WAL — worst case is exactly a sometimes-off home lab); observe the initial snapshot (`op:'r'`) and make the Python poller's first run mimic it (true like-for-like at the 5a.3 swap seam); exercise one source-table DDL change (logical decoding emits no DDL events); exercise one DELETE and handle the **delete event + tombstone pair** — the "log-based CDC catches deletes" payoff made concrete. |

### 14.6 Plane 4 (ML) additions

| # | Decision | Resolution |
|---|----------|-----------|
| N30 | **Shadow rung + promotion gates** (amends §13.7 P3) | The HITL ladder gains **L0 — Shadow**: the model scores live UNS data and publishes to a shadow namespace consumed only by monitoring dashboards; nothing surfaces to operators. **Every model starts at L0.** Per-rung promotion gates (e.g. L0→L1: N days in shadow + false-alert rate below threshold; L2→L3: acceptance rate + zero safety-envelope violations over Z runs) and **automatic demotion** one rung on drift/performance breach. |
| N31 | **ML observability** (new row alongside L7.1 — Prometheus was infra-only) | Per-model **input/prediction drift** (PSI/KS) computed by the serving layer and exported to the existing Prometheus/Grafana; a scheduled **label-join evaluation** job scores past recommendations against LIMS results when they land in gold — the classic *delayed-label* loop, and a beautiful lab lesson (it exercises Planes 1–3 to evaluate Plane 4); a **stated retraining trigger** (even "manual retrain when the drift alert fires" — the trigger must be defined). Candidate library: Evidently (OSS, exports to Prometheus). |
| N32 | **Recommendation TTL / revalidation** | A setpoint recommendation computed at time *t* can be invalid when approved 20 minutes later; P2's layers validate the *value*, not whether it still applies. The recommendation contract (P4) gains `issued_at`, `valid_until` (TTL per P1 metric class — fast variables get short TTLs), and an input-state snapshot/hash. The console greys out expired recommendations; the edge writeback service re-checks live state against the snapshot before writing and rejects stale approvals with a "stale — regenerate" event into the UNS. |
| N33 | **Multivariate SPC** (extends §13.7 P5) | Two-level, still SPC-first: (1) univariate EWMA/CUSUM on the named yield metrics; (2) **PCA-based Hotelling T² + SPE/Q charts across the TEP unit's harmonized metric set, with contribution plots** for diagnosis. TEP is *the* multivariate-SPC literature benchmark — several of its 21 faults shift correlation structure without moving any single variable's mean, invisible to univariate charts. Contribution plots are the SPC-native cousin of P4's SHAP (~50 lines of scikit-learn; no new infrastructure). |
| N34 | **Dataset versioning + model cards** | Training extracts are written **once** to immutable versioned paths (`gold/training/<dataset>/<run-id>/`), never overwritten; path + content hash + row count logged as MLflow run params (upholds §9 determinism at the ML layer; Delta time travel becomes the §13.6 graduate-to version of the same concept). Every registered model gets a **model card** owned by a named gatekeeper — deliberately mirroring `metric_registry` governance: intended use, **max authorized HITL level**, training-data version, safety envelope, eval metrics, SHAP mode, known failure modes. |
| N35 | **Feature single-sourcing + SHAP caveats** (refines §13.7 P4, L6.2) | Feature definitions live **once** as declarative config (name, source metrics, window, aggregation) consumed by *both* the Spark gold job and the edge/online computation — the online/offline split otherwise *creates* training/serving skew; the edge logs its input feature vector with each prediction (N31/N32 need it anyway). P4 refined: L2/L3 recommendation models constrained to classes with fast exact attribution (tree ensembles → TreeSHAP; SPC-native → contribution plots), slower explainers cloud/batch-only; the SHAP `feature_perturbation` choice (interventional vs tree-path-dependent — materially different under TEP's correlated features) is recorded in the model card; console phrasing is **model attribution, not process causation** ("model weighted feed-temp most"), paired with the N33 contribution plot for the process-side view. |
