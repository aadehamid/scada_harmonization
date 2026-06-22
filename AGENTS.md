# AGENTS.md

Guidance for AI agents (and humans) working in this repository.

## Project overview

An **industrial data harmonization & contextualization home lab** that simulates a **multi-site
process / specialty-chemicals manufacturer**. It harmonizes deliberately-divergent OT data from
multiple sites (tags differ site-to-site *and* within a site, by integrator) into a common
Sparkplug B / MQTT **Unified Namespace (UNS)** — **governed as a reusable data product** — then
contextualizes the result into a Neo4j knowledge graph. It is a **learning environment and
architecture prototype**, not a product — the goal is to understand each layer of a modern
industrial data stack before adopting enterprise software that abstracts it away. The simulated
problem mirrors real process/CPG digital-transformation discovery (anonymized industry pains:
days-to-data, site-owned fragmentation, govern-and-reuse, yield improvement); see charter §2.

The project is currently in a **pre-implementation state** (design/charter complete, no source code
yet).

## Picking up the work

**New here? Read [`HANDOFF.md`](HANDOFF.md) first** — it captures current status (decisions resolved,
open PRs, what's done vs. next), the working conventions, and the immediate next action. Then read the
charter below.

## Authoritative source of truth

**`design/PROJECT_CHARTER.md` governs.** Read it first (after `HANDOFF.md`). If anything in this file
or elsewhere conflicts with the charter, the charter wins.

## How we work — learning-first collaboration (IMPORTANT)

The owner is building this lab **to learn the stack at the bare-metal level**. Nothing should be a
black box: the goal is for the owner to understand *every block of code* and *why* it exists. Optimize
for understanding, not speed.

**Session discipline**
- **Update `HANDOFF.md` at the end of EVERY session** — refresh "Current status," git/PR state, and
  "What's next" so the next agent (or the owner) is never confused. This is mandatory, not optional.

**Git / PR discipline (learned the hard way — do NOT repeat)**
- **Branch per change → PR → the _owner_ merges → delete the branch.** Never push straight to `main`.
- **Before telling the owner a PR is "ready to merge," push ALL commits and confirm the branch is fully
  up to date** — run `git status` (clean) and `git log origin/<branch>..HEAD` (empty). *Why:* a PR was
  once merged while later commits were still unpushed, silently dropping a whole work section from
  `main`. Verify the remote branch HEAD is what you think it is *before* you say "ready."
- **Delete every branch as soon as its PR is merged** — local *and* remote (`git branch -d <b>` +
  `git push origin --delete <b>`) — then fast-forward `main`. No merged branch lingers.
- If you add commits to a branch *after* its PR was already merged, those commits are NOT in `main`:
  open a **new** PR for them (you can't reopen a merged PR).

**Build cadence (per component) — explain → align → build → observe → prune**
1. **Explain first.** Before writing non-trivial code, describe *what* we're about to build, *why*, a
   short **concept primer** for any new tech (Sparkplug B, hypertables, CDC/Debezium, Cypher, ISO
   15926, …), and the **alternatives + trade-offs**. Situate it in its charter plane.
2. **Align.** Discuss at a high level and confirm the owner understands the concept before coding.
3. **Build piece by piece.** Small, reviewable increments. Narrate each block (what it does + why).
   Favor explicit, readable code over clever code — this is a teaching codebase.
4. **Run & observe.** Actually run it and look at the output together (e.g. `mosquitto_sub` to see
   Sparkplug messages, SQL against TimescaleDB, Cypher against Neo4j). Seeing it work cements the why.
5. **Prune.** Once aligned and the component is done, remove the teaching scaffolding, keeping only
   useful **code documentation** (docstrings + a short component note). Durable concepts/gotchas go to
   a **learning log** (`design/LEARNING_LOG.md`) so pruning code never loses the learning.

**Medium**
- **Marimo notebooks** (via the `marimo-pair` skill) are the interactive surface for learning and
  prototyping Python logic — explain/experiment cell by cell.
- Infrastructure (brokers, TimescaleDB, OpenPLC, Neo4j, ERPNext) runs as **services** (Docker); the
  notebook/package code talks to them as clients.
- **Notebook → package (DECIDED):** `notebooks/` holds one Marimo notebook **per component** (rich
  explanations, committed, clearly the "learning surface"); `src/scada_harmonizer/` is the **package =
  source of truth** where finalized, documented code graduates. When a component is done: prune the
  notebook's teaching scaffolding (keep a slim demo or retire it), migrate clean code to `src/`,
  durable concepts to `design/LEARNING_LOG.md`.

**Diagrams (DECIDED) — use Eraser, save to the `scada_harmonization` workspace**
- **All project diagrams are created with the Eraser MCP** — architecture, data-flow, sequence, ER,
  ISA-95 topology, knowledge-graph schema, etc. Do **not** produce deliverable diagrams with other
  tools or as committed ASCII art. Eraser is the single source of truth for visual artifacts.
- **Every diagram is saved to the Eraser workspace/folder named `scada_harmonization`** so all diagrams
  live in one place. Always target that folder when calling Eraser.
- **One diagram per architecture view.** Each implementation type (hand-built / Python-centric,
  UMH-anchored, cloud-native) gets its own full architecture diagram in that workspace (charter §5).
- Quick inline **ASCII sketches are fine for discussion**, but the canonical artifact is the Eraser
  diagram — embed/link its URL in the relevant `design/*.md` doc so it's discoverable.
- The Eraser MCP is registered for all local agents (Claude, Codex, Gemini, Cursor, OpenCode, Kimi,
  Hermes); each authenticates via its own OAuth login on first use.

**Pace is owner-set.** Pause at natural boundaries; ask "go deeper or move on?" Don't race ahead.

**Learning practices**
1. **Raw mechanism before convenience wrapper.** Show the actual thing first — a raw `paho-mqtt`
   publish + real Sparkplug payload bytes before a helper; raw SQL/Cypher before an ORM. Justify every
   dependency ("why this library, what it hides"). Biggest guard against black boxes.
2. **Docker Compose is a learning artifact.** Add services one at a time, each explained; the owner
   brings them up/down (`! docker compose up …`). The wiring is half the lesson.
3. **Running glossary.** Maintain a GLOSSARY in `design/LEARNING_LOG.md`; add plain-language defs as
   each term appears (ISA-95, UNS, NBIRTH/DBIRTH, RBE, OLTP/OLAP, WAL, CDC, FLOC, DEXPI, hypertable, …).
4. **Tests as executable understanding.** Small targeted tests (e.g. cross-source equivalence) encode
   what was learned and can't go stale; borrow the ISHE test strategy.
5. **YAGNI / one slice at a time.** Build only what the current phase needs, fully understood. Don't
   scaffold later planes early. Depth over breadth.
6. **Determinism for re-runs.** Seed randomness; make replays deterministic so re-running a block
   while studying it gives the same result.
7. **Owner runs things, not just watches.** Where practical the owner executes commands/queries
   (`! …`), predicts outputs, and compares. Active recall beats passive narration.
8. **Commit history as a learning trail.** Small commits + explanatory messages + the learning log let
   the owner later ask "why is this here?" (the `explain` / `what-happened` skills read provenance).

**Explicit learn-by-building milestones (do NOT shortcut):** **Debezium** (log-based CDC, Phase 5a),
**Redis** (online feature store, Phase 6), **OPC-UA** (real protocol at Geismar, Phase 4), **Spark**
(medallion ETL, Phase 6), **Prometheus** (observability, Phase 3), and **MLflow** (model registry,
Phase 6) are deliberate hands-on goals — build them the real way and explain, even where a simpler
stand-in would suffice. The owner wants the genuine experience. (Full list & rationale: charter §13.)

## Key documentation (all in `design/`)

- `PROJECT_CHARTER.md` — authoritative project definition (purpose, planes, architecture, build sequence, decisions)
- `uns_home_lab_notes.md` — vision & high-level scope
- `hand_built_sparkplug_uns_notes.md` — architecture option: hand-built (build/learn phase)
- `python_centric_uns_notes.md` — implementation philosophy: Python-centric
- `umh_anchored_sparkplug_uns_notes.md` — architecture option: UMH-anchored (later abstraction phase)
- `synthetic_data_generation_notes.md` — data strategy & the 6-layer synthetic pipeline

> **Reference material (local-only):** `reference/docs/` (ISHE harmonization patterns) and
> `reference/engineering_drawing_business_case/` (EngiGraph ontology/graph patterns) are **design
> references only**, not project definitions. The reusable *patterns* have been folded into the
> charter (§7); the business/market framing is discarded. See `reference/README.md`. Do not treat
> them as current scope.

## The three planes

1. **Harmonize (OT)** — synthetic Level 0 → PLC-world disguise → Sparkplug B → UNS; unit/status/timestamp normalization + per-field lineage. *(reference patterns: ISHE / `reference/docs/`)*
2. **Record (Enterprise)** — curated operational events → ERPNext (SAP-like).
3. **Contextualize (Knowledge)** — UNS + IT transactional + ERP + asset topology → **identity reconciliation** → Neo4j knowledge graph (ISO 15926 / DEXPI-aligned) → GraphRAG. *(reference patterns: EngiGraph / `reference/engineering_drawing_business_case/`)*
4. **Apply (Intelligence)** — consumes Planes 1–3; the payoff. **Track A** traditional ML (predictive maintenance, anomaly, time-series forecasting, soft sensors) — **flagship: yield improvement / production-leakage detection**. Runs **per-site edge inference** (real-time, off the local broker) **+ cloud/central training & batch serving**; trains on **three feature planes** (OT historian, IT/`ods_core`, harmonized gold); MLflow deploys the same model to edge + cloud (online Redis / offline gold split). **Closed-loop control with human-in-the-loop**: model → HITL operator console (approve/edit/reject) → approved command via the UNS (Sparkplug setpoint topic) → site edge → controller writeback (OpenPLC/OPC-UA) → actuators — the model never actuates, the controller executes (charter §13.5) [Phase 6]. **Track B** LLM/GenAI (retrieval, NL query, summaries, copilot via GraphRAG over Neo4j) [Phase 7]. *Tooling deferred — built so the foundation feeds both.*

Sources span **IT / OT / ET**: OT (SCADA/PLC tags), IT (Postgres transactional: MES/LIMS/CMMS/quality), ET (engineering topology).

## Architecture: data flow

```
L0 synthetic (TEP process + IIoT machines  +  relational MES/LIMS/CMMS tables)
  → L1/2 PLC-world disguise — hybrid: Python-modeled cryptic tags (N7:20, FIC101_PV)
         per site; ONE site (Beaumont) real OpenPLC over Modbus TCP
  → L3 edge broker: Mosquitto per-site (local Sparkplug, divergent namespace)
  → L3 Python site-forwarder → central EMQX (cross-site conforming = harmonization)
  → L3 OT consumers: Ignition (SCADA), TimescaleDB historian (hypertables), Grafana
  → L3 Postgres (OLTP): role A = separate source systems; role B = ODS in Timescale instance
  → L3/4 Kafka → Parquet/object store → DuckDB ... analytics path (OLAP)
       ↑ Postgres role A → CDC (Python poll → Debezium) → Kafka → identity reconciliation → UNS/Neo4j
  → L4 floci ..................................... local AWS emulation (incl. RDS)
  ── cross-cutting ──
  → ERPNext (enterprise records, on MariaDB) · Neo4j (knowledge graph) · GraphRAG (reasoning)
```

**Storage by concern (no overlap):** time-series→**TimescaleDB**; relational/transactional (OLTP)→Postgres;
analytical (OLAP)→DuckDB; relationships→Neo4j; enterprise→ERPNext (its own MariaDB).

All custom logic is **Python** (Paho MQTT, PySparkplug, pandas, Pydantic, Neo4j driver). Python is a
first-class UNS participant (virtual sensors, Sparkplug publishers, enrichment, inference), not glue.

## Critical design constraints

- **Only Level 0 is synthetic** — everything above behaves like real software.
- **Preserve the PLC-world boundary** — never publish clean semantic names straight from Python; the
  cryptic → harmonized transition is the whole point of the lab.
- **The three-stage mapping table is the spine** — `friendly variable → site-specific PLC tag →
  Sparkplug metric`, carrying unit, range, cadence, asset class, site context, downstream
  ERP/graph IDs, **and governance metadata (owner/"gatekeeper", definition, lineage)**.
- **Govern what you harmonize** — the mapping table / `metric_registry` is a *governed data product*:
  every canonical metric is owned, defined, and lineage-tracked so it is reusable without
  re-interpretation. Local site autonomy + central enterprise standards coexist (global *and* local).
- **Pydantic-first** — every data boundary is a validated model; no raw dicts cross layers.
- **Deterministic, reproducible transforms** — same input → same output.
- **Cross-source equivalence** — the same physical event from different sites must produce identical
  harmonized output. This is the proof of harmonization.
- **Sparkplug B as the contract** — births, aliases, datatypes, lifecycle; not plain JSON-over-MQTT.
- **Harmonize before contextualize** — Neo4j/ERPNext consume the *harmonized* side, not raw values.
- **Reconcile identities; preserve system-of-record authority** — stitch IT/OT/ET keys into one
  identity, but each source stays authoritative for its domain; the Postgres ODS (role B) is a
  derived copy, not the source of truth.
- **Right store for the shape** — time-series→historian, relational→Postgres (OLTP),
  analytical→DuckDB (OLAP), relationships→Neo4j. No engine duplicates another's concern.
- **Config over code** — site mappings, status maps, unit factors, ontology are data.
- **Upgrade-friendly** — every OSS component has a credible enterprise replacement path.

## Domain & data

Enterprise: **Lagos Specialty Chemicals** (UNS root `lagos-chem`), a multi-site process/specialty-chemicals
manufacturer. Anchor datasets (see charter §6):
- **Tennessee Eastman Process** — continuous process units (reactors, columns, loops).
- **Industrial IoT Dataset (Synthetic)** — rotating machines (pumps, compressors, motors).

**4 sites**, each the same units/machines on a different SCADA lineage with divergent naming:
Beaumont (Allen-Bradley, real OpenPLC), Geismar (Siemens), Rotterdam (Ignition-style), Corpus Christi
(CygNet compound tags). Physical meaning is *assigned* at the mapping stage — the data's statistical
shape, not its labels, is the constraint.

## Build sequence (see charter §8)

Phase 0 skeleton → 1 Level-0 replay → 2 PLC disguise + Sparkplug (edge Mosquitto) → 3 OT consume
(TimescaleDB historian/Grafana + real-time alerting + Prometheus observability) → 4 multi-site +
central EMQX + **OpenPLC (Beaumont) & OPC-UA (Geismar)** sites + store-and-forward + Docker IT/OT
segmentation (harmonization proof) → 5a IT source + CDC (Python→Debezium milestone) → 5b context
(ERPNext + Neo4j) → 6 loop closure (**medallion + Spark ETL + MLflow + offline/online feature store** +
ML/inference + floci) → 7 reasoning (GraphRAG) → later: re-platform onto UMH.

**Reference-architecture review (2026-06-21):** the design was benchmarked layer-by-layer against a
real industrial-products target architecture; all add/keep-out decisions and the **three
implementation-variant diagrams** (hand-built/Python-centric · UMH-anchored · cloud-native→floci) are
in **charter §13**. Diagrams live in the Eraser `scada_harmonization` workspace (see "Diagrams" above).

## Build and development commands

**Package/project manager: `uv` (decided) — used for everything; no pip/poetry.** `uv add <pkg>` to
add deps, `uv sync` to install, `uv run <cmd>` to run, `uv.lock` committed, Python version uv-pinned.
Add each dependency *when needed*, with a one-line justification (raw-mechanism-before-wrapper).

**API framework:** FastAPI is the *intended* choice for the Plane 3 query/GraphRAG/copilot API — not
adopted yet; decide when that layer is built (~Phase 5b/7). The core pipeline needs no HTTP backend.

Stack so far: Python + Pydantic v2, pandas, paho-mqtt, PySparkplug, Neo4j driver. No build tooling
exists yet (pre-implementation, Phase 0 pending). Update this section once `pyproject.toml` lands.
</content>
