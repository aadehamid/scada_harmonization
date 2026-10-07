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
`HANDOFF.md`'s status table claimed 41 tests while the suite collected 85 on `main`. The 41 was
correct before the figures tool added tests of its own (#46) and was never updated.

The tool did not catch it. Its first run reported **34 tests**, read from a dated session note, and
left the 41 in the status table untouched, because `scripts/facts.py check` did not treat
`HANDOFF.md` as a current-status document. The pattern found a record and walked past the claim,
which is why telling the two apart is this rule's job rather than the script's. #47 closes the hole
from the other side: it makes §2 the status the check reads.

#47 consolidates the status into `HANDOFF.md` §2 and points the other documents at it. **It is
open, not merged** — treat the consolidation as pending until it lands, and read the copies on
`main` as still authoritative until then.

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

**Incident:** #44 and #45. The working-tree guard passed all four of its stated claims while missing
untracked file rewrites, a file named `-` (which `sha256sum` read as standard input), a dropped
executable bit, and an index change. Each was found by breaking it on purpose after the fact, not
before. A test can also pass for the wrong reason: one written `! docker compose up …` proved
nothing, because the leading `!` is what kept it from being read as a digest, while the same command
without the `!` was welded into `dockercomposeup…`, judged a pin, and failed the build
(#46, `edcb364`).

## Fixing a finding can introduce the next one

**Incident:** #45. Fixing the untracked-file hole in the working-tree guard introduced two more:
dropping git's status snapshot hid mode changes, and the replacement lost index blob ids. Both were
caught only by re-reviewing the fixed diff. Re-run the independent review after a fix, before
pushing it.

## Done when

Every finding in a review is either fixed or answered on the pull request, and the answer says which
it is. A finding accepted without reproducing it is a guess, and becomes a wrong change.
