# Project Handoff

**Purpose:** let any agent (or human) pick up this project without re-deriving context.
**Last updated:** 2026-08-21 (#40 merged; mapping spine still next)

> **RESUME HERE.** Session wrapped 2026-08-20. Next build is the mapping-table
> spine. Paste the kickoff in **§3** (“Next build session”). Do not start
> Sparkplug, extra P&ID pages, or DEXPI unless Hamid redirects. Walkthrough
> stays parallel at §0.2. P&ID leftovers are **§2.1 Track B** (documented, not
> a gate).

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

## 2. Current status (2026-08-21)

**Phase: Phase 1 L0 is on `main` at `753de7a` (after #40). Warehouse is wide Parquet on R2
`lagos-chem-l0`. 1 s machine stream landed (#33). Unit 100 Rev B one-pager + 59-row
tag list landed (#35). Mapping table is unwritten — that is the next build slice.
Walkthrough is a parallel path, not a gate. Cursor remains at §0.2.**

**Do not confuse the two leftovers (Hamid, 2026-08-20).** L0 *data* for Unit 100 is
done. The unfinished P&ID work is a *drawing book* + a later *DEXPI graph*, not
ingestion. The mapping table consumes the 59 L0 names already in
`tests/fixtures/datagen/pid/tag_schedule.csv`. Extra sheets do not unlock
Sparkplug. DEXPI does not unblock Phase 0. See §2.1 and §3.

**Hamid lock (2026-08-18, via Chief Architect; status refreshed 2026-08-19).** Pack the
Diagram 1 v2 L0 cuts as a written note in this file. Do not copy or edit the original
Eraser file `MgnB91QGOhX8xWiKeaAK`. Do not build a second full cloud-architecture canvas
now. The original stays the walkthrough lock target (cursor still §0.2 Purdue). A copy
gets the L0 seat/caption fixes only after the walkthrough is ready to lock. The N8
fast-class hole landed as `#33` (`generate_machine_stream`, P-101 / K-201). Not the
landed Kaggle IIoT file as a 1 s process stream. Not interpolated TEP. Still no mapping
YAML, no Sparkplug, no second plant. The Unit 100 Rev B one-pager landed on `#35` after
this lock (same Phase 1 TEP/IIoT keys). Extra P&ID pages are not drawn. N8 is not rewritten.

**Packed Diagram 1 v2 L0 cuts (Thread B, L0 to PLC). Packed, not drawn. For a later copy only.**

Musts:
1. Split IIoT off the TEP Replay → Sensors → PLC path. Snapshot-per-machine. Do not mix streams.
2. Scan classes are P1 / mapping `source_cadence`, not L0 warehouse. Drop "slower scan classes"
   from TEP and "~1s fast class" from IIoT. N8 fast class = extras + later machine stream.
   Do not rewrite N8.
3. Replay metadata seat (not Sensors): TEP `faultNumber` / `simulationRun` / split; IIoT
   `Machine_ID` / `Machine_Type`.
4. L0 join key: `(source_dataset, source_column)` → `metric_registry`. Poller raw-counts is
   L1 disguise.

Shoulds: R2 `lagos-chem-l0` as Replay upstream (wide Parquet, melt-on-read), distinct from
L4 MinIO; TEP splits are partitions not boxes; "4 sites re-skin" is TEP-only; Sensors
caption so vibration/power are not TEP PVs; HITL "L0 Shadow" (N30) vs Purdue L0.

Design + charter complete; **all infrastructure decisions resolved**. Phase 1 L0
(ingestion / generation / augmentation / replay) is on `main` (PRs #28 + #29 + #31 + #33).
Mapping-table YAML is **not written** and is **not gated** on the walkthrough (owner lock
2026-08-19). Hamid runs Diagram 1 independently. Hand-built Eraser **Diagram 1 v2** is
still the walkthrough + lock target for Diagrams 2 & 3. Those diagrams stay just-in-time.

**Repo snapshot:**

| Fact | Reality |
|------|---------|
| `main` HEAD | `753de7a` after #40. Generators still `#33` / `7b6cdd5` |
| Runtime | Python 3.13 + **polars + pydantic** (`uv`; no pandas) |
| Warehouse | R2 `lagos-chem-l0` wide Parquet, zstd, melt-on-read. 17 objects listed 2026-08-20 |
| R2 object I/O | Works from Cursor Cloud env secrets (`R2_ACCOUNT_ID` / `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY`). No package reader yet. Do not write warehouse objects. |
| Tests | **41** (`uv run pytest`); 34 L0 goldens + Unit 100 P&ID; no network, no full warehouse |
| Phase 1 code | `datagen/{generation,ingestion,augmentation,replay}` + `records.py` / `pipeline.py` |
| 1 s class | `generate_machine_stream` — P-101 / K-201; `friendly_name` = `{machine_id}/{pv}` |
| Goldens | TEP `f5b9d1cf…e6d33516` (do not change); machine stream `84b9f088…2159f0` |
| Unit 100 L0 join | Rev B PDF + 59-row CSV. **Done for ingestion.** Extra pages + DEXPI are other tracks (§2.1) |
| Not in repo | mapping-table YAML; DEXPI / `book.py`; Phase 2+ services; Marimo notebooks; R2 melt client |
| Open PRs | none |
| Walkthrough | **parallel, not a build gate.** §0.1 done; Hamid resumes §0.2 Purdue |

**Exact cursor:** `design/WALKTHROUGH_PROGRESS.md` (surface-independent bookmark). §0.1 ISA-95 is
**done**; **§0.2 Purdue is next**; then §0.3 IEC 62443, then Threads B → C → A, then cross-cutting.

**Phase 1 record:** `design/PHASE1_SYNTHETIC_DATA.md` (HTML twin + assets).
**Datasheet:** `design/PHASE1_DATASHEET.md`. Do not copy that write-up into this file.

### 2.1 Two leftover tracks — do not mix them

**Track A — L0 / ingestion (DONE).** Generate → melt → augment → replay is on
`main`. Warehouse bytes are on R2. The 59 `plant_data_name`s in
`tests/fixtures/datagen/pid/tag_schedule.csv` **are** the L0 names
(`xmeas_*`, `xmv_*`, `P-101/…`, `K-201/…`, `xv_feed`). CI pins the PDF hash
and the 59-name set. You can continue the OT build without more drawings.

**Track B — drawing book + DEXPI (NOT done; not the next build slice).**

| Missing | Kind | When to pick it up |
|---------|------|--------------------|
| Index + analyzer (print AT-201..AT-219) + legend | Extra PDF pages. Architect lock: these **before** more process sheets. Titles become sheet N of N, not “1 of 1”. Caption: “1 second machine stream on P-101 and K-201”. | Owner-triggered drawing lap. Packet: `design/UNIT100_PID.md` → Extra pages. Do not invent a second factory. |
| `models/unit100_dexpi.json`, `tag_schedule.py`, `book.py` | Grok Bot pack. Lost. Graph of equipment / nozzles / lines. | Phase 5b (Neo4j / ET). Do **not** rebuild to unblock mapping or Sparkplug. |
| `data/tag_schedule.parquet` | Drawing note 2. | Issued join is the CSV. Do not recreate parquet as a second pin. |

`provenance=drawing` vs `reconstructed` in the CSV is honest: most
instrument↔TEP pairings were rebuilt after the Grok Bot pack was lost.
That is good enough for mapping-table join keys. Pipe/stream cells are
list columns, not a second naming system.

### This session (2026-08-21): charter §2 scale fold (docs only)

Hamid dropped an Energy & Chemicals / maintenance-reimagined problem statement.
Verdict: same disease, different organ. Folded **patterns** into charter §2
(contextualization + scalability; site-two / ~18-month redeploy; data products
as the scaling mechanism; contextualize-before-models; HITL atrophy). README +
`DOMAIN.md` mission sentence mirrored. Discarded: agentic SAP/PO/work-window
orchestration, AI auto-tag-mapping, MRO dollar figures, vendor name-drops.
Plane 4 flagship stays yield / production-leakage. Mapping-table spine is still
the next **build**. Walkthrough cursor untouched.

### This session (2026-08-20): pick mapping spine; document the fork

Hamid asked where to continue given unfinished P&ID feelings after the
Grok Bot loss. Decision: **next build is the mapping-table spine**
(Phase 0 exit). P&ID extra pages stay an owner-triggered drawing lap
(§2.1 Track B) — not abandoned, not a gate. YAML vs TOML/JSON closed:
**YAML**. First row locked: `xmeas_7` / `PT-101`. R2 object list/get/put
verified from Cursor Cloud secrets; probe object deleted; no package
reader added. Walkthrough cursor untouched.

### This session (2026-08-18): Hamid lock via Chief Architect (docs only)

Hamid locked the order: pack Diagram 1 v2 L0 cuts here; do not touch Eraser
`MgnB91QGOhX8xWiKeaAK`; no second architecture canvas; next work at lock
time was the N8 fast-class hole (later closed by `#33`). Walkthrough cursor
untouched. N8 untouched. One-line pointer in `design/LEARNING_LOG.md`.

### This session (2026-08-18): R2 persist and #31 merged

Hamid persisted L0 on Cloudflare R2 bucket `lagos-chem-l0` (ENAM). Warehouse is wide
Parquet compressed with zstd, including the 9,600,000-row Faulty Testing native.
Raw stays on R2 (1,419,880,076 bytes, no csv). The 58,661,861,866-byte history JSONL
was deleted. 96 GiB was an estimate, never the warehouse. Polars PR #31 merged.
`main` is `7da1621`. Walkthrough stays parallel at §0.2. Datasheet:
`design/PHASE1_DATASHEET.md`. Do not copy the write-up here.

### This session (2026-08-19): merge `origin/main` (`e2c7ff3`) into #32

Fetched `main` and merged. All conflicts were unions (R2 warehouse + datasheet
from this branch; 1 s machine stream #33 and Unit 100 #35 from `main`).
Intent-timing only: the 2026-08-18 lock said next was the N8 hole; `#33`
and `#35` later landed on `main`. Resolution keeps packed L0 cuts + R2
persist, marks the N8 hole done, keeps Unit 100, leaves extra P&ID pages
undrawn. Charter N8 and §8.1 table untouched. Walkthrough cursor untouched.

### This session (2026-08-19): walkthrough parallel + Unit 100 one-pager

Hamid lock: the Diagram 1 walkthrough **runs in parallel** and **does not
block build**. Mapping-table YAML can start when the build needs it. #34
merged (`2003cbb`); leftover docs branch deleted. Recovered the Rev B PDF
from Hamid's upload and landed it under `tests/fixtures/datagen/pid/` with a
59-row reconstructed tag list (1:1 drawing name → existing L0 names). Grok
Bot DEXPI / `tag_schedule.py` pack was not recovered — `provenance` column
says so. Extra pages not this lap. Do not invent a second factory. Do not
stack on #32.

### This session (2026-08-19): git cleanup after #33 merge

`main` is `7b6cdd5` (PR #33 squash-merged). Local leftover
`cursor/phase1-1s-machine-stream-7d33` deleted (`-D` after squash). Remote
already gone; pruned stale `origin/cursor/pandas-to-polars-8a59` (#31) and
`origin/cursor/phase1-1s-machine-stream-7d33`. PR #32 left open. Unit 100
P&ID Rev B was not in the repo at that cleanup (PDF only). Landed later
the same day — see the session note above. Do not invent a second factory.
This pass syncs README, AGENTS, charter §8 reality note, Phase 1 record +
HTML twin, learning log, synthetic-data notes, `tests/README.md`, and the
archived Python-centric banner to `7b6cdd5` / 34 tests. Charter N8 text
untouched. PR **#34** was that docs-only branch (now merged).

### This session (2026-08-18): N8 1 s machine stream (PR #33)

Charter §14 N8 fast class was a hole: Kaggle IIoT is a snapshot, TEP is 180 s,
extras inherited the host grid. Added `generate_machine_stream` — seeded wide
Polars frame at native 1 s UTC, ingested as `SourceDataset.IIOT`. Machine
identity is stream metadata, not an L0 PV (`METADATA_COLUMNS`). Extras ride
that 1 s grid. Golden slice 2×20 s×3 PVs. TEP 180 s and Kaggle-snapshot tests
stay green. Charter N8 text and Phase 0 `source_cadence` untouched. Walkthrough
cursor untouched. Do not stack on PR #32. Follow-up: P1 fix — ingest qualifies
`friendly_name` as `{machine_id}/{pv}` so two machines at the same tick do not
collapse. Raw same-name cadence is 1 s. Machine-stream golden regenerated;
TEP golden SHA unchanged.

### This session (2026-08-18): Hamid lock — pandas → Polars

Polars is the runtime for every tabular job we would have used pandas for. pandas
removed from runtime deps. Golden SHA unchanged. Walkthrough cursor untouched.

### This session (2026-08-18): Phase 1 write-up + status refresh (docs only)

Hamid asked for the Phase 1 synthetic-data record and a refresh of stale status docs after
#28/#29 landed. No product code. Persist rules are Hamid's (keep raw 1.35 GiB; full L0 cache
330,920,000 rows / 54.63 GiB written then deleted; Full Faulty Testing never written). IIoT
Kaggle file is snapshot-per-machine, not 1 s. Walkthrough cursor untouched.

### This session (2026-08-18): pandas, Phase 1 package wiring, ty

Wiring PR **#28 merged** (`8564fed`, 12:34 AM CT). pandas was the first runtime dependency
(superseded: Polars is now the tabular runtime):
ingestion melts wide TEP to long L0 rows; augmentation/replay operate on tabular L0 frames.
`scada_harmonizer.datagen` plus ingestion/augmentation/replay are importable packages.
ty is in the dev group and CI (`uv run ty check` after ruff). Generators followed in PR #29.

### This session (2026-08-17) — docs hygiene (no design change)

Owner asked for a full-repo review, then to land the changes that make sense. **No domain code,
no mapping table, no walkthrough progress.** Fixes:

- `AGENTS.md` still said "pre-implementation / no source code yet" (the 2026-07-27 sweep missed it).
- Heading **"The three planes"** → **"The four planes"** (charter §3, README, AGENTS) — four
  architecture planes; "three source domains" and "three feature planes" are different things.
- Charter §8 Phase 3 still parked `ods_core` in the Timescale instance — contradicts §14 N16.
- Charter §8 sequencing still said "Phase 0 begins after Diagram 1 is locked" — skeleton already
  landed; only the mapping table is gated.
- `DOMAIN.md` + living `synthetic_data_generation_notes.md` still said ISA-88 **batches**; N13 is
  lots. Synthetic notes also stripped leftover `[cite:N]` scrap and marked PySparkplug as candidate.
- README claimed MIT with no `LICENSE` file; added one. Thin CI (`ruff` + pytest smoke).
- Document maps (README, charter §11, this file) now list the walkthrough cursor + learning log.

**Follow-up (same day):** PR #24 merged (`8646a62`); branch `cursor/docs-hygiene-e236` deleted
local + remote. This file's git-state block still said #24 was outstanding — fixed here.

### This session (2026-08-17): Phase 1 L0 contract

Phase 1 L0 contract landed at `design/PHASE1_L0_CONTRACT.md`. Spec holes closed.
Implementation not started. Walkthrough cursor unchanged. Docs-only PR #27.

### This session (2026-08-17): Phase 1 exit lock

Phase 1 exit is replay-only (deterministic sequence + N8 clock). It no longer includes P1 classification or mapping-table `source_cadence`. The L0 cache stores the friendly L0 name. `source_column` is side metadata. Physical meaning waits for the mapping table. Lots, work-order, and material IDs stay Phase 5. Docs-only PR #26.

### This session (2026-07-27) — doc staleness sweep

No design or build work; **synced the stale status docs** to reality after a ~2-week gap. `HANDOFF.md`
still claimed "pre-implementation / no source code yet" and "Phase 0 deferred until Diagrams 1–3 are
complete" — both false since PR #22. Corrected here, in `README.md` (§Status), in `AGENTS.md` (build
tooling section, which explicitly asked to be updated once `pyproject.toml` landed), and with a
one-line reality note in charter §8. `design/WALKTHROUGH_PROGRESS.md` was already current — untouched.

### Sessions 2026-07-07 → 2026-07-11 — Phase 0 skeleton + walkthrough §0.1

**Phase 0 foundation merged (PR #22, `937f40f`) — structure only, deliberately no code stubs.**
- **Part A — Python skeleton:** `pyproject.toml` via `uv init --lib` (src layout), **Python pinned
  3.13** (`.python-version` committed — it is uv's pin), `uv.lock` committed, **zero runtime
  dependencies** (added per-phase with justification, per AGENTS.md). Dev group = **ruff** (E/W/F/I/
  UP/B, 100 cols) + **pytest** (`testpaths = ["tests"]`). `tests/test_package_imports.py` is the
  single smoke test; `notebooks/` reserved as the Marimo learning surface.
- **Part B — full directory structure** mirroring the real project shape, README-only placeholders
  (YAGNI; each README states what lands there and in which phase):
  `src/scada_harmonizer/datagen/{ingestion,augmentation,plc_mapping,sparkplug,context_export,replay}`
  (the 6-layer synthetic pipeline) + the four planes `{harmonize,record,contextualize,apply}`;
  `config/mappings/` (**the three-stage table spine — folder reserved, CONTENT GATED on the
  walkthrough**) + `config/sites/{beaumont,geismar,rotterdam,corpus_christi}` per charter §6;
  `docker/` (compose lands service-by-service from Phase 2, profiles per §8.2); `data/{raw,cache}`
  (payloads gitignored, structure tracked via READMEs).
- ⚠️ **Phase 0 is NOT done.** Its exit criterion (charter §8.1) is the **mapping-table YAML validating
  via Pydantic with the §14 columns** (scaling N17, quality N10, `source_cadence` N8,
  `interpolation_type` N11, UNECE units N18), one measurement across all 4 sites. None of that exists.

**Walkthrough checkpoint (`7b6b468`, direct to `main`).** §0.1 **ISA-95 / IEC 62264** taught and
landed as durable notes in `design/LEARNING_LOG.md` (Concepts + glossary), and
**`design/WALKTHROUGH_PROGRESS.md`** created as a resumable cursor so the walkthrough survives
switching agents/surfaces. It also fixes the walkthrough ownership rule: the walkthrough session owns
`HANDOFF.md` / `WALKTHROUGH_PROGRESS.md` / `LEARNING_LOG.md`; a parallel Phase-0 agent must not edit them.

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
- **Follow-up (same session, later): Diagram 1 reviewed against §14 → Diagram 1 v2 created.**
  Review verdict: bones excellent (zoning, forwarder pattern, command hops); 28 findings where the
  2026-06-23 drawing predated §14 (EMQX "cluster", GuardLogix label, IT-side Redis feeding edge,
  MLflow push-to-edge, iDMZ alerting node, golden-batch label, "command topic" language, single
  cross-zone Prometheus, floci straddling zones, P7 validation point, missing Ignition / UNS→Kafka
  bridge / command_audit / DDATA read-back / ET leg / order-to-cash flows). All applied in a **new
  dated diagram — Diagram 1 v2 (2026-07-06)**, same "SCADA Harmonization" folder:
  https://app.eraser.io/workspace/MgnB91QGOhX8xWiKeaAK?diagram=133RhOiN_-G6Ko5kaTj8&layout=canvas
  (June-23 original kept for history). The review also caught two charter gaps, now fixed: **C6**
  order-to-cash schedule-down conduit added to §14 N21, and the **L6.4 sourcing rule** (cloud
  training reads the OT-historian plane from the lakehouse — no direct OT reads; edge computes
  online features locally). **MinIO** added to §4.1 (hand-built object store). ⚠️ Eraser export API
  returned empty PNGs for this large diagram — verify visually in the app canvas; DSL is confirmed
  stored.
- **Follow-up (same session, final): Diagram 1 v2 layout corrected + OWNER-APPROVED.** The iDMZ
  initially rendered at the far right; fixed purely in DSL across four render-verified experiments
  after discovering Eraser's layout rule (connection **operand order = left-right rank** — see the
  Eraser gotchas). Geometry is now **OT | iDMZ | IT** (Purdue). Owner confirmed *"diagram looks
  good"*; all **four sites verified present** (Beaumont/Geismar are dense because they are the
  real-protocol sites; Rotterdam/Corpus Christi are lean Python-modeled chains, and repeated
  cross-site flows use the "(all sites, shown once)" convention at Beaumont). **No further diagram
  edits planned before the walkthrough** — v2 is the walkthrough surface.
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
  **Added 2026-07-06 (Diagram 1 v2 layout fix):** Eraser's auto-layout ranks nodes by connection
  **operand order — the LEFT operand is placed further left, regardless of arrow direction**
  (`A < B` draws the same arrow as `B > A` but pins A left). To force the Purdue geometry
  OT | iDMZ | IT, every edge touching the iDMZ is declared with the leftward node as the left
  operand (e.g. `TimescaleDB < EMQX` for subscribe-down, `EMQX < Model Serving` for C4). Also:
  `export_diagram` **PNG fails on very large canvases — use JPEG**; reversed dotted arrows `A <-- B`
  parse fine; labeled group-to-group edges (`OT Zone --> iDMZ`) work as zone-order annotations.

### This session (2026-06-29) — owner confirmed Diagram 1 walkthrough plan

Owner reviewed repo scope and **confirmed sequencing:** (1) Diagram 1 end-to-end teaching walkthrough
with external research → (2) lock Diagram 1 → (3) Diagrams 2 & 3 → (4) Phase 0. Detailed agenda in §3.

⏭ **Roadmap (ordered — resequenced 2026-07-06; status refreshed 2026-07-27):**
- (0) ~~Review `design/SAMPLE_*`~~ — **DONE (2026-06-23)** (charter §13.7 patterns adopted).
- (a) **IN PROGRESS — the END-TO-END WALKTHROUGH** (supersedes/absorbs the Diagram-1 teaching
  walkthrough). Three threads per `design/E2E_WALKTHROUGH.md` (A order · B telemetry up ·
  C decision/control back) + the deck (`reference/enterprise_it_ot_deck/`) + web research, walked
  block-by-block against **Diagram 1 v2** using the §3 per-component cadence; the §14 gap checklist
  is *verification only* (already applied to v2). **§0.1 ISA-95 done → resume at §0.2 Purdue**
  (`design/WALKTHROUGH_PROGRESS.md` is the cursor). **Completing the walkthrough locks Diagram 1.**
  See §3.
- (b) ~~Two-components discussion~~ — **DONE** (Databricks + Iggy, charter §13.6).
- (c) **Phase 0 — PARTIALLY DONE.** Repo skeleton **landed early** (PR #22, out of sequence but
  harmless — it is diagram-independent). What remains is the **three-stage mapping table with
  the §14 columns**. The walkthrough does **not** gate it (2026-08-19). Diagrams 2 & 3 do not
  gate it either.
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
- **This session (2026-07-06), four PRs:** **#17** best-practice review adoption (charter §14
  N1–N35, §4.1 pinned stack, plan restructure) → **MERGED**. **#18** order-to-cash + no-WMS +
  `design/E2E_WALKTHROUGH.md` → **MERGED**. **#19** Diagram 1 v2 + conduit C6 + L6.4 sourcing rule +
  MinIO pin → **MERGED**. **#20** Eraser layout gotchas + this session wrap → **MERGED** (`33c9866`).
  Diagram 1 v2 (layout-corrected, owner-approved) lives in Eraser:
  https://app.eraser.io/workspace/MgnB91QGOhX8xWiKeaAK?diagram=133RhOiN_-G6Ko5kaTj8&layout=canvas
- **PR #21** — end-to-end walkthrough opener: §0 three-lens primer (ISA-95 · Purdue · IEC 62443)
  written into `design/E2E_WALKTHROUGH.md` → **MERGED** (`1f2db7c`).
- **PR #22** — Phase 0 foundation: uv skeleton + full directory structure → **MERGED** 2026-07-08
  (`352ae2b`, commit `937f40f`); branch `feat/phase-0-foundation` deleted.
- **`7b6b468`** (2026-07-11) — walkthrough checkpoint (§0.1 ISA-95 notes + `WALKTHROUGH_PROGRESS.md`),
  committed **directly to `main`** as owner-sanctioned small-doc housekeeping (no PR).
- **Branch cleanup (2026-07-07):** all merged `docs/*` PR branches deleted from the remote; stale
  local remote-tracking refs pruned. Only `main` + `entire/*` checkpoint refs remain.
- **PR #23** — docs: sync stale status docs (Phase 0 skeleton landed, walkthrough at §0.2) →
  **MERGED** 2026-07-28 (`215b9e4`).
- **PR #24** — docs hygiene (LICENSE + CI + contradiction sweep) → **MERGED** 2026-08-17
  (`8646a62`); branch `cursor/docs-hygiene-e236` deleted local + remote.
- **PR #26** Phase 1 exit is replay-only: **MERGED** (`f7bab02`).
- **PR #27** Phase 1 L0 contract: **MERGED** (`90cf3d7`).
- **PR #28** wiring (pandas + Phase 1 package inits + ty): **MERGED** 2026-08-18
  12:34 AM CT (`8564fed`); branch `cursor/pandas-wiring-ty-f25b` deleted.
- **PR #29** Phase 1 L0 generators: **MERGED** 2026-08-18 12:56 AM CT (`3039710`);
  branch `cursor/phase1-l0-datagen-5739`.
- **PR #30** Phase 1 synthetic data record: **MERGED** (`47883c7`).
- **PR #31** Polars replaces pandas: **MERGED** (`7da1621`); branch deleted.
- **PR #32** docs: R2 warehouse, Phase 1 datasheet, walkthrough is parallel:
  **MERGED** (`733cfec`); branch `cursor/docs-r2-warehouse-datasheet-3221`
  deleted.
- **PR #33** 1 s machine stream (N8 fast class): **MERGED** (`7b6cdd5`);
  branch `cursor/phase1-1s-machine-stream-7d33` deleted local + remote.
- **PR #34** docs sync to `7b6cdd5` / 34 tests: **MERGED** (`2003cbb`);
  branch `cursor/handoff-git-cleanup-7d33` deleted local + remote.
- **PR #35** Unit 100 one-pager + walkthrough-is-parallel: **MERGED**
  (`a9506d4`); branch `cursor/pid-unit100-onepager-7d33` deleted local + remote.
- **PR #36** mark #35 merged: **MERGED** (`e2c7ff3`).
- **PR #37** mark #32 merged: **MERGED** (`6e3406c`).
- **PR #38** pickup packet (mapping spine next; P&ID leftovers split):
  **MERGED** (`9ffe415`); branch `cursor/handoff-next-mapping-d4f3`
  deleted local + remote.
- **PR #39** mark #38 merged: **MERGED** (`d37409a`).
- **PR #40** charter §2 scale fold: **MERGED** (`753de7a`); branch
  `cursor/charter-problem-scale-2910` deleted local + remote.
- **As of 2026-08-21:** `main` at `753de7a` (#40). Warehouse is R2
  `lagos-chem-l0`. `entire/checkpoints/v1` remains on purpose. No leftover
  `cursor/*` remotes.

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

## 3. What's next — mapping spine is the build; P&ID book is a later lap

### ⭐ Next build session — mapping-table spine (Phase 0 exit)

**Kickoff prompt (paste into a fresh session):**

> Read `HANDOFF.md` §2.1 and §3, `design/PROJECT_CHARTER.md` §6 (three-stage
> table) + §14 N8/N10/N11/N17/N18, `design/PHASE1_L0_CONTRACT.md`, and
> `tests/fixtures/datagen/pid/tag_schedule.csv`. Phase 1 L0 is done. We are
> writing the first mapping-table slice: **one analog × four sites**, YAML +
> Pydantic, including the §14 columns. First row is locked: L0 `xmeas_7` =
> drawing `PT-101` (reactor pressure on R-101). Format is YAML. Explain the
> three stages and the §14 columns, then write the models + YAML + a small
> test. Do not dump all 59 rows. Do not start Sparkplug. Do not rebuild DEXPI.
> Do not draw extra P&ID pages unless I say so.

**Locked for that session (2026-08-20):**

| Item | Value |
|------|--------|
| Format | **YAML** (TOML/JSON question closed) |
| Stage 1 | L0 `friendly_name` already stored: `xmeas_7`. Do not invent a second semantic alias. |
| Drawing join | `PT-101` → `xmeas_7` (CSV row; `provenance=reconstructed`) |
| Stage 3 Sparkplug | `R-101/Pressure` (asset path; Unit 100 / R-101) |
| Sites | Beaumont `N7:20` (AB **raw counts**, N17) · Geismar `DB1.DBD24` (Siemens) · Rotterdam `PT101_PV` (Ignition-style) · Corpus Christi `UNIT100.PT101.PV` (CygNet compound) |
| `source_cadence` | `180s` (TEP honest; do not rewrite N8) |
| `interpolation_type` | `linear` |
| UNECE `unit` | `KPA` (TEP reactor pressure is kPa) |
| Scale | Beaumont: `raw_min=6208` `raw_max=31208` (charter N17 4–20 mA counts) → `eu_min`/`eu_max` in kPa. Other three sites publish EU floats (`scale_linear` identity). Confirm EU span against Downs & Vogel / warehouse min-max in that session — do not guess a process limit in the YAML comment as if measured. |
| Quality | Clean rows `Good`. Per-site quality **map** column exists (N10); Beaumont integer status → Good/Uncertain/Bad/Stale can be a stub map. |
| Governance | owner / definition / lineage on the metric (catalog, not a comment) |
| Out of this slice | lots / work-order / material IDs (Phase 5); machine-stream PVs (already EU; later rows); R2 melt client |

**First-PR files (keep it small):**

1. `config/mappings/` YAML — one metric, four `site` bindings.
2. Pydantic models under `src/scada_harmonizer/datagen/plc_mapping/` (that layer’s first real code; replace the README-only stub).
3. `tests/test_phase0_mapping.py` — load YAML, validate, four sites, §14 columns present, join key equals CSV `PT-101` → `xmeas_7`. No network.

Cadence: explain → align (locks above are the align) → build piece by piece → `uv run pytest` → prune. Learning-first: show the YAML as data before any helper that hides it.

### P&ID drawing lap — pickup when Hamid says so (not the default next)

**Kickoff prompt:**

> Read `design/UNIT100_PID.md` (Extra pages + domain locks) and
> `tests/fixtures/datagen/pid/`. One plant. Rev B process sheet stays. Draw
> index + analyzer (AT-201..AT-219) + legend **before** any new process page.
> Titles are sheet N of N. Say “1 second machine stream on P-101 and K-201”.
> Do not invent a second factory. Do not rebuild DEXPI / `book.py`. Do not
> change L0 names. Update the PDF pin + `design/UNIT100_PID.md` if the book
> hash changes.

### ⭐ Walkthrough (Hamid, parallel — does not block build) — resume at §0.2 (Purdue)

Walkthrough remains a parallel path at §0.2. Cursor: `design/WALKTHROUGH_PROGRESS.md`.
Original Eraser `MgnB91QGOhX8xWiKeaAK` stays the lock target. Packed L0 cuts live in
§2 of this file, not drawn. The N8 fast-class hole is closed (`#33`).

**Not now (unless Hamid redirects):** Diagram 1 lock, Sparkplug, second plant,
DEXPI rebuild, extra P&ID pages, Eraser copy, R2 melt-on-read client in the
package.

Warehouse reminder (not the next piece): R2 `lagos-chem-l0`, wide Parquet, melt-on-read.
Details in `design/PHASE1_SYNTHETIC_DATA.md` and `design/PHASE1_DATASHEET.md`.

**Walkthrough kickoff (when that parallel session runs):** *"Read `design/E2E_WALKTHROUGH.md` (the script),
`design/WALKTHROUGH_PROGRESS.md` (the cursor), and `design/LEARNING_LOG.md` (notes so far). We are
running the Diagram 1 v2 end-to-end teaching walkthrough. §0.1 ISA-95 is done. Continue from §0.2,
the Purdue model, using the five-beat cadence (problem tie-in, mechanism, web research with cited
sources, gap check against Diagram 1 v2, one-line teach-back), pausing for questions between
steps, and logging glossary terms to `design/LEARNING_LOG.md`. After Purdue, do §0.3 IEC 62443, then
Threads B, then C, then A."*

**Diagram URL (v2, 2026-07-06, the walkthrough + lock target):**
https://app.eraser.io/workspace/MgnB91QGOhX8xWiKeaAK?diagram=133RhOiN_-G6Ko5kaTj8&layout=canvas
*(2026-06-23 original kept for history:
https://app.eraser.io/workspace/6Ng61sTaot9VjtU87bEY?diagram=vheRVPpajwodCEDwqnBZ&layout=canvas)*

Cadence, block order, and the §14 gap checklist live in
`design/E2E_WALKTHROUGH.md`. Do not copy them here.

**Walkthrough complete → Diagram 1 locked as the template for Diagrams 2 & 3.**
That lock does **not** unblock the mapping table — the table was never waiting
on it after 2026-08-19. The uv skeleton already landed (PR #22). Diagrams 2 & 3
stay just-in-time (Diagram 2 = UMH Core, §12 #16; Diagram 3 before Phase 6).

---

### Phase 0 — partially complete (skeleton landed; mapping table not written)

**State (2026-07-27): 2 of 3 pieces done.** The `feat/phase-0-foundation` branch shipped as PR #22
and is deleted; the skeleton is on `main`.

- ✅ **1. Python project skeleton** — `pyproject.toml` via **`uv init --lib`** (src layout), Python
  **3.13** pinned, `uv.lock` committed; runtime deps now **polars + pydantic**;
  ruff + pytest + ty in the dev group;
  `src/scada_harmonizer/` (datagen 6 layers + four planes), `config/`, `docker/`, `data/`,
  `notebooks/`, `tests/`. Phase 1 code is in
  `datagen/{generation,ingestion,augmentation,replay}`;
  later layers and the four planes stay README-only.
- ⬜ **2. Three-stage mapping table as config (THE SPINE)** — **NOT started. Next build.**
  Not gated on the walkthrough. `config/mappings/` is reserved. **YAML** + Pydantic,
  first slice = `xmeas_7` / `PT-101` across all 4 sites, **including the §14 columns**
  (N17 `raw_min`/`raw_max`/`eu_min`/`eu_max` + `scale_linear`; N10 quality; N8
  `source_cadence`; N11 `interpolation_type`; N18 UNECE unit codes). Charter §8.1
  Phase-0 exit. Pickup packet is §3 above.
- 🟡 **3. `design/LEARNING_LOG.md`** — seeded and growing (§0.1 ISA-95 concepts + glossary landed
  2026-07-11); continues to fill as the walkthrough proceeds.

**When resuming piece 2:** use the §3 kickoff prompt. Format is YAML (closed 2026-08-20).
Marimo notebook work still starts at **Phase 1**, not here.

### Tooling decided this session
- **`uv`** for all package/project management (`uv add`/`sync`/`run`, committed `uv.lock`). No pip/poetry.
- **FastAPI** = intended-but-deferred backend for the Plane 3 query/copilot API (~Phase 5b/7); core
  pipeline needs no HTTP backend.
- **Plane 4 (Apply / Intelligence)** captured: Track A traditional ML (Phase 6), Track B LLM/GenAI (Phase 7).
- **Redis** = deferred/optional Plane 4 (online feature store etc.); **learning Redis is a goal**.

### Explicit hands-on learning goals (deliberate milestones, like real engagements)
- **Debezium** — log-based CDC (Phase 5a milestone 5a.2/5a.3).
- **Redis** — online feature store (Phase 6 milestone). Both are *learn-by-building*, not shortcuts.

Subsequent build phases (charter §8): 1 Level-0 replay → 2 PLC tag names + Sparkplug (edge Mosquitto) →
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
| `design/E2E_WALKTHROUGH.md` | End-to-end teaching walkthrough script |
| `design/WALKTHROUGH_PROGRESS.md` | Live walkthrough cursor — resume here |
| `design/LEARNING_LOG.md` | Durable concepts + glossary |
| `design/PHASE1_L0_CONTRACT.md` | Phase 1 L0 record + replay identity |
| `design/PHASE1_SYNTHETIC_DATA.md` | Phase 1 land / persist / disk record (HTML twin) |
| `design/PHASE1_DATASHEET.md` | Phase 1 local vs R2 datasheet (HTML twin) |
| `design/UNIT100_PID.md` | Unit 100 P&ID Rev B one-pager + 59-name tag list |
| `AGENTS.md` | Agent working guide — constraints, data flow, domain, build sequence |
| `README.md` | Human-facing summary |
| `design/uns_home_lab_notes.md` | Vision & scope *(archived)* |
| `design/{hand_built,umh_anchored,python_centric}_*_notes.md` | Architecture options (build phase vs. abstraction phase) |
| `design/synthetic_data_generation_notes.md` | Data strategy & the 6-layer synthetic pipeline |
| `reference/README.md` | Index of the local-only reference material (ISHE, EngiGraph) |

---

## 6. No open blocking questions

**Next build = mapping-table spine** (`xmeas_7` / `PT-101` × 4 sites, YAML).
P&ID extra pages are an owner-triggered drawing lap (§2.1 / §3), not a gate
and not abandoned. DEXPI / `book.py` wait for Phase 5b. Do not invent a
second factory.

Walkthrough stays parallel at §0.2. Completing that pass **locks Diagram 1**
as the template for Diagrams 2 & 3. It does **not** gate the mapping table.

No open blocking decisions (§12 #16 resolved → UMH Core). YAML vs TOML/JSON
is **closed: YAML**. PRs #17–#40 merged. Tabular runtime is Polars. Warehouse
is R2 `lagos-chem-l0`. Unit 100 Rev B + 59-row CSV are in
`tests/fixtures/datagen/pid/`.
