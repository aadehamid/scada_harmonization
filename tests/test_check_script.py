"""The working-tree guard in scripts/check.sh.

The guard is what stops a check from passing by editing the tree it checks, so
its own failure modes need proving. Each test below fails when the line that
answers it is removed from the script:

* a path the guard could not read was skipped instead of stopping the snapshot,
  so a file at mode 000 could be rewritten under it and the state never moved;
* the guard inherited the caller's environment, so `GIT_DIR` with `GIT_WORK_TREE`
  pointed it at another repository, where its snapshot collapsed to the hash of
  the empty string, while the checks still ran here;
* a git read that failed dropped out of the snapshot instead of stopping it, so
  under a failing `ls-files` the contents and mode lines went missing and a mode
  change moved the state not at all;
* the two reads that name the repository let their own failure through, so a
  `git` that answered correctly and then returned 128 was believed.

The script is copied into a throwaway repository rather than run in this one: it
runs uv, ruff and pytest, which a test cannot start from inside the suite.
`--tree-state` asks the guard for its snapshot and stops before any check.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.test_facts import _scratch_env

REPO = Path(__file__).resolve().parent.parent
CHECK_SH = REPO / "scripts" / "check.sh"
STATE = re.compile(r"^tree_state: ([0-9a-f]{64})$", re.MULTILINE)


def _repo(tmp_path: Path, name: str) -> Path:
    """A throwaway repository holding a copy of the real check script.

    Copied rather than written out here, so the tests follow the script itself
    instead of a paraphrase of it that drifts from it.
    """
    repo = tmp_path / name
    (repo / "scripts").mkdir(parents=True)
    shutil.copy2(CHECK_SH, repo / "scripts" / "check.sh")
    (repo / "notes.md").write_text("a tracked file that is not the script\n")
    env = _scratch_env()

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)

    git("init", "-q", "-b", "main")
    git("add", "-A")
    git("commit", "-q", "-m", "the scratch repo")
    return repo


def _tree_state(
    repo: Path, extra_env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Ask the guard for its snapshot, run from outside the repository.

    The environment starts from the tests' own git environment, which already
    has the redirecting names cleared, so what a test sets here is the only
    redirection in play.
    """
    return subprocess.run(
        ["bash", str(repo / "scripts" / "check.sh"), "--tree-state"],
        capture_output=True,
        text=True,
        cwd=repo.parent,
        env={**_scratch_env(), **(extra_env or {})},
    )


def _state(result: subprocess.CompletedProcess[str]) -> str:
    found = STATE.search(result.stdout)
    assert found, f"no snapshot in stdout: {result.stdout!r} stderr: {result.stderr!r}"
    return found.group(1)


def test_the_guard_snapshots_the_tree_it_is_run_in(tmp_path: Path) -> None:
    """The harness, and the property the rest rests on: the value moves."""
    repo = _repo(tmp_path, "repo")
    result = _tree_state(repo)
    assert result.returncode == 0, result.stderr
    before = _state(result)

    (repo / "new-file").write_text("written after the snapshot\n")
    assert _state(_tree_state(repo)) != before, "an edit left the snapshot where it was"


def test_a_path_the_guard_cannot_read_stops_it(tmp_path: Path) -> None:
    """A skipped read is worse than a failed one: the path leaves both snapshots.

    A path missing from the before and after snapshots compares equal, so a check
    that rewrote a file the guard could not read would still pass.
    """
    if os.geteuid() == 0:
        pytest.skip("root reads a mode-000 file, so the read cannot fail")

    repo = _repo(tmp_path, "repo")
    secret = repo / "secret"
    secret.write_text("first\n")
    secret.chmod(0)
    try:
        result = _tree_state(repo)
    finally:
        secret.chmod(0o600)

    assert result.returncode != 0
    assert "could not be hashed" in result.stderr


