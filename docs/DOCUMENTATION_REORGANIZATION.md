# Documentation reorganization record

Status: local reorganization in progress on `docs/reorganize-project-documents`.
Review and shipping evidence is recorded below as it becomes available.

## Authorization

The owner requested:

> I want you to use $project-discovery in batch without my approval to reorganize the repo in the similar way as the repo exmaple cited in the skill. You have my permission to reorganize the repo and streamline the documents. Do you understand?

The owner subsequently identified the reference:

> By the way you can use this as the refrence repo on how we wshould organize this repo. https://github.com/aadehamid/pearland-petroleum-corporation

The owner qualified the approach and authorized a PR:

> Please do not force the file reoranization. make sure it makes sesne. Raise PR when it makes sessn to do so. Keep a running log of what you did so that i can review tomorrow

These instructions permit batch editing, verification, and a reviewable PR.
Existing project decisions retain their authority. The owner merges.

## Reference assessment

Reference: `aadehamid/pearland-petroleum-corporation`, revision
`01027a84be5d453cbb4e2ea091e4884729918b15`.
Read with authenticated `gh api`: the repository tree, README, AGENTS, master
index, and architecture decision register. The tree shows mostly `.gitkeep`
component directories; it supplies organization evidence, not runtime evidence.
No reference program or test was executed. Its architecture choices are not
implementation requirements for this lab.

| Reference practice | Evidence | Treatment here | Consequence |
| --- | --- | --- | --- |
| Numbered project documents in `docs/` | PPC document tree and master index | Adapt with LSC document IDs | A consistent reading package and stable subject names |
| Master index with a reading map | PPC-000 | Adapt in LSC-000 | Readers choose the document that owns the answer |
| Short agent entry point | PPC AGENTS | Adapt | Detailed methods move out of always-loaded instructions |
| Decision register | PPC-REG-001 | Adapt as a navigation index | Preserve existing charter IDs and decision authority |
| Architecture split across documents | PPC document tree | Keep this lab's charter intact | Existing section references and amendments keep their meaning |
| Component directory placeholders | Recursive tree | Exclude | Existing src-layout package, config, tests, Docker, and notebooks retain their roles |
| EPM/ECE dependency and reference stack | PPC README | Exclude | No new project coupling, tool selection, or scope expansion |

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

## Verification and delivery

Baseline `scripts/check.sh` passed before edits. A staged temporary checkout
also passed all checks, including 127 tests, with uv cache redirected to `/tmp`.
The actual-checkout `scripts/check.sh` and pre-push hook passed. Changing the
README schedule figure from 59 to 58 made the hook exit 1 with the correct
figure mismatch; the original bytes were restored. Local Markdown/HTML paths
and linked headings resolve across the tracked repository. Final committed
review and remote results will be recorded in the PR.
A working-tree independent review found no lost charter decisions or working rules.
Its migration-source, dated-anchor, and reading-copy-label findings were reproduced
and corrected. The reviewer used gpt-6-sol; the author uses the session model. No diagrams were created or edited. No external source claims,
versions, licenses, or runtime designs were changed; reference inspection assessed
organization only. Optional grilling and domain-modeling helpers are unavailable;
this run uses existing domain definitions and introduces no new design.

The branch began at PR #53's guard-fix commit. PR #52 and PR #53 were open when
inspected. The reorganization PR must identify that dependency or move to main
after the parent lands; unrelated guard changes must not be presented as this change.

## Implementation handoff

This batch reorganizes documentation. The first implementation milestone remains
the mapping slice in HANDOFF section 3. Confirm the engineering-unit span using
source or warehouse evidence before finalizing that row. Later extraction,
infrastructure, and model decisions stay at their original phase gates.
