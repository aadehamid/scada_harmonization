# Development guide

Status: existing development instructions relocated from `AGENTS.md`.
Paths are repository-relative. Current implementation status is in
[HANDOFF.md](../HANDOFF.md).

## Build and development commands

**Package/project manager: `uv` (decided) — used for everything; no pip/poetry.** `uv add <pkg>` to
add deps, `uv sync` to install, `uv run <cmd>` to run, `uv.lock` committed, Python version uv-pinned.
Add each dependency *when needed*, with a one-line justification (raw-mechanism-before-wrapper).

**API framework:** FastAPI is the *intended* choice for the Plane 3 query/GraphRAG/copilot API — not
adopted yet; decide when that layer is built (~Phase 5b/7). The core pipeline needs no HTTP backend.

**Build setup** (current status is in `HANDOFF.md` §2):
`pyproject.toml` exists, created with `uv init --lib` (src layout). Python is **pinned to 3.13**
via a committed `.python-version` (uv's pin — do not gitignore it); `uv.lock` is committed.
Runtime deps are **polars** (wide→long melt, tabular L0 frames, 1 s machine stream) and
**pydantic** (L0 boundary). Each further dependency is added in the phase that needs it, with a
one-line justification. The dev group holds **ruff** (lint + format; `E,W,F,I,UP,B`; 100
columns), **pytest** (`testpaths = ["tests"]`), **ty**, and **markdown-it-py**.
The Markdown parser is a development dependency for document validation;
[its token API](https://markdown-it-py.readthedocs.io/en/latest/using.html#the-token-stream)
handles link syntax, code examples, and HTML boundaries. Runtime dependencies
remain polars and pydantic.

Commands: `uv sync` · `uv run pytest` · `uv run ruff check .` · `uv run ruff format .` · `uv run ty check`

**Checks run through one script: `scripts/check.sh`.** It runs ruff check, ruff
format `--check`, ty, pytest, `scripts/facts.py check`, and `scripts/facts.py links`. It fails if the
checks change the working tree. CI calls it; so does the pre-push hook. **Add a
gate there, not in `ci.yml` and not in the hook**, so a local run and a CI run
stay identical.

**Figures and searches come from `scripts/facts.py`**, never from counting by
hand. `head`, `tests`, `names`, `hashes` report the repo's numbers; `search`
finds text across line breaks, which `grep` cannot; `status` lists every place a
document claims which commit `main` is at; `check` fails when a quoted figure
contradicts its source and is wired into the check script. `--json` for
machine-readable output.

`links` checks tracked Markdown and HTML navigation without network access. It
checks local link and image targets, reference definitions, Markdown ATX and Setext heading
fragments (including duplicate headings), and HTML `id`/anchor targets. Root-relative
paths start at the repository root; URL queries do not change the file target.
It also checks whole-file rows in [the migration map](DOCUMENT_PATHS.md): current
labels must name their destinations, retired files must stay absent, and live
links must use current paths.

Historical path mentions in prose, inline code, fenced or indented examples, and
HTML comments remain untouched. Actual links in historical documents are still
checked. External URLs, renderer-specific extensions, JavaScript-generated
links, CSS URLs, and non-Markdown/non-HTML fragments are outside this check.
Markdown uses CommonMark parsing with table support. The checker reads link
and image tokens, resolves reference definitions, and sends HTML tokens to
the HTML attribute parser. It does not judge undefined reference labels, which
render as plain text. Run it with `uv run python scripts/facts.py links` so the
development dependency is available.

Install the hook once per clone (it is repo-local config, not committed):

```sh
git config core.hooksPath scripts/hooks
```

Git skips a missing or non-executable hook silently, so after installing, prove
it runs: `git hook run pre-push`.

**Repo layout** (later layers still README-only, per YAGNI):

```
src/scada_harmonizer/
  datagen/{generation,ingestion,augmentation,replay}  # Phase 1 code on main
  datagen/{plc_mapping,sparkplug,context_export}  # later phases
  {harmonize,record,contextualize,apply}    # the four planes
config/
  mappings/                                 # three-stage table spine. RESERVED. Walkthrough does not gate it
  sites/{beaumont,geismar,rotterdam,corpus_christi}
docker/    # compose lands service-by-service from Phase 2 (profiles per charter §8.2)
data/{raw,cache}    # local scratch only. Not the durable warehouse (R2 lagos-chem-l0)
notebooks/ # Marimo learning surface, one per component
tests/     # L0 goldens, Unit 100 P&ID, and verification tools
```

**Later stack** (not yet added): paho-mqtt ≥2.x, pysparkplug 0.6.x (**candidate** — PyPI status
Pre-Alpha; verify Sparkplug 3.0 behavior in Phase 2, fallback = hand-rolled `spBv1.0` protobuf),
Neo4j driver. **Tool versions/editions/licenses: charter §4.1 pinned stack** (EMQX ≥5.9
single-node BSL, TimescaleDB Community/TSL, ERPNext v15/16, Redis 8 AGPLv3, …).
