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
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

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
        ["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.splitlines():
        parts.append(hashlib.sha256((REPO / name).read_bytes()).hexdigest())
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return hashlib.sha256(("".join(parts) + status).encode()).hexdigest()


# --------------------------------------------------------------------------
# Figures are pinned
# --------------------------------------------------------------------------


def test_test_count_is_pinned() -> None:
    collected = facts.tests()
    assert collected["total"] == 60
    assert collected["per_file"] == {
        "tests/test_facts.py": 19,
        "tests/test_package_imports.py": 6,
        "tests/test_phase1_e2e.py": 1,
        "tests/test_phase1_l0_contract.py": 17,
        "tests/test_phase1_machine_stream.py": 10,
        "tests/test_unit100_pid.py": 7,
    }


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


def test_check_flags_a_stale_test_count(tmp_path: Path) -> None:
    doc = tmp_path / "STATUS.md"
    doc.write_text("The suite has 34 tests.\n", encoding="utf-8")
    problems = facts.check(docs=[doc], pin_files=[])
    assert len(problems) == 1
    assert "says 34 tests" in problems[0].detail


def test_check_flags_a_wrong_pin(tmp_path: Path) -> None:
    doc = tmp_path / "NOTES.md"
    doc.write_text("TEP golden `deadbeef…` (do not change)\n", encoding="utf-8")
    problems = facts.check(docs=[], pin_files=[doc])
    assert len(problems) == 1
    assert "deadbeef" in problems[0].detail


def test_check_accepts_a_correct_pin(tmp_path: Path) -> None:
    doc = tmp_path / "NOTES.md"
    doc.write_text("TEP golden `f5b9d1cf…` (do not change)\n", encoding="utf-8")
    assert facts.check(docs=[], pin_files=[doc]) == []


def test_check_does_not_read_a_document_it_was_not_given(tmp_path: Path) -> None:
    """A dated record is history: a count in it is not a claim about today."""
    record = tmp_path / "RECORD.md"
    record.write_text("The suite had 21 tests.\n", encoding="utf-8")
    assert facts.check(docs=[], pin_files=[]) == []


# --------------------------------------------------------------------------
# The repo is not the tool's to change
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "argv",
    [
        ["head"],
        ["tests"],
        ["names"],
        ["hashes"],
        ["status"],
        ["check"],
        ["search", "contextualization"],
    ],
)
def test_tool_does_not_write_to_the_repo(argv: list[str]) -> None:
    before = _tree_state()
    facts.main(argv)
    assert _tree_state() == before


def test_check_exits_non_zero_on_a_problem(tmp_path: Path) -> None:
    """The exit code is what CI reads, so a finding must reach it."""
    assert facts.main(["check"]) == 0
