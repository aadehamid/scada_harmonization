# Reference Material

Superseded source documents and external references kept **for consultation, not as current scope**.
The active, authoritative project definition is
[`../design/PROJECT_CHARTER.md`](../design/PROJECT_CHARTER.md).

The two business-case folders originated as separate ER&I AI Innovation Challenge business cases. The
reusable **technical patterns** in them have been extracted into the charter (§7); the business /
market / sales framing is **not** part of this project. Consult them only for the details noted below.

> **Local-only:** the subfolders are gitignored (private business-case material / third-party
> content). This README is tracked so the repository documents that the reference material exists
> and what it is for.

## What to consult each for

| Folder | Originally | Consult it for (maps to charter plane) |
|--------|-----------|-----------------------------------------|
| `docs/` | **ISHE** — Industrial Semantic Harmonization Engine (SCADA tag harmonization) | **Plane 1 (Harmonize):** canonical Pydantic model hierarchy, ISA-95 identity model, per-field lineage, transform primitives (unit/status/timestamp), and the in-memory UNS semantics used as a **reference spec / test oracle** for the real Sparkplug B UNS. |
| `engineering_drawing_business_case/` | **EngiGraph** — engineering-drawing knowledge graph | **Plane 3 (Contextualize):** ISO 15926 / DEXPI ontology foundation, multi-level ontology architecture, node/edge vocabulary, GraphRAG pattern, and graph-algorithm use cases (isolation-path, centrality, impact analysis). |
| `enterprise_it_ot_deck/` | **External slide deck** — "Enterprise IT vs Manufacturing/OT" (third-party consulting material; drop the slide images here) | **The end-to-end walkthrough (Thread A):** the ten-handoff order-to-cash flow, the L0–L4 systems vocabulary (CRM/ERP/WMS/MES/SCADA/PLC…), integration pains, and organizational red flags. Used as the *transaction-thread* script in [`../design/E2E_WALKTHROUGH.md`](../design/E2E_WALKTHROUGH.md) — which adds the two threads the deck lacks (telemetry up, decision/control back). |

## What was deliberately NOT carried forward

- Market sizing, TAM/revenue projections, persona pain tables, competitor matrices, named clients,
  and challenge-submission framing.
- The narrow O&G-only scope (Well/ESP; CygNet/Wonderware/Ignition). Keep the *patterns*, swap the
  *examples* for the multi-site process/chemicals assets the home lab simulates.
- EngiGraph's CV/VLM P&ID-extraction pipeline (symbol detection, OCR, VLM) — the home lab
  synthesizes graph topology directly, so only the ontology + graph + query layers are relevant.
