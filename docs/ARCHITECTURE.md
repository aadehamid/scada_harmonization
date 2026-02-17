# Architecture Design
## SCADA Harmonization Service

---

## 1. System Overview

The system follows a pipeline architecture with explicit error branching. Every data boundary is enforced by a Pydantic model.

```
Input JSON → Source Detection → Adapter → Raw Extracted Event → Transform → Canonical Model → UNS Envelope → Output
                                                                     ↓ (validation failure)
                                                               Dead-Letter Handler → dead_letter.jsonl
```

### Entry Point

The system is invoked via a CLI that accepts:

- A directory of fixture files (batch mode)
- A single JSON file
- Stdin (piped JSON lines)

The CLI reads events, routes each through the pipeline, publishes to the in-memory UNS, and writes results to:

- `output/canonical.jsonl` — successfully harmonized events (only changed values, per report-by-exception)
- `output/dead_letter.jsonl` — rejected events with structured errors
- In-memory UNS state — queryable via CLI or Python API

---

## 2. Pydantic Model Architecture

Pydantic is the backbone of every data boundary. The model hierarchy and the Pydantic features exercised at each layer:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Source Layer                                  │
│                                                                     │
│  SourceAEvent ──┐                                                   │
│  SourceBEvent ──┼──→  Discriminated Union (source auto-detection)   │
│  SourceCEvent ──┘     Field(alias=...) for legacy key mapping       │
│                       model_validator for structural checks          │
└─────────────────────────┬───────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    Intermediate Layer                                │
│                                                                     │
│  RawExtractedEvent     Adapter output — normalized field names,     │
│                        original units preserved, ISA-95 identity    │
│                        extracted. Pydantic model with Optional       │
│                        fields and source metadata.                   │
└─────────────────────────┬───────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    Canonical Layer                                   │
│                                                                     │
│  CanonicalTelemetry    Strict validation: constrained types          │
│    ├─ WellTelemetry    (PositiveFloat, ranges), field_validator     │
│    └─ ESPTelemetry     for unit conversion, model_validator for      │
│                        cross-field checks, Enum for status.          │
│                                                                     │
│  DataQuality           Structured quality assessment (enum + flags) │
│  FieldLineage          Per-field source mapping and conversion log  │
└─────────────────────────┬───────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     Output Layer                                    │
│                                                                     │
│  UNSEnvelope           Topic generation from ISA-95 hierarchy.      │
│                        model_serializer for output formatting.       │
│                        Embeds payload, context, meta, data_quality. │
│                                                                     │
│  DeadLetterEntry       Structured error with original payload,      │
│                        field-level errors from ValidationError,      │
│                        source system, and processing timestamp.      │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     UNS Simulation Layer                             │
│                                                                     │
│  InMemoryUNS           Python dict as MQTT broker simulation.       │
│                        Retained state per topic. Report-by-          │
│                        exception filtering. Birth certificate        │
│                        generation. Wildcard topic matching.          │
│                                                                     │
│  BirthCertificate      Full-state snapshot on first device contact. │
│                        Pydantic model published to .../birth topic. │
└─────────────────────────────────────────────────────────────────────┘
```

### Pydantic Feature Map

| Pydantic Feature          | Where Used                          | Purpose                                              |
|---------------------------|-------------------------------------|------------------------------------------------------|
| `Field(alias=...)`        | Source models (A, B, C)             | Map legacy key names to normalized field names        |
| Discriminated Union       | Source detection / routing          | Auto-select the correct source model from payload shape |
| `field_validator`         | Canonical model                     | Unit conversion, timestamp parsing, range checks     |
| `model_validator`         | Canonical model                     | Cross-field consistency (e.g., status vs flow rate)  |
| Constrained types         | Canonical model                     | `ge=0`, `le=15000` on measurement fields             |
| `Enum`                    | Status, EquipmentClass, DataQuality | Type-safe categorical values                         |
| `model_serializer`        | UNS envelope                        | Custom JSON output formatting                        |
| `model_json_schema()`     | Schema export                       | Generate JSON Schema for canonical contract          |
| `ValidationError`         | Dead-letter handler                 | Structured, field-level error extraction             |
| `computed_field`          | Birth certificate                   | Derive full-state snapshot from canonical event      |

---

## 3. ISA-95 Context Model

The canonical identity follows ISA-95 Part 2 hierarchy:

| ISA-95 Level     | Example Mapping | Description                    |
|------------------|-----------------|--------------------------------|
| Enterprise       | Exxon           | Top-level organization         |
| Site             | Permian         | Geographic or operational site |
| Area             | North           | Subdivision within site        |
| Cell             | Pad-12          | Work cell / pad / unit         |
| Equipment Class  | Well / ESP      | Asset type (enum)              |
| Equipment ID     | E-77            | Specific asset identifier      |

This hierarchy is:
- Extracted by each source adapter from the source's own naming convention
- Enforced as required fields in the canonical model
- Used to generate deterministic UNS topics

---

## 4. Logical Architecture

```
                    ┌──────────────────┐
                    │   CLI / Runner   │
                    │  (entry point)   │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
  fixture files ──→ │  Event Loader    │
                    │  (read + parse)  │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Source Detector / │
                    │ Adapter Registry │──→ selects adapter based on
                    └────────┬─────────┘    payload shape or config
                             ↓
              ┌──────────────┼──────────────┐
              ↓              ↓              ↓
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │  Adapter A   │ │  Adapter B   │ │  Adapter C   │
     │  (CygNet)    │ │ (Wonderware) │ │  (Ignition)  │
     └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
              └──────────────┼──────────────┘
                             ↓
                    ┌──────────────────┐
                    │  Raw Extracted   │
                    │  Event           │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Transform Layer  │
                    │  - Units         │
                    │  - Status        │
                    │  - Timestamp     │
                    │  - Lineage       │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Canonical Model  │──→ Pydantic validation
                    │  (strict)        │
                    └───┬──────────┬───┘
                        ↓          ↓
                   (success)   (failure)
                        ↓          ↓
              ┌────────────┐ ┌──────────────────┐
              │ UNS Topic  │ │  Dead-Letter      │
              │ Builder    │ │  Handler           │
              └─────┬──────┘ └────────┬───────────┘
                    ↓                 ↓
              ┌────────────┐ ┌──────────────────┐
              │ UNS        │ │  dead_letter.jsonl│
              │ Envelope   │ └──────────────────┘
              └─────┬──────┘
                    ↓
              ┌──────────────────┐
              │  In-Memory UNS   │
              │  (retained state)│
              └───┬──────────┬───┘
                  ↓          ↓
            (changed)   (unchanged)
                  ↓          ↓
           ┌────────────┐  (suppressed —
           │ canonical   │   report-by-
           │  .jsonl     │   exception)
           └────────────┘
