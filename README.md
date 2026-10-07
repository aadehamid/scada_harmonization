# Industrial Data Harmonization & Contextualization Home Lab

A home lab that **simulates a multi-site process / specialty-chemicals manufacturer** in which
similar operational realities are represented differently across sites — then **harmonizes** those
disparate OT representations into a common enterprise language through a Sparkplug B / MQTT
**Unified Namespace (UNS)**, and **contextualizes** the result into a knowledge graph meaningful to
OT, IT, analytics, ML, ERP, and graph-based reasoning systems.

This is a **learning environment and architecture prototype** — built to understand every layer of
a modern industrial data stack at the bare-metal level *before* adopting enterprise software that
abstracts those layers away.

> **Authoritative project definition:** [`design/PROJECT_CHARTER.md`](design/PROJECT_CHARTER.md).
> This README is a summary; the charter governs.
> **Continuing the work / new agent?** Start with [`HANDOFF.md`](HANDOFF.md) for current status and next steps.

## The problem being simulated

The industry does not have a data problem. It has a **contextualization and scalability** problem:
same physical reality, different names, and a model that works at one site is an eighteen-month
redo at the next. Different sites, lines, and machines represent the *same underlying reality*
differently — local PLC naming, controller memory structures, brownfield integrations, divergent
tag taxonomies, and even different integrators per project (so tags diverge *within* a site too).
What should be enterprise-comparable data arrives as site-specific, cryptic, inconsistent signals —
and the cost is operational: analytics data can take **days to assemble by hand**, real-time data
stays **fragmented and "owned" by sites**, and ML can't scale because context was never a product.
**Contextualize before models.** The lab deliberately manufactures this mess (same reality,
different names per site), then proves it can be conformed to one namespace, **governed as a
reusable data product**, and enriched into connected context. The problem mirrors real process /
CPG / Energy & Chemicals discovery (anonymized industry pains); see charter §2.

The **engineering (ET) leg** carries the same disease. P&IDs hold equipment, pipe, valve,
instrument, and connection information, but the meaning has to be interpreted: a recognized tag
does not establish which equipment it identifies, and an intersecting line does not establish a
pipe connection. A one-time conversion then drifts as tags change, equipment is removed, and
connections are rerouted. This lab **builds the drawing-to-graph path** from its own Unit 100 P&ID
— vector sheet first, then scanned variants — publishing an engineering graph with source
evidence, stable identities, and revision control (Phase 5b.1). A related **private** project by
the same owner, `aadehamid/Engineering_Drawing_to_Graph`, adds the structured route: pull records
from an authoring-system backend and convert them to DEXPI 2.0.

## The four planes

Sources span the classic **IT / OT / ET** divide: OT (SCADA/PLC tags), IT (on-prem
business-transactional data in PostgreSQL — MES/LIMS/CMMS/quality), and ET (engineering topology).

| Plane | What it does | Key tech |
|-------|--------------|----------|
| **1 — Harmonize** (OT) | synthetic Level 0 → PLC-world disguise → Sparkplug B → UNS; unit/status/timestamp normalization + per-field lineage | OpenPLC + **OPC-UA**, two-tier MQTT (**Mosquitto** edge + **EMQX** central, Python forwarder w/ store-and-forward), Sparkplug B, Ignition, **TimescaleDB**, Grafana |
| **2 — Record** (Enterprise) | curated operational events → SAP-like business records | ERPNext |
| **3 — Contextualize** (Knowledge) | UNS + IT transactional + ERP + asset topology → **identity reconciliation** → knowledge graph → reasoning | Neo4j (ISO 15926 / DEXPI-aligned ontology), GraphRAG |
| **4 — Apply** (Intelligence) | consumes Planes 1–3 — **Track A** traditional ML (predictive maintenance, anomaly, forecasting; **flagship: yield improvement / production-leakage, human-in-the-loop & edge-executed**; scored back to UNS) · **Track B** LLM/GenAI (retrieval, copilot via GraphRAG) | ML stack + LLM/GraphRAG *(tooling deferred to Phases 6–7)* |

**Storage by concern (no overlap):** time-series → **TimescaleDB** historian;
relational/transactional (OLTP) → **PostgreSQL** (transactional source-of-record + derived ODS, the
ODS in its own IT-side Postgres — zone split, charter §14 N16); analytical (OLAP) → **medallion lakehouse** (Bronze/Silver/
Gold via **Spark ETL**) + **DuckDB** over Parquet; relationships → Neo4j; enterprise records → ERPNext.
Pipeline/infra observability via **Prometheus + Grafana**.

## Guiding principle

> Only **Level 0 (the physical world)** is synthetic. Everything above — PLC-facing structures,
> messaging, historian, analytics, ERP, knowledge graph, cloud — behaves like a real OT/IT stack
> assembled from open-source or free/community software.

## Data strategy

The domain is **data-driven, not dictated**, so realistic data is always available:

- **Tennessee Eastman Process** — continuous chemical-process units (reactors, columns, loops)
- **Industrial IoT Dataset (Synthetic)** — rotating machines (pumps, compressors, motors)

