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

# The published figure. One place, so adding a test here is a one-line change
# rather than a hunt through the assertions. `scripts/facts.py tests` reports
# the same number, and `scripts/facts.py check` fails when the docs disagree.
EXPECTED_TESTS = 85

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
    assert collected["total"] == EXPECTED_TESTS
    # The breakdown is not pinned file by file: adding a test to an existing
    # file would then need this line edited too, for no gain. What matters is
    # that every collected file is under tests/ and the parts sum to the total
    # pytest reported.
    per_file = collected["per_file"]
    assert per_file, "no test files reported"
    assert all(name.startswith("tests/") for name in per_file)
    assert sum(per_file.values()) == EXPECTED_TESTS


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
    facts.main(argv)
    assert _tree_state() == before


def test_check_exits_zero_on_the_clean_repo() -> None:
    assert facts.main(["check"]) == 0


def test_check_exits_non_zero_on_a_problem(monkeypatch: pytest.MonkeyPatch) -> None:
    """The exit code is what CI reads, so a finding must reach it."""
    monkeypatch.setattr(facts, "check", lambda *a, **k: [facts.Problem("x.md", 1, "boom")])
    assert facts.main(["check"]) == 1
