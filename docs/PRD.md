# SCADA Harmonization & Contextualization Service
## Product Requirements Document (PRD)

---

## 1. Overview

This project implements a standalone industrial data harmonization service that ingests heterogeneous SCADA telemetry events and produces standardized, ISA-95-aligned canonical telemetry messages suitable for enterprise analytics and Unified Namespace (UNS) streaming architectures.

The system simulates a real brownfield harmonization program where multiple legacy operational systems publish semantically inconsistent telemetry data — the kind of integration friction encountered when consolidating acquisitions (e.g., Pioneer/CygNet, Denbury/Wonderware) into a unified enterprise platform.

This project is intentionally designed to:

- Apply ISA-95 Part 2 for physical equipment hierarchy
- Standardize naming conventions and units
- Normalize status encodings
- Enforce canonical telemetry contracts
- Provide lineage and explainability
- Produce robust error handling and dead-letter routing

**Pydantic is a first-class architectural concern.** The project uses Pydantic extensively as both the validation engine and the modeling framework. Every data boundary — source ingestion, intermediate extraction, canonical validation, UNS envelope construction, error reporting — is enforced by a Pydantic model. This makes the project a practical vehicle for learning advanced Pydantic features including discriminated unions, field/model validators, aliases, custom types, constrained fields, and serializers.

---

## 2. Problem Statement

Industrial telemetry systems often suffer from:

- **Inconsistent naming conventions:** camelCase, snake_case, hyphenated keys (e.g., `PUMP_01_TEMP` vs `P-101.T` vs `pump-1-temperature`)
- **Different JSON shapes:** flat vs nested vs topic-based identity
- **Different units:** bpd vs m³/day, psi vs kPa, °F vs °C
- **Inconsistent status encodings:** "P", "RUN", "Producing", "ONLINE"
- **Unreliable timestamps:** ISO strings, epoch seconds, epoch milliseconds, missing
- **Lack of contextual hierarchy:** no ISA-95 alignment, no standard asset model

This is compounded during M&A integration, where acquired companies bring entirely different SCADA platforms (CygNet, Wonderware, FactoryTalk) with proprietary tag structures and naming conventions. Without harmonization, the "metadata problem" makes raw tags useless for enterprise analytics and AI/ML applications.

These issues prevent:

- Cross-site KPI standardization
- Enterprise-level analytics and AI applications
- Reliable streaming architectures (UNS)
- M&A system integration (the primary business driver)
- Trustworthy predictive maintenance and autonomous control

---

## 3. Goals

The system must:

1. Ingest events from 3 heterogeneous source types representing different legacy SCADA platforms
2. Support multiple equipment classes (Wells and ESPs at minimum)
3. Extract ISA-95 contextual hierarchy from each source's naming convention
4. Normalize units and statuses to canonical standards
5. Validate telemetry constraints (type, range, cross-field consistency)
6. Emit canonical enterprise-aligned events via Pydantic models
7. Simulate a Unified Namespace with in-memory retained state, topic hierarchy, and wildcard queries
8. Provide per-field mapping lineage metadata
9. Produce structured error outputs with dead-letter routing for invalid events
10. Score data quality for each canonical event
11. Demonstrate report-by-exception (only emit when values change)
12. Generate birth certificate events for initial device state

---

## 4. Non-Goals

This system does NOT:

- Connect to real MQTT brokers or OPC UA servers
- Implement Sparkplug B protocol or Protobuf serialization
- Implement a full historian or time-series database
- Perform persistent storage beyond local JSONL files
- Replace SCADA systems or PLCs
- Implement real-time streaming (batch/file-based processing only)
- Perform fuzzy/AI-assisted tag matching (deterministic mapping only)

It is a contextualization and harmonization layer with an in-memory UNS simulation. The UNS is simulated using a Python dictionary (topic → last payload) rather than a live MQTT broker, but the concepts demonstrated — retained state, topic hierarchy, report-by-exception, wildcard subscriptions — are directly transferable to a broker-backed implementation.

---

## 5. Functional Requirements

