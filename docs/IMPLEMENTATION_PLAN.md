# Implementation Plan
## Milestones M0–M9

---

## M0 — Foundation and Fixtures

**Goal:** Establish the project skeleton, dependencies, and realistic test data.

### Project Structure
```
scada_harmonizer/
├── pyproject.toml
├── README.md
├── src/
│   └── scada_harmonizer/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point
│       ├── pipeline.py         # Pipeline orchestrator
│       ├── models/
│       │   ├── __init__.py
│       │   ├── sources.py      # Source-specific Pydantic models
│       │   ├── canonical.py    # Canonical telemetry models
│       │   ├── envelope.py     # UNS envelope model
│       │   ├── errors.py       # Dead-letter entry model
│       │   └── lineage.py      # Field lineage model
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── registry.py     # Adapter registry / source detection
│       │   ├── source_a.py     # CygNet adapter
│       │   ├── source_b.py     # Wonderware adapter
│       │   └── source_c.py     # Ignition/MQTT adapter
│       ├── transforms/
│       │   ├── __init__.py
│       │   ├── units.py        # Unit conversion functions
│       │   ├── status.py       # Status normalization
│       │   └── timestamps.py   # Timestamp parsing
│       ├── uns/
│       │   ├── __init__.py
│       │   ├── namespace.py    # InMemoryUNS (retained state, RBE, birth certs)
│       │   ├── topics.py       # Topic builder and sanitizer
│       │   └── wildcards.py    # MQTT-style wildcard matching
│       └── writers/
│           ├── __init__.py
│           └── jsonl.py        # JSONL output writers
├── tests/
│   ├── __init__.py
│   ├── test_adapters.py
│   ├── test_transforms.py
│   ├── test_canonical.py
│   ├── test_pipeline.py
│   ├── test_equivalence.py    # Cross-source equivalence tests
│   └── test_uns.py            # UNS simulation tests (state, RBE, wildcards)
└── fixtures/
    ├── source_a/
    │   ├── valid_well.json
    │   ├── valid_esp.json
    │   └── broken_missing_ts.json
    ├── source_b/
    │   ├── valid_well.json
    │   ├── valid_esp.json
    │   └── broken_bad_pressure.json
    ├── source_c/
    │   ├── valid_well.json
    │   ├── valid_esp.json
    │   └── broken_malformed.json
    └── equivalence/
        ├── well_e77_source_a.json
        ├── well_e77_source_b.json
        └── well_e77_source_c.json
```

### Tasks
- Initialize `pyproject.toml` with dependencies: `pydantic>=2.0`, `typer`, `pytest`, `pytest-cov`
- Create package structure as above
- Create CLI skeleton using Typer (accepts input path, output directory)
- **Design and write fixture files** for all three sources — both valid and broken variants
- Design **equivalence fixtures**: the same physical event (Well E-77 at a specific timestamp) represented in all three source formats
- Verify: `pytest` runs, CLI prints help

---

## M1 — Canonical Model and Error Model

**Goal:** Define the canonical contract and the error contract first — these are the targets everything else adapts to.

**Pydantic features exercised:** Enum, constrained types (`ge`, `le`), `Field()`, `model_validator`, Optional fields, nested models.

### Tasks
- Define `EquipmentClass` enum (`Well`, `ESP`)
- Define `CanonicalStatus` enum (`Producing`, `ShutIn`, `Offline`, `Unknown`)
- Define `DataQuality` model (quality enum + flags list)
- Define `FieldLineage` model (source_key, original_value, conversion, canonical_field)
- Define `CanonicalTelemetry` base model with ISA-95 identity fields
- Define `WellTelemetry` and `ESPTelemetry` submodels with equipment-specific measurements and range constraints
- Define `DeadLetterEntry` model (error_id, source_system, timestamp, errors list, original_payload)
- Add `model_validator` for cross-field data quality checks (e.g., zero flow while producing)
- **Tests:** Construct canonical models from dicts, verify validation catches out-of-range values, verify data quality flags fire

---

## M2 — Source Adapters

**Goal:** Build adapters that parse each source format and extract ISA-95 identity + raw measurements.

**Pydantic features exercised:** `Field(alias=...)`, discriminated union, `model_validator` for structural checks.

### Tasks
- Define `RawExtractedEvent` intermediate model (normalized field names, original units preserved, ISA-95 identity, source metadata)
- Define `SourceAEvent` Pydantic model with aliases for CygNet-style keys
- Define `SourceBEvent` Pydantic model with aliases for Wonderware-style keys
- Define `SourceCEvent` Pydantic model for nested Ignition/MQTT structure
- Implement Source A adapter: parse compound tag name to extract ISA-95 hierarchy
- Implement Source B adapter: map discrete fields to ISA-95 hierarchy
- Implement Source C adapter: parse MQTT topic path to extract ISA-95 hierarchy
- Implement adapter registry with source auto-detection (discriminated union on payload shape)
- **Tests:** Each adapter correctly parses its valid fixtures into `RawExtractedEvent`; auto-detection routes correctly

---

## M3 — Error Handling and Dead-Letter Routing

**Goal:** Establish error handling early so all subsequent milestones can rely on it.

### Tasks
- Implement dead-letter handler: catch `ValidationError`, extract field-level errors, build `DeadLetterEntry`
- Implement JSONL writer for dead-letter output
- Implement JSONL writer for canonical output
- Wire error routing: adapter failure → dead-letter, transform failure → dead-letter, validation failure → dead-letter
- **Tests:** Broken fixtures from each source produce dead-letter entries with correct error messages and preserved original payloads

---

## M4 — Transformation Layer

**Goal:** Convert raw extracted events into canonical units, statuses, and timestamps.

**Pydantic features exercised:** `field_validator` for unit conversion, custom types.

