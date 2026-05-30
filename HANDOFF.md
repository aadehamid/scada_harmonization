# Project Handoff

**Purpose:** let any agent (or human) pick up this project without re-deriving context.
**Last updated:** 2026-05-30

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

**Three planes:** Plane 1 **Harmonize** (OT → Sparkplug B UNS) · Plane 2 **Record** (curated events →
ERPNext) · Plane 3 **Contextualize** (UNS + IT transactional + ET topology → identity reconciliation →
Neo4j + GraphRAG). Sources span the **IT / OT / ET** divide.

The authoritative, always-current definition is **`design/PROJECT_CHARTER.md`**. If anything here
conflicts with the charter, the charter wins.

---

## 2. Current status (2026-05-30)

**Phase: pre-implementation.** Design + charter complete; **all infrastructure decisions resolved**;
**no source code yet.**

### Git / PR state
- **PR #1** — charter + README/AGENTS rewrite + move business cases to `reference/` → **MERGED** to `main`.
- **PR #2** — PostgreSQL OLTP tier + IT/OT/ET source model → **MERGED** to `main`.
- **PR #3** — resolve infra decisions (#2,3,4,6,7,8) + schema layout + README/AGENTS sync →
  **OPEN, awaiting user merge** on branch `docs/resolve-infra-decisions`.
  - ⚠️ **First action for the next agent:** confirm PR #3 is merged, then delete its branch
    (local + remote). If not yet merged, do not start Phase 0 on top of it without the user's nod.

### Resolved decisions (all in charter §4/§6/§12)
| # | Decision | Resolution |
|---|----------|-----------|
| 1 | Domain | Multi-site process / specialty-chemicals (data-driven by TEP + Industrial IoT) |
| 2 | MQTT broker | **Two-tier:** Mosquitto per-site edge + EMQX OSS central UNS, connected by a **Python site-forwarder** (not a raw broker bridge — preserves Sparkplug state; the forwarder is the cross-site harmonization point) |
| 3 | Historian | **TimescaleDB** (SQL everywhere; modeling not ingest rate is the bottleneck) |
| 4 | PLC literalness | **Hybrid** — most sites Python-modeled cryptic tags; **one** site (Beaumont) real **OpenPLC** over Modbus TCP |
| 6 | Sites + enterprise | **Lagos Specialty Chemicals** (UNS root `lagos-chem`); **4 sites** — Beaumont (Allen-Bradley), Geismar (Siemens), Rotterdam (Ignition-style), Corpus Christi (CygNet) |
| 7 | Postgres deployment | Historian + role-B ODS consolidated in the Timescale instance (separate schemas); role-A source systems in a **separate** Postgres home so CDC captures from a foreign system |
| 8 | CDC | **Start Python poll** (Debezium-shaped events), **design for Debezium**, with an explicit hands-on Debezium learning milestone in Phase 5a (5a.1 → 5a.2 → 5a.3) |

Plus the **relational schema layout** (charter §4): two Postgres homes —
`ts_historian` + `ods_core` + `erp_shadow` (Timescale, pipeline-owned) and `mes`/`lims`/`cmms`/`quality`
(separate Postgres, source-of-record). Boundary rules: no cross-home FKs; reconciliation in
`ods_core.identity_map`; lane discipline; Neo4j reads the reconciled side only.

---

## 3. What's next — Phase 0 (turn design into code)

Once PR #3 is merged:

1. `pyproject.toml` + `src/` package layout (Python project; Pydantic v2, pandas, paho-mqtt, PySparkplug).
2. **The three-stage name mapping table as config** — seeded with the 4 sites' divergent naming
   conventions (`friendly variable → site-specific PLC tag → Sparkplug metric` + unit/range/cadence/
   asset-class/site/IDs). **This is the spine of the lab — build it well and the rest is plumbing.**
3. One asset modeled **end-to-end** as the seed the rest of the pipeline grows from.

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

The session ended with all infra decisions resolved and PR #3 opened. There is **no unanswered
question blocking progress** — the next concrete action is: **merge PR #3 → delete its branch → start
Phase 0.**
</content>