### 5.1 Multi-Source Ingestion

The system must support three source types that represent realistic legacy SCADA platforms with different naming conventions, JSON shapes, and engineering units.

**Source A — CygNet-style legacy flat JSON:**

Flat key-value pairs using underscore-delimited compound names. Imperial units. Status as short codes.

```json
{
  "tag": "PERMIAN_NORTH_PAD12_WELL_E77",
  "flow": 1250.5,
  "pressure": 3200.0,
  "temp": 185.0,
  "status": "P",
  "ts": "2024-03-15T14:30:00Z"
}
```

**Source B — Wonderware-style legacy flat JSON:**

Different key names, metric units (m³/day, kPa, °C), verbose status strings, epoch timestamps.

```json
{
  "wellId": "E-77",
  "site": "Permian",
  "area": "North",
  "pad": "Pad-12",
  "flowRate_m3d": 198.8,
  "tubingPressure_kPa": 22063.0,
  "temperature_c": 85.0,
  "wellStatus": "Producing",
  "timestamp": 1710513000
}
```

**Source C — Ignition/MQTT UNS-style nested JSON:**

Hierarchical structure with topic-embedded identity. Mixed units. Epoch milliseconds.

```json
{
  "topic": "Exxon/Permian/North/Pad-12/ESP/E-77/telemetry",
  "payload": {
    "intake_pressure_psi": 1850.0,
    "motor_temp_f": 275.0,
    "motor_amps": 42.5,
    "vibration_ips": 0.35,
    "status": "RUN"
  },
  "timestamp_ms": 1710513000000
}
```

### 5.2 Equipment Classes

The system must support at minimum two equipment classes to demonstrate that the canonical model is genuinely generic:

**Well telemetry:**
- flow_rate_bpd (barrels per day)
- tubing_pressure_psi
- temperature_f
- status

**ESP (Electric Submersible Pump) telemetry:**
- intake_pressure_psi
- motor_temperature_f
- motor_current_amps
- vibration_ips (inches per second)
- status

### 5.3 Canonical Model

The canonical telemetry event must include:

**ISA-95 Identity:**
- `enterprise` (string, required)
- `site` (string, required)
- `area` (string, required)
- `cell` (string, required — the pad or unit)
- `equipment_class` (enum: `Well`, `ESP`)
- `equipment_id` (string, required)

**Telemetry Measurements:**
- Equipment-class-specific measurement fields (see 5.2)
- All measurements normalized to canonical units (imperial)

**Event Metadata:**
- `event_time` (timezone-aware UTC datetime, required)
- `status` (enum: `Producing` / `ShutIn` / `Offline` / `Unknown`)
- `data_quality` (structured — see 5.9)

**Lineage:**
- `meta.source_system` (which source type produced this event)
- `meta.source_event_id` (hash or identifier of the original payload)
- `meta.field_lineage` (per-field mapping: source key, original value, conversion applied)

### 5.4 ISA-95 Alignment

The canonical identity must follow ISA-95 Part 2 hierarchy:

```
Enterprise → Site → Area → Cell → Equipment Class → Equipment ID
```

Each source adapter must extract this hierarchy from the source's own naming convention — whether that's a compound tag name (Source A), discrete fields (Source B), or a topic path (Source C).

### 5.5 Unit Normalization

Convert to canonical imperial units:

| Source Unit | Canonical Unit | Conversion |
|-------------|---------------|------------|
| m³/day      | bpd           | × 6.28981  |
| kPa         | psi           | × 0.145038 |
| °C          | °F            | × 9/5 + 32 |

Conversions must be deterministic and recorded in field lineage.

### 5.6 Status Normalization

Map all source status codes to a canonical enum:

| Canonical Status | Source A | Source B      | Source C |
|------------------|----------|---------------|----------|
| Producing        | "P"      | "Producing"   | "RUN"    |
| ShutIn           | "S"      | "ShutIn"      | "STOP"   |
| Offline          | "X"      | "Offline"     | "OFF"    |
| Unknown          | (any other) | (any other) | (any other) |

