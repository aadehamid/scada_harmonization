# Domain Narrative — Lagos Specialty Chemicals

> A narrative backstory for the simulated enterprise. It exists to make the harmonization problem
> **concrete and memorable**: every technical quirk in the lab (why Beaumont speaks Allen-Bradley,
> why Geismar is metric, why Corpus Christi uses compound tags) traces to a business event here.
> This is fiction in service of learning — only **Level 0** is synthetic; see
> [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md), which governs.

---

## The company

**Lagos Specialty Chemicals (LSC)** is a mid-cap specialty-chemicals manufacturer headquartered in
**Lagos, Nigeria**. It began in the 1990s blending industrial solvents and coatings additives for the
West African market, then grew — first organically, then aggressively **by acquisition** — into a
multinational producer of specialty intermediates and polymer additives.

Its plants run a continuous **reaction → separation → stripping** process (reactants in, two liquid
products + byproduct out — the Tennessee Eastman process archetype), supported by the usual rotating
equipment: feed pumps, recycle compressors, agitator motors, transfer pumps.

LSC's problem is the problem of every roll-up: **each plant was built or acquired at a different time,
by different engineers, on a different control platform, in a different unit system, with different tag
conventions.** Headquarters now wants enterprise-wide analytics, predictive maintenance, and an AI
copilot — but the operational data is fragmented across four incompatible dialects. That gap is the
entire reason this lab exists.

UNS root: **`lagos-chem`** · ISA-95 enterprise level: **Lagos Specialty Chemicals**.

---

## How it grew — and why the data is a mess

| Era | Event | Site | Control heritage | Why it looks the way it does |
|-----|-------|------|------------------|------------------------------|
| 1990s | Founding + first West African operations | *(HQ, not a lab site)* | — | Solvents/coatings origins; the corporate data culture |
| ~2005 | First US Gulf Coast plant (oldest asset) | **Beaumont, TX** | **Allen-Bradley** PLCs | Legacy **brownfield**; cryptic AB register tags (`N7:20`, `FIC101_PV`); imperial units; terse status codes. In the lab this is one of **two real-protocol sites** — a real **OpenPLC** runtime (Modbus TCP) — the genuine "memory address → meaning" lesson. |
| ~2012 | Acquired a competitor's plant, originally built by a European licensor/EPC | **Geismar, LA** | **Siemens** S7 | Despite being on the US coast, it was engineered to European standards: Siemens addressing (`DB10.DBD4`, `MW100`) and **metric** units (m³/h, kPa, °C). Verbose status strings. In the lab: the **second real-protocol site** — a real **OPC-UA server** (`asyncua`), per charter §13 L1.1. |
| ~2018 | Greenfield European expansion | **Rotterdam, NL** | Modern **Ignition / MQTT** stack | Newest, cleanest build: verbose semi-semantic nested names, metric units, its own status vocabulary. Looks "almost harmonized" already — but on its *own* terms. |
| ~2022 | Acquired a midstream/feedstock terminal to secure raw-material supply (backward integration) | **Corpus Christi, TX** | **CygNet** (oil-&-gas heritage) | Different industry entirely. Compound flat tags that **encode the hierarchy in the name** (`CC_NORTH_U12_FIC101`); mixed units. The "we bought an O&G asset and inherited its SCADA" story. |

The result: the **same physical reading** — say, a reactor feed-flow — exists under four unrelated
names, in two unit systems, with four status vocabularies, across four SCADA lineages. A human
engineer can squint and reconcile them; a machine cannot. Harmonization is the act of making the
machine able to.

The mess runs deeper than the four lineages. Within a single site, **tag modeling also varies by the
system integrator** LSC contracted for each project — so even one plant is internally inconsistent.
Today, getting analytics-ready data means engineers **pulling historian extracts by hand — sometimes
days of work** — and each site quietly treats its real-time data as **its own**, not an enterprise
asset. Meanwhile corporate IT is mid-flight on an **SAP ECC → S/4 migration**, so the business-record
layer is itself a moving target. HQ's response is not just "one namespace" but **one namespace that is
governed and reusable**: every harmonized metric gets an owner, a definition, and lineage — a data
product the whole enterprise can trust — while sites keep local autonomy (the *global-and-local* ask).

---

## The cast of divergence (what the lab must reconcile)

| Dimension | Beaumont | Geismar | Rotterdam | Corpus Christi |
|-----------|----------|---------|-----------|----------------|
| SCADA lineage | Allen-Bradley | Siemens | Ignition-style | CygNet |
| Tag style | AB register (`N7:20`) | Siemens address (`DB10.DBD4`) | verbose semantic | compound hierarchy-encoding |
| Units | imperial | metric | metric | mixed |
| Status codes | terse | verbose | own vocabulary | O&G-style |
| PLC in lab | **real OpenPLC** (Modbus TCP) | **real OPC-UA** (`asyncua`) | Python-modeled | Python-modeled |

This single roster deliberately spans **every harmonization dimension at once** — naming style, unit
system, status vocabulary, addressing scheme, and real-vs-modeled control — so the lab proves the
hard cases, not the easy one.

---

## The mission (what LSC is trying to achieve = the lab's four planes)

1. **Harmonize** the four dialects into **one Unified Namespace** (Sparkplug B / MQTT) — "same reality,
   one name" — and **govern** it as a reusable data product (owners, definitions, lineage).
2. **Record** curated operational events into enterprise systems (ERPNext) and reconcile them with the
   plant's transactional systems (MES/LIMS/CMMS/quality).
3. **Contextualize** everything into a **knowledge graph** (Neo4j) — assets, tags, events, batches,
   work orders, lab results, engineering topology — enabling cross-domain reasoning and a GraphRAG
   copilot.
4. **Apply** the foundation — traditional ML (flagship: **yield improvement / production-leakage**,
   delivered as human-in-the-loop, edge-executed recommendations) and a GenAI copilot.

Get there and LSC unlocks enterprise analytics, predictive maintenance, yield gains, and trustworthy
AI. That's the payoff the lab is built to demonstrate end to end.
