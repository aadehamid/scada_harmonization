#!/usr/bin/env python3
"""The repo's figures and its searches, defined once.

Documents quote numbers: how many tests exist, how many plant-data names the tag
schedule holds, what the fixture hashes are. Every agent that counts them by
hand counts differently, and each difference becomes a wrong figure in a
document. This tool is the single definition of each figure.

It also searches ignoring line breaks. A claim split across two lines is
invisible to `grep`, and that is how a stale claim survives a sweep: the words
are there, the pattern is not.

Read-only. It never writes to the repo, and `check` is wired into
`scripts/check.sh` so a quoted figure that contradicts the source fails the
build.

Usage:
    scripts/facts.py head            branch and commit
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
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Sequence
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

# Documents that describe the repo as it is now. A dated session note or a
# phase record states what was true when it was written, so a figure in one is
# history, not a claim about today, and `check` does not read it.
CURRENT_STATUS_DOCS: tuple[Path, ...] = (
    REPO / "README.md",
    REPO / "AGENTS.md",
    REPO / "tests" / "README.md",
)

# Directories that are not the project's own prose or code.
SKIP_DIRS = frozenset(
    {".git", ".venv", "__pycache__", ".ruff_cache", ".pytest_cache", "node_modules"}
)
SKIP_PREFIXES = ("reference/", "data/")

# A quoted digest prefix, as the golden pins are written: eight hex digits and
# an ellipsis. Deliberately narrow — a bare short hash is usually a commit.
PIN_PATTERN = re.compile(r"\b([0-9a-f]{8})…")
TEST_COUNT_PATTERN = re.compile(r"\b(\d+)\s+tests?\b")
ROW_COUNT_PATTERN = re.compile(r"\b(\d+)-(?:row|name)\b")
HEAD_CLAIM_PATTERN = re.compile(r"main[^.\n]{0,20}`([0-9a-f]{7,40})`")


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------


def head() -> dict[str, str]:
    """The branch and commit the working copy is on."""
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    commit = _git("rev-parse", "HEAD")
    return {"branch": branch, "commit": commit, "short": commit[:7]}


def tests() -> dict[str, object]:
    """Collected tests, total and per file, from pytest itself.

    Runs the project's own command rather than reimplementing discovery, so the
    figure cannot drift from what the suite actually collects.
    """
    result = subprocess.run(
        ["uv", "run", "pytest", "--collect-only", "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"pytest --collect-only failed:\n{result.stdout}{result.stderr}")

    per_file: Counter[str] = Counter()
    for line in result.stdout.splitlines():
        match = re.match(r"^(tests/\S+?)::", line.strip())
        if match:
            per_file[match.group(1)] += 1
    total = sum(per_file.values())
    if total == 0:
        raise SystemExit("pytest collected nothing; refusing to report a count of zero")
    return {"total": total, "per_file": dict(sorted(per_file.items()))}


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


def flatten(text: str) -> tuple[str, list[int]]:
    """Collapse whitespace runs to single spaces, keeping a map back to lines.

    Returns the flattened text and, for each character in it, the 1-based line
    of the original file it came from.
    """
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
        if char.isspace():
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


def check(
    docs: Sequence[Path] | None = None,
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
    real_prefixes = {digest[:8] for digest in hashes().values()}

    for path in CURRENT_STATUS_DOCS if docs is None else docs:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for quoted in TEST_COUNT_PATTERN.findall(line):
                if int(quoted) != total:
                    problems.append(
                        Problem(
                            _label(path),
                            number,
                            f"says {quoted} tests; the suite collects {total}",
                        )
                    )
            for quoted in ROW_COUNT_PATTERN.findall(line):
                if int(quoted) != row_count:
                    problems.append(
                        Problem(
                            _label(path),
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
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for quoted in PIN_PATTERN.findall(line):
                if quoted not in real_prefixes:
                    problems.append(
                        Problem(
                            _label(path),
                            number,
                            f"quotes pin {quoted}…, which matches no pinned fixture",
                        )
                    )
    return problems


# --------------------------------------------------------------------------
# Plumbing
# --------------------------------------------------------------------------


def _label(path: Path) -> str:
    """Repo-relative where possible; a path outside the repo is reported whole."""
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def _git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def _render(command: str, payload: object) -> None:
    if command == "head":
        data = payload
        print(f"{data['branch']} at {data['commit']}")  # type: ignore[index]
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
    for name in ("head", "tests", "names", "hashes", "status", "check"):
        sub.add_parser(name)
    search_parser = sub.add_parser("search")
    search_parser.add_argument("pattern")

    args = parser.parse_args(argv)

    if args.command == "head":
        payload: object = head()
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
