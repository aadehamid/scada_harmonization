#!/usr/bin/env python3
"""The repo's figures and its searches, defined once.

Documents quote numbers: how many tests exist, how many plant-data names the tag
schedule holds, what the fixture hashes are. Every agent that counts them by
hand counts differently, and each difference becomes a wrong figure in a
document. This tool is the single definition of each figure.

It also searches ignoring line breaks. A claim split across two lines is
invisible to `grep`, and that is how a stale claim survives a sweep: the words
are there, the pattern is not.

It does not modify tracked files, and `check` is wired into `scripts/check.sh`
so a quoted figure that contradicts the source fails the build. Collection runs
with pytest's cache provider and bytecode writing off; ignored caches such as
`.pytest_cache` and `__pycache__` are outside that guarantee.

Usage:
    scripts/facts.py head            the branch and commit you are on
    scripts/facts.py main            the tip of main, as this clone last saw it
    scripts/facts.py tests           collected test count, total and per file
    scripts/facts.py names           plant-data names from the tag schedule
    scripts/facts.py hashes          pinned fixture SHA-256 digests
    scripts/facts.py status          every "main is at <sha>" claim, with file:line
    scripts/facts.py search PATTERN  repo-wide, ignoring line breaks
    scripts/facts.py check           fail if a quoted figure contradicts the source

Add --json before the command for machine-readable output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIXTURES = REPO / "tests" / "fixtures" / "datagen"
TAG_SCHEDULE = FIXTURES / "pid" / "tag_schedule.csv"

# Fixtures whose digest is a published pin. A document that quotes one of these
# is making a checkable claim, so `check` verifies it.
PINNED_FIXTURES: tuple[Path, ...] = (
    FIXTURES / "golden_l0_slice.jsonl",
    FIXTURES / "golden_machine_stream_l0_slice.jsonl",
    FIXTURES / "pid" / "LSC-U100-PID-001_revB.pdf",
)

# Documents that describe the repo as it is now, and the section within them
# when only part of the file is a status claim. A dated session note or a phase
# record states what was true when it was written, so a figure in one is
# history, not a claim about today, and `check` does not read it.
#
# HANDOFF.md is mostly dated session notes, so only its current-status section
# is read — but it *is* read, because since the status was consolidated there,
# it is the one document that can go stale in a way the owner would act on.
CURRENT_STATUS_DOCS: tuple[tuple[Path, str | None], ...] = (
    (REPO / "README.md", None),
    (REPO / "AGENTS.md", None),
    (REPO / "tests" / "README.md", None),
    (REPO / "HANDOFF.md", "## 2. Current status"),
    # §2.1 sits below a sub-heading but is still current state, not history: it
    # carries the schedule's name count. Reading only §2 left it unchecked.
    (REPO / "HANDOFF.md", "### 2.1"),
)

# Directories that are not the project's own prose or code.
SKIP_DIRS = frozenset(
    {".git", ".venv", "__pycache__", ".ruff_cache", ".pytest_cache", "node_modules"}
)
SKIP_PREFIXES = ("reference/", "data/")

# Pins are read from code spans, not from prose. Hunting for digest-shaped
# tokens in running text cannot be made correct: every round of review found
# another way for a malformed pin to hide in the words around it, and the
# pattern that catches one case flags correct sentences in another. A code span
# is an explicit boundary the document already draws, so the tool uses it.
#
# A pin is recognised by its strict form — hex, ellipsis, hex — after the
# whitespace inside the span is removed, so a pin wrapped inside its backticks
# is read as one token rather than two.
#
# Known limit, deliberately not closed: something that is not that form is not
# a pin, so a mistyped digit (`f5b9d1cg…`) is not judged at all. Catching
# malformed digests means guessing at intent in prose, which six review rounds
# showed cannot be done without flagging correct documents. What this checks is
# that a published pin is a real fixture digest; the fixture files themselves
# are pinned by the test suite.
CODE_SPAN = re.compile(r"`([^`]*)`")
PIN_TOKEN = re.compile(r"\A([0-9a-f]+)…([0-9a-f]*)\Z")
PIN_PREFIX_LENGTH = 8
# "60 tests" and "60 passed" are both claims about the suite; the second is the
# wording pytest itself prints.
TEST_COUNT_PATTERN = re.compile(r"\b(\d+)\s+(?:tests?|passed)\b")
# "59-row", "59-name" and "59 plant-data names" all state the same figure.
ROW_COUNT_PATTERN = re.compile(r"\b(\d+)(?:-(?:row|name)|\s+plant-data)\b")

# Which figure each current-status document is expected to quote. Named per
# document so a document that quietly drops a claim is a failure rather than a
# silent gap: an aggregate "some document quoted it" rule lets one document
# mask another that has gone stale.
EXPECTED_CLAIMS: dict[str, tuple[str, ...]] = {
    # README no longer quotes the test count: it points at this tool instead,
    # so there is nothing there to go stale.
    "README.md": ("row count",),
    "AGENTS.md": ("test count", "row count"),
    "tests/README.md": ("test count", "row count"),
    # Keyed by the section as well as the file, because the two HANDOFF
    # sections carry different figures. Requiring the wrong one would ask a
    # section for a claim it never made; requiring too little would let a
    # claim vanish from the parser without failing the gate.
    "HANDOFF.md ## 2. Current status": ("test count", "row count"),
    "HANDOFF.md ### 2.1": ("row count",),
}
HEAD_CLAIM_PATTERN = re.compile(r"main[^.\n]{0,20}`([0-9a-f]{7,40})`")


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------


def head() -> dict[str, str]:
    """The branch and commit the working copy is on."""
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    commit = _git("rev-parse", "HEAD")
    return {"branch": branch, "commit": commit, "short": commit[:7]}


def main_branch() -> dict[str, str]:
    """The tip of `main` as this clone last saw it, and where the checkout is.

    `head` answers "what am I on"; this answers "what is on main", which are
    different questions on a branch. It reads `origin/main`, the last fetched
    value, and says so rather than implying a fetch just happened.
    """
    origin = _git("rev-parse", "origin/main")
    return {
        "main": origin,
        "main_short": origin[:7],
        "checked_out": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "checkout_is_main": "yes" if _git("rev-parse", "HEAD") == origin else "no",
    }


def tests() -> dict[str, object]:
    """Collected tests, total and per file, from pytest itself.

    The total is the number pytest reports, not a sum this tool computes: a
    count derived from parsing node lines silently undercounts the moment a
    node does not look the way the parser expects. The per-file breakdown is
    cross-checked against pytest's own figure, so a parse that misses nodes
    fails loudly instead of reporting a smaller number as fact.

    Collection is run with the bytecode and cache providers off, so asking the
    question does not write into the repository.
    """
    result = subprocess.run(
        [
            "uv",
            "run",
            # The directory to run in, and the project to run in, are on the
            # command line because uv otherwise takes them from the environment,
            # where `UV_WORKING_DIR` and `UV_PROJECT` outrank `cwd=REPO` and the
            # command would collect another project's tests.
            "--directory",
            str(REPO),
            "--project",
            str(REPO),
            # `--no-env-file` because uv loads a file named by `UV_ENV_FILE`, or
            # a `.env` beside the project, into the child's environment. A file
            # can put `PYTEST_ADDOPTS` back after `_env()` has cleared it, and a
            # `--rootdir` from there collects another project's tests.
            "--no-env-file",
            "pytest",
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
        env={**_env(), "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode != 0:
        raise SystemExit(f"pytest --collect-only failed:\n{result.stdout}{result.stderr}")

    reported = re.search(r"(\d+)\s+tests? collected", result.stdout)
    if reported is None:
        raise SystemExit(
            "pytest did not report a collected total; refusing to guess one.\n"
            f"{result.stdout[-2000:]}"
        )
    total = int(reported.group(1))

    per_file: Counter[str] = Counter()
    for line in result.stdout.splitlines():
        match = re.match(r"^(tests/\S+?)::", line.strip())
        if match:
            per_file[match.group(1)] += 1

    parsed = sum(per_file.values())
    if parsed != total:
        raise SystemExit(
            f"pytest collected {total} but {parsed} node lines parsed; "
            "the per-file breakdown is incomplete"
        )
    _require_collected_here(per_file)
    return {"total": total, "per_file": dict(sorted(per_file.items()))}


def _require_collected_here(per_file: Mapping[str, int]) -> None:
    """Stop unless every collected test is a file in this repository.

    The command line says which directory and project to collect, and no
    environment variable can overrule an explicit uv flag. That is an argument
    about the flags being right, though, and it fails silently the day one of
    them is dropped or a channel nobody listed gets through. So look at what
    came back: a collected node that is not a file under `REPO` is another
    project's suite, however it got collected.
    """
    elsewhere = sorted(
        name for name in per_file if not (REPO / name).is_file() or not _is_inside_repo(REPO / name)
    )
    if elsewhere or not per_file:
        raise SystemExit(
            "pytest did not collect this repository's tests"
            + (f"; these are not files here: {', '.join(elsewhere)}" if elsewhere else "")
            + ". Something in this shell points the collection elsewhere."
        )


def names() -> dict[str, object]:
    """The plant-data names the tag schedule issues.

    The schedule is the join between the Unit 100 drawing and the L0 names, so
    its rows are the population every "59-name" claim is about.
    """
    lines = TAG_SCHEDULE.read_text(encoding="utf-8").splitlines()
    header, *rows = [line for line in lines if line.strip()]
    columns = header.split(",")
    index = columns.index("plant_data_name")
    plant_names = [row.split(",")[index] for row in rows]
    return {
        "source": str(TAG_SCHEDULE.relative_to(REPO)),
        "rows": len(rows),
        "unique_names": len(set(plant_names)),
        "names": plant_names,
    }


def hashes() -> dict[str, str]:
    """SHA-256 of each pinned fixture, keyed by its repo-relative path."""
    return {
        str(path.relative_to(REPO)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in PINNED_FIXTURES
    }


# --------------------------------------------------------------------------
# Search
# --------------------------------------------------------------------------


def flatten(text: str, *, markdown: bool = False) -> tuple[str, list[int]]:
    """Collapse whitespace runs to single spaces, keeping a map back to lines.

    Returns the flattened text and, for each character in it, the 1-based line
    of the original file it came from.

    With ``markdown``, emphasis and code marks are treated as whitespace too,
    so ``**34** tests`` reads as ``34 tests``. Substitutions are one character
    for one, which keeps every offset, and so the line map, valid.
    """
    marks = "*_`" if markdown else ""
    chars: list[str] = []
    line_of: list[int] = []
    line = 1
    pending_space = False
    for char in text:
        if char == "\n":
            line += 1
            if not pending_space and chars:
                chars.append(" ")
                line_of.append(line - 1)
            pending_space = True
            continue
        if char.isspace() or char in marks:
            if not pending_space and chars:
                chars.append(" ")
                line_of.append(line)
            pending_space = True
            continue
        chars.append(char)
        line_of.append(line)
        pending_space = False
    return "".join(chars), line_of


def tracked_text_files() -> list[Path]:
    """Every tracked file worth searching: no binaries, no vendored trees."""
    listed = _git("ls-files").splitlines()
    keep = []
    for name in listed:
        if name.startswith(SKIP_PREFIXES):
            continue
        if any(part in SKIP_DIRS for part in Path(name).parts):
            continue
        path = REPO / name
        try:
            path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        keep.append(path)
    return keep


@dataclass(frozen=True)
class Hit:
    path: str
    line: int
    text: str


def search(pattern: str) -> list[Hit]:
    """Find `pattern` anywhere in the repo, including across line breaks."""
    compiled = re.compile(pattern, re.IGNORECASE)
    hits: list[Hit] = []
    for path in tracked_text_files():
        flat, line_of = flatten(path.read_text(encoding="utf-8"))
        for match in compiled.finditer(flat):
            start = max(0, match.start() - 40)
            end = min(len(flat), match.end() + 40)
            hits.append(
                Hit(
                    path=str(path.relative_to(REPO)),
                    line=line_of[match.start()],
                    text=flat[start:end].strip(),
                )
            )
    return hits


def status_claims() -> list[Hit]:
    """Every place a document claims which commit `main` is at.

    Reported, not judged: a session note recording `main` at the time is
    history, while a status line making the same claim is stale. Telling them
    apart is a reader's call, so this lists them rather than failing.
    """
    hits: list[Hit] = []
    for path in tracked_text_files():
        if path.suffix != ".md":
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if HEAD_CLAIM_PATTERN.search(line):
                hits.append(
                    Hit(
                        path=str(path.relative_to(REPO)),
                        line=number,
                        text=line.strip(),
                    )
                )
    return hits


# --------------------------------------------------------------------------
# Consistency
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Problem:
    path: str
    line: int
    detail: str


def _section(path: Path, heading: str | None) -> tuple[str, int]:
    """One section of a file, and the 1-based file line its heading sits on.

    The line is returned so a reported finding points at the line in the file
    rather than the line in the slice — a claim at slice line 8 is useless to
    someone looking for file line 94.

    A section runs from its heading to the next heading of *any* level. That
    is what both HANDOFF cases need: §2 must stop before the subsection §2.1,
    and §2.1 must stop before the next top-level section — and it must not run
    on into the dated session notes filed beneath either, which are history.
    Raises rather than returning nothing, because a heading that has been
    renamed must be noticed, not silently left unchecked.
    """
    text = path.read_text(encoding="utf-8")
    if heading is None:
        return text, 1
    start = text.find(heading)
    if start == -1:
        raise SystemExit(f"{_label(path)} has no section {heading!r}")
    following = re.compile(r"^#+ ", re.MULTILINE).search(text, start + len(heading))
    end = following.start() if following else len(text)
    return text[start:end], text.count("\n", 0, start) + 1


def _claims(text: str, pattern: re.Pattern[str]) -> list[tuple[int, str]]:
    """Every match of `pattern` in `text`, with the line each one starts on.

    Matched against the flattened text, so a claim wrapped across two lines is
    still found. Line-by-line scanning is what lets a stale figure survive a
    sweep, and that is the failure this whole tool exists to stop.
    """
    flat, line_of = flatten(text, markdown=True)
    return [(line_of[match.start()], match.group(1)) for match in pattern.finditer(flat)]


def check(
    docs: Sequence[Path | tuple[Path, str | None]] | None = None,
    pin_files: Sequence[Path] | None = None,
) -> list[Problem]:
    """Compare every quoted figure against the source it is about.

    The document lists are parameters so a test can point them at a temporary
    file. Comparing against the real documents would mean editing one to prove
    the check works, and a test that writes to the repo is a test that can pass
    by changing what it checks.
    """
    problems: list[Problem] = []

    total = int(tests()["total"])  # type: ignore[arg-type]
    row_count = int(names()["rows"])  # type: ignore[arg-type]
    digests = hashes()

    # A caller may name a whole file or a section of one, so a test can point
    # the check at a section without editing a real document.
    targets = (
        CURRENT_STATUS_DOCS
        if docs is None
        else tuple(entry if isinstance(entry, tuple) else (entry, None) for entry in docs)
    )
    for path, heading in targets:
        label = _label(path) if heading is None else f"{_label(path)} {heading}"
        # Claims are found in the flattened text, so one wrapped across two
        # lines is still a claim. Scanning line by line is what lets a stale
        # figure survive, and it is the failure this tool exists to stop.
        body, first_line = _section(path, heading)
        # Claim lines are relative to the slice; shift them back to file lines
        # so a finding points somewhere the reader can actually go.
        offset = first_line - 1
        test_claims = [(offset + n, v) for n, v in _claims(body, TEST_COUNT_PATTERN)]
        row_claims = [(offset + n, v) for n, v in _claims(body, ROW_COUNT_PATTERN)]

        # Each document is asked for the figures it is expected to carry. A
        # document that stops quoting one is a gap, not a pass.
        expected = EXPECTED_CLAIMS.get(label, ())
        if "test count" in expected and not test_claims:
            problems.append(Problem(label, 0, "quotes no test count to verify"))
        if "row count" in expected and not row_claims:
            problems.append(Problem(label, 0, "quotes no row/name count to verify"))

        for number, quoted in test_claims:
            if int(quoted) != total:
                problems.append(
                    Problem(label, number, f"says {quoted} tests; the suite collects {total}")
                )
        for number, quoted in row_claims:
            if int(quoted) != row_count:
                problems.append(
                    Problem(
                        label,
                        number,
                        f"says {quoted}-row/name; the schedule has {row_count}",
                    )
                )

    # A pin is quoted the same way everywhere, so a wrong one is checkable
    # wherever it appears — including in dated records, where the fixture
    # digest does not age.
    for path in tracked_text_files() if pin_files is None else pin_files:
        if path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for span in CODE_SPAN.finditer(text):
            token = "".join(span.group(1).split())
            found = PIN_TOKEN.match(token)
            if found is None:
                # Not pin-shaped: an ellipsis meaning "and so on", a command, a
                # path. Left alone rather than guessed at.
                continue
            line = text.count("\n", 0, span.start()) + 1
            prefix, suffix = found.group(1), found.group(2)
            if len(prefix) != PIN_PREFIX_LENGTH:
                problems.append(
                    Problem(
                        _label(path),
                        line,
                        f"quotes pin {prefix}…{suffix}, whose prefix is not "
                        f"{PIN_PREFIX_LENGTH} hex digits",
                    )
                )
                continue

            # Both ends must belong to the *same* fixture. Checking the prefix
            # against the union of all fixtures would accept a swapped pin,
            # because the wrong digest is still a real one.
            #
            # Known limit, deliberately not closed: a complete, well-formed
            # digest of the *wrong* fixture matches one fixture, and only the
            # prose around the span says which fixture was meant. This check
            # guarantees digest membership, not fixture attribution — that is a
            # reader's rule for the review standards, not a pattern.
            matches = [
                name
                for name, digest in digests.items()
                if digest.startswith(prefix) and (not suffix or digest.endswith(suffix))
            ]
            if len(matches) != 1:
                problems.append(
                    Problem(
                        _label(path),
                        line,
                        f"quotes pin {prefix}…{suffix}, which matches "
                        f"{len(matches)} pinned fixtures, not one",
                    )
                )
    return problems


# --------------------------------------------------------------------------
# Plumbing
# --------------------------------------------------------------------------


# Variables in the caller's shell that point a subprocess at something other
# than what this tool meant.
_REDIRECTING_ENV = (
    # pytest takes extra arguments from here, so a `-k` in the caller's shell
    # selects a subset, and a subset reported as the suite total is a wrong
    # figure.
    "PYTEST_ADDOPTS",
    # git's outrank the working directory: with `GIT_DIR` set, every git command
    # here answers for another repository while `cwd=REPO` says otherwise, and
    # `GIT_INDEX_FILE` points it at another repository's index, where `ls-files`
    # lists nothing.
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
)


def _env() -> dict[str, str]:
    """The environment subprocesses run in, with the caller's redirections cleared.

    This list is the ways we know a caller's shell can point a child somewhere
    else, and a list like that is never finished — git and uv each read more
    variables than anyone writes down. So it is not what makes the figures
    trustworthy: `_require_this_repo` asks git which repository it is answering
    about and stops when the answer is another one, and `tests()` names the
    directory uv runs in on the command line, where uv's own variables cannot
    reach it.
    """
    return {k: v for k, v in os.environ.items() if k not in _REDIRECTING_ENV}


def _label(path: Path) -> str:
    """Repo-relative where possible; a path outside the repo is reported whole."""
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, check=False, env=_env()
    )
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def _is_inside_repo(path: Path) -> bool:
    """Whether a path, once resolved, is the repository or under it."""
    try:
        path.resolve().relative_to(REPO.resolve())
    except ValueError:
        return False
    return True


def _checkout_git_dir() -> Path:
    """The git directory this checkout's own `.git` names.

    Read from the filesystem, so the environment cannot answer it: this is the
    one thing about the repository that no variable in the caller's shell can
    change.
    """
    marker = REPO / ".git"
    if marker.is_dir():
        return marker.resolve()
    if marker.is_file():
        # A linked worktree or a submodule keeps its metadata in the repository
        # that owns it and leaves a pointer here instead of a directory.
        head = marker.read_text(encoding="utf-8").splitlines()[0]
        return (REPO / head.partition(":")[2].strip()).resolve()
    raise SystemExit(f"{marker} is neither a file nor a directory; {REPO} is not a checkout")


def _require_this_repo() -> None:
    """Stop unless git is answering about this checkout.

    The figures are only worth anything if they describe `REPO`, and a wrong
    answer here does not look wrong: another project's suite, another
    repository's tip, all report as plain numbers. So ask git what it is
    actually reading, rather than trusting that `_env()` covered every way a
    shell can redirect it.

    Two questions, because two things can be moved separately. Is the git
    directory the one this checkout points at, and is the working tree `REPO`?
    `GIT_DIR` moves the first while the second still answers `REPO`, which is
    why `--show-toplevel` alone would not have found the finding that started
    this.

    Compared against `.git` and not against `REPO/.git`: a linked worktree's git
    directory is `<main>/.git/worktrees/<name>` and a submodule's is
    `<parent>/.git/modules/<name>`, both outside the checkout, and both
    ordinary. Refusing those would fail a correct case.
    """
    expected = _checkout_git_dir()
    actual = Path(_git("rev-parse", "--absolute-git-dir")).resolve()
    if actual != expected:
        raise SystemExit(
            f"git is reading the repository at {actual}, but the checkout at {REPO} "
            f"points at {expected}. Something in this shell points git elsewhere — a "
            "GIT_DIR, or a variable this tool does not know about. Unset it and run again."
        )

    top = Path(_git("rev-parse", "--show-toplevel")).resolve()
    if top != REPO.resolve():
        raise SystemExit(
            f"git's working tree is {top}, not {REPO}. Something in this shell points "
            "git at another checkout. Unset it and run again."
        )


def _render(command: str, payload: object) -> None:
    if command == "head":
        data = payload
        print(f"{data['branch']} at {data['commit']}")  # type: ignore[index]
    elif command == "main":
        data = payload
        print(f"main is at {data['main_short']} as this clone last saw it")  # type: ignore[index]
        print(f"  checkout: {data['checked_out']}")  # type: ignore[index]
        print("  run `git fetch` for a live value; `origin/main` is the last fetched one")
    elif command == "tests":
        data = payload
        print(f"{data['total']} tests collected")  # type: ignore[index]
        for name, count in data["per_file"].items():  # type: ignore[index,union-attr]
            print(f"  {count:>3}  {name}")
    elif command == "names":
        data = payload
        print(f"{data['rows']} rows, {data['unique_names']} unique plant-data names")
        print(f"  source: {data['source']}")
    elif command == "hashes":
        for name, digest in payload.items():  # type: ignore[union-attr]
            print(f"{digest}  {name}")
    elif command in {"search", "status"}:
        hits = payload
        if not hits:
            print("no matches")
        for hit in hits:  # type: ignore[union-attr]
            print(f"{hit.path}:{hit.line}: {hit.text}")
        print(f"\n{len(hits)} match(es)")  # type: ignore[arg-type]
    elif command == "check":
        problems = payload
        if not problems:
            print("every quoted figure matches its source")
        for problem in problems:  # type: ignore[union-attr]
            print(f"{problem.path}:{problem.line}: {problem.detail}")
        print(f"\n{len(problems)} problem(s)")  # type: ignore[arg-type]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("head", "main", "tests", "names", "hashes", "status", "check"):
        sub.add_parser(name)
    search_parser = sub.add_parser("search")
    search_parser.add_argument("pattern")

    args = parser.parse_args(argv)

    _require_this_repo()

    if args.command == "head":
        payload: object = head()
    elif args.command == "main":
        payload = main_branch()
    elif args.command == "tests":
        payload = tests()
    elif args.command == "names":
        payload = names()
    elif args.command == "hashes":
        payload = hashes()
    elif args.command == "search":
        payload = search(args.pattern)
    elif args.command == "status":
        payload = status_claims()
    else:
        payload = check()

    if args.json:
        if args.command in {"search", "status"}:
            body: object = [hit.__dict__ for hit in payload]  # type: ignore[union-attr]
        elif args.command == "check":
            body = [problem.__dict__ for problem in payload]  # type: ignore[union-attr]
        else:
            body = payload
        print(json.dumps({"command": args.command, "head": head(), "result": body}, indent=2))
    else:
        _render(args.command, payload)

    # Only `check` reports failure; the rest are queries.
    if args.command == "check" and payload:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
