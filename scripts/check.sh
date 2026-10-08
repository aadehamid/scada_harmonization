#!/usr/bin/env bash
# The project's checks, in one place. CI runs this script; the pre-push hook runs it.
#
# Adding a gate? Add it here, not in ci.yml and not in the hook, so a local run
# and a CI run always run the same things.
#
# Usage: scripts/check.sh
#        scripts/check.sh --tree-state   print the working-tree guard's snapshot
#                                        and stop, without running a check.
#                                        The guard's own tests drive this.
set -euo pipefail

# What this script examines is decided here, not by the shell that called it.
#
# The git names point git at another repository, index or object store while the
# working directory still says this one. With `GIT_DIR` and `GIT_WORK_TREE` set,
# the snapshot below comes out as one unchanging value: measured, two edits to
# README.md under those two variables moved it not at all. The rest change the
# checks themselves — `UV_WORKING_DIR` takes `uv run` out of the project
# altogether, `PYTEST_ADDOPTS` selects a subset of the suite, `PYTHONPATH`
# decides which module a name means. A local run and a CI run have to run the
# same things, so all of them go.
#
# The git and pytest names are `_REDIRECTING_ENV` in scripts/facts.py, which
# carries the reasoning for each one, plus three more of that family
# (`GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_COMMON_DIR`, `GIT_NAMESPACE`) that no
# test here exercises. That tool answers uv on its command lines instead, so the
# four `UV_` names are this script's own. A list of variables is never finished,
# so the assertion below does not lean on this one.
dropped=()
for name in \
  GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY \
  GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_COMMON_DIR GIT_NAMESPACE \
  GIT_CONFIG_PARAMETERS GIT_CONFIG_COUNT \
  PYTEST_ADDOPTS PYTEST_PLUGINS PYTHONPATH \
  UV_WORKING_DIR UV_PROJECT UV_PROJECT_ENVIRONMENT UV_CONFIG_FILE; do
  if [ -n "${!name:-}" ]; then
    dropped+=("$name")
    unset "$name"
  fi
done
if [ "${#dropped[@]}" -gt 0 ]; then
  echo >&2 "note: ignoring from the caller's environment: ${dropped[*]}"
fi

# The root is this file's own parent, not an answer from git, so that a redirect
# the list above misses shows up as the refusal below rather than as a guard
# watching another tree from the right directory.
repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd -- "$repo"

# Ask git which repository it is answering about, since dropping variables is
# only as good as the list. Two questions, because two things move separately:
# `GIT_DIR` moves the git directory while `--show-toplevel` still answers this
# checkout, so that question alone would not find it. Both expected answers come
# from the filesystem, where no variable can reach them.
marker="$repo/.git"
if [ -d "$marker" ]; then
  want_git_dir="$(cd -- "$marker" && pwd -P)"
elif [ -f "$marker" ]; then
  # A linked worktree or a submodule keeps its metadata elsewhere and leaves a
  # pointer here instead of a directory.
  want_git_dir="$(cd -- "$repo/$(sed -n '1s/^gitdir: *//p' "$marker")" && pwd -P)"
else
  echo >&2 "FAIL: $marker is neither a file nor a directory; $repo is not a checkout."
  exit 1
fi
got_git_dir="$(git rev-parse --absolute-git-dir 2>/dev/null || true)"
got_toplevel="$(git rev-parse --show-toplevel 2>/dev/null || true)"
# Resolve both through the filesystem, so a symlinked path on one side is not
# read as a difference between two names for the same directory.
if [ -d "$got_git_dir" ]; then
  got_git_dir="$(cd -- "$got_git_dir" && pwd -P)"
fi
if [ -d "$got_toplevel" ]; then
  got_toplevel="$(cd -- "$got_toplevel" && pwd -P)"
fi
if [ "$got_git_dir" != "$want_git_dir" ] || [ "$got_toplevel" != "$repo" ]; then
  echo >&2 "FAIL: git is answering about ${got_git_dir:-(nothing)} with working tree"
  echo >&2 "      ${got_toplevel:-(nothing)}, but this checkout is $repo pointing at"
  echo >&2 "      $want_git_dir. Something in this shell points git elsewhere."
  echo >&2 "      Unset it and run again."
  exit 1
fi

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
tracked_paths() {
  git ls-files -z --cached --others --exclude-standard
}

tree_state() {
  local contents entries
  # A read that fails has to stop the snapshot, not drop out of it: a path
  # missing from both snapshots compares equal, so a check that rewrote a file
  # the guard could not read would still reach "All checks passed." It did — a
  # file at mode 000 whose contents were replaced twice produced the same state
  # every time.
  #
  # The status has to be taken here, not left to `set -e`. Neither read is the
  # last command in the group below, and a group's status is its last command's,
  # so nothing else sees `xargs` exit 123 on a failed read.
  #
  # Every path goes through './' or a trailing '--', so a file named '--help' is
  # read as a path rather than as an option to the tool. The './' prefix is
  # load-bearing: sha256sum reads a bare '-' operand as standard input even after
  # '--', so a file named '-' would never be read.
  if ! contents="$(tracked_paths | sort -z | sed -z 's|^|./|' | xargs -0 -r sha256sum --)"; then
    echo >&2 "FAIL: a tracked path could not be hashed."
    return 1
  fi
  # Mode, filesystem type, and — for a symlink — its target, quoted and escaped
  # by %N, so a target ending in a newline cannot collide with a different name.
  if ! entries="$(tracked_paths | sort -z | sed -z 's|^|./|' | xargs -0 -r stat -c '%A %F %N' --)"; then
    echo >&2 "FAIL: a tracked path could not be stat-ed."
    return 1
  fi
  {
    printf '%s\n' "$contents" "$entries"
    # Content hashes miss mode changes and index state (an executable bit
    # dropped from the hook, for one), so keep git's own view alongside them.
    git status --porcelain --untracked-files=all
    # Status records change *categories*, not index blob ids: a staged blob can
    # change while the status string stays 'MM' and the working file is
    # untouched. --stage carries the blob id, mode and stage for each path.
    git ls-files --stage -z
  } | sha256sum | cut -d' ' -f1
}

# For the guard's own tests: print what a run would compare, and stop. The tests
# copy this script into a throwaway repository, where the checks below could not
# run; a snapshot is all they need from it.
if [ "${1:-}" = "--tree-state" ]; then
  # An assignment, not `echo "$(tree_state)"`: a snapshot that failed stops the
  # script here, the same way the `before=` below stops it.
  state="$(tree_state)"
  echo "tree_state: $state"
  exit 0
fi

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