@pytest.mark.parametrize("question", ["rev-parse --absolute-git-dir", "rev-parse --show-toplevel"])
def test_a_git_answer_that_fails_is_not_believed(tmp_path: Path, question: str) -> None:
    """The two reads that name the repository answer for their status too.

    Both used `|| true`, which turns "git is broken" into "git agreed": a `git`
    that ran the real `rev-parse`, printed the expected directory and then
    returned 128 was believed, and the guard carried on to its snapshot. An
    exported `git` stands in, answering the named question with the truth and a
    failing status, and every other command honestly.
    """
    repo = _repo(tmp_path, "repo")
    result = _tree_state(
        repo,
        {
            "BASH_FUNC_git%%": (
                "() {\n"
                '  command git "$@"\n'
                "  local rc=$?\n"
                f'  if [ "${{1:-}} ${{2:-}}" = "{question}" ]; then return 128; fi\n'
                "  return $rc\n"
                "}"
            )
        },
    )

    assert result.returncode != 0, result.stdout
    assert "could not name" in result.stderr, result.stderr


@pytest.mark.parametrize("command", ["ls-files -z", "status --porcelain", "ls-files --stage"])
def test_a_git_read_that_fails_stops_the_guard(tmp_path: Path, command: str) -> None:
    """Each read the snapshot is assembled from answers for its own failure.

    The path list came from a process substitution, which discards the exit
    status of what it runs. A `git ls-files` that failed therefore left the list
    empty, the two reads after it succeeded on nothing, and the snapshot stopped
    moving: measured, a tracked file going from mode 644 to mode 600 — a change
    the mode line is the only home for — left the state identical. The identity
    checks above let the injected `git` through, because those ask `rev-parse`.
    """
    repo = _repo(tmp_path, "repo")
    asked = f'"{command}"'
    result = _tree_state(
        repo,
        {
            "BASH_FUNC_git%%": (
                "() {\n"
                f'  if [ "${{1:-}} ${{2:-}}" = {asked} ]; then\n'
                '    echo "fatal: injected failure" >&2\n'
                "    return 128\n"
                "  fi\n"
                '  command git "$@"\n'
                "}"
            )
        },
    )

    assert result.returncode != 0, result.stdout
    assert "could not" in result.stderr, result.stderr


def test_a_caller_cannot_point_the_guard_at_another_repository(tmp_path: Path) -> None:
    """`GIT_DIR` and `GIT_WORK_TREE` are what an inherited environment gives it.

    Under both, the snapshot is the hash of nothing at all, and the guard passes
    for any change to this tree.
    """
    here = _repo(tmp_path, "here")
    (here / "here-only").write_text("one\n")
    elsewhere = _repo(tmp_path, "elsewhere")
    (elsewhere / "there-only").write_text("two\n")

    clean = _state(_tree_state(here))
    assert clean != _state(_tree_state(elsewhere)), "the two scratch trees are not different"

    redirected = _tree_state(
        here, {"GIT_DIR": str(elsewhere / ".git"), "GIT_WORK_TREE": str(elsewhere)}
    )
    assert redirected.returncode == 0, redirected.stderr
    assert _state(redirected) == clean


def test_a_caller_cannot_hide_a_path_with_injected_config(tmp_path: Path) -> None:
    """`GIT_CONFIG_PARAMETERS` outranks every config file, and can set an ignore.

    `core.excludesFile` from the environment takes an untracked path out of
    `--exclude-standard`, so the path leaves both snapshots and an edit to it
    would compare equal.
    """
    repo = _repo(tmp_path, "repo")
    (repo / "probe").write_text("content\n")
    ignore = tmp_path / "ignore"
    ignore.write_text("probe\n")
    clean = _state(_tree_state(repo))

    hidden = _tree_state(
        repo,
        {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.excludesFile",
            "GIT_CONFIG_VALUE_0": str(ignore),
        },
    )
    assert hidden.returncode == 0, hidden.stderr
    assert _state(hidden) == clean


def test_a_caller_cannot_answer_for_git(tmp_path: Path) -> None:
    """The drop list is not the whole defence, and this is what the rest is for.

    A shell function exported as `git` answers every command the guard runs, and
    no list of variable names covers it. So the guard asks git which repository
    it is reading, and refuses when the answer is some other one.
    """
    repo = _repo(tmp_path, "repo")
    result = _tree_state(repo, {"BASH_FUNC_git%%": "() { echo /elsewhere; }"})

    assert result.returncode != 0
    assert "points git elsewhere" in result.stderr


