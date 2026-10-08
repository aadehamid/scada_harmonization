# Agent instructions

## Start here

1. Read [HANDOFF.md](HANDOFF.md) sections 2 and 3 for current status and the next slice.
2. Read [the project charter](docs/LSC-001_Problem_Statement_and_Project_Charter.md). It governs scope, architecture, constraints, and decisions.
3. Read [working conventions](docs/WORKING_CONVENTIONS.md) before editing. They own the learning cadence, Git workflow, diagram rules, and session discipline.
4. Use [the master index](docs/LSC-000_Master_Index.md) to find the document for the task.
5. Read [REVIEW_STANDARDS.md](REVIEW_STANDARDS.md) before reviewing a change.

## Before acting

- Load the clear-writing skill before writing text for people.
- Follow the charter rather than archived notes or another repository's design.
- Explain and align before non-trivial code. Work one understood slice at a time.
- Every change uses a branch and PR. The owner merges. Never push to `main`.
- Record decisions from the owner's words; a merge alone does not approve a design.
- Preserve unrelated changes. Stage paths explicitly and keep local tooling and private reference material out of commits.
- Update `HANDOFF.md` at the end of every session. Current status belongs in section 2; dated records belong in [session history](docs/history/SESSION_LOG.md).

## Checks and tools

Run `scripts/check.sh` before every push. Add mechanical gates there so CI and
local checks remain the same. See [the development guide](docs/DEVELOPMENT.md)
for commands and the [review standards](REVIEW_STANDARDS.md) for judgement.

Figures and searches come from `scripts/facts.py`. Extend that shared tool when
needed rather than writing a separate counting script. Current figures belong
in the handoff and the owning records, rather than this instruction file.

Install the tracked hook once per clone:

```sh
git config core.hooksPath scripts/hooks
```

Prove it runs with `git hook run pre-push`. Preserve an existing shared hook
configuration; consult the way-of-working skill before changing it.

## Boundaries

The charter owns the four planes, PLC-world boundary, identity reconciliation,
source authority, Sparkplug contract, deterministic transforms, and phase exits.
Read its sections 6, 8, 9, and 14 before changing those contracts.

Project diagrams use Eraser in the `scada_harmonization` workspace. Details are
in [working conventions](docs/WORKING_CONVENTIONS.md). Reference materials in
`reference/` are local-only evidence, not scope or dependencies.
