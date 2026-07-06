# Project Handoff

**Purpose:** let any agent (or human) pick up this project without re-deriving context.
**Last updated:** 2026-07-06

> **Read order for a new agent:** (1) this file → (2) `design/PROJECT_CHARTER.md` (authoritative
> and governing) → (3) `AGENTS.md` (working constraints) → (4) the `design/*_notes.md` for depth.

---

## 1. What this project is

An **industrial data harmonization & contextualization home lab**: it simulates a multi-site
**process / specialty-chemicals manufacturer** where each site represents the *same* operational
reality differently, then **harmonizes** that into one Sparkplug B / MQTT Unified Namespace (UNS) and
**contextualizes** it into a Neo4j knowledge graph. It is a **learning environment / architecture
prototype** — the explicit goal is to understand each layer at the bare-metal level *before* adopting
enterprise software that abstracts it away.

**Four planes:** Plane 1 **Harmonize** (OT → Sparkplug B UNS) · Plane 2 **Record** (curated events →
ERPNext) · Plane 3 **Contextualize** (UNS + IT transactional + ET topology → identity reconciliation →
Neo4j + GraphRAG) · Plane 4 **Apply** (intelligence: Track A traditional ML — predictive maintenance/
anomaly/forecasting, scored back to UNS; Track B LLM/GenAI — retrieval/copilot via GraphRAG; tooling
deferred to Phases 6–7). Sources span the **IT / OT / ET** divide.

The authoritative, always-current definition is **`design/PROJECT_CHARTER.md`**. If anything here
conflicts with the charter, the charter wins.

---

## 2. Current status (2026-07-06)

