# SCADA Harmonization & Contextualization Service

A data harmonization pipeline that transforms heterogeneous industrial SCADA telemetry into standardized, ISA-95-aligned canonical messages for enterprise analytics and Unified Namespace (UNS) streaming architectures.

## Problem

Industrial telemetry systems suffer from:

- **Inconsistent naming** — camelCase, snake_case, hyphenated keys across sources
- **Varied JSON structures** — flat vs nested vs topic-based identity
- **Disparate units** — bpd vs m³/day, psi vs kPa, °F vs °C
- **Inconsistent status codes** — "P", "RUN", "Producing" mean the same thing
- **Unreliable timestamps** — ISO strings, epoch seconds, milliseconds, or missing
- **No contextual hierarchy** — lack of ISA-95 alignment

This fragmentation blocks cross-site KPI standardization, enterprise analytics, reliable streaming, M&A integration, and trustworthy AI applications.

## Solution

This service provides a centralized harmonization layer that:

1. Ingests events from multiple heterogeneous SCADA sources
2. Extracts ISA-95 contextual hierarchy (Enterprise → Site → Area → Cell → Equipment)
3. Normalizes units (m³/day → bpd, kPa → psi, °C → °F)
4. Standardizes status codes to a canonical enum
5. Validates telemetry constraints with strict Pydantic models
6. Emits canonical, enterprise-aligned events
7. Generates UNS-compatible topic structures
8. Provides full mapping lineage and explainability
9. Routes invalid events to dead-letter with structured errors

## Architecture

```
Input JSON → Source Adapter → Raw Extracted → Transform Layer → Canonical Model → UNS Envelope
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed design and [docs/PRD.md](docs/PRD.md) for full requirements.

## License

MIT
