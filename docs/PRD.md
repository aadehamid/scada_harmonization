# SCADA Harmonization & Contextualization Service
## Product Requirements Document (PRD)

---

## 1. Overview

This project implements a standalone industrial data harmonization service that ingests heterogeneous SCADA telemetry events and produces standardized, ISA-95-aligned canonical telemetry messages suitable for enterprise analytics and Unified Namespace (UNS) streaming architectures.

The system simulates a real brownfield harmonization program where multiple legacy operational systems publish semantically inconsistent telemetry data.

This project is intentionally designed to:
- Apply ISA-95 Part 2 for physical equipment hierarchy
- Standardize naming conventions and units
- Normalize status encodings
- Enforce canonical telemetry contracts
- Provide lineage and explainability
- Produce robust error handling and dead-letter routing

While Pydantic is used for validation and schema enforcement, the project is not Pydantic-centric — it is a complete data engineering mini-system.

---

## 2. Problem Statement

Industrial telemetry systems often suffer from:

- Inconsistent naming conventions (camelCase, snake_case, hyphenated keys)
- Different JSON shapes (flat vs nested vs topic-based identity)
- Different units (bpd vs m³/day, psi vs kPa, °F vs °C)
- Inconsistent status encodings ("P", "RUN", "Producing")
- Unreliable timestamps (ISO, epoch, ms, missing)
- Lack of contextual hierarchy (no ISA-95 alignment)

This prevents:
- Cross-site KPI standardization
- Enterprise-level analytics
- Reliable streaming architectures
- M&A system integration
- Trustworthy AI applications

---

## 3. Goals

The system must:

1. Ingest events from 3 heterogeneous source types
2. Extract ISA-95 contextual hierarchy
3. Normalize units and statuses
4. Validate telemetry constraints
5. Emit canonical enterprise-aligned events
6. Publish UNS-compatible topic structures
7. Provide mapping lineage metadata
8. Produce structured error outputs for invalid events

---

## 4. Non-Goals

This system does NOT:
- Connect to real MQTT brokers
- Implement a full historian
- Perform persistent storage beyond local JSONL
- Replace SCADA systems

It is a contextualization and harmonization layer only.

---

## 5. Functional Requirements

### 5.1 Multi-Source Ingestion
The system must support:

- Source A (legacy flat JSON with non-standard keys)
- Source B (legacy flat JSON with different units/status codes)
- Source C (UNS-style nested JSON + topic identity)

### 5.2 Canonical Model

Canonical telemetry must include:

- enterprise
- site
- area
- cell (pad)
- equipment_class
- equipment_id
- event_time (UTC datetime)
- flow_rate_bpd
- tubing_pressure_psi
- temperature_f
- status (Producing / ShutIn / Offline / Unknown)
- optional data_quality
- meta (source system + lineage)

### 5.3 ISA-95 Alignment

The canonical identity must follow:

Enterprise → Site → Area → Cell → Equipment Class → Equipment ID

### 5.4 Unit Normalization

Convert:
- m³/day → bpd
- kPa → psi
- °C → °F

### 5.5 Status Normalization

Map source codes to canonical enum:
- Producing
- ShutIn
- Offline
- Unknown

### 5.6 Timestamp Handling

Accept:
- ISO strings
- Epoch seconds
- Epoch milliseconds

Normalize to timezone-aware UTC datetime.

### 5.7 UNS Output

Topic format: {enterprise}/{site}/{area}/{cell}/{equipment_class}/{equipment_id}/telemetry


Output envelope:

```json
{
  "topic": "...",
  "event_time": "...",
  "payload": { canonical telemetry },
  "context": { ISA-95 hierarchy },
  "meta": { lineage + source }
}

5.8 Error Handling

Invalid events must:

Produce structured validation errors

Be routed to dead_letter.jsonl

Include failure reason and original payload snapshot

6. Success Criteria

The system successfully:

Processes mixed events from all sources

Produces identical canonical output regardless of source

Converts units correctly

Normalizes statuses correctly

Rejects malformed payloads with clear error messages

Produces deterministic UNS topics

Tracks lineage for each canonical field

7. Acceptance Testing

Unit conversion tests pass

Status mapping tests pass

Timestamp parsing tests pass

Valid fixtures produce canonical events

Broken fixtures produce dead-letter entries

