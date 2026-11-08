# LSC-REF-001. Reference stack reuse assessment

Version: 1. Status: draft assessment for PR review. Candidate additions remain
proposals. This record does not amend approved component choices.

Purpose: assess the PPC stack before choosing different tools for this lab.
Dependencies: [the charter](LSC-001_Problem_Statement_and_Project_Charter.md),
especially sections 4.1, 8, 13, and 14. This document owns the reference comparison;
the charter owns component decisions. HANDOFF section 2 owns implementation status.

## Evidence and selection rule

The owner asked to reuse the reference stack where it makes sense. PPC was
inspected at revision `01027a84be5d453cbb4e2ea091e4884729918b15`.
Its [technology map](https://github.com/aadehamid/pearland-petroleum-corporation/blob/01027a84be5d453cbb4e2ea091e4884729918b15/docs/PPC-002_Enterprise_Architecture_and_Technology_Stack.md)
describes intended roles. Its mostly empty component directories do not prove
that the stack ran. No reference application was executed for this assessment.

Reuse an existing shared choice first. For a missing capability, assess the PPC
component before proposing a substitute. Keep the lab's real-protocol exercises,
zone boundaries, deterministic transforms, and learning sequence. A component
addition needs a specific use case and acceptance evidence at its phase gate.

## Shared choices already in the project

The following choices already match PPC. Their decisions remain in the charter;
this comparison adds no dependency or installation.

| Shared component | LSC responsibility | Existing authority |
| --- | --- | --- |
| Cloudflare R2 | Durable L0 warehouse; keep the existing project bucket | LSC-005 and LSC-006 |
| PostgreSQL | Plant transactional source and separate IT-side ODS | Charter sections 4 and 14 N16 |
| ERPNext | Curated enterprise records and the order-to-cash thread | Sections 6, 8, and decision 18 |
| Debezium and Kafka | Log-based CDC and enterprise event transport | Phase 5a; section 14 N26 |
| DuckDB | Interactive analytical queries over Parquet | Sections 4 and 13 L4 |
| Neo4j Community | Reconciled graph context and GraphRAG | Sections 7 and 13 L5 |
| Grafana OSS | Historian views and technical monitoring | Sections 4 and 13 L7 |
| MLflow | Experiments, model registry, and publish-to-score lesson | Sections 13 L6 and 14 N34 |
| Databricks Free Edition | Later managed-lakehouse comparison after the hand-built lesson | Section 13.6 |

These are shared design choices, not claims that all services are implemented.
Read [HANDOFF.md](../HANDOFF.md) before using a service.

## Candidates for actual gaps

Each row is an assessment proposal. A phase review must choose the exact version,
check its license and dependencies, and run the stated experiment before adoption.
The current task installs none of them.

| PPC component | Fit in this lab | Recommendation and evidence needed |
| --- | --- | --- |
| OpenLineage | Run-level lineage for Spark inputs and outputs | Assess a Phase 6 pilot. Reconcile dataset IDs with the existing registry and reproduce a failed run without publishing successful lineage. |
| OpenMetadata | Catalog discovery across metrics, ODS, lakehouse, and graph | Assess when these components exist. Demonstrate one catalog view that consumes existing owners and definitions without becoming a second authority. |
| Great Expectations | Data quality checks over analytical datasets | Compare with current Pydantic and pytest checks at Phase 6. Adopt only for a missing dataset-level rule with a demonstrated failure and quarantine path. |
| AML and Azimutt | Review of relational source and ODS schemas | Assess a generated view of the existing schema. Keep Pydantic boundary contracts authoritative and project diagrams in Eraser. |
| Dagster | Scheduling and recovery across multiple analytical jobs | Assess when Phase 6 has dependent jobs. Demonstrate deterministic backfill and recovery with existing package code before adding an orchestrator. |
| DuckLake | Cataloged analytical storage alongside DuckDB | Compare at the lakehouse gate. Preserve real Spark ETL; test the required Spark read/write path, replay, schema changes, and rollback before selecting a format. |
| Jena/Fuseki | Formal semantics beyond the minimal operational graph | Assess only if a concrete ontology query or validation rule needs it. Start with the charter's ISO 15926/DEXPI-aligned Neo4j model. |
| Plotly Dash | The Phase 6 recommendation and approval console | Assess against the charter's console behavior. Require identity, TTL checks, authorized approval, command audit, and telemetry read-back. |
| StatsForecast/MLForecast, DoWhy/EconML, PyMC, OR-Tools | Forecasting, causal, uncertainty, or optimization experiments | Evaluate only against a Phase 6 question and held-out baseline. Keep causal claims separate from predictive accuracy and retain human approval for actions. |
| Ollama, LangGraph, Langfuse | Local inference, controlled copilot workflow, and evaluation | Assess at Phase 7 after graph retrieval works. Verify model rights, cited answers, failure recovery, and absence of unauthorized command execution. |

OpenLineage documents a dataset/job/run model and a Spark integration. That makes
it a candidate for the run-lineage gap, not proof of compatibility with this lab.
[OpenLineage documentation](https://openlineage.io/docs/), inspected 2026-10-08 UTC.

DuckLake documents a SQL catalog with Parquet storage and lists a Spark client
whose maturity must be assessed. The current charter requires Spark ETL; DuckDB
availability alone cannot close that requirement.
[DuckLake documentation](https://ducklake.select/docs/stable/), inspected 2026-10-08 UTC.

## Choices with a different approved responsibility here

| PPC component or source | LSC treatment | Reason and reconsideration point |
| --- | --- | --- |
| PostgreSQL pgvector | Keep Neo4j's native vector index | Charter L5.2 selects it for GraphRAG. Revisit only if a separate document-retrieval requirement warrants another store. |
| Cloudflare D1 and Workers | Keep workflow state and command audit in the approved zone design | Hosting an approval workflow externally needs a demonstrated use case and a reviewed conduit. R2 reuse does not require these services. |
| Superset | Keep the present Grafana/notebook path | Charter section 13.3 defers a BI platform. Revisit for a defined analytical consumer after governed datasets exist. |
| Twenty, logistics MySQL, edge SQLite | Keep MES/LIMS/CMMS Postgres sources and the established site protocol roster | PPC's source diversity serves its commercial model. LSC already has different source dialects and real PLC/protocol exercises. |
| EIA, NOAA, EPA, PHMSA feeds | Do not add external feeds to the current build | No approved phase exit needs these observations. A later use case can assess relevant feeds individually. |
| EPM/ECE project coupling | Keep the current charter's domain and boundaries | PPC's upstream project dependencies do not establish dependencies for this lab. |

## External reference vocabularies assessed (not adopted)

This section sits outside the PPC comparison: it records third-party vocabularies assessed
against the charter, with the review that keeps a domain reference from becoming an adopted
dependency. Each row is a proposal; a phase review must still choose the exact version and
demonstrate the stated use before any adoption.

| Vocabulary | Verdict | Basis and reconsideration point |
| --- | --- | --- |
| **Brick Schema** (brickschema.org) — building-automation ontology, BSD-3-Clause, RDF + SHACL rule sets + QUDT units | **Reference only; not adopted.** Brick is **buildings-centric** — its introduction names the subsystems "HVAC, lighting, fire, security and so on" — so it cannot carry the lab's canonical process vocabulary (reactors, columns, process topology): Plane 3's ontology stays ISO 15926/DEXPI-aligned (§12 #13). It **does overlap** on generic equipment the lab's machines use — `Pump` and `Valve` (with their subclass blocks) and `Compressor` exist in Brick v1.5.0's equipment definitions — which is exactly why a crosswalk is plausible but also never sufficient on its own. Borrowed as **patterns**: (1) Brick's point semantics are explicit — its point modules separate what each point means (measured / desired / commanded / observed / alarm / parameter) — the same kind of semantic explicitness the lab builds through metric semantics in `metric_registry`, wire datatypes in Sparkplug, and the ISA-18.2 alarm model in §14 N20; this is a worked precedent for keeping those meanings distinct, not a schema to import (the charter's objects are not shaped like an Alarm point class); (2) QUDT quantity kinds are the real-world precedent for N18's "QUDT-style unit nodes later" hook; (3) SHACL rule sets shipped alongside the ontology match the §12 #13 `pyshacl` gate; (4) the `ref:` external-reference pattern (BACnet / time-series / IFC pointers from semantics to data) parallels the mapping table's join keys. **Bounded Phase 5b/7 proposal, two parts:** (a) an optional **vocabulary-mapping crosswalk** using plain SKOS mapping relations between class terms (lab ontology ↔ Brick) — the standard SKOS mapping use, kept outside `identity_map` because class-level similarity establishes no same-referent evidence and cannot use §14 N36's identity match rules; (b) the §14 N36 exercise stays as designed — typing **identity_map rows for concrete identities** (the N15 seeded case, `P-101A` vs `EQ-4471`) with `skos:closeMatch` only where same-referent evidence exists. Reconsider at Phase 5b.1 (crosswalk) or Phase 7 (GraphRAG interoperability); a reconsideration re-inspects the release in force. |

Evidence, inspected 2026-11-08 UTC: release and license from the Brick repository
The release and license are from the Brick repository
([github.com/BrickSchema/Brick](https://github.com/BrickSchema/Brick), BSD-3-Clause; v1.5.0
published 2026-10-29, with nightly builds); the stable-release table,
Turtle/JSON-LD/RDF-XML distributions, and tooling notes from
[brickschema.org/resources](https://brickschema.org/resources/) (1.4.4, 2025-05-01; 1.3.0,
2022-10-12); the OWL-to-SHACL move from the v1.3.0 GitHub release notes
("moving from an OWL-based ontology to a SHACL-based ontology",
[github.com/BrickSchema/Brick/releases/tag/v1.3.0](https://github.com/BrickSchema/Brick/releases/tag/v1.3.0));
the subsystem list from the Brick introduction page
("HVAC, lighting, fire, security and so on",
[docs.brickschema.org/intro.html](https://docs.brickschema.org/intro.html)); the point-type
taxonomy and external-reference pattern from the Brick v1.5.0 point modules
(`bricksrc/sensor.py`, `setpoint.py`, `command.py`, `status.py`, `alarm.py`,
`parameter.py`) and documentation;
the Python package from PyPI (brickschema 0.8.0: its default dependencies are `owlrl`,
`pyshacl`, `pyshifty`, `rdflib`, and `reasonable`; the default SHACL engine is `shifty`
with `engine="pyshacl"` as the explicit alternative, and the default OWL 2 RL reasoner is
`reasonable`). `pyshacl` and `rdflib` are the libraries already pinned in §4.1, but a future
adoption would also bring the three default dependencies the lab does not use — assessed
before any install. The domain comparison (buildings vs. process) is read against the
charter's §2 domain table and against Brick v1.5.0's equipment definitions
(`bricksrc/equipment.py`, which defines `Pump`, `Compressor`, and `Valve`).

## Documentation coverage

Existing documents already cover the domain, synthetic data, L0 contract, Phase 1
records, drawings, learning, architecture, governance, roadmap, and phase exits.
The [master index](LSC-000_Master_Index.md) points at their owners. Rewrite those
records where clarity needs work. Add a document only when it owns missing guidance
or evidence with a different update cycle.

The reference comparison was missing, so this record is new. Detailed source
readiness and integration evidence may need a register; repeated charter summaries
do not need separate documents. Later phase-specific contracts should be written
with their implementation slice, using the selected PPC components where suitable.

## Questions to close at the existing phase gates

These are review questions and bounded proposals. They do not rewrite charter
contracts or authorize infrastructure changes.

| Gate | Missing implementation detail | Proposed evidence |
| --- | --- | --- |
| Phase 0 mapping boundary | Which incoming types may be coerced? | Parse each site's syntax once. Test accepted and rejected Python and wire inputs before publishing a canonical record. Pydantic strict mode has type-specific exceptions for JSON input; select settings deliberately. [Pydantic strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/). |
| Phase 4c zone monitoring | How does central monitoring receive OT-zone metrics under N21? | Prometheus federation pulls selected series through `/federate`. Direct IT-to-OT scraping violates N21. Review a conduit such as OT-initiated export to an iDMZ receiver, then prove connection direction and preserved labels. The receiver and protocol remain unselected. [Prometheus federation](https://prometheus.io/docs/prometheus/latest/federation/). |
| Phase 6 multi-object publication | When is a new run complete for readers? | Assess immutable run paths with a validated manifest published last. Interrupt an upload and prove readers reject the partial run. Verify the chosen store's operations and concurrent-writer behavior. |
| Phase 5/6 recovery | Which state survives independently of sensor replay? | Include identity stewardship, engineering approvals, dead-letter dispositions, and command audit in a restore drill. These decisions cannot be reconstructed from readings alone. |

R2 documents strong object consistency and cache-related exceptions. That does
not establish a transaction across separate object writes. The proposed manifest
boundary needs its own failure experiment. The S3 compatibility table must be
checked for each operation used.
[R2 consistency](https://developers.cloudflare.com/r2/reference/consistency/),
[S3 compatibility](https://developers.cloudflare.com/r2/api/s3/api/), inspected
2026-10-08 UTC. No warehouse object was written during this documentation work.