The enterprise is **Lagos Specialty Chemicals** (UNS root `lagos-chem`), operating **4 sites** —
**Beaumont** (Allen-Bradley, real OpenPLC/Modbus), **Geismar** (Siemens, real OPC-UA via `asyncua`),
**Rotterdam** (Ignition-style), **Corpus Christi** (CygNet) — each running the same units/machines but on a different SCADA lineage
with deliberately divergent naming. Physical meaning is *assigned* at the mapping stage, anchored by
the **three-stage name mapping table** — `friendly variable → site-specific PLC tag → Sparkplug
metric` — which is the spine of the lab. The table doubles as a **governed data-product catalog**
(each metric has an owner/"gatekeeper", definition, and lineage), so harmonized signals are reusable
without re-interpretation.

The generator also produces **synthetic relational tables** (MES/LIMS/CMMS/quality) seeded into
Postgres, with their own business keys deliberately *not* aligned to OT identities — extending the
"same reality, different representation" principle to transactional data and creating the
identity-reconciliation problem at the heart of Plane 3.

## Implementation approach

The three architecture notes are **phases of one architecture**, not competing projects:

- **Build & learn → hand-built + Python-centric.** Wire every component explicitly so each boundary
  is visible; Python is a first-class UNS participant, not just glue.
- **Abstraction (later) → UMH-anchored.** Replace the hand-wired forwarders/bridges/streaming leg
  with **UMH Core** (Apache-2.0; `benthos-umh` + embedded Redpanda) once the internals are understood
  *(decided — charter §12 #16; TimescaleDB/Grafana stay hand-built)*.

These styles are captured as **three full architecture diagrams** — hand-built/Python-centric ·
UMH-anchored · cloud-native (floci→AWS) — in the Eraser `scada_harmonization` workspace. The design
was benchmarked layer-by-layer against a real industrial-products target architecture (charter §13).

Every component is upgrade-friendly (OSS broker → enterprise; Ignition Maker → licensed; floci →
real AWS) without invalidating the design.

## Documentation

| Document | Role |
|----------|------|
| [`design/PROJECT_CHARTER.md`](design/PROJECT_CHARTER.md) | **Authoritative project definition** |
| `aadehamid/Engineering_Drawing_to_Graph` *(private — not linkable from here)* | Related project, same owner — engineering drawings to a maintained engineering graph; adds the structured-backend route |
| [`design/DOMAIN.md`](design/DOMAIN.md) | Domain narrative — Lagos Specialty Chemicals backstory |
| [`design/E2E_WALKTHROUGH.md`](design/E2E_WALKTHROUGH.md) | End-to-end teaching walkthrough script (Threads A/B/C) |
| [`design/WALKTHROUGH_PROGRESS.md`](design/WALKTHROUGH_PROGRESS.md) | Live walkthrough cursor — resume here |
| [`design/LEARNING_LOG.md`](design/LEARNING_LOG.md) | Durable concepts + glossary |
| [`design/PHASE1_L0_CONTRACT.md`](design/PHASE1_L0_CONTRACT.md) | Phase 1 L0 record + replay identity |
| [`design/PHASE1_SYNTHETIC_DATA.md`](design/PHASE1_SYNTHETIC_DATA.md) | Phase 1 land / persist / disk record |
| [`design/PHASE1_DATASHEET.md`](design/PHASE1_DATASHEET.md) | Phase 1 local vs R2 datasheet |
| [`design/UNIT100_PID.md`](design/UNIT100_PID.md) | Unit 100 P&ID Rev B one-pager + 59-name tag list |
| [`design/uns_home_lab_notes.md`](design/uns_home_lab_notes.md) | Vision & high-level scope *(archived — superseded on decided items by the charter)* |
| [`design/hand_built_sparkplug_uns_notes.md`](design/hand_built_sparkplug_uns_notes.md) | Architecture: hand-built *(archived — superseded on decided items)* |
| [`design/umh_anchored_sparkplug_uns_notes.md`](design/umh_anchored_sparkplug_uns_notes.md) | Architecture: UMH-anchored (abstraction phase) *(archived — describes UMH Classic; adopted target = UMH Core, charter §12 #16)* |
| [`design/python_centric_uns_notes.md`](design/python_centric_uns_notes.md) | Implementation philosophy: Python-centric *(archived — superseded on decided items)* |
| [`design/synthetic_data_generation_notes.md`](design/synthetic_data_generation_notes.md) | Data strategy & the 6-layer pipeline |

## Status

**Current status is in [`HANDOFF.md`](HANDOFF.md) §2** — the phase, the `main` HEAD, open pull
requests, what has landed and what is next. This file does not repeat it: three copies of the
status drifted apart, quoting `main` at two different commits while the truth was a third.

Figures quoted anywhere in this repo come from `scripts/facts.py`, which `scripts/check.sh` runs.
Add a gate there, not in CI and not in the pre-push hook.

## License

[MIT](LICENSE)
