# Project Handoff

**Purpose:** let any agent (or human) pick up this project without re-deriving context.
**Last updated:** 2026-06-23

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

## 2. Current status (2026-06-22)

**Phase: pre-implementation.** Design + charter complete; **all infrastructure decisions resolved**;
**no source code yet.** Architecture diagrams begun in Eraser (hand-built diagram #1 in progress).

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

⏭ **Open for next session / agent:**
- (0) ~~Review the owner-provided reference `design/SAMPLE_*`~~ — **DONE (2026-06-23):** audited the CPG
  DYI/AYM reference pattern-by-pattern. Design validated; adopted **9 patterns** (charter **§13.7**):
  Tier 1 — scan-rate/deadband strategy (P1), defense-in-depth closed-loop safety (P2), graded HITL
  L1/L2/L3 (P3), explainability as required ML output (P4), SPC/adaptive control charts (P5); Tier 2 —
  equipment-type templates (P6), Bronze schema validation (P7), business-joins-downstream principle (P8),
  golden-batch reference (P9). Tier 3 noted as conscious scope choices (no CV, no connected-worker,
  central-EMQX-UNS kept). (`SAMPLE_*` stays local-only/gitignored.)
- (a) **NEXT SESSION — teaching walkthrough of Diagram 1 (owner's explicit plan).** Before drawing
  Diagrams 2 & 3, walk **component-by-component through Diagram 1**, explaining *why each piece exists in
  terms of the problem we're solving*, at a depth the owner can **teach to others / build a presentation**
  from. For each component: tie it to the problem → explain the mechanism → **do a web search to augment**
  the project's own material so the teaching is comprehensive and current → note any **gap or refinement**
  → update the diagram where needed. Two goals: (1) a presentation the owner will deliver, (2) surface
  further refinements. **This is the review pass that locks Diagram 1 as the template.** Diagram 1 already
  has §13.7 patterns + §13.8 OT/IT zoning applied and the owner approved its look (2026-06-23).
  Eraser: folder "SCADA Harmonization", fileId `6Ng61sTaot9VjtU87bEY`, diagramId `vheRVPpajwodCEDwqnBZ`.
- (b) ~~The "two components" discussion~~ — **DONE** (Databricks + Iggy, charter §13.6).
- (c) Then draw **Diagram 2 (UMH-anchored)** and **Diagram 3 (cloud-native → floci)**, matching #1.
- (d) Then start **Phase 0**.

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
- **PR #1–#5** — earlier charter / infra / gitignore work → **MERGED**.
- **PR #6** — anonymized industry discovery → **MERGED** (`2d99eb5`); branch deleted.
- **PR #7** — diagram convention (Eraser → `scada_harmonization`) → **MERGED**; branch deleted.
- **PR #8** — reference-architecture review (charter §13) → **MERGED** (`2a4db7b`); branch deleted.
  *(Lesson: #8 existed because #7 was merged before its later commits were pushed — see git/PR discipline in AGENTS.md.)*
- **PR #9** — git/PR discipline notes → **MERGED** (`adc85b4`); branch deleted.
- **This session's doc update** → branch `docs/session-eraser-diagrams-plane4`, **awaiting owner merge**
  (no code; design + §13.5). The Eraser diagram itself lives in Eraser, not git.
- ⚠️ **Next agent:** merge this branch → continue refining Diagram 1 → discuss the two components → draw Diagrams 2 & 3 → Phase 0.

### Resolved decisions (all in charter §4/§6/§12)
| # | Decision | Resolution |
|---|----------|-----------|
| 1 | Domain | Multi-site process / specialty-chemicals (data-driven by TEP + Industrial IoT) |
| 2 | MQTT broker | **Two-tier:** Mosquitto per-site edge + EMQX OSS central UNS, connected by a **Python site-forwarder** (not a raw broker bridge — preserves Sparkplug state; the forwarder is the cross-site harmonization point) |
| 3 | Historian | **TimescaleDB** (SQL everywhere; modeling not ingest rate is the bottleneck) |
| 4 | PLC literalness | **Hybrid** — Rotterdam & Corpus Christi Python-modeled; **two real protocol sites: OpenPLC/Modbus (Beaumont) + OPC-UA/`asyncua` (Geismar)** (charter §13 L1.1) |
| 6 | Sites + enterprise | **Lagos Specialty Chemicals** (UNS root `lagos-chem`); **4 sites** — Beaumont (Allen-Bradley), Geismar (Siemens), Rotterdam (Ignition-style), Corpus Christi (CygNet) |
| 7 | Postgres deployment | Historian + role-B ODS consolidated in the Timescale instance (separate schemas); role-A source systems in a **separate** Postgres home so CDC captures from a foreign system |
| 8 | CDC | **Start Python poll** (Debezium-shaped events), **design for Debezium**, with an explicit hands-on Debezium learning milestone in Phase 5a (5a.1 → 5a.2 → 5a.3) |

Plus the **relational schema layout** (charter §4): two Postgres homes —
`ts_historian` + `ods_core` + `erp_shadow` (Timescale, pipeline-owned) and `mes`/`lims`/`cmms`/`quality`
(separate Postgres, source-of-record). Boundary rules: no cross-home FKs; reconciliation in
`ods_core.identity_map`; lane discipline; Neo4j reads the reconciled side only.

---

## 3. What's next — Phase 0 (turn design into code)

**State:** branch `feat/phase-0-foundation` exists (doc/decision commits only; **no code yet**). Phase 0
was paused mid-discussion for an owner break.

### ⭐ IMMEDIATE NEXT ACTION (do this first, before any code)

**Re-explain Phase 0 to the owner (learning-first), then align, then build.** The owner is learning the
stack bare-metal and may resume with a *different agent*, so do NOT assume the prior explanation is
fresh — **walk through the Phase 0 concept again from scratch**, conversationally, and get explicit
alignment before writing files. The owner specifically wants this re-explanation to happen.

Re-explanation must cover (this is the script to reproduce):

- **What Phase 0 is:** foundation/scaffolding — *not* Marimo notebook work (Marimo starts Phase 1 with
  real runtime logic). Three pieces:
  1. **Python project skeleton** — `pyproject.toml` **managed by `uv`** + `src/scada_harmonizer/` +
     `notebooks/` + `tests/`. Concepts to teach: `src/` layout, package-vs-scripts, `uv` workflow
     (`uv add`/`sync`/`run`, `uv.lock`), minimal deps (add each when needed, justify it).
  2. **The three-stage name mapping table as config (THE SPINE 🫀)** — `friendly variable →
     site-specific PLC tag → Sparkplug metric` + metadata (unit, range, cadence, asset class, ISA-95
     path, downstream IDs). Format leaning **YAML**, validated on load by a **Pydantic** model (the
     owner's first hands-on Pydantic concept + ISA-95 made concrete). Model ONE measurement (e.g. a
     reactor feed-flow) across ALL 4 sites' divergent naming — seeing one physical truth expressed 4
     ways, validated into one canonical identity, is the harmonization thesis in miniature.
  3. **Seed `design/LEARNING_LOG.md`** — learning log + glossary, from day one.
- **Open alignment questions to ask the owner:** (a) Phase 0 scope OK? (b) **YAML** for the mapping
  config (vs TOML/JSON/CSV)? (c) start with a deep concept walk-through of the three-stage table (fully
  worked 4-site example) or go straight to drafting skeleton + first mapping?
- **Then build** per the cadence: explain → align → build piece by piece → run & observe → prune.

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
3 OT consume (TimescaleDB + Grafana) → 4 multi-site + central EMQX + OpenPLC site (harmonization proof)
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
- **Commit messages** end with the trailer: `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
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

All design work is merged to `main`; no open PRs. There is **no unanswered question blocking
progress** — the next concrete action is to **start Phase 0** in learning-first mode (concept primer
for the repo skeleton + three-stage mapping table → align → build → seed `design/LEARNING_LOG.md`).
</content>
