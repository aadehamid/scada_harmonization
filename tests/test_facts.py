"""Tests for scripts/facts.py — the repo's figures and searches.

Three kinds of test, per the guardrail that a check which has never failed may
pass vacuously:

* figures are pinned, so a change to the suite or the schedule is noticed;
* the input is broken on purpose (a phrase wrapped across lines, a stale count,
  a wrong pin) and the same answer is expected;
* the tool is shown not to write to the repo.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# The published figure. One place, so adding a test here is a one-line change
# rather than a hunt through the assertions. `scripts/facts.py tests` reports
# the same number, and `scripts/facts.py check` fails when the docs disagree.
EXPECTED_TESTS = 101

_spec = importlib.util.spec_from_file_location("facts", REPO / "scripts" / "facts.py")
assert _spec is not None and _spec.loader is not None
facts = importlib.util.module_from_spec(_spec)
# Register before executing: dataclasses look their own module up in
# sys.modules while the class body is being built.
sys.modules["facts"] = facts
_spec.loader.exec_module(facts)


def _tree_state() -> str:
    """Content hash of every tracked file, plus untracked presence."""
    parts: list[str] = []
    for name in subprocess.run(
        ["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True, env=facts._env()
    ).stdout.splitlines():
        parts.append(hashlib.sha256((REPO / name).read_bytes()).hexdigest())
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
        env=facts._env(),
    ).stdout
    return hashlib.sha256(("".join(parts) + status).encode()).hexdigest()


# --------------------------------------------------------------------------
# Figures are pinned
# --------------------------------------------------------------------------


def test_test_count_is_pinned() -> None:
    collected = facts.tests()
    assert collected["total"] == EXPECTED_TESTS
    # The breakdown is not pinned file by file: adding a test to an existing
    # file would then need this line edited too, for no gain. What matters is
    # that every collected file is under tests/ and the parts sum to the total
    # pytest reported.
    per_file = collected["per_file"]
    assert per_file, "no test files reported"
    assert all(name.startswith("tests/") for name in per_file)
    assert sum(per_file.values()) == EXPECTED_TESTS


def _scratch_repo(tmp_path: Path) -> tuple[Path, str]:
    """A repository on `feature`, whose `origin/main` is one commit behind it.

    Built from scratch so the test does not depend on this clone's refs: PR CI
    checks out a merge ref and may not have `origin/main` at all. Returns the
    path and the commit `origin/main` names.

    The environment is `facts._env()`, which drops the variables that tell git
    which repository to use. Inherited, `GIT_DIR` outranks `cwd`, so these
    commands would commit to, move `origin/main` in, and branch *that*
    repository instead, and this directory would never become a repository at
    all — while `test_scratch_repo_ignores_a_redirected_environment` still had to
    be the one to notice.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {
        **facts._env(),
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }

    def git(*args: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)

    git("init", "-q", "-b", "main")
    git("commit", "-q", "--allow-empty", "-m", "on main")
    main_sha = (
        subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, env=env
        )
        .stdout.decode()
        .strip()
    )
    git("update-ref", "refs/remotes/origin/main", main_sha)
    git("checkout", "-q", "-b", "feature")
    git("commit", "-q", "--allow-empty", "-m", "on the branch")
    return repo, main_sha


def test_main_reports_main_not_the_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """On a branch these are different commits, and the status needs main.

    `head` answers "what am I on"; pointing a reader at it from a status
    section hands them the feature branch's commit as main's.
    """
    repo, main_sha = _scratch_repo(tmp_path)

    monkeypatch.setattr(facts, "REPO", repo)
    result = facts.main_branch()
    assert result["main"] == main_sha, "it answers for main, not for the checkout"
    assert result["checked_out"] == "feature"
    assert result["checkout_is_main"] == "no"


