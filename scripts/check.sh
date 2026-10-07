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
# thing it is supposed to be checking. Hash tracked content plus untracked
# presence before and after, and fail on any difference.
tree_state() {
  {
    git ls-files -z | xargs -0 sha256sum 2>/dev/null
    git status --porcelain --untracked-files=all
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

after="$(tree_state)"
if [ "$before" != "$after" ]; then
  echo >&2
  echo "FAIL: the checks changed the working tree." >&2
  git status --short >&2
  exit 1
fi

echo
echo "All checks passed."
