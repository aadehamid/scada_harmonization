# Documentation reorganization record

Status: reorganization proposed in [PR #54](https://github.com/aadehamid/scada_harmonization/pull/54). Not merged.
Review and shipping evidence is recorded below as it becomes available.

## Authorization

The owner requested:

> I want you to use $project-discovery in batch without my approval to reorganize the repo in the similar way as the repo exmaple cited in the skill. You have my permission to reorganize the repo and streamline the documents. Do you understand?

The owner subsequently identified the reference:

> By the way you can use this as the refrence repo on how we wshould organize this repo. https://github.com/aadehamid/pearland-petroleum-corporation

The owner qualified the approach and authorized a PR:

> Please do not force the file reoranization. make sure it makes sesne. Raise PR when it makes sessn to do so. Keep a running log of what you did so that i can review tomorrow

These instructions permit batch editing, verification, and a reviewable PR.
Existing project decisions retain their authority. The PR reviewer merges.

The owner clarified the content and reuse requirements:

> Resuse the tech stack in the refrence repor where it makes sesne to do so.

> you already majority of some of the documents in this repo we just need to organize them and rewrite them where it makes sesne to do and add new docs where they are missing.

> and use $clear-writing for the writings

After asking that all PRs be merged, the owner clarified who performs that action:

> dont merge them... the PR reviewer will do the merging. you just need to watch and address any feedback and poush again. this should be in the way of working skill?

This latest instruction governs delivery. Agents do not merge. Way-of-working's
changing workflow requires watching, addressing holds on the same branch, and
pushing reviewed fixes until the reviewer merges or the owner closes the PR.

## Reference assessment

Reference: `aadehamid/pearland-petroleum-corporation`, revision
`01027a84be5d453cbb4e2ea091e4884729918b15`.
Read with authenticated `gh api`: the repository tree, README, AGENTS, master
index, architecture decision register, and subject documents PPC-002, PPC-004,
PPC-007, PPC-008, PPC-009, PPC-010, PPC-011, PPC-013, and PPC-REF-001.
The tree shows mostly `.gitkeep`
component directories; it supplies organization evidence, not runtime evidence.
No reference program or test was executed. Its architecture choices are not
implementation requirements for this lab. The owner's later reuse instruction
requires assessing PPC choices before proposing substitutes.

| Reference practice | Evidence | Treatment here | Consequence |
| --- | --- | --- | --- |
| Numbered project documents in `docs/` | PPC document tree and master index | Adapt with LSC document IDs | A consistent reading package and stable subject names |
| Master index with a reading map | PPC-000 | Adapt in LSC-000 | Readers choose the document that owns the answer |
| Short agent entry point | PPC AGENTS | Adapt | Detailed methods move out of always-loaded instructions |
| Decision register | PPC-REG-001 | Adapt as a navigation index | Preserve existing charter IDs and decision authority |
| Architecture split across documents | PPC document tree | Keep this lab's charter intact | Existing section references and amendments keep their meaning |
| Component directory placeholders | Recursive tree | Exclude | Existing src-layout package, config, tests, Docker, and notebooks retain their roles |
| EPM/ECE dependency | PPC README | Keep LSC boundaries | No new project coupling follows from reference inspection |
| Reference stack | PPC-002 and PPC-REF-001 | Assess shared choices and actual gaps | REF-001 records reuse and phase-gated candidates |

Before the owner supplied PPC, enterprise-performance-model was inspected as a
working assumption because way-of-working cites it. PPC supersedes that assumption.

## Changes and reasons

| Artifact | Responsibility | Change |
| --- | --- | --- |
| `README.md` | Human entry point | Short project explanation, reading order, and repository responsibilities |
| `AGENTS.md` | Agent entry point | Startup, boundaries, checks, and pointers |
| `docs/LSC-000_Master_Index.md` | Package navigation | Document register, architecture reading map, and authority |
| `docs/LSC-001_Problem_Statement_and_Project_Charter.md` | Governing project definition | Move intact; preserve numbered sections and decisions |
| `docs/LSC-002` through `LSC-010` | Existing domain, strategy, contracts, records, and learning | Move by existing responsibility; retain document bodies except references |
| `docs/LSC-REG-001_Decision_Index.md` | Decision navigation | Point at original IDs rather than duplicate their resolutions |
| `docs/WORKING_CONVENTIONS.md` | Collaboration method | Relocate existing rules and preserve unique handoff conventions |
| `docs/DEVELOPMENT.md` | Development commands | Relocate setup and shared-tool instructions |
| `HANDOFF.md` section 2 | Current status | Retain single-source status; remove historical and copied design summaries |
| `docs/history/SESSION_LOG.md` | Historical evidence | Preserve dated sessions and earlier handoff excerpts |
| `docs/archive/` | Superseded alternatives | Separate from current project definitions |
| `docs/assets/` | Reading-copy illustrations | Keep assets with the Markdown and HTML reading copies |
| References in package docstrings and tests | Document discovery | Update paths; runtime behavior remains the same |
| `scripts/facts.py` | Figure verification | Stop requiring figures in the short AGENTS entry point; retain status and record checks |

The [path migration table](DOCUMENT_PATHS.md) lets a reviewer locate every moved
artifact. The [running log](REORGANIZATION_LOG.tsv) records actions, reasons,
evidence, and follow-up. Paths in historical prose describe the original checkout;
current navigation links point at the reorganized package.

The follow-up rewrites dense prose in LSC-002 and adds two missing records:
LSC-REG-002 inventories sources, interfaces, capture boundaries, and acceptance
questions. LSC-REF-001 assesses shared PPC choices and candidates for actual gaps.
An overlap audit omitted seven draft subject guides because the charter already
owns those definitions. The approved charter remains intact.

## Verification and delivery

Baseline `scripts/check.sh` passed before edits. A staged temporary checkout
also passed all checks, including 127 tests, with uv cache redirected to `/tmp`.
The actual-checkout `scripts/check.sh` and pre-push hook passed. Changing the
README schedule figure from 59 to 58 made the hook exit 1 with the correct
figure mismatch; the original bytes were restored. Local Markdown/HTML paths
and linked headings resolve across the tracked repository. The separate gpt-6-sol reviewer cleared committed change `ffc2c00` against
base `0b7a5a2`. That change was pushed and PR #54 opened. Cursor review and
reviewer merge remain pending. Later documentation-only updates are also reviewed
before each push; the PR carries the current exact-commit verdict.
A working-tree independent review found no lost charter decisions or working rules.
Its migration-source, dated-anchor, and reading-copy-label findings were reproduced
and corrected. The reviewer used gpt-6-sol; the author uses the session model. No diagrams were
created or edited. The first commit assessed organization only. The follow-up adds
cited primary-source research and explicitly proposed phase questions. It installs
no components and changes no approved runtime design. Optional grilling and
domain-modeling helpers are unavailable; this run uses existing domain definitions.

The branch began at PR #53's guard-fix commit. PR #54 targets that branch
until #53 lands. Its diff is the documentation change, not the guard repair.
After #53 lands, inspect main and retarget this PR; review any reconciliation
with #52's pending session note. The PR reviewer merges each PR.

## Implementation handoff

This batch reorganizes documentation. The first implementation milestone remains
the mapping slice in HANDOFF section 3. Confirm the engineering-unit span using
source or warehouse evidence before finalizing that row. Later extraction,
infrastructure, and model decisions stay at their original phase gates.