def test_scratch_repo_ignores_a_redirected_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`GIT_DIR` in the caller's shell must not move the test's work elsewhere.

    Without `facts._env()` the helper's `init`, `commit`, `update-ref` and
    `checkout -b` all ran against the repository `GIT_DIR` names -- adding a
    commit, moving its `origin/main` onto it, and leaving it on `feature` -- and
    the scratch directory stayed empty. The test above then passed anyway,
    against the other repository's refs, which is what makes this worth pinning
    separately: it passed for the wrong reason.

    `scripts/check.sh` cannot see this. Its tree hash covers file contents,
    `git status --porcelain` and `git ls-files --stage`, none of which record
    the current branch or `origin/main`.
    """
    other = tmp_path / "other"
    other.mkdir()
    clean = facts._env()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=other, check=True, env=clean)
    subprocess.run(
        ["git", "commit", "-q", "--allow-empty", "-m", "other"], cwd=other, check=True, env=clean
    )
    head = (
        subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=other, check=True, capture_output=True, env=clean
        )
        .stdout.decode()
        .strip()
    )
    subprocess.run(
        ["git", "update-ref", "refs/remotes/origin/main", head], cwd=other, check=True, env=clean
    )

    # What a wrapper, direnv or `git --git-dir` leaves behind. `cwd` does not
    # override it, so every git command the helper runs would use this.
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    repo, _ = _scratch_repo(tmp_path)

    def ask(*args: str) -> str:
        return (
            subprocess.run(["git", *args], cwd=other, check=True, capture_output=True, env=clean)
            .stdout.decode()
            .strip()
        )

    assert (repo / ".git").exists(), "the scratch directory must become its own repository"
    assert ask("rev-parse", "HEAD") == head, "the other repository's HEAD must not move"
    assert ask("rev-parse", "refs/remotes/origin/main") == head, (
        "its origin/main must not be moved onto a commit the test made"
    )
    assert ask("rev-parse", "--abbrev-ref", "HEAD") == "main", (
        "it must not be left on the test's feature branch"
    )
    assert ask("rev-list", "--count", "--all") == "1", "no commit may be added to it"


def test_uv_working_dir_cannot_move_which_tests_are_collected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A `UV_WORKING_DIR` in the caller's shell must not be collected instead.

    uv takes the directory to run in from `UV_WORKING_DIR`, and it outranks the
    `cwd` the tool passes, so `tests()` collected the other project's suite. That
    figure is not an error: it comes back with a total, a per-file breakdown, and
    a zero exit status, and lands in whatever document quotes it.
    """
    other = tmp_path / "other"
    (other / "tests").mkdir(parents=True)
    (other / "pyproject.toml").write_text(
        '[project]\nname = "other"\nversion = "0"\nrequires-python = ">=3.13"\n',
        encoding="utf-8",
    )
    (other / "tests" / "test_other.py").write_text("def test_only_one(): pass\n", encoding="utf-8")

    monkeypatch.setenv("UV_WORKING_DIR", str(other))
    monkeypatch.setenv("UV_PROJECT", str(other))

    assert facts.tests()["total"] == EXPECTED_TESTS, "it collects this repository's suite"


def test_a_dotenv_file_cannot_put_a_cleared_redirect_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """uv loads a file into the child's environment, after `_env()` has cleared it.

    `UV_ENV_FILE` names a dotenv file uv reads, and `.env` beside the project is
    read too, so a file can set `PYTEST_ADDOPTS` again once this tool has removed
    it from the environment it passes. A `--rootdir` from there collects the
    other project's suite, and the flags that name the directory do not stop it:
    pytest is running in `REPO`, asked to read its tests from somewhere else.
    """
    other = tmp_path / "other"
    (other / "tests").mkdir(parents=True)
    (other / "pyproject.toml").write_text(
        '[project]\nname = "other"\nversion = "0"\nrequires-python = ">=3.13"\n',
        encoding="utf-8",
    )
    (other / "tests" / "test_other.py").write_text("def test_only_one(): pass\n", encoding="utf-8")
    dotenv = tmp_path / "redirect.env"
    dotenv.write_text(f'PYTEST_ADDOPTS="--rootdir={other} {other}/tests"\n', encoding="utf-8")

    monkeypatch.setenv("UV_ENV_FILE", str(dotenv))

    assert facts.tests()["total"] == EXPECTED_TESTS, "it collects this repository's suite"