def test_the_guard_names_the_variables_it_dropped(tmp_path: Path) -> None:
    """The uv names need this test: a snapshot runs no check, so nothing else reaches them.

    `UV_WORKING_DIR` takes `uv run` out of the project altogether and
    `PYTEST_ADDOPTS` selects part of the suite, so both are dropped before a
    check runs.
    """
    repo = _repo(tmp_path, "repo")
    result = _tree_state(
        repo,
        {
            "UV_WORKING_DIR": "/nowhere",
            "UV_PROJECT": "/nowhere",
            "PYTEST_ADDOPTS": "-k nothing",
            "PYTHONPATH": "/nowhere",
        },
    )

    assert result.returncode == 0, result.stderr
    assert "ignoring from the caller's environment" in result.stderr
    for name in ("UV_WORKING_DIR", "UV_PROJECT", "PYTEST_ADDOPTS", "PYTHONPATH"):
        assert name in result.stderr


def test_the_guard_accepts_a_linked_worktree(tmp_path: Path) -> None:
    """A worktree's git directory is outside its checkout, behind a pointer file.

    git writes that pointer as an absolute path, so a guard that joins it to the
    checkout root names a directory nothing created and refuses a legitimate
    tree. `--tree-state` is enough: the refusal happens before any check.
    """
    main = _repo(tmp_path, "main")
    worktree = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(main), "worktree", "add", "-q", str(worktree)],
        check=True,
        capture_output=True,
        env=_scratch_env(),
    )
    assert (worktree / ".git").is_file(), "git now writes something other than a pointer file"

    result = _tree_state(worktree)
    assert result.returncode == 0, result.stderr
    assert _state(result)


def test_the_guard_resolves_a_relative_git_pointer(tmp_path: Path) -> None:
    """git writes a worktree's pointer absolute and a submodule's relative.

    The worktree test covers one form and this covers the other, where the path
    has to be resolved against the checkout rather than used as it stands: a
    guard that joins every pointer to the root names a directory that is not
    there and refuses the tree.
    """
    repo = _repo(tmp_path, "repo")
    moved = tmp_path / "moved-git-dir"
    (repo / ".git").rename(moved)
    (repo / ".git").write_text(f"gitdir: ../{moved.name}\n")

    result = _tree_state(repo)
    assert result.returncode == 0, result.stderr
    assert _state(result)


def test_a_deleted_tracked_file_does_not_stop_the_guard(tmp_path: Path) -> None:
    """An unstaged deletion is where a working tree spends most of its time.

    `git ls-files --cached` lists the path and reading it fails, so a guard that
    treats that as a broken read refuses to run at all until the work is
    finished. The deletion belongs in the snapshot, which the status line
    carries, and putting the file back has to restore the state it had.
    """
    repo = _repo(tmp_path, "repo")
    tracked = repo / "notes.md"
    original, mode = tracked.read_bytes(), tracked.stat().st_mode
    before = _state(_tree_state(repo))

    tracked.unlink()
    deleted = _tree_state(repo)
    assert deleted.returncode == 0, deleted.stderr
    assert _state(deleted) != before, "the deletion did not move the snapshot"

    tracked.write_bytes(original)
    tracked.chmod(mode)
    assert _state(_tree_state(repo)) == before


def test_the_guard_records_where_a_symlink_points(tmp_path: Path) -> None:
    """Where a link points is the only place two of its changes show up.

    The content hash follows a link, so a link repointed at a file with the same
    contents hashes the same. And a broken link fails a content read outright, so
    `-e` alone would drop it from the mode line with it: without the `|| -L` in
    `present_paths`, repointing one broken link at another would leave the
    snapshot where it was. Both retargets below move it, and putting the links
    back restores the state exactly.
    """
    repo = _repo(tmp_path, "repo")
    (repo / "real-a").write_text("identical\n")
    (repo / "real-b").write_text("identical\n")
    (repo / "link").symlink_to("real-a")
    (repo / "broken").symlink_to("nowhere")

    before = _state(_tree_state(repo))

    (repo / "link").unlink()
    (repo / "link").symlink_to("real-b")
    assert _state(_tree_state(repo)) != before, "a link pointing at equal contents moved nothing"

    # Put the first link back before testing the second, or the state the
    # broken-link assertion compares to carries the earlier retarget with it and
    # the assertion would hold however the broken link is treated.
    (repo / "link").unlink()
    (repo / "link").symlink_to("real-a")

    (repo / "broken").unlink()
    (repo / "broken").symlink_to("nowhere-else")
    assert _state(_tree_state(repo)) != before, "a broken link repointed moved nothing"

    (repo / "broken").unlink()
    (repo / "broken").symlink_to("nowhere")
    assert _state(_tree_state(repo)) == before, "putting the links back did not restore the state"


