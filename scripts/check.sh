#!/usr/bin/env bash
# The project's checks, in one place. CI runs this script; the pre-push hook runs it.
#
# Adding a gate? Add it here, not in ci.yml and not in the hook, so a local run
# and a CI run always run the same things.
#
# Usage: scripts/check.sh
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# A check that writes to the repo is a bug: a local run and a CI run would then
# disagree about what the repo contains, and a gate could pass by editing the
# thing it is supposed to be checking.
#
# Four snapshots, because each misses something the others catch:
#   contents          an edit to any file, tracked or untracked
#   type and mode     an untracked script that loses its execute bit changes
#                     neither its contents nor git's status
#   symlink targets   the content hash follows a link, so a link retargeted to
#                     a file with identical contents is otherwise invisible
#   status and index  a staged blob can change while the working file and the
#                     status wording stay the same
#
# Scope: tracked and non-ignored files. Ignored build paths (.venv/,
# __pycache__/, .pytest_cache/, .ruff_cache/) are outside it.
#
# The './' prefix is load-bearing: sha256sum reads a bare '-' operand as
# standard input even after '--', so a file named '-' would never be read.
tracked_paths() {
  git ls-files -z --cached --others --exclude-standard
}

tree_state() {
  {
    # Every path goes through './' or a trailing '--', so a file named '--help'
    # is read as a path rather than as an option to the tool.
    tracked_paths | sort -z | sed -z 's|^|./|' | xargs -0 -r sha256sum -- 2>/dev/null
    # Mode, filesystem type, and — for a symlink — its target, quoted and
    # escaped by %N, so a target ending in a newline cannot collide with a
    # different name. One call covers what two would: fewer places to be wrong,
    # and no command substitution to strip a trailing newline.
    tracked_paths | sort -z | sed -z 's|^|./|' | xargs -0 -r stat -c '%A %F %N' -- 2>/dev/null
    # Content hashes miss mode changes and index state (an executable bit
    # dropped from the hook, for one), so keep git's own view alongside them.
    git status --porcelain --untracked-files=all
    # Status records change *categories*, not index blob ids: a staged blob can
    # change while the status string stays 'MM' and the working file is
    # untouched. --stage carries the blob id, mode and stage for each path.
    git ls-files --stage -z
  } | sha256sum | cut -d' ' -f1
}

before="$(tree_state)"

echo "== ruff check =="
uv run ruff check .

echo
echo "== ruff format --check =="
uv run ruff format --check .

echo
echo "== ty check =="
uv run ty check

echo
echo "== pytest =="
uv run pytest

echo
echo "== quoted figures =="
uv run python scripts/facts.py check

after="$(tree_state)"
if [ "$before" != "$after" ]; then
  echo >&2
  echo "FAIL: the checks changed the working tree." >&2
  git status --short >&2
  exit 1
fi

echo
echo "All checks passed."