def test_an_inherited_plugin_cannot_add_to_the_collection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A plugin pytest loads can append arguments after the flags have been read.

    `PYTEST_PLUGINS` names a module pytest imports before it collects, and
    `PYTHONPATH` says where to find it. This hook appends one node id, so the run
    reports a single test — and reports it as `tests/test_facts.py`, this
    repository's own file, because collected names are relative to pytest's
    rootdir. The check on the collected names cannot tell that apart; only not
    loading the plugin can.
    """
    (tmp_path / "collect_one.py").write_text(
        "def pytest_load_initial_conftests(early_config, parser, args):\n"
        '    args.append("tests/test_facts.py::test_test_count_is_pinned")\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    monkeypatch.setenv("PYTEST_PLUGINS", "collect_one")

    assert facts.tests()["total"] == EXPECTED_TESTS, "it collects this repository's suite"


def test_a_collected_test_from_outside_the_repository_is_refused(tmp_path: Path) -> None:
    """The flags being right is an argument; this is the check on the answer.

    Whatever puts pytest somewhere else — a flag dropped from the command line, a
    variable nobody has listed — the names that come back are the evidence. A node
    that is not a file under `REPO` is another project's suite, and no figure may
    be reported from it.
    """
    with pytest.raises(SystemExit, match="not collect this repository's tests"):
        facts._require_collected_here({"tests/test_other.py": 3})

    # A traversal out of the repository is not inside it either, even when the
    # name starts the way the parser requires.
    outside = tmp_path / "outside"
    (outside / "tests").mkdir(parents=True)
    (outside / "tests" / "test_other.py").write_text(
        "def test_only_one(): pass\n", encoding="utf-8"
    )
    escaping = f"tests/{os.path.relpath(outside / 'tests' / 'test_other.py', facts.REPO)}"
    with pytest.raises(SystemExit, match="not collect this repository's tests"):
        facts._require_collected_here({escaping: 1})

    # Nothing collected at all is not an answer either.
    with pytest.raises(SystemExit, match="not collect this repository's tests"):
        facts._require_collected_here({})

    assert facts._require_collected_here({"tests/test_facts.py": 1}) is None


def test_a_linked_worktree_is_this_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A linked worktree keeps its git directory outside the checkout.

    `git worktree add` puts the metadata in `<main>/.git/worktrees/<name>` and
    leaves a `gitdir:` pointer in the checkout, and a submodule does the same
    under `<parent>/.git/modules`. Comparing git's answer against `REPO/.git`
    would refuse both, which fails a correct case, so the check compares against
    what this checkout's own `.git` names.
    """
    main = tmp_path / "main"
    main.mkdir()
    clean = facts._env()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=main, check=True, env=clean)
    subprocess.run(
        ["git", "commit", "-q", "--allow-empty", "-m", "x"], cwd=main, check=True, env=clean
    )
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "worktree", "add", "-q", "--detach", str(linked), "HEAD"],
        cwd=main,
        check=True,
        env=clean,
    )

    monkeypatch.setattr(facts, "REPO", linked)
    facts._require_this_repo()