### Tasks
- Implement unit conversion functions (m³/day → bpd, kPa → psi, °C → °F) with constants
- Implement status normalization with per-source lookup tables
- Implement timestamp parsing (ISO, epoch seconds, epoch milliseconds → UTC datetime)
- Wire transforms: `RawExtractedEvent` → apply conversions → construct `CanonicalTelemetry`
- Record lineage during transformation (source key, original value, conversion applied)
- **Tests:** Unit conversion round-trips within tolerance; all status codes map correctly; all timestamp formats parse to identical UTC datetime

---

## M5 — Pipeline Orchestrator

**Goal:** Wire all stages together into a complete, runnable pipeline.

### Tasks
- Implement `pipeline.py`: read input → detect source → adapt → transform → validate → route (canonical output or dead-letter)
- Wire CLI to pipeline: `scada-harmonize run --input fixtures/ --output output/`
- Handle batch processing: iterate over files in input directory
- Produce summary on completion: count of processed, succeeded, dead-lettered
- **Tests:** End-to-end pipeline test — run all fixtures, verify correct outputs and dead-letter entries

---

## M6 — UNS Simulation: Namespace, Topics, and State

**Goal:** Implement the Unified Namespace simulation — the in-memory retained state layer, topic hierarchy with data categories, report-by-exception filtering, birth certificates, and wildcard queries. This is what makes the project a UNS demonstration, not just a data transformer.

**Pydantic features exercised:** `model_serializer` for output formatting, `computed_field` for birth certificates, nested models.

### Tasks

#### 6a. Topic Builder
- Implement topic builder: ISA-95 fields → sanitized, lowercase, hyphenated topic string
- Support data category suffixes: `telemetry`, `status`, `birth`
- Sanitize all segments: lowercase, spaces → hyphens, strip special characters
- **Tests:** Topic generation is deterministic; special characters are stripped

#### 6b. UNS Envelope
- Define `UNSEnvelope` Pydantic model (topic, event_time, payload, context, meta, data_quality)
- Define `BirthCertificate` Pydantic model (full-state snapshot with all telemetry + context)
- Integrate envelope construction into the pipeline (after canonical validation)

#### 6c. In-Memory UNS
- Implement `InMemoryUNS` class with:
  - `state: dict[str, UNSEnvelope]` — retained state per topic (last known value)
  - `publish(envelope)` — updates retained state, appends to history
  - `get_state(topic)` — returns current retained value for a topic
  - `export_to_jsonl(path)` — writes history to file
- **Tests:** After processing events, `get_state()` returns the latest payload per topic

#### 6d. Report-by-Exception
- Before writing to output, compare incoming payload against retained state
- If telemetry values are unchanged from the retained state, suppress the publish
- Still update the `event_time` in retained state (the value was confirmed, just not changed)
- **Tests:** Processing the same event twice produces output only on the first occurrence; changed values produce new output

#### 6e. Birth Certificates
- Track which equipment IDs have been seen (set of strings)
- On first contact, emit a `BirthCertificate` to the `birth` data category topic
- Birth certificate includes all telemetry values, ISA-95 context, and equipment metadata
- **Tests:** First event for a device emits a birth record; subsequent events do not

#### 6f. Wildcard Queries
- Implement MQTT-style wildcard matching against the state dictionary:
  - `+` matches exactly one topic level
  - `#` matches zero or more remaining levels
- Expose via CLI: `scada-harmonize query "exxon/+/+/+/esp/+/telemetry"`
- Expose as Python API: `uns.query("exxon/permian/#")` → list of matching envelopes
- **Tests:** `+` matches single level; `#` matches remaining levels; non-matching patterns return empty; exact matches work

---

## M7 — Lineage Tracking (continued)

**Goal:** Ensure every canonical field carries full provenance back to its source.

### Tasks
- Finalize `FieldLineage` model: source_key, original_value, conversion, canonical_field
- Build lineage records during adapter and transform stages
- Embed lineage dict in canonical event's `meta.field_lineage`
- Ensure lineage survives through to UNS envelope output
- **Tests:** Every field in a canonical event has a corresponding lineage entry; lineage correctly reflects conversions applied

---

## M8 — Config-Driven Mapping (Advanced)

**Goal:** Externalize source-specific configuration to YAML so new sources can be added without code changes.

**Pydantic features exercised:** Pydantic models for config validation.

### Tasks
- Define YAML schema for source mappings (adapter class, status map, unit conversions)
- Define Pydantic models to validate the YAML config on load
- Refactor adapters to read from config rather than hardcoded constants
- Demonstrate: add a hypothetical Source D via config only (no new Python code)
- **Tests:** Config loads and validates; pipeline produces correct output using config-driven adapters

---

## Stretch Goals

- **CLI flags:** Strict vs lenient mode (strict rejects Suspect quality; lenient passes them through)
- **Metrics summary:** Output a JSON report with counts per source, per equipment class, per quality level
- **Property-based tests:** Use Hypothesis to generate random payloads and verify the pipeline never crashes (only dead-letters)
- **JSON Schema export:** Use `model_json_schema()` to export the canonical contract as a shareable JSON Schema document
- **Cross-source equivalence test suite:** Automated verification that the same physical event from all three sources produces byte-identical canonical output
- **4th source type via config:** Prove M8 works by adding a new source entirely through YAML configuration
- **UNS state snapshot export:** Dump the full in-memory namespace state as a JSON tree (mirrors the topic hierarchy structure)
- **Death certificates:** Detect stale topics (no update within a configurable window) and emit offline sentinel records
- **Two-tier namespace:** Maintain both a `_raw/` namespace (pre-contextualization) and the canonical namespace side by side, demonstrating the raw→contextualized data flow
