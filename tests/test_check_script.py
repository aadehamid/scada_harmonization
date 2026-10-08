"""The working-tree guard in scripts/check.sh.

The guard is what stops a check from passing by editing the tree it checks, so
its own failure modes need proving. Each test below fails when the line that
answers it is removed from the script — all but the one that pins ty's own
precedence between an explicit flag and an environment variable, which fails if
the tool ever reverses it:

* a path the guard could not read was skipped instead of stopping the snapshot,
  so a file at mode 000 could be rewritten under it and the state never moved;
* the guard inherited the caller's environment, so `GIT_DIR` with `GIT_WORK_TREE`
  pointed it at another repository, where its snapshot collapsed to the hash of
  the empty string, while the checks still ran here;
* a git read that failed dropped out of the snapshot instead of stopping it, so
  under a failing `ls-files` the contents and mode lines went missing and a mode
  change moved the state not at all;
* the two reads that name the repository let their own failure through, so a
  `git` that answered correctly and then returned 128 was believed;
* the type checker could be pointed at a configuration that excludes every path,
  so `ty check` reported that it had found no files and the gate passed having
  read nothing;
* the checks inherited the caller's environment, so a `UV_WORKING_DIR`, a
  `PYTEST_ADDOPTS` or a `TY_CONFIG_FILE` in the shell decided what they ran and
  what they read.

The script is copied into a throwaway repository rather than run in this one: it
runs uv, ruff and pytest, which a test cannot start from inside the suite.
`--tree-state` asks the guard for its snapshot and stops before any check. The
one exception runs the real ty on a throwaway project of its own, because what it
asserts is ty's behaviour and no copy of the script can carry that.

The guard builds the environment its checks run in, and `PATH` is the one thing
it passes through as the caller had it. So a caller's own `git` or `uv` reaches
it as a stub earlier on `PATH`, and everything else arrives through the `env=`
argument: an exported shell function cannot reach the guard at all, which is the
change these tests were rewritten for.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.test_facts import _scratch_env

REPO = Path(__file__).resolve().parent.parent
CHECK_SH = REPO / "scripts" / "check.sh"
STATE = re.compile(r"^tree_state: ([0-9a-f]{64})$", re.MULTILINE)


def _bash() -> str:
    """The absolute path to bash, since a test may hand the guard its own `PATH`.

    The guard is run by its path rather than by name for the same reason: a test
    that sets `PATH` to a stub directory, or to nothing, has not stopped this
    process from finding its own shell.
    """
    found = shutil.which("bash")
    assert found, "these tests run the guard with bash"
    return found


BASH = _bash()

# What the guard promises its checks can see, and nothing else. The four after
# the marker are bash's own, set in the environment of every command it runs.
# What the guard promises its checks can see, and nothing else. The four after
# it are bash's own, set in the environment of every command it runs.
CHECK_ENV_ALLOWED = (
    "PATH",
    "HOME",
    "TMPDIR",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
)
BASH_OWN_NAMES = ("PWD", "SHLVL", "OLDPWD", "_")

# A caller's environment, as the tests hand it over: every name the guard used to
# drop, and one that no list ever held. None of them may reach the checks.
HOSTILE_CALLER_ENV = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_NAMESPACE",
    "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_COUNT",
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_SYSTEM",
    "PYTEST_ADDOPTS",
    "PYTEST_PLUGINS",
    "PYTHONPATH",
    "TY_CONFIG_FILE",
    "UV_WORKING_DIR",
    "UV_PROJECT",
    "UV_PROJECT_ENVIRONMENT",
    "UV_CONFIG_FILE",
    "UV_ENV_FILE",
    "A_VARIABLE_NOBODY_LISTED",
)


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

    What is passed in `env` is a caller's environment, and the guard rebuilds it
    before doing anything: only `PATH`, `HOME`, `TMPDIR` and the locale survive.
    `HOME` is one of those and git reads the user's configuration under it, so it
    is pointed at an empty directory. Without that, the machine's own git
    configuration would decide what the scratch snapshots hold.
    """
    home = repo.parent / "home"
    home.mkdir(exist_ok=True)
    return subprocess.run(
        [BASH, str(repo / "scripts" / "check.sh"), "--tree-state"],
        capture_output=True,
        text=True,
        cwd=repo.parent,
        env={**_scratch_env(), "HOME": str(home), **(extra_env or {})},
    )


def _state(result: subprocess.CompletedProcess[str]) -> str:
    found = STATE.search(result.stdout)
    assert found, f"no snapshot in stdout: {result.stdout!r} stderr: {result.stderr!r}"
    return found.group(1)


def _stub(tmp_path: Path, name: str, body: str) -> Path:
    """A directory holding an executable `name`, for the front of `PATH`."""
    stub_dir = tmp_path / f"stub-{name}"
    stub_dir.mkdir(exist_ok=True)
    stub = stub_dir / name
    stub.write_text(f"#!/usr/bin/env bash\n{body}")
    stub.chmod(0o755)
    return stub_dir