```

---

## 5. Core Components

### 5.1 Source Detector and Adapter Registry

The system must determine which adapter to use for each incoming event. Two strategies are supported:

- **Explicit routing:** The source type is provided as metadata (e.g., filename convention, CLI flag, or a `source_type` field in the JSON).
- **Auto-detection via discriminated union:** Pydantic's discriminated union inspects the payload shape (presence of `topic` key → Source C, presence of `wellId` → Source B, presence of `tag` → Source A).

The adapter registry maps source types to adapter classes, making it extensible for future sources.

### 5.2 Adapters

Each adapter is responsible for:
- Parsing the source-specific JSON into a Pydantic source model (using `Field(alias=...)`)
- Extracting ISA-95 identity from the source's naming convention
- Outputting a `RawExtractedEvent` with normalized field names but original units/values preserved
- Recording which source fields mapped to which extracted fields (for lineage)

### 5.3 Transform Layer

Operates on `RawExtractedEvent` and produces inputs for the `CanonicalTelemetry` model:

- **Unit conversion:** Deterministic, recorded in lineage (e.g., `kPa × 0.145038 → psi`)
- **Status normalization:** Lookup table per source, unmapped codes → `Unknown`
- **Timestamp normalization:** Detect format, convert to timezone-aware UTC datetime
- **Lineage assembly:** Build per-field lineage records during transformation

### 5.4 Canonical Model

Strict Pydantic model with:
- Constrained numeric types (non-negative, bounded ranges)
- Enum-based status and equipment class
- `field_validator` for final type coercion
- `model_validator` for cross-field checks (e.g., data quality flagging)
- Equipment-class-specific submodels (`WellTelemetry`, `ESPTelemetry`)

### 5.5 Data Quality Scorer

Runs as part of canonical model validation:
- Assigns `Good`, `Suspect`, or `Bad` quality rating
- Produces a list of flags describing any issues detected
- Does not reject events — quality scoring is informational, not gating

### 5.6 Lineage Module

Tracks per-field:
- `source_key` — the original key name in the source JSON
- `original_value` — the raw value before conversion
- `conversion` — description of transformation applied (e.g., `"kPa_to_psi"`, `"none"`)
- `canonical_field` — the resulting field in the canonical model

Lineage is a Pydantic model (`FieldLineage`) embedded in the canonical event's `meta` section.

### 5.7 Dead-Letter Handler

- Catches `ValidationError` from Pydantic
- Extracts field-level errors into a structured `DeadLetterEntry` model
- Preserves the original payload snapshot
- Writes to `dead_letter.jsonl`

### 5.8 UNS Topic Builder and Envelope

- Derives the topic string from the ISA-95 hierarchy fields
- Appends data category suffix (`telemetry`, `status`, `birth`)
- Sanitizes topic segments: lowercase, spaces → hyphens, strip special characters
- Wraps the canonical event in a `UNSEnvelope` Pydantic model containing: topic, event_time, payload, context, meta, and data_quality

### 5.9 In-Memory UNS (Namespace Simulation)

The `InMemoryUNS` class simulates the core behaviors of an MQTT broker-backed Unified Namespace without requiring external infrastructure:

```python
class InMemoryUNS:
    state: dict[str, UNSEnvelope]   # topic → last retained payload
    history: list[UNSEnvelope]      # ordered log of all publishes (for JSONL export)
    births: set[str]                # equipment IDs that have sent birth certificates