**Phase: pre-implementation — Diagram 1 teaching walkthrough (next).** Design + charter complete;
**all infrastructure decisions resolved**; **no source code yet.** Hand-built Eraser Diagram 1 is
drawn, §13.7 patterns + §13.8 OT/IT zoning applied, owner approved its look (2026-06-23).
**Resequenced (owner-confirmed 2026-07-06):** Diagram 1 walkthrough → lock → **Phase 0 immediately**;
Diagrams 2 & 3 are drawn **just-in-time** later (charter §8 sequencing note; Diagram 2's target is
decided — **UMH Core**, §12 #16).

### This session (2026-07-06) — IT/OT best-practice review adopted (charter §14 + §4.1)

Ran a deep multi-lens best-practice review (UNS/Sparkplug · IEC 62443/Purdue zoning · ISA-95/-88
modeling · streaming/lakehouse · historian ops · industrial-ML safety · tool fact-check · plan
integrity; all web-verified) of every design doc. **The architecture was validated** (forwarder-not-
bridge, EMQX-in-iDMZ, Z3/Z4 zoning, P8, graded HITL all match or exceed published practice); the
genuine gaps were adopted as **charter §14 (ledger N1–N35)**. Highlights:

- **N1/N2 — Sparkplug↔ISA-95 namespace encoding decided** (the §6 `lagos-chem/...` root vs Sparkplug's
  fixed `spBv1.0/...` topics were incompatible as written): site tier = pure Sparkplug
  (`group_id=lagos-chem:<site>`); enterprise tier = retained plain-MQTT ISA-95 republish on EMQX.
- **N3–N5** — forwarder = compliant Edge Node per site (bdSeq/seq/alias remap/NCMD Rebirth/
  `is_historical` flush); Primary Host named per tier; closed-loop commands are **NCMD/DCMD**, not
  "setpoint topics" (L6.5 amended).
- **N8–N12** — replay clock decided (TEP is 3-minute data → re-classed; simulated clock w/ rebasing);
  at-least-once + idempotent sinks; **quality model** (Good/Uncertain/Bad/Stale = 5th divergence
  dimension); historian lifecycle; store-and-forward semantics.
- **N13–N20** — **lot-based MES** (continuous process; ISA-88 out, ISA-106 in; `mes.production_lot` +
  material model); identity_map survivorship; **`ods_core` split to an IT-side Postgres** (zone fix,
  amends #7); Beaumont raw-counts scaling; UNECE units; ISA-18.2 alarm model.
- **N21–N25** — conduit inventory + "no IT-initiated connections into OT" rule; broker authn +
  per-branch ACLs; TLS on forwarder→EMQX; `command_audit`; **SIS/GuardLogix conflation corrected**
  (BPCS-level guard; IEC 61511 note).
- **N26–N35** — Apicurio schema registry (5a.2); Bronze immutable-raw; dead-letter redrive; CDC ops
  specifics; **L0 Shadow HITL rung**; ML drift monitoring + delayed-label eval; recommendation TTL;
  **multivariate SPC (PCA T²/SPE)**; dataset versioning + model cards; feature single-sourcing.
- **Tool/version reality (charter §4.1 pinned stack):** EMQX ≥5.9 **BSL 1.1 single-node** (the old
  "EMQX OSS bridges+clustering" justification was factually wrong); PySparkplug 0.6.x downgraded to
  *candidate* (Pre-Alpha); TimescaleDB Community ≥2.26 / TigerData; **UMH pivoted to UMH Core** (new
  open decision §12 #16 — re-validate before Diagram 2); Redis 8 AGPLv3; ERPNext v15/16; Ignition
  Maker 8.3 gotchas; floci fallback.
- **Follow-up (same session): §12 #16 RESOLVED — UMH Core adopted** as the abstraction target
  (Apache-2.0 umh-core + benthos-umh; embedded Redpanda source-available/free; Management Console =
  optional SaaS, lab runs standalone YAML; Core replaces forwarders/bridges/streaming — Timescale +
  Grafana stay hand-built).
- **Follow-up (same session, post-merge): deck coverage check + two decisions.** Owner supplied an
  external "Enterprise IT vs Manufacturing/OT" slide deck (now local-only in
  `reference/enterprise_it_ot_deck/`, gitignored) and asked whether the lab can cover/describe it.
  Verdict: ~85% covered natively; gaps = L4 business breadth + the demand→floor direction. Resolved:
  **§12 #18 order-to-cash thin thread** (ERPNext SO → MRP → Work Order → lot → Delivery Note +
  Invoice, Phase 5b) and **§12 #19 no separate WMS** (ERPNext stock moves + `material_lot` events).
  Created **`design/E2E_WALKTHROUGH.md`** — the end-to-end walkthrough guide: Thread A (order thread,
  from the deck) + Thread B (telemetry up) + Thread C (decision/control back — both absent from the
  deck) + cross-cutting narratives + a describe-anyway table for every consciously-omitted system
  (CRM, WMS, PLM, EMS/BMS, batch execution, robotics/vision, SIS, low-code, middleware).
- **Plan:** Phase 4 split into **4a/4b/4c**; per-phase **exit criteria** (§8.1); **risk register**
  (§8.2 — incl. the 16–24 GB RAM reality → compose profiles per phase); staleness sweep (Geismar
  OPC-UA drift, archived-note banners, stray `</content>`/`DOCEOF` artifacts); `LEARNING_LOG.md`
  seeded.

### This session (2026-06-22) — Eraser architecture diagrams (hand-built #1, in progress)

Eraser MCP authenticated in Claude; began the three §13.4 implementation-variant diagrams.

- **Diagram 1 of 3 — Hand-built / Python-centric** created in the Eraser folder **"SCADA Harmonization"**
  (the project's existing folder; the convention's `scada_harmonization`). **URL:**
  https://app.eraser.io/workspace/6Ng61sTaot9VjtU87bEY?diagram=vheRVPpajwodCEDwqnBZ&layout=canvas
  Built to **reference-level density**: Level 0 device layer (synthetic TEP+IIoT replay, sensors,
  actuators) → L1/L2 PLC (OpenPLC/OPC-UA/Python) → two-tier brokers (4 Mosquitto edge + 1 EMQX cluster)
  + Python site-forwarders (store-and-forward + cross-site conforming = harmonization) → DMZ/Docker
  boundary → OT consumers, IT sources+CDC+file-drop, ods_core mapping store, medallion lakehouse+Spark,
  ERPNext, Neo4j+GraphRAG, ML, Prometheus/floci, 5 consumer personas, richly labeled flows.
- **New Plane-4 design refinements DECIDED this session** (now charter **§13.5**): edge inference runs
  **per-site** (true edge) + cloud/central for training/batch; ML trains on **three feature planes**
  (OT historian, IT/ods_core, harmonized gold); MLflow deploys the same model to **edge + cloud**;
  online(Redis)/offline(gold) split; **closed-loop control with HITL** — model → HITL Operator Console
  (approve/edit/reject) → approved command via **UNS Sparkplug setpoint topic** → site edge → controller
  writeback (OpenPLC/OPC-UA) → actuators. Model never actuates; controller executes; human gates.
- Two-tier MQTT broker topology clarified/visualized (no new decision — charter §4): 1 Mosquitto per
  site (local autonomy + local Sparkplug map) + 1 EMQX central cluster (enterprise harmonized namespace).
- **Two-component evaluation DECIDED** (now charter **§13.6**): **Databricks Free Edition** → adopt as a
  "graduate-to managed lakehouse" milestone + cloud-native-variant option (Delta Lake, Unity Catalog;
  build medallion by hand first, then mirror) — *not* in the hand-built core. **Apache Iggy** → keep
  **Kafka** as the backbone; Iggy only as an optional explore milestone on a non-Debezium stream (Iggy
  has no Debezium/Connect ecosystem and is incubating).
- ⚠️ **Eraser gotcha:** the AI edit path (`update_diagram`) repeatedly **reverses connection arrow
  directions**. Use **`manually_update_diagram`** (verbatim DSL) whenever direction matters.

### Diagram 1 refinement session (2026-06-23, later)
Refined **Diagram 1 (Hand-built / Python-centric)** in Eraser to reflect the §13.7 audit patterns and
fix OT/IT zoning. Diagram lives in the **"SCADA Harmonization"** Eraser folder (fileId
`6Ng61sTaot9VjtU87bEY`, diagramId `vheRVPpajwodCEDwqnBZ`):
https://app.eraser.io/workspace/6Ng61sTaot9VjtU87bEY?diagram=vheRVPpajwodCEDwqnBZ&layout=canvas
- Added all 9 §13.7 patterns visually (P1 scan-rate note · P2 defense-in-depth safety group on the
  writeback · P3 graded HITL console · P4 SHAP on recommendations · P5 SPC labels · P6 equipment-template
  registry · P7 Bronze schema-validation + dead_letter · P8 downstream-join note · P9 golden-batch node).
- **OT/IT zoning corrected → new charter §13.8 (Z1–Z4):** the diagram is now **three zones** — **OT
  (left, L0–3)** · **iDMZ (middle, L3.5)** · **IT/Cloud (right, L4–5)**. **EMQX moved into the iDMZ** as
  the OT/IT conduit (Z2); **MES/LIMS/CMMS/Quality + plant Postgres moved to OT-side Level 3** (Z3, ERPNext
  stays IT); historian/Grafana/console/safety are OT-side (Z4). iDMZ crossed by exactly 3 flows
  (telemetry up, CDC up, cloud-recommendation down).
- **Owner approved the current diagram look.** Still the working hand-built diagram; once locked it
  becomes the template for Diagrams 2 (UMH) & 3 (cloud-native).
- **Eraser gotchas captured to memory:** AI `update_diagram` reverses arrow directions → use
  `manually_update_diagram`; all diagrams go in the "SCADA Harmonization" folder.

### This session (2026-06-29) — owner confirmed Diagram 1 walkthrough plan

Owner reviewed repo scope and **confirmed sequencing:** (1) Diagram 1 end-to-end teaching walkthrough
with external research → (2) lock Diagram 1 → (3) Diagrams 2 & 3 → (4) Phase 0. Detailed agenda in §3.

⏭ **Roadmap (ordered — resequenced 2026-07-06):**
- (0) ~~Review `design/SAMPLE_*`~~ — **DONE (2026-06-23)** (charter §13.7 patterns adopted).
- (a) **IN PROGRESS — Diagram 1 teaching walkthrough** (owner confirmed 2026-06-29; timeboxed, now
  armed with the §14 gap checklist below). See §3.
- (b) ~~Two-components discussion~~ — **DONE** (Databricks + Iggy, charter §13.6).
- (b2) **After Diagram 1 locked → end-to-end narrative walkthrough** — three threads per
  `design/E2E_WALKTHROUGH.md` (order thread from the deck · telemetry thread · decision/control
  thread back), describing industry practice fully incl. consciously-omitted systems.
- (c) **Then → Phase 0** (repo skeleton + the three-stage mapping table **with the
  §14 columns**). Diagrams 2 & 3 no longer gate Phase 0.
- (d) **Just-in-time:** Diagram 2 (UMH Core — decided, §12 #16; draw before the "Later" re-platform)
  · Diagram 3 (cloud-native → floci, before Phase 6).

### Previous session (2026-06-21) — industry discovery, Eraser MCP, full architecture review
A long working session, three threads:

**1. Real-world industry discovery (MERGED, PR #6).** Two anonymized consulting discovery slides (a
global specialty-chemicals manufacturer + a global packaged-foods/CPG manufacturer) folded into the
problem statement as *problem patterns*. Validated the thesis; sharpened it (days-to-data, within-site
integrator divergence, govern-and-reuse, M&A footprint + SAP ECC→S/4, yield/HITL feedback). Resolved
charter §12 **#13** (governance → lightweight governed catalog) and **#14** (Plane 4 flagship → yield).
No company names anywhere (branch history squashed clean before merge).

**2. Diagram convention + Eraser MCP (PR #7, branch `docs/diagram-convention-eraser`).** DECIDED: all
project diagrams are created with the **Eraser MCP** and saved to the Eraser workspace
**`scada_harmonization`** (AGENTS.md "Diagrams", HANDOFF conventions, charter tooling). Eraser MCP
installed across all local agents (Claude, Codex, Gemini, Cursor, OpenCode, Kimi, Hermes; **`pi` has no
MCP support**) — each still needs its **own OAuth login on first use** (per-tool, interactive; Hermes
saved but disabled until login).

**3. Reference-architecture review → charter §13 (same branch).** Benchmarked the design **layer by
layer (8 layers)** against a real industrial-products target architecture. Resolved 18 add/keep-out
decisions (charter **§13.1 ledger**). Net-new: OPC-UA (Geismar), edge store-and-forward, Docker-network
segmentation, historian-less site, real-time alerting, medallion lakehouse + Spark ETL, batch ingestion,
MLflow, online/offline feature store, Prometheus+Grafana observability. New learning milestones: OPC-UA,
Spark, Prometheus, MLflow (join Debezium + Redis). **Three implementation-variant diagrams** to draw in
Eraser (hand-built/Python-centric · UMH-anchored · cloud-native→floci) — **NOT yet drawn; owner asked to
hold.**

(All 2026-06-21 work is **merged to `main`**; see Git/PR state below.)

### Git / PR state
- **PR #1–#9** — charter, infra, diagram convention, §13 review, git discipline → **MERGED**.
- **PR #15** — handoff teaching-walkthrough plan → **MERGED** (`90b6cc1`).
- **PR #16** — Diagram-1 walkthrough sequencing confirmation → **MERGED** (`bcbd8cd`).
- **This session (2026-07-06)** — branch `docs/itot-best-practice-review-adoption` — the best-practice
  review adoption (4 themed commits: staleness sweep · tool/version pins · charter §14 N1–N35 ·
  plan restructure + this handoff). **PR open — owner to merge**, then delete the branch.

### Resolved decisions (all in charter §4/§6/§12)
| # | Decision | Resolution |
|---|----------|-----------|
| 1 | Domain | Multi-site process / specialty-chemicals (data-driven by TEP + Industrial IoT) |
| 2 | MQTT broker | **Two-tier:** Mosquitto per-site edge + **EMQX ≥5.9 central UNS (BSL 1.1, single node** — clustering is paid; pre-5.9 "OSS" had no Kafka/Postgres bridges), connected by a **Python site-forwarder** (not a raw broker bridge — preserves Sparkplug state; the forwarder is the cross-site harmonization point) |
| 3 | Historian | **TimescaleDB** (SQL everywhere; modeling not ingest rate is the bottleneck) |
| 4 | PLC literalness | **Hybrid** — Rotterdam & Corpus Christi Python-modeled; **two real protocol sites: OpenPLC/Modbus (Beaumont) + OPC-UA/`asyncua` (Geismar)** (charter §13 L1.1) |
| 6 | Sites + enterprise | **Lagos Specialty Chemicals** (UNS root `lagos-chem`); **4 sites** — Beaumont (Allen-Bradley), Geismar (Siemens), Rotterdam (Ignition-style), Corpus Christi (CygNet) |
| 7 | Postgres deployment | ~~Historian + role-B ODS consolidated in the Timescale instance~~ **Amended (§14 N16): three Postgres homes** — OT-side Timescale (`ts_historian`), **IT-side Postgres** (`ods_core` + `erp_shadow` — the consolidation straddled the iDMZ), OT-side plant Postgres (role A, CDC-captured) |
| 8 | CDC | **Start Python poll** (Debezium-shaped events), **design for Debezium**, with an explicit hands-on Debezium learning milestone in Phase 5a (5a.1 → 5a.2 → 5a.3) |

Plus the **relational schema layout** (charter §4): two Postgres homes —
`ts_historian` + `ods_core` + `erp_shadow` (Timescale, pipeline-owned) and `mes`/`lims`/`cmms`/`quality`
(separate Postgres, source-of-record). Boundary rules: no cross-home FKs; reconciliation in
`ods_core.identity_map`; lane discipline; Neo4j reads the reconciled side only.

---

## 3. What's next — Diagram 1 teaching walkthrough (then Diagrams 2–3, then Phase 0)

### ⭐ IMMEDIATE NEXT ACTION (do this first — Phase 0 starts as soon as Diagram 1 locks)

**End-to-end teaching walkthrough of Eraser Diagram 1 (Hand-built / Python-centric).** Owner goal:
understand and be able to **explain the full data and integration flow** — each component's role, why it
exists, and where it sits — well enough to **teach others / build a presentation**. Use external research
to validate best practices and augment explanations. **Identify gaps in Diagram 1 and correct them** in
Eraser as we go. This pass **locks Diagram 1 as the template** for Diagrams 2 & 3.

**Diagram URL:** https://app.eraser.io/workspace/6Ng61sTaot9VjtU87bEY?diagram=vheRVPpajwodCEDwqnBZ&layout=canvas

**Per-component cadence (repeat for every block on the diagram):**
1. **Problem tie-in** — which real pain (days-to-data, site divergence, governance, identity, yield/HITL)
   does this component solve?
2. **Mechanism** — what it does, inputs/outputs, protocols/formats, which plane/zone it lives in.
3. **External research** — web search for current best practice / industry convention; note where we align
   or deliberately diverge (e.g. central EMQX UNS vs per-plant-only brokers — charter §13.7 Tier 3,
   "broker topology divergence" bullet).
4. **Gap check** — missing arrow, wrong zone, missing consumer, ambiguous flow? Log it; fix in Eraser
   (`manually_update_diagram` when arrow direction matters).
5. **One-line teach-back** — a sentence the owner can reuse in a presentation.

**Suggested walkthrough order (follow the data, left → right, OT → iDMZ → IT):**

| Block | Components to cover |
|-------|---------------------|
| **A — Problem & L0** | Synthetic TEP + IIoT replay; why only L0 is synthetic; scan-rate/deadband (P1) |
| **B — OT edge (L1–2)** | Sensors/actuators; OpenPLC/Modbus (Beaumont); OPC-UA (Geismar); Python-modeled PLCs (Rotterdam, Corpus Christi); equipment-type templates (P6) |
| **C — OT messaging (L3)** | Per-site Mosquitto; Sparkplug B contract (births/RBE); Python Sparkplug publishers; local site namespace |
| **D — Harmonization** | Python site-forwarder (store-and-forward L1.2); cross-site conforming; `metric_registry` / three-stage mapping table as governed data product |
| **E — iDMZ (L3.5)** | Central EMQX UNS broker (Z2); the three iDMZ crossings (telemetry ↑, CDC ↑, recommendations ↓) |
| **F — OT consumers (L3)** | TimescaleDB historian; Grafana; Ignition; real-time alerting (L2.1); HITL operator console + graded HITL (P3); defense-in-depth safety on writeback (P2); historian-less site (L1.4) |
| **G — OT transactional (L3, IT-domain)** | MES/LIMS/CMMS/Quality + plant Postgres (Z3); why they're OT-side by ISA-95; P8 business-joins-downstream |
| **H — iDMZ → IT streaming** | CDC (Python poll → Debezium milestone); Kafka; UNS → Kafka bridge |
| **I — IT storage & analytics (L4–5)** | `ods_core` + `identity_map` (MDM analog L3.1); medallion Bronze/Silver/Gold + Spark ETL; Bronze schema validation + dead_letter (P7); DuckDB OLAP; batch/file-drop (L4.2); golden-batch reference (P9) |
| **J — Enterprise & context** | ERPNext (L4); Neo4j + GraphRAG; ISO 15926/DEXPI ontology (minimal start L5.1) |
| **K — Plane 4 (Apply)** | Edge inference (per-site) + cloud training; three feature planes; MLflow; Redis online / gold offline (L6.2); SPC/EWMA (P5); SHAP explainability (P4); closed-loop UNS command path (L6.5) |
| **L — Cross-cutting** | Prometheus + Grafana observability (L7.1); Docker OT/IT segmentation (L1.3); floci AWS emulation; 5 consumer personas; Databricks/Iggy as post-hand-built options (§13.6) |

**§14 gap checklist (2026-07-06 review — fold into each block's step 4 "Gap check"; fix in Eraser):**

| Block | Charter §14 items to verify / correct in Diagram 1 |
|-------|-----------------------------------------------------|
| C / D / E | **N1** namespace encoding (site tier = `spBv1.0/...`; retained ISA-95 republish at EMQX); **N3/N4** forwarder-as-Edge-Node + Primary-Host STATE; EMQX labeled **single node** (not "cluster" — BSL) |
| E | **N21** the five conduits + initiation direction (no IT-initiated into OT); **N23** TLS on forwarder→EMQX |
| F | **N10** quality flow; **N20** ISA-18.2 alarm node placed per-site edge; **N24** `command_audit` |
| G | **N13/N14** `production_lot` + `material_definition`/`material_lot` tables (not `batch`) |
| H | **N6** UNS→Kafka bridge as the protobuf decode point (holds BIRTH state); **C3** Debezium/Connect dual-homed in the iDMZ |
| I | **N16** `ods_core`/`erp_shadow` moved to IT-side Postgres; **N27** Bronze immutable-raw; **N28** dead-letter redrive path |
| K | **N30** L0 shadow namespace; **N32** TTL on recommendations; **N33** T²/SPE; **N5** DCMD command-path arrows (console → EMQX → forwarder → DCMD → PLC → DDATA read-back) |
| L | **N21** Prometheus per zone (federated), Redis per-site OT-side; zone labels |

**Session deliverables:**
- Owner can narrate **end-to-end flows** (OT telemetry path, IT CDC path, closed-loop command path,
  analytics/ML path, context/graph path) without looking at notes.
- **Gap log** — anything found → fixed in Diagram 1 or recorded as a charter follow-up if it needs a
  decision.
- Durable teaching notes → `design/LEARNING_LOG.md` (glossary entries as terms appear).

**After Diagram 1 is locked:** run the **end-to-end narrative walkthrough** (three threads —
`design/E2E_WALKTHROUGH.md` + the deck in `reference/enterprise_it_ot_deck/`), then **Phase 0 starts**
(resequenced 2026-07-06); Diagrams 2 & 3 are drawn just-in-time later (Diagram 2 = UMH Core, decided
§12 #16; Diagram 3 before Phase 6).

---

### Phase 0 (after diagrams — turn design into code)

**State:** deferred until Diagrams 1–3 are complete. Branch `feat/phase-0-foundation` may exist from
earlier discussion (doc/decision commits only; **no code yet**).

When Phase 0 starts, re-explain from scratch (learning-first), align, then build:

- **What Phase 0 is:** foundation/scaffolding — *not* Marimo notebook work (Marimo starts Phase 1). Three pieces:
  1. **Python project skeleton** — `pyproject.toml` via **`uv`** + `src/scada_harmonizer/` + `notebooks/` + `tests/`.
  2. **Three-stage mapping table as config (THE SPINE)** — YAML + Pydantic validation; one measurement across all 4 sites.
  3. **Seed `design/LEARNING_LOG.md`** — learning log + glossary.
- **Alignment questions:** Phase 0 scope OK? YAML vs TOML/JSON? Deep concept walk-through first or straight to skeleton?
- **Then build** per cadence: explain → align → build → run & observe → prune.

### Tooling decided this session
- **`uv`** for all package/project management (`uv add`/`sync`/`run`, committed `uv.lock`). No pip/poetry.
- **FastAPI** = intended-but-deferred backend for the Plane 3 query/copilot API (~Phase 5b/7); core
  pipeline needs no HTTP backend.
- **Plane 4 (Apply / Intelligence)** captured: Track A traditional ML (Phase 6), Track B LLM/GenAI (Phase 7).
- **Redis** = deferred/optional Plane 4 (online feature store etc.); **learning Redis is a goal**.

### Explicit hands-on learning goals (deliberate milestones, like real engagements)
- **Debezium** — log-based CDC (Phase 5a milestone 5a.2/5a.3).
- **Redis** — online feature store (Phase 6 milestone). Both are *learn-by-building*, not shortcuts.

Subsequent build phases (charter §8): 1 Level-0 replay → 2 PLC disguise + Sparkplug (edge Mosquitto) →
3 OT consume (TimescaleDB + Grafana) → 4a harmonization proof (Python-modeled sites + forwarders +
central EMQX + equivalence suite) → 4b real-protocol sites (OpenPLC Beaumont & OPC-UA Geismar) →
4c resilience & zoning (store-and-forward, Docker segmentation, historian-less site)
→ 5a IT source + CDC (Debezium milestone) → 5b context (ERPNext + Neo4j) → 6 loop closure (ML/inference
+ floci) → 7 reasoning (GraphRAG) → later: re-platform onto UMH.

---

## 4. How to work on this project (observed conventions & preferences)

- **One decision at a time.** The user prefers deliberate, discussed decisions over bulk choices.
- **Learning-first.** The user wants to understand the bare-metal mechanics before enterprise tooling.
  When recommending, explain the *why* and surface trade-offs honestly (e.g. the Sparkplug-bridge
  caveat, log-based vs. poll CDC). The user explicitly wants hands-on **Debezium** experience.
- **Git workflow:** create a **branch per change → open a PR → the _user_ merges → the assistant then
  deletes the branch** (local + remote) and fast-forwards `main`. Do **not** push straight to `main`.
  **Delete the branch as soon as its PR is merged** (`git branch -d` + `git push origin --delete`).
- **Before telling the user a PR is "ready to merge," push ALL commits and verify the branch is fully
  up to date** — `git status` clean and `git log origin/<branch>..HEAD` empty. (Learned the hard way:
  PR #7 was merged before later commits were pushed, dropping charter §13 from `main` until PR #8 fixed
  it. Commits added to a branch *after* its PR merged are NOT in `main` — open a **new** PR for them.)
- **Commit messages** end with a `Co-Authored-By` trailer naming the assisting model (currently
  `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`; use whichever model actually assisted).
- **Never commit `.codex/`** (unrelated pre-existing tooling, like `.claude/`). Stage files explicitly.
- **`reference/` is local-only** — `reference/docs/` (ISHE) and `reference/engineering_drawing_business_case/`
  (EngiGraph) are gitignored private business-case material kept as design references; only
  `reference/README.md` is tracked. Mine them for *patterns* (ISHE → Plane 1 Pydantic/harmonization;
  EngiGraph → Plane 3 ISO 15926 ontology/graph), not business framing.
- **Charter governs.** Keep `PROJECT_CHARTER.md` authoritative; mirror changes into README/AGENTS so
  they don't drift.
- **Learning-first, no black boxes.** The owner is learning the stack bare-metal. Per component:
  **explain → align → build piece by piece → run & observe → prune** (keep docstrings + a short note;
  durable concepts go to `design/LEARNING_LOG.md`). Use **Marimo** (`marimo-pair`) for interactive
  learning in `notebooks/` (one per component); migrate finalized code into the `src/scada_harmonizer/`
  package (the source of truth). Prefer raw mechanism before convenience wrappers; Docker Compose is a
  learning artifact; keep a glossary; tests encode understanding; YAGNI; deterministic re-runs; owner
  runs commands themselves. See AGENTS.md → "How we work" for the full cadence + practices.
- **Diagrams → Eraser only, saved to the `scada_harmonization` Eraser workspace.** All project diagrams
  are created with the **Eraser MCP** (registered for every local agent) and saved to the Eraser folder
  **`scada_harmonization`**; embed/link the diagram URL in the relevant `design/*.md`. See AGENTS.md →
  "Diagrams (DECIDED)".
- **Update `HANDOFF.md` at the end of EVERY session** (status, git/PR state, next steps). Mandatory.

---

## 5. Key references

| Path | What it is |
|------|-----------|
| `design/PROJECT_CHARTER.md` | **Authoritative project definition** (read this first after this file) |
| `design/DOMAIN.md` | Domain narrative — Lagos Specialty Chemicals backstory (why the 4 sites diverge) |
| `AGENTS.md` | Agent working guide — constraints, data flow, domain, build sequence |
| `README.md` | Human-facing summary |
| `design/uns_home_lab_notes.md` | Vision & scope |
| `design/{hand_built,umh_anchored,python_centric}_*_notes.md` | Architecture options (build phase vs. abstraction phase) |
| `design/synthetic_data_generation_notes.md` | Data strategy & the 6-layer synthetic pipeline |
| `reference/README.md` | Index of the local-only reference material (ISHE, EngiGraph) |

---

## 6. No open blocking questions

The next concrete action is the **Diagram 1 end-to-end teaching walkthrough** (§3) with the §14 gap
checklist; **Phase 0 starts as soon as Diagram 1 locks** (resequenced 2026-07-06). No open blocking
decisions (§12 #16 resolved → UMH Core). The best-practice-review PR **#17** (branch
`docs/itot-best-practice-review-adoption`) awaits the owner's merge.
