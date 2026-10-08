# Project Handoff

**Purpose:** let any agent (or human) pick up this project without re-deriving context.
**Last updated:** 2026-10-07 (ET leg now in scope — drawing-to-graph build; Phase 5b split; mapping spine still next)

Read section 2 for current status and section 3 for the next build slice.
The [master index](docs/LSC-000_Master_Index.md) maps each subject to its owner.

---

## 1. Project authority

[The project charter](docs/LSC-001_Problem_Statement_and_Project_Charter.md)
defines the project. This file owns continuity and current status.

## 2. Current status (2026-10-07)

> **This section is the only place the current status lives.** `README.md` and
> `AGENTS.md` point here rather than restating it, because three copies drifted:
> they quoted `main` at two different commits while the truth was a third.

**Phase: Phase 1 L0 is on `main`. Warehouse is wide Parquet on R2 `lagos-chem-l0`. 1 s machine
stream landed (#33). Unit 100 Rev B one-pager + 59-row tag list landed (#35). The figures tool
landed (#46). Mapping table is unwritten — that is the next build slice. Walkthrough is a parallel
path, not a gate. Cursor remains at §0.2.**

**The `main` tip is deliberately not pinned in this file.** It moves on every merge, and a pin here
went stale twice — once while this very section was being written. The table below gives the
command that reports it instead: `scripts/facts.py main`, which answers "what is on main" and not
"what am I on". `scripts/facts.py status` lists every place a document still claims a commit, so a
new one is easy to find and remove.

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
| `main` HEAD | Run `scripts/facts.py main` — not `head`, which reports the branch you are on. Not pinned here: it moves on every merge |
| Runtime | Python 3.13 + **polars + pydantic** (`uv`; no pandas) |
| Warehouse | R2 `lagos-chem-l0` wide Parquet, zstd, melt-on-read. 17 objects listed 2026-08-20 |
| R2 object I/O | Works from Cursor Cloud env secrets (`R2_ACCOUNT_ID` / `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY`). No package reader yet. Do not write warehouse objects. |
| Tests | **127 tests** — from `scripts/facts.py tests`, never counted by hand. No network, no full warehouse |
| Phase 1 code | `datagen/{generation,ingestion,augmentation,replay}` + `records.py` / `pipeline.py` |
| 1 s class | `generate_machine_stream` — P-101 / K-201; `friendly_name` = `{machine_id}/{pv}` |
| Goldens | TEP `f5b9d1cf…e6d33516` (do not change); machine stream `84b9f088…2159f0` |
| Unit 100 L0 join | Rev B PDF + 59-row CSV. **Done for ingestion.** Extra pages + DEXPI are other tracks (§2.1) |
| Not in repo | mapping-table YAML; DEXPI / `book.py`; Phase 2+ services; Marimo notebooks; R2 melt client |
| Open PRs | Run `gh pr list --state open`. Not listed here, for the same reason |
| Walkthrough | **parallel, not a build gate.** §0.1 done; Hamid resumes §0.2 Purdue |

**Exact cursor:** `docs/LSC-009_Walkthrough_Progress.md` (surface-independent bookmark). §0.1 ISA-95 is
**done**; **§0.2 Purdue is next**; then §0.3 IEC 62443, then Threads B → C → A, then cross-cutting.

**Phase 1 record:** `docs/LSC-005_Phase_1_Data_Record.md` (HTML twin + assets).
**Datasheet:** `docs/LSC-006_Phase_1_Datasheet.md`. Do not copy that write-up into this file.

### 2.1 Two leftover tracks — do not mix them

**Track A — L0 / ingestion (DONE).** Generate → melt → augment → replay is on
`main`. Warehouse bytes are on R2. The 59 `plant_data_name`s in
`tests/fixtures/datagen/pid/tag_schedule.csv` **are** the L0 names
(`xmeas_*`, `xmv_*`, `P-101/…`, `K-201/…`, `xv_feed`). CI pins the PDF hash
and the 59-name set. You can continue the OT build without more drawings.

**Track B — drawing book + DEXPI (NOT done; not the next build slice; now in scope
for Phase 5b.1, §12 #20).**

| Missing | Kind | When to pick it up |
|---------|------|--------------------|
| Index + analyzer (print AT-201..AT-219) + legend | Extra PDF pages. Architect lock: these **before** more process sheets. Titles become sheet N of N, not “1 of 1”. Caption: “1 second machine stream on P-101 and K-201”. | Owner-triggered drawing lap. Packet: `docs/LSC-007_Unit_100_Engineering_Record.md` → Extra pages. Do not invent a second factory. |
| `models/unit100_dexpi.json`, `tag_schedule.py`, `book.py` | Grok Bot pack. Lost. Graph of equipment / nozzles / lines. | **Phase 5b.1** (engineering graph — the ET leg is now in scope, §12 #20). Do **not** rebuild to unblock mapping or Sparkplug. |
| `data/tag_schedule.parquet` | Drawing note 2. | Issued join is the CSV. Do not recreate parquet as a second pin. |

`provenance=drawing` vs `reconstructed` in the CSV is honest: most
instrument↔TEP pairings were rebuilt after the Grok Bot pack was lost.
That is good enough for mapping-table join keys. Pipe/stream cells are
list columns, not a second naming system.

### Documentation reorganization in progress

The owner authorized batch reorganization and document streamlining. Work is
local on `docs/reorganize-project-documents`, based on the existing guard-fix
branch. PRs #52 and #53 were open at inspection. The reorganization is pending in
[PR #54](https://github.com/aadehamid/scada_harmonization/pull/54), initially based
on #53 so its diff contains only this concern.

The original collaboration rules now live in
[docs/WORKING_CONVENTIONS.md](docs/WORKING_CONVENTIONS.md). Dated session notes
and their recorded Git state were extracted into
[docs/history/SESSION_LOG.md](docs/history/SESSION_LOG.md).
The batch scope, reference revision, evidence, and next action are in
[docs/DOCUMENTATION_REORGANIZATION.md](docs/DOCUMENTATION_REORGANIZATION.md).

The actual-checkout `scripts/check.sh` and pre-push hook passed. The hook also
rejected a deliberately incorrect schedule figure, which was restored. Working-tree
review findings were corrected. A separate gpt-6-sol reviewer cleared committed change `ffc2c00` against
#53's base. The branch was pushed and PR #54 opened. Cursor feedback and
owner merge remain pending. Retarget to main after #53 lands and keep the
branch fully pushed before reporting readiness.

### Decision authority

Existing decision identifiers and qualifications live in charter sections 12,
13, and 14. Use [the decision index](docs/LSC-REG-001_Decision_Index.md) to find
them. This handoff does not maintain a second decision ledger.

---

## 3. What's next — mapping spine is the build; P&ID book is a later lap

### Next build session — mapping-table spine (Phase 0 exit)

**Kickoff prompt (paste into a fresh session):**

> Read `HANDOFF.md` §2.1 and §3, `docs/LSC-001_Problem_Statement_and_Project_Charter.md` §6 (three-stage
> table) + §14 N8/N10/N11/N17/N18, `docs/LSC-004_Level_0_Contract.md`, and
> `tests/fixtures/datagen/pid/tag_schedule.csv`. Phase 1 L0 is done. We are
> writing the first mapping-table slice: **one analog × four sites**, YAML +
> Pydantic, including the §14 columns. First row is locked: L0 `xmeas_7` =
> drawing `PT-101` (reactor pressure on R-101). Format is YAML. Explain the
> three stages and the §14 columns, then write the models + YAML + a small
> test. Do not dump all 59 rows. Do not start Sparkplug. Do not start the
> Phase 5b.1 drawing extraction (that is a later phase, and its toolchain is not
> selected).
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

> Read `docs/LSC-007_Unit_100_Engineering_Record.md` (Extra pages + domain locks) and
> `tests/fixtures/datagen/pid/`. One plant. Rev B process sheet stays. Draw
> index + analyzer (AT-201..AT-219) + legend **before** any new process page.
> Titles are sheet N of N. Say “1 second machine stream on P-101 and K-201”.
> Do not invent a second factory. Do not start Phase 5b.1 extraction. Do not
> change L0 names. Update the PDF pin + `docs/LSC-007_Unit_100_Engineering_Record.md` if the book
> hash changes.

### Walkthrough (Hamid, parallel — does not block build) — resume at §0.2 (Purdue)

Walkthrough remains a parallel path at §0.2. Cursor: `docs/LSC-009_Walkthrough_Progress.md`.
Original Eraser `MgnB91QGOhX8xWiKeaAK` stays the lock target. Packed L0 cuts live in
§2 of this file, not drawn. The N8 fast-class hole is closed (`#33`).

**Not now (unless Hamid redirects):** Diagram 1 lock, Sparkplug, second plant,
DEXPI rebuild, extra P&ID pages, Eraser copy, R2 melt-on-read client in the
package.

Warehouse reminder (not the next piece): R2 `lagos-chem-l0`, wide Parquet, melt-on-read.
Details in `docs/LSC-005_Phase_1_Data_Record.md` and `docs/LSC-006_Phase_1_Datasheet.md`.

**Walkthrough kickoff (when that parallel session runs):** *"Read `docs/LSC-008_End_to_End_Walkthrough.md` (the script),
`docs/LSC-009_Walkthrough_Progress.md` (the cursor), and `docs/LSC-010_Learning_Log.md` (notes so far). We are
running the Diagram 1 v2 end-to-end teaching walkthrough. §0.1 ISA-95 is done. Continue from §0.2,
the Purdue model, using the five-beat cadence (problem tie-in, mechanism, web research with cited
sources, gap check against Diagram 1 v2, one-line teach-back), pausing for questions between
steps, and logging glossary terms to `docs/LSC-010_Learning_Log.md`. After Purdue, do §0.3 IEC 62443, then
Threads B, then C, then A."*

**Diagram URL (v2, 2026-07-06, the walkthrough + lock target):**
https://app.eraser.io/workspace/MgnB91QGOhX8xWiKeaAK?diagram=133RhOiN_-G6Ko5kaTj8&layout=canvas
*(2026-06-23 original kept for history:
https://app.eraser.io/workspace/6Ng61sTaot9VjtU87bEY?diagram=vheRVPpajwodCEDwqnBZ&layout=canvas)*

Cadence, block order, and the §14 gap checklist live in
`docs/LSC-008_End_to_End_Walkthrough.md`. Do not copy them here.

**Walkthrough complete → Diagram 1 locked as the template for Diagrams 2 & 3.**
That lock does **not** unblock the mapping table — the table was never waiting
on it after 2026-08-19. The uv skeleton already landed (PR #22). Diagrams 2 & 3
stay just-in-time (Diagram 2 = UMH Core, §12 #16; Diagram 3 before Phase 6).

---

## 4. Working method

Follow [working conventions](docs/WORKING_CONVENTIONS.md) for the learning
cadence, Git workflow, diagrams, and handoff discipline. Follow
[the development guide](docs/DEVELOPMENT.md) for checks and tools.

## 5. Document map

Use [the master index](docs/LSC-000_Master_Index.md). Historical session notes
are in [the session log](docs/history/SESSION_LOG.md).

## 6. Implementation gates

The first mapping slice still needs an engineering-unit span supported by the
source or warehouse evidence. See section 3. Later phase gates and exit criteria
are in charter section 8.1. This documentation reorganization does not select the
Phase 5b.1 extraction toolchain or close implementation gates.