def _git_stub(tmp_path: Path, when: str, then: str) -> Path:
    """A `git` earlier on `PATH` than the real one.

    `when` is matched against the first two arguments, and an empty `when`
    matches every call. Where it matches, `then` runs, with `$real` naming the
    real git so a stub can answer honestly and then fail, or answer something
    else entirely. Everywhere else the real git runs.
    """
    real = shutil.which("git")
    assert real, "these tests need git"
    guard = "true" if not when else f'[ "${{1:-}} ${{2:-}}" = "{when}" ]'
    return _stub(
        tmp_path, "git", f'real="{real}"\nif {guard}; then\n  {then}\nfi\nexec "$real" "$@"\n'
    )


def _path_env(stub_dir: Path) -> dict[str, str]:
    """A caller's environment with a stub directory in front on `PATH`."""
    return {"PATH": f"{stub_dir}:{_scratch_env()['PATH']}"}


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
    returned 128 was believed, and the guard carried on to its snapshot. A stub
    on `PATH` stands in for that `git`, answering the named question with the
    truth and a failing status, and every other command honestly.
    """
    repo = _repo(tmp_path, "repo")
    stub = _git_stub(tmp_path, question, '"$real" "$@"\n  exit 128')
    result = _tree_state(repo, _path_env(stub))

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
    checks above let the stub through, because those ask `rev-parse`.
    """
    repo = _repo(tmp_path, "repo")
    stub = _git_stub(tmp_path, command, 'echo "fatal: injected failure" >&2\n  exit 128')
    result = _tree_state(repo, _path_env(stub))

    assert result.returncode != 0, result.stdout
    assert "could not" in result.stderr, result.stderr


def test_a_caller_cannot_point_the_guard_at_another_repository(tmp_path: Path) -> None:
    """`GIT_DIR` and `GIT_WORK_TREE` are what an inherited environment gives it.

    Under both, the snapshot is the hash of nothing at all, and the guard passes
    for any change to this tree. The guard builds its own environment now, so the
    two arrive at the script and stop there; the assertion is the same one it
    always was, and it fails if the rebuild is removed.
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
    """Rebuilding the environment is not the whole defence, and this is the rest.

    `PATH` is passed on as the caller had it, because that is how the tools are
    found, so a `git` of theirs can answer every command the guard runs, and no
    amount of rebuilding the environment covers that. So the guard asks git which
    repository it is reading, and refuses when the answer is some other one.
    """
    repo = _repo(tmp_path, "repo")
    stub = _git_stub(tmp_path, "", "echo /elsewhere\n  exit 0")
    result = _tree_state(repo, _path_env(stub))

    assert result.returncode != 0, result.stdout
    assert "points git elsewhere" in result.stderr, result.stderr


def test_a_variable_claiming_the_environment_is_built_is_not_believed(tmp_path: Path) -> None:
    """The rebuild is this script's decision, never the caller's account of it.

    A check that starts a nested run of this script hands it an environment the
    guard itself built, so a marker naming that state was in the environment the
    next guard started with, and it skipped the rebuild — letting a caller's
    `GIT_DIR` through. Measured, under `scripts/check.sh`: five of the guard's own
    tests failed there and passed when the file was run on its own. The marker is
    an argument now, and this is the test that says so.
    """
    here = _repo(tmp_path, "here")
    (here / "here-only").write_text("one\n")
    elsewhere = _repo(tmp_path, "elsewhere")
    (elsewhere / "there-only").write_text("two\n")
    clean = _state(_tree_state(here))

    lied_to = _tree_state(
        here,
        {
            "SCADA_CHECK_FIXED_ENV": "1",
            "GIT_DIR": str(elsewhere / ".git"),
            "GIT_WORK_TREE": str(elsewhere),
        },
    )
    assert lied_to.returncode == 0, lied_to.stderr
    assert _state(lied_to) == clean


def test_the_guard_refuses_a_shell_with_no_path(tmp_path: Path) -> None:
    """A shell with no `PATH` cannot run the tools, and is told so.

    Without the check the first thing to fail is the guard's own re-exec: bash
    cannot find `env`, and the message names a line of the script instead of what
    is wrong. Either way the run refuses, so what is asserted is which refusal.
    """
    repo = _repo(tmp_path, "repo")
    result = subprocess.run(
        [BASH, str(repo / "scripts" / "check.sh"), "--tree-state"],
        capture_output=True,
        text=True,
        cwd=repo.parent,
        env={**_scratch_env(), "PATH": ""},
    )

    assert result.returncode != 0, result.stdout
    assert "PATH is empty" in result.stderr, result.stderr


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


def test_the_checks_run_without_the_callers_environment(tmp_path: Path) -> None:
    """The checks' half, on the path that runs checks rather than a snapshot.

    A stub `uv` stands in for the checks and reads its own environment. It fails
    if any name the caller set is still there — the twenty the old list held, and
    one that no list ever held — and it fails on any name at all beyond the
    allow-list, which is what "the environment is built here" means. It also
    fails if `PATH` or `HOME` is missing, since dropping those would break the
    checks rather than protect them.

    The stub refuses a call without `--no-env-file` as well, which rebuilding the
    environment does not cover: a `pyproject.toml` or a `uv.toml` can name an
    environment file, and nothing here takes that away. The type check gets the
    same treatment for the same reason: it has to name its configuration on the
    command line, because an explicit `--config-file` outranks the variable.
    """
    repo = _repo(tmp_path, "repo")
    allowed = " ".join(CHECK_ENV_ALLOWED + BASH_OWN_NAMES)
    stub_dir = _stub(
        tmp_path,
        "uv",
        f"""# Stands in for uv. The checks' only job here is to read the environment
