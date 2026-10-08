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
# The checks are given an environment this script builds: `env -i`, and then the
# four things no check can find for itself. Everything else the caller had is
# gone, exported shell functions and `BASH_ENV` with it.
#
# What that replaces is a list of names to drop, grown by a review round at a
# time. Each name on it was a way the caller's shell could decide what the
# checks looked at. `GIT_DIR` with `GIT_WORK_TREE` points git at another
# repository while the working directory still says this one, and the snapshot
# came out as one unchanging value: measured, two edits to README.md under those
# two moved it not at all. `UV_WORKING_DIR` takes `uv run` out of the project
# altogether. `PYTEST_ADDOPTS` selects part of the suite: a file naming
# `PYTEST_ADDOPTS=-k test_check_script` ran 17 of the suite's tests, deselected
# 107, and this script still printed "All checks passed." `PYTHONPATH` decides
# which module a name means. `TY_CONFIG_FILE` names the file ty reads, and a
# configuration that excludes every path leaves `ty check` with nothing to look
# at, which ty reports as a warning and not as a failure.
#
# A list of names is never finished, and each round found another one. An
# environment that is built instead is finished: a name nobody has thought of
# yet is left out for the same reason as the names above it.
#
# Kept, because no check can find them for itself: `PATH`, which is how the
# tools are found; `HOME`, under which uv keeps its cache and its Python
# installs; `TMPDIR`, which a check may
# write through; and the locale, which decides how output is encoded. A CI run
# supplies those four too. Their values can differ between machines.
# Anything else a check needs belongs in the repository's own configuration —
# `pyproject.toml`, `uv.toml`, `ty.toml` — which both runs read, and not in the
# caller's shell, which only one of them has.
# Git's global configuration is fixed separately. A core.excludesFile in
# HOME/.gitconfig hid an untracked file that a check edited, so both snapshots
# omitted it and the guard passed (PR #53). HOME remains available to uv.
# Git also defaults core.excludesFile to HOME/.config/git/ignore without a
# global config file. Fix that setting at command scope, above config files.
# Repository .gitignore and .git/info/exclude still define the scope below.
#
# Two defences live past this, because no environment reaches them. Every
# `uv run` below carries `--no-env-file`: a `pyproject.toml` or a `uv.toml` can
# name an environment file, and nothing here takes that away. And `ty check`
# names its configuration on the command line, where an explicit
# `--config-file` outranks the variable. The tests cover both flags.
#
# `PATH` is passed on as the caller had it, so a `git` they put in front of the
# real one answers every question asked here. The two reads further down ask git
# which repository it is reading, and refuse when the answer is another one.
if [ "${1:-}" != "--env-built" ]; then
  if [ -z "${PATH:-}" ]; then
    echo >&2 "FAIL: PATH is empty, so the tools this script runs cannot be found."
    echo >&2 "      Set it and run again."
    exit 1
  fi
  # The `cd` runs in a subshell, so it names this script without moving the
  # shell that is about to be replaced by it.
  self="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/$(basename -- "${BASH_SOURCE[0]}")"
  fixed=(env -i "PATH=$PATH" "GIT_CONFIG_GLOBAL=/dev/null"
    "GIT_CONFIG_COUNT=1" "GIT_CONFIG_KEY_0=core.excludesFile"
    "GIT_CONFIG_VALUE_0=/dev/null")
  # Only a name that is set is passed on: an empty `HOME` is worse than none,
  # since uv would then look for its cache under the filesystem root.
  for name in HOME TMPDIR LANG LC_ALL LC_CTYPE; do
    if [ -n "${!name:-}" ]; then
      fixed+=("$name=${!name}")
    fi
  done
  # `--env-built` is how the second run knows it is the second run, and it is an
  # argument rather than a variable for a measured reason: a variable is
  # inherited. With the marker in the environment, the checks below start
  # processes of their own — pytest runs the guard's own tests — and the nested
  # run of this script found the marker already set, skipped the rebuild, and let
  # a caller's `GIT_DIR` through. Five of the guard's own tests failed on it. A
  # caller who passes this argument has taken the guard off their own run, which
  # is the same choice as handing it one of the variables above.
  exec "${fixed[@]}" "$self" --env-built "$@"
fi

# The snapshot below is asked for by name, so the flag comes off argv here rather
# than reaching the checks: `--tree-state` is still the first argument of what is
# left.
shift

echo >&2 "note: the checks run under a fixed environment — PATH, HOME, TMPDIR and the"
echo >&2 "      locale. The caller's other variables are not passed on."

# The root is this file's own parent, not an answer from git, so that a redirect
# the environment above did not answer for shows up as the refusal below rather
# than as a guard watching another tree from the right directory.
repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd -- "$repo"

# Ask git which repository it is answering about, since the environment is only
# half of it: `PATH` is the caller's, so the `git` that answers may not be the
# one this repo is checked out with. Two questions, because two things move
# separately: `GIT_DIR` moves the git directory while `--show-toplevel` still
# answers this checkout, so that question alone would not find it. Both expected
# answers come from the filesystem, where no variable can reach them.
marker="$repo/.git"
if [ -d "$marker" ]; then
  want_git_dir="$(cd -- "$marker" && pwd -P)"
