# Working conventions

Status: existing project rules, relocated. The owner clarified PR merge responsibility during this documentation batch.

Source: the "How we work" section of `AGENTS.md` before this reorganization.
The project charter governs scope and design; this file owns the collaboration
method. See [AGENTS.md](../AGENTS.md) for startup instructions and
[REVIEW_STANDARDS.md](../REVIEW_STANDARDS.md) for review judgement.

## How we work — learning-first collaboration (IMPORTANT)

The owner is building this lab **to learn the stack at the bare-metal level**. Nothing should be a
black box: the goal is for the owner to understand *every block of code* and *why* it exists. Optimize
for understanding, not speed.

**Session discipline**
- **Update `HANDOFF.md` at the end of EVERY session** — refresh "Current status," git/PR state, and
  "What's next" so the next agent (or the owner) is never confused. This is mandatory, not optional.

**Review discipline**
- **Mechanical rules live in `scripts/check.sh`; judgement rules live in `REVIEW_STANDARDS.md`.**
  The reviewer reads that file, and it grows only from findings a reviewer actually made, each with
  the incident that taught it. Do not restate the check script there, and do not add a rule without
  an incident.

**Git / PR discipline (learned the hard way — do NOT repeat)**
- Use a branch per change and open a PR. The PR reviewer merges. Agents watch,
  address feedback, run checks and independent review, and push fixes. Agents
  never merge or push straight to `main`. See the owner's clarification in
  [the reorganization record](DOCUMENTATION_REORGANIZATION.md#authorization).
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
   a **learning log** (`docs/LSC-010_Learning_Log.md`) so pruning code never loses the learning.

**Medium**
- **Marimo notebooks** (via the `marimo-pair` skill) are the interactive surface for learning and
  prototyping Python logic — explain/experiment cell by cell.
- Infrastructure (brokers, TimescaleDB, OpenPLC, Neo4j, ERPNext) runs as **services** (Docker); the
  notebook/package code talks to them as clients.
- **Notebook → package (DECIDED):** `notebooks/` holds one Marimo notebook **per component** (rich
  explanations, committed, clearly the "learning surface"); `src/scada_harmonizer/` is the **package =
  source of truth** where finalized, documented code graduates. When a component is done: prune the
  notebook's teaching scaffolding (keep a slim demo or retire it), migrate clean code to `src/`,
  durable concepts to `docs/LSC-010_Learning_Log.md`.

**Diagrams (DECIDED) — use Eraser, save to the `scada_harmonization` workspace**
- **All project diagrams are created with the Eraser MCP** — architecture, data-flow, sequence, ER,
  ISA-95 topology, knowledge-graph schema, etc. Do **not** produce deliverable diagrams with other
  tools or as committed ASCII art. Eraser is the single source of truth for visual artifacts.
- **Every diagram is saved to the Eraser workspace/folder named `scada_harmonization`** so all diagrams
  live in one place. Always target that folder when calling Eraser.
- **One diagram per architecture view.** Each implementation type (hand-built / Python-centric,
  UMH-anchored, cloud-native) gets its own full architecture diagram in that workspace (charter §5).
- Quick inline **ASCII sketches are fine for discussion**, but the canonical artifact is the Eraser
  diagram — embed/link its URL in the relevant `docs/*.md` doc so it's discoverable.
- **Eraser gotchas:** (1) the AI edit path (`update_diagram`) reverses arrow directions — use
  `manually_update_diagram` (verbatim DSL) when direction matters; (2) auto-layout ranks nodes by
  **connection operand order** (the LEFT operand lands further left, regardless of arrow direction —
  `A < B` = same arrow as `B > A`, different layout) — declare each cross-zone edge with the
  leftward zone's node as the left operand to force zone geometry; (3) `export_diagram` PNG fails on
  very large canvases — export **JPEG**.
- The Eraser MCP is registered for all local agents (Claude, Codex, Gemini, Cursor, OpenCode, Kimi,
  Hermes); each authenticates via its own OAuth login on first use.

**Pace is owner-set.** Pause at natural boundaries; ask "go deeper or move on?" Don't race ahead.

**Learning practices**
1. **Raw mechanism before convenience wrapper.** Show the actual thing first — a raw `paho-mqtt`
   publish + real Sparkplug payload bytes before a helper; raw SQL/Cypher before an ORM. Justify every
   dependency ("why this library, what it hides"). Biggest guard against black boxes.
2. **Docker Compose is a learning artifact.** Add services one at a time, each explained; the owner
   brings them up/down (`! docker compose up …`). The wiring is half the lesson.
3. **Running glossary.** Maintain a GLOSSARY in `docs/LSC-010_Learning_Log.md`; add plain-language defs as
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

**Explicit learn-by-building milestones (do NOT shortcut):** **P&ID extraction** (vector text and
geometry → OCR and symbol detection → vision-model assist; Phase 5b.1) and **DEXPI 2.0** (Phase
5b.1), **Debezium** (log-based CDC, Phase 5a),
**Redis** (online feature store, Phase 6), **OPC-UA** (real protocol at Geismar, Phase 4), **Spark**
(medallion ETL, Phase 6), **Prometheus** (observability, Phase 3), and **MLflow** (model registry,
Phase 6) are deliberate hands-on goals — build them the real way and explain, even where a simpler
stand-in would suffice. The owner wants the genuine experience. (Full list & rationale: charter §13.)
Optional *later* "graduate-to / explore" milestones (charter §13.6): **Databricks Free Edition**
(graduate the hand-built medallion to a managed lakehouse — Delta Lake, Unity Catalog) and **Apache
Iggy** (explore as an alternative streaming engine on a non-Debezium stream; **Kafka stays the backbone**).

## Commit and local-reference conventions

Commit messages include a `Co-Authored-By` trailer naming the model that assisted.
Stage paths explicitly. Do not commit `.codex/` or other unrelated local tooling.

`reference/` is local-only. Only its README is tracked. The ISHE and EngiGraph
materials supply reusable patterns, not project scope or business framing.
The companion engineering-drawing repository is private and is a separate project.

For this documentation batch, the owner's permission removes drafting pauses.
The explain-and-align cadence still governs subsequent component implementation.
