
---

# `docs/ARCHITECTURE.md`

```markdown
# Architecture Design
## SCADA Harmonization Service

---

## 1. System Overview

The system follows a clean pipeline architecture:

Input → Adapter → Raw Extracted Event → Transformation → Canonical Model → UNS Output

---

## 2. ISA-95 Context Model

The canonical identity follows ISA-95 Part 2 hierarchy:

| ISA-95 Level | Upstream Mapping |
|--------------|-----------------|
| Enterprise   | Exxon           |
| Site         | Permian         |
| Area         | North           |
| Cell         | Pad-12          |
| Equipment Class | Well        |
| Equipment ID | E-77            |

This hierarchy is enforced in canonical output and UNS topic generation.

---

## 3. Logical Architecture

            +------------------+
Incoming JSON → | Source Adapter |
+------------------+
↓
+------------------+
| Raw Extracted |
+------------------+
↓
+------------------+
| Transform Layer |
| - Units |
| - Status |
| - Timestamp |
+------------------+
↓
+------------------+
| Canonical Model |
+------------------+
↓
+------------------+
| UNS Envelope |
+------------------+


---

## 4. Core Components

### 4.1 Adapters
- Extract raw values
- Identify ISA-95 context
- Preserve original keys

### 4.2 Transform Layer
- Deterministic unit conversion
- Status normalization
- Timestamp normalization

### 4.3 Canonical Model
- Strict validation rules
- Enforced types and ranges
- Enum-based status

### 4.4 Lineage Module
Tracks:
- Source key → canonical field mapping
- Conversion applied
- Any coercion performed

### 4.5 Dead-Letter Handler
- Structured error model
- JSONL output

---

## 5. UNS Topic Generation

Derived purely from ISA-95 hierarchy:

enterprise/site/area/cell/equipment_class/equipment_id/telemetry


---

## 6. Design Principles

- Source systems remain unchanged
- Harmonization is centralized
- Deterministic transformations
- Explainable mapping
- Strict validation at canonical boundary

