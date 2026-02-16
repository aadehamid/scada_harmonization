# Implementation Plan
## Milestones M0–M7

---

## M0 — Foundation

- Create repo structure
- Add fixtures
- CLI skeleton
- Define canonical ISA-95 context model

---

## M1 — Source Adapters

- Implement Source A adapter
- Implement Source B adapter
- Implement Source C adapter
- Output raw extracted events

---

## M2 — Canonical Model

- Implement Pydantic canonical telemetry model
- Add validation rules
- Parse valid fixtures successfully

---

## M3 — Transformation Layer

- Unit conversion functions
- Status normalization map
- Timestamp parsing utilities
- Add tests

---

## M4 — ISA-95 + UNS Envelope

- Topic builder
- Output envelope builder
- Integration tests

---

## M5 — Lineage Tracking

- Track source → canonical mapping
- Track conversions
- Include lineage in meta section

---

## M6 — Dead-Letter & Error Handling

- Structured error model
- Dead-letter writer
- Validation failure routing

---

## M7 — Config-Driven Mapping (Advanced)

- YAML-based mapping config
- Adapter refactor to use config
- Add new source via config only

---

## Stretch Goals

- Add CLI flags (strict vs lenient mode)
- Add metrics summary output
- Add property-based tests
- Add JSON schema export