def test_the_tool_stops_when_a_redirect_it_does_not_know_about_is_in_play(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The env list is a list, so the guarantee has to come from elsewhere.

    `_env()` covers the variables that are known to point git at another
    repository. Anything it misses would be silent: the figures would describe
    that repository and look like ordinary numbers. Here the filter is made to
    pass the environment through, standing in for a variable nobody has written
    down yet, and the tool must refuse rather than report.
    """
    other = tmp_path / "other"
    other.mkdir()
    clean = facts._env()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=other, check=True, env=clean)

    monkeypatch.setattr(facts, "_env", lambda: dict(os.environ))
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))

    with pytest.raises(SystemExit, match="points git elsewhere"):
        facts.main(["head"])


def test_tag_schedule_names_are_pinned() -> None:
    schedule = facts.names()
    assert schedule["rows"] == 59
    assert schedule["unique_names"] == 59
    names = schedule["names"]
    assert len([n for n in names if n.startswith("xmeas_")]) == 41
    assert len([n for n in names if n.startswith("xmv_")]) == 11


def test_pinned_fixture_hashes_are_stable() -> None:
    digests = facts.hashes()
    assert len(digests) == 3
    assert all(len(digest) == 64 for digest in digests.values())
    assert (
        digests["tests/fixtures/datagen/golden_l0_slice.jsonl"]
        == "f5b9d1cfdaf9f298d9cdcbcb926bc3486dfdac1cccff7816b34ac290e6d33516"
    )


# --------------------------------------------------------------------------
# The input is broken on purpose
# --------------------------------------------------------------------------


def test_flatten_joins_a_wrapped_phrase() -> None:
    flat, _ = facts.flatten("the same physical\nevent replayed")
    assert flat == "the same physical event replayed"


def test_flatten_collapses_whitespace_runs() -> None:
    flat, _ = facts.flatten("a\n\n\n   b\t c")
    assert flat == "a b c"


def test_flatten_maps_back_to_the_original_line() -> None:
    flat, line_of = facts.flatten("one\ntwo\nthree")
    assert flat[flat.index("three")] == "t"
    assert line_of[flat.index("three")] == 3


def test_search_finds_a_phrase_split_across_lines() -> None:
    """grep cannot see this one; the phrase starts on one line and ends on the next."""
    pattern = "diagrams describe equipment"
    assert (
        not subprocess.run(
            ["grep", "-rq", pattern, "--include=*.md", "."],
            cwd=REPO,
            check=False,
        ).returncode
        == 0
    )
    hits = facts.search(pattern)
    assert hits, "the tool must find a phrase grep misses"
    assert any(hit.path == "design/PROJECT_CHARTER.md" for hit in hits)


def _check(tmp_path: Path, *, doc: str = "", pin: str = "") -> list[facts.Problem]:
    """Check a document and a pin file alongside a baseline.

    The baseline carries the correct figures, so the vacuity guard stays quiet
    and each test is about the one claim it writes.
    """
    baseline = tmp_path / "BASELINE.md"
    baseline.write_text(
        f"The suite has {EXPECTED_TESTS} tests and a 59-name schedule.\n", encoding="utf-8"
    )
    docs = [baseline]
    pins: list[Path] = []
    if doc:
        subject = tmp_path / "SUBJECT.md"
        subject.write_text(doc, encoding="utf-8")
        docs.append(subject)
    if pin:
        notes = tmp_path / "NOTES.md"
        notes.write_text(pin, encoding="utf-8")
        pins.append(notes)
    return facts.check(docs=docs, pin_files=pins)


STALE = f"says 34 tests; the suite collects {EXPECTED_TESTS}"


def test_check_flags_a_stale_test_count(tmp_path: Path) -> None:
    assert [p.detail for p in _check(tmp_path, doc="The suite has 34 tests.\n")] == [STALE]


def test_check_flags_a_count_wrapped_across_lines(tmp_path: Path) -> None:
    """Scanning line by line is what lets this one through."""
    assert [p.detail for p in _check(tmp_path, doc="The suite has\n34\ntests.\n")] == [STALE]


def test_check_flags_the_passed_wording(tmp_path: Path) -> None:
    assert [p.detail for p in _check(tmp_path, doc="uv run pytest is 34 passed.\n")] == [STALE]


def test_check_accepts_a_correct_count(tmp_path: Path) -> None:
    assert _check(tmp_path, doc=f"uv run pytest is {EXPECTED_TESTS} passed.\n") == []


def test_check_flags_markdown_emphasis(tmp_path: Path) -> None:
    """`**34** tests` is the same claim as `34 tests`."""
    assert [p.detail for p in _check(tmp_path, doc="The suite has **34** tests.\n")] == [STALE]


def test_check_flags_the_plant_data_wording(tmp_path: Path) -> None:
    """`34 plant-data names` states the schedule figure without a hyphen."""
    problems = _check(tmp_path, doc="The tag list has 34 plant-data names.\n")
    assert [p.detail for p in problems] == ["says 34-row/name; the schedule has 59"]


def test_check_accepts_the_plant_data_wording(tmp_path: Path) -> None:
    assert _check(tmp_path, doc="The tag list has 59 plant-data names.\n") == []


def test_check_does_not_let_one_document_mask_another(tmp_path: Path) -> None:
    """A correct baseline must not excuse a stale document beside it."""
    good = tmp_path / "GOOD.md"
    good.write_text(f"The suite has {EXPECTED_TESTS} tests and a 59-name schedule.\n")
    stale = tmp_path / "STALE.md"
    stale.write_text("The suite has 34 tests.\n")
    problems = facts.check(docs=[good, stale], pin_files=[])
    assert [p.detail for p in problems] == [STALE]


def test_check_requires_the_claims_a_document_is_expected_to_carry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A document that stops quoting a figure is a gap, not a pass."""
    empty = tmp_path / "EMPTY.md"
    empty.write_text("Nothing quotable here.\n", encoding="utf-8")
    monkeypatch.setitem(facts.EXPECTED_CLAIMS, str(empty), ("test count", "row count"))
    assert [p.detail for p in facts.check(docs=[empty], pin_files=[])] == [
        "quotes no test count to verify",
        "quotes no row/name count to verify",
    ]


def test_check_flags_a_wrong_pin(tmp_path: Path) -> None:
    problems = _check(tmp_path, pin="TEP golden `deadbeef…` (do not change)\n")
    assert len(problems) == 1
    assert "deadbeef" in problems[0].detail


def test_check_flags_a_pin_whose_suffix_belongs_to_another_fixture(tmp_path: Path) -> None:
    """Both ends must come from one fixture, or a pin can be half-swapped."""
    problems = _check(tmp_path, pin="TEP golden `f5b9d1cf…2159f0` (do not change)\n")
    assert len(problems) == 1
    assert "matches 0 pinned fixtures" in problems[0].detail


def test_check_flags_a_truncated_pin_suffix(tmp_path: Path) -> None:
    problems = _check(tmp_path, pin="TEP golden `f5b9d1cf…000` (do not change)\n")
    assert len(problems) == 1
    assert "matches 0 pinned fixtures" in problems[0].detail


def test_check_flags_an_over_long_pin_suffix(tmp_path: Path) -> None:
    """The suffix must be read whole, not shortened to fit."""
    problems = _check(tmp_path, pin="TEP golden `f5b9d1cf…e6d335160` (do not change)\n")
    assert len(problems) == 1
    assert "matches 0 pinned fixtures" in problems[0].detail


def test_check_flags_a_pin_wrapped_inside_its_code_span(tmp_path: Path) -> None:
    """A pin is one token, so a wrap inside the span is not a space between two."""
    problems = _check(tmp_path, pin="TEP golden `f5b9d1cf…\n00000000` (do not change)\n")
    assert len(problems) == 1
    assert "matches 0 pinned fixtures" in problems[0].detail


def test_check_flags_a_pin_prefix_of_the_wrong_length(tmp_path: Path) -> None:
    problems = _check(tmp_path, pin="TEP `f5b9d1cff…e6d33516`\n")
    assert len(problems) == 1
    assert "not 8 hex digits" in problems[0].detail


def test_check_judges_an_all_letter_digest(tmp_path: Path) -> None:
    """`deadbeef` is all hex letters, so it must still be read as a pin."""
    problems = _check(tmp_path, pin="TEP `deadbeef…`\n")
    assert len(problems) == 1
    assert "deadbeef" in problems[0].detail


@pytest.mark.parametrize(
    "span",
    [
        "f5b9d1cg…e6d33516",  # mistyped prefix digit
        "f5b9d1cf…zzzzzzzz",  # suffix that is not hex
        "f5b9d1cf…e6d33516-g",  # punctuation inside the pin
    ],
)
def test_check_leaves_a_malformed_pin_alone(tmp_path: Path, span: str) -> None:
    """A documented limit: not pin-shaped means not judged.

    Catching these means guessing at intent in prose, and six review rounds
    showed every rule that catches one flags correct documents in another. The
    fixture files themselves are pinned by the test suite, so this check only
    claims that a published pin is a real digest.
    """
    assert _check(tmp_path, pin=f"TEP `{span}`\n") == []


def test_check_accepts_a_correct_pin(tmp_path: Path) -> None:
    assert _check(tmp_path, pin="TEP golden `f5b9d1cf…e6d33516` (do not change)\n") == []


def test_check_accepts_a_prefix_only_pin(tmp_path: Path) -> None:
    """LEARNING_LOG quotes one this way, and a lone prefix is unambiguous."""
    assert _check(tmp_path, pin="machine stream `84b9f088…`\n") == []


@pytest.mark.parametrize(
    "text",
    [
        "Run `docker compose up …` first\n",
        "Run `! docker compose up …` first\n",
        "Then `uv run pytest …`\n",
        "Machines `P-101/…` and `K-201/…`\n",
        "Topic `lagos-chem/<site>/<area>/…`\n",
        "TEP golden `f5b9d1cf…` then deadbeef\n",
    ],
)
def test_check_leaves_ordinary_ellipsis_alone(tmp_path: Path, text: str) -> None:
    """`…` means "and so on" far more often than it means a pin."""
    assert _check(tmp_path, pin=text) == []


def test_section_stops_at_a_subsection(tmp_path: Path) -> None:
    """A dated note filed below a status section is not status."""
    doc = tmp_path / "H.md"
    doc.write_text(
        "## 2. Current status\n\nThe suite has 85 tests.\n\n### This session (2024-01-01)\n\n"
        "The suite had 34 tests.\n",
        encoding="utf-8",
    )
    body, first_line = facts._section(doc, "## 2. Current status")
    assert "85 tests" in body
    assert "34 tests" not in body
    assert first_line == 1, "the heading is the first line of this file"


def test_section_reports_the_file_line_of_its_heading(tmp_path: Path) -> None:
    """A finding must point at a line the reader can go to, not a slice line."""
    doc = tmp_path / "H.md"
    doc.write_text(f"intro\nintro\nintro\n{HEADING}\n\nThe suite has 34 tests.\n")
    body, first_line = facts._section(doc, HEADING)
    assert first_line == 4
    claims = facts._claims(body, facts.TEST_COUNT_PATTERN)
    assert [first_line - 1 + n for n, _ in claims] == [6]


def test_section_stops_at_a_shallower_heading(tmp_path: Path) -> None:
    """Reading a subsection must not run on into the next top-level section."""
    doc = tmp_path / "H.md"
    doc.write_text(
        "## 2. Current status\n\nThe suite has 91 tests.\n\n"
        "### 2.1\n\nA 59-name schedule.\n\n"
        "### This session\n\nThe suite had 34 tests.\n\n"
        "## 3. Next\n\nHistorical: 21 tests.\n",
        encoding="utf-8",
    )
    sub, _ = facts._section(doc, "### 2.1")
    assert "59-name" in sub
    assert "34 tests" not in sub, "the dated note below is history"
    assert "21 tests" not in sub, "the next top-level section is outside"


def test_section_raises_when_the_heading_is_gone(tmp_path: Path) -> None:
    """A renamed heading must be noticed, not silently left unchecked."""
    doc = tmp_path / "H.md"
    doc.write_text("## Something else\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        facts._section(doc, "## 2. Current status")


HEADING = "## 2. Current status"


def test_check_flags_a_stale_count_inside_a_named_section(tmp_path: Path) -> None:
    doc = tmp_path / "H.md"
    doc.write_text(f"{HEADING}\n\nThe suite has 34 tests.\n", encoding="utf-8")
    problems = facts.check(docs=[(doc, HEADING)], pin_files=[])
    assert [p.detail for p in problems] == [STALE]
    assert problems[0].path == f"{doc} {HEADING}"


def test_check_requires_a_readable_test_count_in_a_named_section(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A count the parser cannot read is a gap, not a pass.

    Without this, a figure could be reformatted out of the pattern and the
    section would stop being checked while the gate still reported success.
    """
    doc = tmp_path / "H.md"
    doc.write_text(f"{HEADING}\n\nThe suite has **34**.\n", encoding="utf-8")
    monkeypatch.setitem(facts.EXPECTED_CLAIMS, f"{doc} {HEADING}", ("test count", "row count"))
    details = [p.detail for p in facts.check(docs=[(doc, HEADING)], pin_files=[])]
    assert "quotes no test count to verify" in details
    assert "quotes no row/name count to verify" in details


def test_check_ignores_history_below_a_named_section(tmp_path: Path) -> None:
    doc = tmp_path / "H.md"
    doc.write_text(
        f"{HEADING}\n\nThe suite has {EXPECTED_TESTS} tests.\n\n"
        "### This session\n\nThe suite had 34 tests.\n",
        encoding="utf-8",
    )
    assert facts.check(docs=[(doc, HEADING)], pin_files=[]) == []


def test_check_does_not_read_a_document_it_was_not_given(tmp_path: Path) -> None:
    """A dated record is history: a count in it is not a claim about today."""
    record = tmp_path / "RECORD.md"
    record.write_text("The suite had 21 tests.\n", encoding="utf-8")
    problems = facts.check(docs=[], pin_files=[])
    assert all("RECORD.md" not in problem.path for problem in problems)


# --------------------------------------------------------------------------
# The repo is not the tool's to change
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "argv",
    [
        ["head"],
        ["main"],
        ["tests"],
        ["names"],
        ["hashes"],
        ["status"],
        ["check"],
        ["search", "contextualization"],
    ],
)
def test_tool_does_not_write_to_the_repo(argv: list[str]) -> None:
    """Tracked content and untracked presence are unchanged.

    Ignored caches are outside this guarantee, and the tool says so.
    """
    before = _tree_state()
    try:
        facts.main(argv)
    except SystemExit:
        # `main` exits when this clone has no origin/main; PR CI can be one.
        # The requirement is that nothing is written either way.
        pass
    assert _tree_state() == before


def test_check_exits_zero_on_the_clean_repo() -> None:
    assert facts.main(["check"]) == 0


def test_check_exits_non_zero_on_a_problem(monkeypatch: pytest.MonkeyPatch) -> None:
    """The exit code is what CI reads, so a finding must reach it."""
    monkeypatch.setattr(facts, "check", lambda *a, **k: [facts.Problem("x.md", 1, "boom")])
    assert facts.main(["check"]) == 1