elif [ -f "$marker" ]; then
  # A linked worktree or a submodule keeps its metadata elsewhere and leaves a
  # pointer here instead of a directory. git writes an absolute path for a
  # worktree and one relative to the checkout for a submodule, and both resolve
  # against the working directory, which `cd` above put at the checkout root. So
  # the pointer is used as it stands: joining it to the root would name
  # `$repo//tmp/...`, a directory nothing created, and refuse a worktree that
  # `git worktree add` had just made.
  pointer="$(sed -n '1s/^gitdir: *//p' "$marker")"
  if [ ! -d "$pointer" ]; then
    echo >&2 "FAIL: $marker points at '$pointer', which is not a directory."
    exit 1
  fi
  want_git_dir="$(cd -- "$pointer" && pwd -P)"
else
  echo >&2 "FAIL: $marker is neither a file nor a directory; $repo is not a checkout."
  exit 1
fi
# Both reads are asked for their status. `|| true` in its place turns "git is
# broken" into "git agreed": a `git` that ran the real `rev-parse`, printed the
# expected directory and then returned 128 was believed, and the guard went on.
# A read that failed has not answered, and an unanswered question is not a
# comparison that passed. The value comparison below still covers a git that
# answers with the wrong directory, or with nothing.
if ! got_git_dir="$(git rev-parse --absolute-git-dir 2>/dev/null)"; then
  echo >&2 "FAIL: git could not name the repository it is reading. Something in"
  echo >&2 "      this shell is breaking it; unset it and run again."
  exit 1
fi
if ! got_toplevel="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  echo >&2 "FAIL: git could not name the working tree it is reading. Something in"
  echo >&2 "      this shell is breaking it; unset it and run again."
  exit 1
fi
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

# `--cached` lists a tracked file that has been deleted from the working tree
# without staging, and reading that path fails; a broken symlink fails a content
# read too. Neither is a check doing something, and a checkout is in both states
# while someone works, so each read below takes the paths it can handle. The
# status and index lines keep those paths in the snapshot, so a deletion or a
# retargeted link still moves it. A regular file that cannot be read is a
# different matter, and it stops the snapshot.
#
# Each filter reads the path list from its standard input, so it sits inside the
# pipeline whose status is checked. `<(tracked_paths)` in its place discards the
# status of what it runs: a `git ls-files` that failed left an empty list, both
# reads answered happily on nothing, and the state stopped moving — measured, a
# tracked file changed from mode 644 to mode 600 under a failing enumeration and
# the snapshot stood still. `pipefail` carries the failed enumeration out.
hashable_paths() {
  local path
  while IFS= read -r -d '' path; do
    if [ -f "$path" ]; then printf '%s\0' "$path"; fi
  done
}

# stat reports on the link itself, so it answers for a broken one; `-e` alone
# would drop that path, and `%N` below is what records the link's target.
present_paths() {
  local path
  while IFS= read -r -d '' path; do
    if [ -e "$path" ] || [ -L "$path" ]; then printf '%s\0' "$path"; fi
  done
}

tree_state() {
  local contents entries status index
  # A read that fails has to stop the snapshot, not drop out of it: a path
  # missing from both snapshots compares equal, so a check that rewrote a file
  # the guard could not read would still reach "All checks passed." It did — a
  # file at mode 000 whose contents were replaced twice produced the same state
  # every time.
  #
  # So every read is asked for its own status, and none of them is left to an
  # enclosing group: a group's status is its last command's, and a pipeline's is
  # its last stage's unless `pipefail` is set.
  #
  # Every path goes through './' or a trailing '--', so a file named '--help' is
  # read as a path rather than as an option to the tool. The './' prefix is
  # load-bearing: sha256sum reads a bare '-' operand as standard input even after
  # '--', so a file named '-' would never be read.
  if ! contents="$(tracked_paths | hashable_paths | sort -z | sed -z 's|^|./|' | xargs -0 -r sha256sum --)"; then
    echo >&2 "FAIL: the paths could not be listed, or one could not be hashed."
    return 1
  fi
  # Mode, filesystem type, and — for a symlink — its target, quoted and escaped
  # by %N, so a target ending in a newline cannot collide with a different name.
  if ! entries="$(tracked_paths | present_paths | sort -z | sed -z 's|^|./|' | xargs -0 -r stat -c '%A %F %N' --)"; then
    echo >&2 "FAIL: the paths could not be listed, or one could not be stat-ed."
    return 1
  fi
  # Content hashes miss mode changes and index state (an executable bit dropped
  # from the hook, for one), so keep git's own view alongside them.
  if ! status="$(git status --porcelain --untracked-files=all)"; then
    echo >&2 "FAIL: git could not report the working tree's status."
    return 1
  fi
  # Status records change *categories*, not index blob ids: a staged blob can
  # change while the status string stays 'MM' and the working file is untouched.
  # --stage carries the blob id, mode and stage for each path.
  if ! index="$(git ls-files --stage -z | sha256sum | cut -d' ' -f1)"; then
    echo >&2 "FAIL: git could not report the index."
    return 1
  fi
  printf '%s\n' "$contents" "$entries" "$status" "$index" | sha256sum | cut -d' ' -f1
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
uv run --no-env-file ruff check .

echo
echo "== ruff format --check =="
uv run --no-env-file ruff format --check .

echo
echo "== ty check =="
# Named on the command line as well as argued for at the top of this script,
# because an explicit `--config-file` outranks the variable whatever the
# environment holds, and the file it names is this repo's.
uv run --no-env-file ty check --config-file ty.toml

echo
echo "== pytest =="
uv run --no-env-file pytest

echo
echo "== quoted figures =="
uv run --no-env-file python scripts/facts.py check

after="$(tree_state)"
if [ "$before" != "$after" ]; then
  echo >&2
  echo "FAIL: the checks changed the working tree." >&2
  git status --short >&2
  exit 1
fi

echo
echo "All checks passed."
