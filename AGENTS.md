# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

SCADA Harmonization Service — a Python pipeline that transforms heterogeneous industrial SCADA telemetry (from 3 different legacy source formats) into standardized, ISA-95-aligned canonical messages for enterprise analytics and Unified Namespace (UNS) streaming. The project is currently in a **pre-implementation state** (documentation only, no source code yet).

## Key Documentation

- `docs/PRD.md` — Full product requirements with fixture examples and acceptance criteria
- `docs/ARCHITECTURE.md` — Pipeline architecture, Pydantic model hierarchy, component design
- `docs/IMPLEMENTATION_PLAN.md` — Milestone breakdown (M0–M8) with planned project structure and tasks

## Planned Project Structure

When implementation begins, the package lives under `src/scada_harmonizer/` with this layout:
- `cli.py` — Typer-based CLI entry point
- `pipeline.py` — Pipeline orchestrator
- `models/` — Pydantic models: `sources.py`, `canonical.py`, `envelope.py`, `errors.py`, `lineage.py`
- `adapters/` — Source-specific adapters (`source_a.py` CygNet, `source_b.py` Wonderware, `source_c.py` Ignition) + `registry.py`
- `transforms/` — `units.py`, `status.py`, `timestamps.py`
- `uns/` — `namespace.py` (InMemoryUNS), `topics.py`, `wildcards.py`
- `writers/` — `jsonl.py`
- `tests/` at project root
- `fixtures/` at project root with `source_a/`, `source_b/`, `source_c/`, `equivalence/` subdirs

## Build and Development Commands

```
# Dependencies (planned)
# pyproject.toml with: pydantic>=2.0, typer, pytest, pytest-cov

# Install in dev mode
pip install -e ".[dev]"

# Run tests
pytest

# Run a single test
pytest tests/test_adapters.py::test_source_a_valid

# Run with coverage
pytest --cov=scada_harmonizer

# CLI usage (planned)
scada-harmonize run --input fixtures/ --output output/
scada-harmonize query "exxon/+/+/+/esp/+/telemetry"
```

## Architecture: Data Flow

```
Input JSON → Source Detection (discriminated union) → Adapter → RawExtractedEvent → Transform Layer → CanonicalTelemetry → UNS Envelope → InMemoryUNS
                                                                                          ↓ (validation failure)
                                                                                    DeadLetterEntry → dead_letter.jsonl
```

Every data boundary is a Pydantic model. No raw dicts cross layer boundaries.

## Three Source Formats

| Source | Style | Key Traits |
|--------|-------|------------|
| A (CygNet) | Flat JSON, compound tag name | Imperial units, short status codes ("P"/"S"/"X"), ISO timestamps |
| B (Wonderware) | Flat JSON, discrete fields | Metric units (m³/day, kPa, °C), verbose statuses, epoch seconds |
| C (Ignition) | Nested JSON with MQTT topic | Topic-embedded ISA-95 identity, mixed units, epoch milliseconds |

Source auto-detection uses Pydantic discriminated union on payload shape: `topic` key → Source C, `wellId` → Source B, `tag` → Source A.

## Critical Design Constraints

- **Pydantic-first**: All models use Pydantic v2. Use `Field(alias=...)` in source models, discriminated unions for routing, `field_validator`/`model_validator` in canonical models, constrained types (`ge`, `le`) for ranges, `model_serializer` for UNS envelope output.
- **ISA-95 hierarchy** is required on all canonical events: Enterprise → Site → Area → Cell → Equipment Class → Equipment ID.
- **Canonical units are imperial**: m³/day → bpd (×6.28981), kPa → psi (×0.145038), °C → °F (×9/5+32).
- **Status normalization**: All sources map to enum `Producing`/`ShutIn`/`Offline`/`Unknown`. Unmapped codes → `Unknown` (never raise).
- **Deterministic transforms**: Same input must always produce same output.
- **Cross-source equivalence**: The same physical event from any source must produce identical canonical output — this is the core proof of harmonization.
- **Report-by-exception**: UNS only emits when values change from retained state.
- **Birth certificates**: First event per device emits a full-state snapshot to `.../birth` topic.
- **Dead-letter routing**: Invalid events go to `dead_letter.jsonl` with structured Pydantic `ValidationError` details, never silently dropped.

## Equipment Classes

Two supported: `Well` (flow_rate_bpd, tubing_pressure_psi, temperature_f) and `ESP` (intake_pressure_psi, motor_temperature_f, motor_current_amps, vibration_ips). Each has class-specific measurement fields and range constraints defined in the canonical model.

## Testing Strategy

- **Unit tests**: Conversion functions, status mapping, timestamp parsing, range validation, data quality flags
- **Integration tests**: Valid/broken fixtures through full pipeline
- **Cross-source equivalence tests**: Same physical event from all 3 sources → identical canonical output
- **UNS tests**: Retained state, report-by-exception, birth certificates, wildcard matching (`+` single level, `#` remaining levels)
- **Edge cases**: Missing optional fields, null required fields, out-of-range values, empty payloads, duplicate events

## Output Files

- `output/canonical.jsonl` — Successfully harmonized events (only changed values per report-by-exception)
- `output/dead_letter.jsonl` — Rejected events with structured errors and original payload