# they were given and to look at how they were called.
allowed=" {allowed} "
case " $* " in
  *" --no-env-file "*) ;;
  *) echo >&2 "uv was called without --no-env-file: $*"; exit 4 ;;
esac
if [[ " $* " == *" ty check "* && " $* " != *" --config-file ty.toml "* ]]; then
  echo >&2 "ty was called without its configuration named: $*"
  exit 5
fi
for name in {" ".join(HOSTILE_CALLER_ENV)}; do
  if [ -n "${{!name:-}}" ]; then
    echo >&2 "leaked into the checks: $name"
    exit 3
  fi
done
for name in PATH HOME; do
  if [ -z "${{!name:-}}" ]; then
    echo >&2 "the guard did not pass on $name"
    exit 6
  fi
done
for name in $(compgen -e); do
  case "$allowed" in
    *" $name "*) ;;
    *) echo >&2 "in the checks' environment, and not on the allow-list: $name"; exit 7 ;;
  esac
done
exit 0
""",
    )

    result = subprocess.run(
        [BASH, str(repo / "scripts" / "check.sh")],
        capture_output=True,
        text=True,
        cwd=repo.parent,
        env={
            **_scratch_env(),
            **_path_env(stub_dir),
            **dict.fromkeys(HOSTILE_CALLER_ENV, "/nowhere"),
        },
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "All checks passed." in result.stdout


def test_a_check_that_edits_the_tree_is_refused(tmp_path: Path) -> None:
    """The comparison the guard exists for, on the path that runs the checks.

    Every other test in this file stops at `--tree-state`, which returns before
    a check runs. This one lets a stub `uv` write to a tracked file, and the run
    has to refuse: a check that edits what it is checking is how a gate passes
    without the change being there.
    """
    repo = _repo(tmp_path, "repo")
    stub_dir = _stub(tmp_path, "uv", 'echo "edited" >> notes.md\nexit 0\n')

    result = subprocess.run(
        [BASH, str(repo / "scripts" / "check.sh")],
        capture_output=True,
        text=True,
        cwd=repo.parent,
        env={**_scratch_env(), **_path_env(stub_dir)},
    )

    assert result.returncode != 0, result.stdout
    assert "the checks changed the working tree" in result.stderr, result.stderr


def test_a_named_config_outranks_the_type_check_variable(tmp_path: Path) -> None:
    """The flag the script passes, against the variable, on the real ty.

    That an explicit `--config-file` outranks `TY_CONFIG_FILE` is ty's own
    behaviour, so a stub cannot settle it and the installed ty runs here. A
    project holding a type error is checked twice under the variable, once with
    the configuration named on the command line and once with ty left to the
    variable: the first reports the error, and the second reports having found no
    files at all — which is the fail-open the flag exists to close.
    """
    project = tmp_path / "checked"
    project.mkdir()
    (project / "pyproject.toml").write_text('[project]\nname = "scratch"\nversion = "0"\n')
    (project / "probe.py").write_text('x: int = "not an int"\n')
    (project / "ty.toml").write_text('[src]\ninclude = ["probe.py"]\n')
    excluding = tmp_path / "exclude-everything.toml"
    excluding.write_text('[src]\nexclude = ["**"]\n')

    ty = Path(sys.executable).parent / "ty"
    assert ty.exists(), f"ty is not installed beside {sys.executable}"

    def check(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(ty), "check", *args],
            capture_output=True,
            text=True,
            cwd=project,
            env={**os.environ, "TY_CONFIG_FILE": str(excluding)},
        )

    pinned = check("--config-file", "ty.toml")
    assert pinned.returncode != 0, pinned.stdout + pinned.stderr
    assert "probe.py" in pinned.stdout + pinned.stderr, "the planted error was not reported"

    left_to_the_variable = check()
    assert left_to_the_variable.returncode == 0, (
        left_to_the_variable.stdout + left_to_the_variable.stderr
    )
    assert "No python files found" in left_to_the_variable.stdout + left_to_the_variable.stderr
