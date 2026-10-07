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
# Hash the *contents* of every non-ignored file, tracked and untracked alike.
# Hashing names alone is not enough: an untracked file that a check rewrites
# keeps its path, so a name-only snapshot cannot see the change.
#
# The './' prefix is load-bearing: sha256sum reads a bare '-' operand as
# standard input even after '--', so a file named '-' would never be read.
#
# Known limit: sha256sum follows symlinks, so retargeting a symlink to a file
# with identical bytes would not be seen. This repo tracks no symlinks and no
# gate creates one. If that changes, snapshot lstat types here as well.
tree_state() {
  {
    git ls-files -z --cached --others --exclude-standard \
      | sort -z \
      | sed -z 's|^|./|' \
      | xargs -0 -r sha256sum -- 2>/dev/null
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
