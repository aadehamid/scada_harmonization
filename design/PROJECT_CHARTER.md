# Project Charter — Industrial Data Harmonization & Contextualization Home Lab

**Status:** Authoritative project definition. Supersedes scattered framing in the superseded
source docs now under `reference/` (`reference/docs/` and
`reference/engineering_drawing_business_case/`); `README.md` and `AGENTS.md` are aligned to it.

**Last updated:** 2026-05-28

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
and uneven operational modeling. What should be enterprise-comparable data arrives as
site-specific, cryptic, inconsistent signals.

The lab deliberately manufactures this mess (same reality, different names per site), then proves
it can be conformed to one namespace and enriched into connected context.

The full problem has **two halves of contextualization**:

| Half | Problem | Lab plane |
|------|---------|-----------|
| **Operational data** | SCADA tags are cryptic, inconsistent, machine-unreadable | Harmonize (Plane 1) |
| **Engineering context** | Asset topology and relationships are trapped in static documents/silos | Contextualize (Plane 3) |

Clean operational data **plus** accurate engineering/relationship context = a complete foundation
for industrial AI. Neither is useful at full scale without the other.

---

## 3. The three planes

```
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
│   UNS + ERP + asset topology → Neo4j knowledge graph → GraphRAG          │
│   ISO 15926 / DEXPI-aligned ontology · traversal & reasoning queries     │
│   reference design: reference/engineering_drawing_business_case/         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Layered technical architecture (ISA-95 view)

| Level | Role | Implementation |
|-------|------|----------------|
| **L0** | Synthetic & benchmark process reality | Python replay of benchmark datasets + generated signals |
| **L1/2** | PLC-world representation (brownfield realism) | OpenPLC and/or PLC-style tags (`N7:20`, `MW100`, `DB10.DBD4`, `FIC101_PV`) |
| **L3 — transport/UNS** | Harmonization backbone | MQTT broker (Mosquitto / EMQX OSS) + **Sparkplug B** |
| **L3 — OT consumers** | SCADA / storage / dashboards | Ignition Maker Edition, InfluxDB / TimescaleDB / QuestDB, Grafana |
| **L3/4 — analytics** | Streaming & analytical path | Kafka → Parquet/object store → DuckDB |
| **L4 — IT/cloud** | Cloud-shaped landing zone | floci (local AWS emulation: S3, Lambda, Kinesis, Glue, Athena, …) |
| **Cross-cutting — enterprise** | SAP-like business records | ERPNext |
| **Cross-cutting — knowledge** | Connected-context graph + reasoning | Neo4j + GraphRAG |
| **Cross-cutting — glue** | All custom logic | **Python** (Paho MQTT, PySparkplug, pandas, Pydantic, Neo4j driver) |

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

This table also carries unit, range, cadence, asset class, site context, and the
work-order/batch/material/graph-entity IDs that later feed ERPNext and Neo4j. **Build this table
well and the rest is plumbing.**

**Six implementation layers** (from `synthetic_data_generation_notes.md`):
1. Ingestion · 2. Augmentation · 3. PLC mapping · 4. Sparkplug · 5. Context export · 6. Replay/orchestration

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
| **2** | PLC disguise + Sparkplug | Mapping + Sparkplug publisher → Mosquitto/EMQX; verify NBIRTH/DBIRTH/NDATA |
| **3** | OT consume | InfluxDB historian + Grafana; optionally Ignition Maker as SCADA consumer |
| **4** | Multi-site | Clone asset template with *different* site tags → prove harmonization |
| **5** | Context | Context-export → ERPNext events + Neo4j graph (asset↔tag↔event↔work-order) |
| **6** | Loop closure | Python ML/inference publishes scores back into Sparkplug; floci cloud landing |
| **7** | Reasoning | GraphRAG over Neo4j for troubleshooting / lineage / impact queries |
| **Later** | Abstraction | Re-platform L3 backbone onto UMH Community |

Phases 0–4 are the core harmonization proof. Phases 5–7 are the contextualization story.

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
- **Config over code** — site mappings, status maps, unit factors, ontology are data.
- **Upgrade-friendly** — every OSS component has a credible paid/enterprise replacement path.
- **Python as a first-class participant** — not just glue; a native UNS node.

---

## 10. Scope

**In scope:** synthetic multi-site data; PLC-world disguise; Sparkplug B/MQTT UNS; historian +
dashboards; ERPNext enterprise integration; Neo4j knowledge graph + GraphRAG; floci cloud
emulation; Python ML/inference round-trip.

**Out of scope (for now):** real PLC/field hardware; live SCADA connections; document/P&ID
CV-VLM extraction; production security hardening; real cloud accounts; real ERP deployments
beyond ERPNext community.

---

## 11. Document map

| Document | Role |
|----------|------|
| `design/PROJECT_CHARTER.md` | **This file — authoritative project definition** |
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
2. **Broker choice** — Mosquitto (minimal) vs. EMQX OSS (richer, clearer enterprise path).
3. **Historian choice** — InfluxDB vs. TimescaleDB vs. QuestDB.
4. **How literal the PLC layer is** — full OpenPLC runtime vs. Python-modeled controller tags.
5. **When ERPNext and Neo4j enter** — Phase 5 as planned, or earlier stubs.
6. **Number & identity of sites** — exact site names and how many (≥2) for the first build.
</content>
</invoke>