Unmapped status codes must resolve to `Unknown` (not raise an error).

### 5.7 Timestamp Handling

Accept:
- ISO 8601 strings (with or without timezone)
- Epoch seconds (integer or float)
- Epoch milliseconds (integer)

Normalize to timezone-aware UTC datetime. Naive ISO strings must be assumed UTC. Missing timestamps must trigger a validation error (dead-letter).

### 5.8 Validation Constraints

The canonical model must enforce:

**Type constraints:**
- All measurement fields must be numeric (float)
- All identity fields must be non-empty strings
- Status must be a valid enum member
- Event time must be a valid datetime

**Range constraints:**
- `flow_rate_bpd` >= 0
- `tubing_pressure_psi` >= 0 and <= 15000
- `temperature_f` >= -40 and <= 500
- `intake_pressure_psi` >= 0 and <= 10000
- `motor_current_amps` >= 0
- `vibration_ips` >= 0

**Cross-field constraints:**
- `Producing` status with `flow_rate_bpd == 0` should flag `data_quality` as `Suspect` (not reject)
- Missing optional measurement fields are allowed but must be reflected in `data_quality`

### 5.9 Data Quality

Each canonical event must include a structured `data_quality` assessment:

- `quality` (enum: `Good` / `Suspect` / `Bad`)
- `flags` (list of strings describing any issues detected)

Examples of flags:
- `"zero_flow_while_producing"` — status is Producing but flow rate is zero
- `"coerced_status_to_unknown"` — original status was not in the mapping
- `"missing_optional_field:vibration_ips"` — an optional measurement was absent
- `"timestamp_assumed_utc"` — naive ISO string was treated as UTC

### 5.10 Unified Namespace (UNS) Simulation

The project simulates a Unified Namespace — the architectural pattern where all operational data is organized in a single, hierarchical, event-driven namespace that represents the current state of the entire operation. In production, a UNS is backed by an MQTT broker; here it is simulated with an in-memory Python dictionary.

#### 5.10.1 Topic Hierarchy

Topics follow the ISA-95 hierarchy with a data category suffix:

```
{enterprise}/{site}/{area}/{cell}/{equipment_class}/{equipment_id}/{data_category}
```

**Data categories:**

| Category     | Purpose                                     | Example Topic                                        |
|--------------|---------------------------------------------|------------------------------------------------------|
| `telemetry`  | Real-time measurement values                | `exxon/permian/north/pad-12/well/e-77/telemetry`    |
| `status`     | Operating state changes                     | `exxon/permian/north/pad-12/well/e-77/status`       |
| `birth`      | Initial full-state snapshot on first contact | `exxon/permian/north/pad-12/well/e-77/birth`        |

All topic segments must be lowercase, with spaces replaced by hyphens and special characters stripped.

#### 5.10.2 Retained State (In-Memory UNS)

The system maintains an in-memory dictionary keyed by topic path, storing the last published payload for each topic. This simulates MQTT retained messages — the core mechanism that makes a UNS a "live mirror" of the physical world.

Any consumer can query the current state of any topic (or topic pattern) at any time without waiting for the next publish.

#### 5.10.3 Report-by-Exception

When processing a batch of events, the system must compare each incoming canonical event against the retained state for its topic. If the telemetry values have not changed, the event is **not re-published** (not written to output). Only changes are emitted.

This simulates the bandwidth-efficient report-by-exception pattern used in production UNS/MQTT architectures.

#### 5.10.4 Birth Certificates

The first time a device (equipment_id) appears in the namespace, the system must emit a **birth certificate** — a full-state snapshot published to the `birth` data category topic. The birth certificate includes:

- All current telemetry values
- ISA-95 context
- Equipment class and metadata
- Timestamp of first contact

This simulates MQTT birth messages (NBIRTH/DBIRTH in Sparkplug B) that enable auto-discovery of devices.

#### 5.10.5 Wildcard Queries

The system must support querying the in-memory UNS state using wildcard patterns, simulating MQTT wildcard subscriptions:

