# mappings — the three-stage mapping table (THE SPINE)

> **Status: folder reserved — content not written yet.**
> The Diagram 1 walkthrough runs **in parallel** and does **not** gate this
> table (owner lock 2026-08-19). Build this table well and the rest is plumbing.

What will live here (charter §6 + §8.1 Phase 0 exit criteria): the
`friendly source variable → site-specific PLC tag → Sparkplug metric + asset path` table,
carrying unit, range, cadence, asset class, site context, downstream ERP/graph IDs, and
governance metadata (owner/"gatekeeper", definition, lineage), plus the §14 columns —
raw→EU scaling (N17), per-site quality mapping (N10), `source_cadence` (N8),
`interpolation_type` (N11), UNECE Rec 20 unit codes (N18). Validated by Pydantic models;
one measurement defined across all 4 sites. Grown-up home: `ods_core.metric_registry`.
