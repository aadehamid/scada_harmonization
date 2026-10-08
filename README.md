# Industrial data harmonization and contextualization home lab

This lab simulates Lagos Specialty Chemicals, a manufacturer whose sites represent
similar equipment and process data with different tags, units, and identities.
It turns those differences into a governed Sparkplug B Unified Namespace, then
connects operational, business, and engineering context in a knowledge graph.

The lab is a learning environment and architecture prototype. Only the physical
Level 0 data is synthetic. The software above it exercises real protocols,
services, and data contracts.

## Start here

1. Read [HANDOFF.md](HANDOFF.md) sections 2 and 3 for current status and what to build next.
2. Read [the project charter](docs/LSC-001_Problem_Statement_and_Project_Charter.md) for the problem, scope, architecture, decisions, and phase exit criteria.
3. Use [the master index](docs/LSC-000_Master_Index.md) to choose a subject or learning path.
4. Read [working conventions](docs/WORKING_CONVENTIONS.md) and [the development guide](docs/DEVELOPMENT.md) before making changes.

## What the lab explores

| Plane | Responsibility | Charter |
| --- | --- | --- |
| Harmonize | Conform site-specific OT representations into reusable telemetry | Section 3, Plane 1 |
| Record | Turn curated operational events into enterprise records | Section 3, Plane 2 |
| Contextualize | Reconcile IT, OT, and engineering identities into connected context | Section 3, Plane 3 |
| Apply | Use the governed context for ML and graph-based reasoning | Section 3, Plane 4 |

The three-stage mapping connects a Level 0 variable to a site PLC tag and a
Sparkplug metric. The Unit 100 engineering record links the 59-name tag schedule
to that work. See [the engineering record](docs/LSC-007_Unit_100_Engineering_Record.md)
and [the Level 0 contract](docs/LSC-004_Level_0_Contract.md).

The drawing-to-graph learning path is defined in charter section 8, Phase 5b.1.
The related private project `aadehamid/Engineering_Drawing_to_Graph` adds an
authoring-system backend route; it is a separate project, not a dependency.

## Repository layout

| Path | Responsibility |
| --- | --- |
| `docs/` | Numbered project documents, learning guides, and document index |
| `docs/archive/` | Superseded design alternatives |
| `docs/history/` | Dated session records |
| `src/scada_harmonizer/` | Python package and finalized component code |
| `config/` | Site configuration and mapping bindings |
| `docker/` | Infrastructure configuration |
| `notebooks/` | Marimo learning notebooks |
| `tests/` | Tests and small deterministic fixtures |
| `scripts/` | Shared verification and facts tools |
| `data/` | Ignored local scratch data |
| `reference/` | Local-only reference material; its README is tracked |

The charter governs project definitions. `HANDOFF.md` section 2 owns current
status. Document history does not change either authority.

## Development

Use `uv` for Python project management. Run `scripts/check.sh` for the repository
gates; CI and the pre-push hook call the same script. Figures and searches come
from `scripts/facts.py`. See [the development guide](docs/DEVELOPMENT.md).

## License

[MIT](LICENSE)