```

**Retained state:** Every `publish(envelope)` call updates `state[topic]` with the latest payload. This is the "live mirror" — any consumer can query current state at any time.

**Report-by-exception:** Before writing to output, the UNS compares the incoming payload against the retained state. If the telemetry values are unchanged, the publish is suppressed. Only changes are written to `canonical.jsonl`.

**Birth certificates:** The first time a device publishes, the UNS emits a birth certificate to the `birth` data category topic (e.g., `.../well/e-77/birth`). This full-state snapshot enables auto-discovery.

**Wildcard queries:** The UNS supports MQTT-style wildcard matching against its state dictionary:

- `+` matches exactly one topic level
- `#` matches zero or more remaining levels
- Example: `exxon/permian/+/+/esp/+/telemetry` returns all ESP telemetry across the Permian site

**Topic tree:** The namespace forms a hierarchical tree that mirrors the physical operation:

```
exxon/
  permian/
    north/
      pad-12/
        well/
          e-77/
            telemetry   ← last known measurements
            status      ← last known operating state
            birth       ← initial full-state snapshot
        esp/
          e-77/
            telemetry
            status
            birth
      pad-13/
        ...
    south/
      ...
```

---

## 6. Configuration Layer

The system uses a layered configuration approach:

- **Status mappings:** Per-source status code → canonical enum lookup tables
- **Unit conversions:** Conversion factor definitions (source unit → canonical unit)
- **Adapter registry:** Maps source type identifiers to adapter classes
- **Validation rules:** Range bounds for measurement fields

In early milestones, these are defined as Python constants. In the advanced milestone (M7), they are externalized to YAML files validated by Pydantic models — allowing new sources to be added via configuration only.

```yaml
# Example: source_mappings.yaml
sources:
  source_a:
    adapter: "CygNetAdapter"
    status_map:
      "P": "Producing"
      "S": "ShutIn"
      "X": "Offline"
    units:
      flow: { from: "bpd", to: "bpd", factor: 1.0 }
      pressure: { from: "psi", to: "psi", factor: 1.0 }
      temperature: { from: "fahrenheit", to: "fahrenheit", factor: 1.0 }
```

---

## 7. Design Principles

- **Pydantic-first:** All data boundaries are enforced by Pydantic models. No raw dicts cross layer boundaries.
- **Source systems remain unchanged:** Harmonization adapts to the source, never the reverse.
- **Deterministic transformations:** Same input always produces same output. No randomness, no external state.
- **Fail-fast with structured errors:** Invalid data is caught at the earliest possible boundary and routed to dead-letter with full context.
- **Explainable mapping:** Every canonical field carries lineage back to its source.
- **Configuration over code:** Source-specific details (status maps, unit factors) are data, not logic.
- **Strict validation at canonical boundary:** The canonical model is the quality gate. Upstream layers are permissive; the canonical model is not.
