# datagen: the 6-layer synthetic data pipeline

Only **Level 0 (the physical world) is synthetic**; everything above behaves like real
software. This package produces that Level 0 world from benchmark datasets (TEP, Industrial
IoT) plus Phase 1 OT extras, in six layers
(`design/synthetic_data_generation_notes.md`). The L0 record and replay identity live in
`design/PHASE1_L0_CONTRACT.md`. Lots, work-order, and material IDs stay Phase 5
(`context_export`).

| Layer | Subpackage | Role | Phase |
|-------|-----------|------|-------|
| 1 | `ingestion/` | load/validate/normalize benchmark datasets, cache replay forms | 1 |
| 2 | `augmentation/` | OT extras only: synthetic signals, states, messiness | 1 |
| 3 | `plc_mapping/` | friendly variable → site-specific cryptic PLC tag | 2 |
| 4 | `sparkplug/` | PLC-world values → Sparkplug B publish (births, aliases, NDATA) | 2 |
| 5 | `context_export/` | business events/IDs for ERPNext + Neo4j flows | 5 |
| 6 | `replay/` | cadence, simulated clock, speed factor, backfill vs live | 1 |

Folders are placeholders until their phase starts (YAGNI: no pre-written stubs).