- `+` matches a single level: `exxon/permian/+/+/esp/+/telemetry` → all ESP telemetry across the Permian site
- `#` matches all remaining levels: `exxon/permian/north/#` → everything in the North area

This can be exposed via the CLI (e.g., `scada-harmonize query "exxon/+/+/+/esp/#"`) or as a Python API.

#### 5.10.6 Output Envelope

Each published message uses the UNS envelope format:

```json
{
  "topic": "exxon/permian/north/pad-12/well/e-77/telemetry",
  "event_time": "2024-03-15T14:30:00+00:00",
  "payload": { },
  "context": {
    "enterprise": "Exxon",
    "site": "Permian",
    "area": "North",
    "cell": "Pad-12",
    "equipment_class": "Well",
    "equipment_id": "E-77"
  },
  "meta": {
    "source_system": "source_a",
    "source_event_id": "abc123...",
    "field_lineage": { }
  },
  "data_quality": {
    "quality": "Good",
    "flags": []
  }
}
```

### 5.11 Error Handling and Dead-Letter Routing

Invalid events must:

- Produce structured validation errors (leveraging Pydantic's `ValidationError`)
- Be routed to `dead_letter.jsonl`
- Include:
  - Failure reason (list of field-level errors)
  - Original payload snapshot
  - Source system identifier
  - Timestamp of processing attempt

```json
{
  "error_id": "...",
  "source_system": "source_b",
  "timestamp": "2024-03-15T14:31:00+00:00",
  "errors": [
    {
      "field": "event_time",
      "message": "Missing required field: timestamp",
      "type": "missing"
    }
  ],
  "original_payload": { }
}
```

---

## 6. Success Criteria

The system successfully:

- Processes mixed events from all three sources and both equipment classes
- **Produces identical canonical output regardless of source** — the same physical event arriving via Source A and Source B yields the same canonical telemetry
- Converts units correctly (verified by round-trip tolerance tests)
- Normalizes statuses correctly across all source mappings
- Rejects malformed payloads with clear, structured error messages
- Produces deterministic, sanitized UNS topics with data category suffixes
- Maintains an in-memory UNS with retained state per topic
- Suppresses duplicate publishes via report-by-exception
- Emits birth certificates on first contact per device
- Supports wildcard topic queries against the namespace state
- Tracks per-field lineage for every canonical event
- Scores data quality with meaningful flags

---

## 7. Acceptance Testing

### 7.1 Unit Tests
- Unit conversion functions pass (with tolerance for floating-point)
- Status mapping covers all source codes plus unknown fallback
- Timestamp parsing handles ISO, epoch seconds, epoch milliseconds, and missing
- Range validators reject out-of-bounds values
- Data quality flags fire for cross-field inconsistencies

### 7.2 Integration Tests
- Valid fixtures from each source produce correct canonical events
- Broken fixtures produce dead-letter entries with meaningful error messages
- End-to-end pipeline: raw source JSON → adapter → transform → canonical → UNS envelope

### 7.3 Cross-Source Equivalence Tests
- The same physical event represented in Source A and Source B format produces **identical** canonical output (the core proof that harmonization works)

### 7.4 Edge Case Tests
- Missing optional fields are handled gracefully (not rejected)
- Null values in required fields produce dead-letter entries
- Out-of-range values produce dead-letter entries with specific field errors
- Empty payloads, malformed JSON structures
- Duplicate events (same event_time + equipment_id)

### 7.5 Output Validation
- Canonical JSONL output is valid, line-delimited JSON
- Dead-letter JSONL output contains original payload and structured errors
- UNS topics are lowercase, hyphenated, and deterministic

### 7.6 UNS Simulation Tests
- Retained state: after processing, the in-memory UNS holds the last payload per topic
- Report-by-exception: processing the same event twice produces output only on the first occurrence
- Birth certificates: the first event for a device emits a birth record; subsequent events do not
- Wildcard queries: `+` matches single level, `#` matches remaining levels
- Data categories: telemetry and status events produce distinct topic paths for the same device
