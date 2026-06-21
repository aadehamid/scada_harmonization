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

Different sites, lines, and machines represent the *same underlying reality* differently — local
PLC naming, controller memory structures, brownfield integrations, divergent tag taxonomies, and
even different integrators per project (so tags diverge *within* a site too). What should be
enterprise-comparable data arrives as site-specific, cryptic, inconsistent signals — and the cost is
operational: analytics data can take **days to assemble by hand**, real-time data stays **fragmented
and "owned" by sites**, and ML can't scale across the enterprise. The lab deliberately manufactures
this mess (same reality, different names per site), then proves it can be conformed to one namespace,
**governed as a reusable data product**, and enriched into connected context. The problem mirrors
real process/CPG transformation discovery (anonymized industry pains); see charter §2.

## The three planes

Sources span the classic **IT / OT / ET** divide: OT (SCADA/PLC tags), IT (on-prem
business-transactional data in PostgreSQL — MES/LIMS/CMMS/quality), and ET (engineering topology).

| Plane | What it does | Key tech |
|-------|--------------|----------|
| **1 — Harmonize** (OT) | synthetic Level 0 → PLC-world disguise → Sparkplug B → UNS; unit/status/timestamp normalization + per-field lineage | OpenPLC, two-tier MQTT (**Mosquitto** edge + **EMQX** central, Python forwarder), Sparkplug B, Ignition, **TimescaleDB**, Grafana |
| **2 — Record** (Enterprise) | curated operational events → SAP-like business records | ERPNext |
| **3 — Contextualize** (Knowledge) | UNS + IT transactional + ERP + asset topology → **identity reconciliation** → knowledge graph → reasoning | Neo4j (ISO 15926 / DEXPI-aligned ontology), GraphRAG |
| **4 — Apply** (Intelligence) | consumes Planes 1–3 — **Track A** traditional ML (predictive maintenance, anomaly, forecasting; **flagship: yield improvement / production-leakage, human-in-the-loop & edge-executed**; scored back to UNS) · **Track B** LLM/GenAI (retrieval, copilot via GraphRAG) | ML stack + LLM/GraphRAG *(tooling deferred to Phases 6–7)* |

**Storage by concern (no overlap):** time-series → **TimescaleDB** historian;
relational/transactional (OLTP) → **PostgreSQL** (transactional source-of-record + derived ODS, the
ODS co-located in the Timescale instance); analytical (OLAP) → **DuckDB** over Parquet;
relationships → Neo4j; enterprise records → ERPNext.

## Guiding principle

> Only **Level 0 (the physical world)** is synthetic. Everything above — PLC-facing structures,
> messaging, historian, analytics, ERP, knowledge graph, cloud — behaves like a real OT/IT stack
> assembled from open-source or free/community software.

## Data strategy

The domain is **data-driven, not dictated**, so realistic data is always available:

- **Tennessee Eastman Process** — continuous chemical-process units (reactors, columns, loops)
- **Industrial IoT Dataset (Synthetic)** — rotating machines (pumps, compressors, motors)

The enterprise is **Lagos Specialty Chemicals** (UNS root `lagos-chem`), operating **4 sites** —
**Beaumont** (Allen-Bradley, real OpenPLC), **Geismar** (Siemens), **Rotterdam** (Ignition-style),
**Corpus Christi** (CygNet) — each running the same units/machines but on a different SCADA lineage
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
- **Abstraction (later) → UMH-anchored.** Replace the hand-wired backbone with United Manufacturing
  Hub Community once the internals are understood.

Every component is upgrade-friendly (OSS broker → enterprise; Ignition Maker → licensed; floci →
real AWS) without invalidating the design.

## Documentation

| Document | Role |
|----------|------|
| [`design/PROJECT_CHARTER.md`](design/PROJECT_CHARTER.md) | **Authoritative project definition** |
| [`design/DOMAIN.md`](design/DOMAIN.md) | Domain narrative — Lagos Specialty Chemicals backstory |
| [`design/uns_home_lab_notes.md`](design/uns_home_lab_notes.md) | Vision & high-level scope |
| [`design/hand_built_sparkplug_uns_notes.md`](design/hand_built_sparkplug_uns_notes.md) | Architecture: hand-built |
| [`design/umh_anchored_sparkplug_uns_notes.md`](design/umh_anchored_sparkplug_uns_notes.md) | Architecture: UMH-anchored (abstraction phase) |
| [`design/python_centric_uns_notes.md`](design/python_centric_uns_notes.md) | Implementation philosophy: Python-centric |
| [`design/synthetic_data_generation_notes.md`](design/synthetic_data_generation_notes.md) | Data strategy & the 6-layer pipeline |

## Status

Pre-implementation — design and charter complete, all infrastructure decisions resolved (broker,
historian, PLC realism, sites/enterprise, Postgres deployment, CDC). Build not yet started; next is
Phase 0 (repo skeleton + the three-stage mapping table). See the charter's build sequence (Phases 0–7).

## License

MIT
</content>