def test_a_caller_cannot_hide_a_path_with_a_config_file(tmp_path: Path) -> None:
    """`GIT_CONFIG_GLOBAL` swaps the file git reads for its configuration.

    A setting there — `core.excludesFile` — takes an untracked path out of
    `--exclude-standard`, so the path leaves the snapshot's every line and an
    edit to it compares equal. The injected file names an ignore, so the run
    that ignores it proves the file is not being read.
    """
    repo = _repo(tmp_path, "repo")
    ignore = tmp_path / "ignore"
    ignore.write_text("probe\n")
    injected = tmp_path / "injected.gitconfig"
    injected.write_text(f"[core]\n\texcludesFile = {ignore}\n")

    without_probe = _state(_tree_state(repo))
    (repo / "probe").write_text("content\n")
    with_probe = _state(_tree_state(repo))
    assert with_probe != without_probe, "the new path never entered the snapshot"

    hidden = _tree_state(repo, {"GIT_CONFIG_GLOBAL": str(injected)})
    assert hidden.returncode == 0, hidden.stderr
    assert _state(hidden) == with_probe


DROPPED_FROM_THE_CHECKS = (
    "UV_WORKING_DIR",
    "UV_PROJECT",
    "UV_PROJECT_ENVIRONMENT",
    "UV_CONFIG_FILE",
    "UV_ENV_FILE",
    "PYTEST_ADDOPTS",
    "PYTEST_PLUGINS",
    "PYTHONPATH",
)


def test_the_checks_run_without_the_callers_environment(tmp_path: Path) -> None:
    """The checks' half of the list, on the path that runs checks rather than a snapshot.

    A stub `uv` stands in for the checks, reads its own environment and fails if
    any of these names is still in it, so an `unset` removed from the loop shows
    up here as a failing check. Nothing else reaches them: `--tree-state` runs no
    check at all. The git names are covered by the tests above, and are left out
    here so this one fails for its own reason.

    The stub also refuses a call without `--no-env-file`, which is the half of
    this a name cannot carry: `UV_ENV_FILE` names a file uv loads into the child,
    and a `pyproject.toml` or `uv.toml` can name one too, where dropping the
    variable reaches nothing. Measured on the script before that flag: a file
    setting `PYTEST_ADDOPTS=-k test_check_script` selected 17 tests of the
    suite, deselected 107, and the run still printed "All checks passed."
    """
    repo = _repo(tmp_path, "repo")
    stub_dir = tmp_path / "stub"
    stub_dir.mkdir()
    stub = stub_dir / "uv"
    stub.write_text(
        f"""#!/usr/bin/env bash
# Stands in for uv. The checks' only job in this test is to read the environment
# and to look at how it was called.
case " $* " in
  *" --no-env-file "*) ;;
  *) echo >&2 "uv was called without --no-env-file: $*"; exit 4 ;;
esac
for name in {" ".join(DROPPED_FROM_THE_CHECKS)}; do
  if [ -n "${{!name:-}}" ]; then
    echo >&2 "leaked into the checks: $name"
    exit 3
  fi
done
exit 0
"""
    )
    stub.chmod(0o755)

    result = subprocess.run(
        ["bash", str(repo / "scripts" / "check.sh")],
        capture_output=True,
        text=True,
        cwd=repo.parent,
        env={
            **_scratch_env(),
            "PATH": f"{stub_dir}:{os.environ['PATH']}",
            **dict.fromkeys(DROPPED_FROM_THE_CHECKS, "/nowhere"),
        },
    )

    assert "leaked" not in result.stderr, result.stderr
    assert "without --no-env-file" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stdout + result.stderr
    assert "All checks passed." in result.stdout
