# Review standards

The rules a reviewer applies that a script cannot. Everything mechanical — figures, hashes,
formatting, tests, the working-tree guard — runs in `scripts/check.sh`, and this file does not
repeat it. If a rule here can be made mechanical, move it into the check script and delete it from
here.

Each rule names the incident that taught it, with the pull request it happened on. A rule without
an incident is a guess, and this file does not carry guesses.

## A status claim must be true now; a record must be true when written

**Incident:** #43, #46, #47. `README.md`, `AGENTS.md` and `HANDOFF.md` each restated the current
status, and drifted: they quoted `main` at two different commits while the truth was a third, and
`HANDOFF.md`'s status table still claimed 41 after the suite had grown past it: it collected 60
when the figures tool was first written, 85 when #46 merged, and nothing updated the 41.

The tool did not catch it, for two independent reasons. Its test-count comparison read three
documents — `README.md`, `AGENTS.md` and `tests/README.md` — and not `HANDOFF.md`, so the table's
figure was compared with nothing. The tool did open that file: `status_claims()` and the pin scan
both walk every tracked Markdown file, and `HANDOFF.md` is in both. Neither of them judges a test
count inside it, which is the part that matters. And its pattern wants a number followed by `tests`
or `passed`, which the cell `| Tests | **41** (`uv run pytest`) |` is not, so the same stale figure
would have survived being read. #47 closed the first of those: it points the count comparison at
§2 of `HANDOFF.md`, and rewrites the cell into a form the pattern sees.

**#47 landed the consolidation.** `HANDOFF.md` §2 is the only place the status lives, and
`README.md` and `AGENTS.md` point at it rather than restating it. `scripts/facts.py check` reads
that section, so a stale **test count** there now fails the build.

That is the whole of what it judges there. Its patterns are a test count, a row or name count, and
a pin in a code span, and the same table holds figures that are none of those. Reproduced: changing
the warehouse cell's `17 objects` to `99 objects` leaves `check` reporting no problem, while
changing the test-count cell in the same table to `41 tests` fails at that line. A section the tool
reads is not every figure in it judged, so the numbers its patterns do not reach are still a
reviewer's to weigh. The warehouse count is one of them, two rows below the test count.

A dated session note or a phase record that names the commit it was written at is **history**, and
is correct as written. Do not "fix" it. `scripts/facts.py status` lists every such claim; deciding
which are status and which are history is this rule.

## A digest that matches a fixture is not proof it is the right fixture

**Incident:** #46. The adversarial review found that a complete, well-formed digest of the *wrong*
fixture passes, because the check matches a digest against the set of fixtures and only the prose
around it says which one was meant. `scripts/facts.py check` proves membership, and that both ends
of a pin belong to one fixture; it does not prove attribution, and the tool's comment says so. Read
the sentence.

## Check the population the sentence claims

**Incident:** #46. The figures guard first summed parsed test-node lines, which silently
undercounted the moment a node did not look the way the parser expected. It now uses pytest's own
reported total and fails when the breakdown disagrees. A count of mentions, or a figure copied from
an earlier message, is a different population from the one the sentence claims.

`scripts/facts.py` defines each population once, from the source file's structure. If a figure is
missing, extend the tool — never count by hand, and never write a script for the occasion.

## A check that has never failed has not been tested

**Incident:** #44 and #45. The working-tree guard passed its stated claims while missing three
changes: an untracked file rewritten, which the status line reports by path while its bytes were
never hashed; a file named `-`, which `sha256sum` read as standard input even after `--`; and a
staged blob swapped with the working file untouched, where the status string stayed `MM`. Each was
found by breaking the guard on purpose after the fact, not before, and the first repair brought a
fourth of its own — the next rule. A test can also pass for the wrong reason: one written
`! docker compose up …` proved nothing, because the leading `!` is what kept it from being read as a
digest, while the same command without the `!` was welded into `dockercomposeup…`, judged a pin, and
failed the build (#46, `edcb364`).

## Fixing a finding can introduce the next one

**Incident:** #45. The first repair of the untracked-file hole dropped git's status line from the
snapshot, which hid mode changes: removing the execute bit from `scripts/hooks/pre-push` left every
content hash unchanged, and git skips a non-executable hook without a word. The second pass put the
status line back and added `git ls-files --stage`, which the guard had never stored, so a staged
blob could change with the worktree untouched. Both were caught by re-reviewing the fixed diff.
Re-run the independent review after a fix, before pushing it.

## Done when

Every finding in a review is either fixed or answered on the pull request, and the answer says which
it is. A finding accepted without reproducing it is a guess, and becomes a wrong change.

**Incident:** #48, on this file's first draft. Three of its incidents were written from memory and
attributed the wrong evidence: the tool was blamed for a record it never read, the guard for a blind
spot its own status line already covered, and the repair for losing blob ids it had never stored.
Each was rewritten only after running the command that showed what happened.
