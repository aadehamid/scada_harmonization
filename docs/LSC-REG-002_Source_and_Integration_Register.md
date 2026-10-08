# LSC-REG-002 Source and integration register

Version: 0.1. Status: DRAFT inventory and phase-gated integration guide.
Prepared 2026-10-08 UTC (2026-10-07 US/Central).

This register gives sources and interfaces stable IDs for document traceability.
It does not declare planned services implemented. Runtime status belongs in
[HANDOFF.md](../HANDOFF.md), section 2. The
[charter](LSC-001_Problem_Statement_and_Project_Charter.md) owns phase gates and
architecture. The [L0 record](LSC-005_Phase_1_Data_Record.md) and
[datasheet](LSC-006_Phase_1_Datasheet.md) own current input artifacts and figures.

## Source inventory

IDs below are draft documentation identifiers. Local plant names and source
business keys remain unchanged. Owners describe source responsibility; named
steward assignments remain pending.

| ID | Source and shape | Authority and evidence | Route and gate |
| --- | --- | --- | --- |
| SRC-01 | TEP `.RData` and prepared wide Parquet | Published process dynamics; L0 record/datasheet own selected artifacts and hashes | L0 ingestion/augmentation/replay; preserve native cadence under L0 contract |
| SRC-02 | IIoT source zip and prepared Parquet | Published synthetic machine snapshot; datasheet owns durable artifacts | L0 replay; do not imply the snapshot supplies the 1-second generated stream |
| SRC-03 | Python-generated machine stream | Seeded generator and golden fixtures own reproducible L0 values | Separate `iiot` stream under L0 contract; do not mix cadence with TEP |
| SRC-04 | Rotterdam local OT | Site publisher supplies cryptic/local metrics, source time, quality | Site Mosquitto then forwarder, Phases 2/4a |
| SRC-05 | Corpus Christi local OT | Site publisher supplies compound tags; clock-skew fixture is phase-gated | Site Mosquitto then forwarder, Phases 2/4a/4c |
| SRC-06 | Beaumont local OT | Real OpenPLC/Modbus supplies raw counts; mapping supplies EU conversion | Site publisher/forwarder, Phase 4b |
| SRC-07 | Geismar local OT | Real OPC-UA supplies values and StatusCodes | Site publisher/forwarder, Phase 4b |
| SRC-08 | Plant role-A Postgres MES/material tables | MES owns lots, production windows, consumed/produced material records | Poll CDC then Debezium, Phase 5a |
| SRC-09 | Plant role-A Postgres LIMS/quality tables | LIMS owns sample result/disposition | CDC then identity reconciliation, Phase 5a |
| SRC-10 | Plant role-A Postgres CMMS/log tables | CMMS owns maintenance status; plant logs own source events | CDC then identity reconciliation, Phase 5a |
| SRC-11 | Unit 100 Rev B vector PDF and drawing-name schedule | Reviewed sheet/evidence owns engineering topology; LSC-007 owns fixture details | Vector extraction then scanned/degraded variants, Phase 5b.1 |
| SRC-12 | ERPNext records in MariaDB | ERPNext owns enterprise business records | API/integration and derived `erp_shadow`, Phase 5b.2 |
| SRC-13 | Mapping configuration, later `metric_registry` | Governed metric meaning, units, cadence, owner, transform and lineage | Forwarder and promotion validation; schema review precedes dependent phases |

## Integration inventory

The charter section 14 owns session state, recovery, and storage promotion.
Latency budgets, credentials, selected versions, retention, and named owners must
be filled from implementation evidence at the listed gate.

| ID | Source to target and contract | Delivery/recovery boundary | Acceptance dependency |
| --- | --- | --- | --- |
| INT-01 | SRC-01/02/03 to L0 frames and replay; Pydantic L0 record | Deterministic input/cache/seed/clock identity | LSC-004 fixtures and canonical hashes |
| INT-02 | Local PLC-world publisher to site Mosquitto; Sparkplug 3.0 | Birth/aliases/sequence/death and site Primary Host STATE | Phase 2 observed lifecycle and library conformance |
| INT-03 | Site forwarder to central EMQX; new canonical Sparkplug session | C1 OT-initiated TLS; on-disk N12 buffer and historical reconnect | Phase 4a equivalence/ACL/TLS; Phase 4c outage/overflow drill |
| INT-04 | Central EMQX to retained enterprise MQTT topics | ISA-95 republish under N1/N2; source time and quality preserved | Late subscriber observes retained enterprise state, not retained Sparkplug DATA |
| INT-05 | Central Sparkplug to Kafka; `CanonicalTelemetry`, canonical asset key | C2 IT connection to iDMZ; stateful alias resolution and idempotent consumer effects | N6 birth-state decode and per-asset partition workload |
| INT-06 | Local/canonical telemetry to Timescale historian | N9 unique time/metric identity; original timestamps and historical backfill | Phase 3 schema and Phase 4c outage/compression observation |
| INT-07 | SRC-08/09/10 to Kafka through Python poll; `ChangeEvent` JSON | Snapshot-compatible first read; documented missed-delete/intermediate-update limits | Phase 5a.1 observed workload and restart cursor |
| INT-08 | SRC-08/09/10 to Kafka through Connect/Debezium; Avro/Apicurio | C3 iDMZ conduit; snapshot/log position, delete/tombstone, WAL guard | Phase 5a.2 real log CDC, DDL/converter test and WAL recovery |
| INT-09 | Canonical CDC to IT-side ODS and Neo4j | Identity-map validity, domain survivorship, source authority | Phase 5a/5b ambiguous-match and source-update/delete tests |
| INT-10 | SRC-11 to engineering model and graph | Evidence/revision/review status survives publication | Phase 5b.1 vector/scanned/degraded stage evidence |
| INT-11 | SRC-12 to derived enterprise context; order integration down | ERP API authority and explicit C6 zone crossing | Phase 5b.2 contract, source lineage, and no undeclared IT-to-OT connection |
| INT-12 | Kafka/file drops to Bronze, then Spark Silver/Gold | Immutable evidence; registry validation at promotion; linked dead letter/redrive | Phase 6 determinism, lateness/dedup, product completeness and replay |

Kafka topic offsets identify transport positions. They do not replace physical
event identity or a source system's primary key. A tombstone must remain
distinguishable from malformed empty input. Product run IDs identify computation
attempts rather than new physical observations.

## Capture boundaries and acceptance questions

These questions identify implementation gaps. They are draft review gates,
not newly approved contracts. They supplement the charter's existing phase exits.

| Interface | Question or failure case | Evidence needed before implementation acceptance |
| --- | --- | --- |
| INT-03/05 | Which fields prove cross-site equivalence without discarding provenance? | A fixture compares canonical meaning, unit, value, quality, and event time while preserving different site/source lineage. |
| INT-05 | What happens when birth state is missing? | Consumer withholds undecodable aliases, requests rebirth, and resolves the new alias space. No guessed metric reaches Kafka. |
| INT-08 | What happens after the WAL guard removes needed history? | Reviewed stop/resnapshot procedure records log position, snapshot boundary, and source/derived-state reconciliation. |
| INT-09/12 | Which lot owns a reading exactly on a time boundary? | Review an interval convention, then prove adjacent windows do not double-count. A half-open interval is a candidate, not a decision. |
| INT-12 | What can Bronze replay actually reconstruct? | A capture manifest distinguishes original PLC evidence from already canonical Kafka records and original CDC envelopes. |
| INT-12 | Which delayed records fit the live watermark? | A workload covers duplicates, in-budget late records, and historical recompute beyond the budget. |
| INT-12 | How do late inputs revise a published product? | Reviewed output version, completeness rule, correction policy, and consumer notification. Missing values remain explicit. |

Bronze is unchanged from its integration input under N27. Kafka telemetry is
already harmonized under N6, so its Bronze copy cannot reconstruct missing PLC
bytes. Preserve raw forwarder/dead-letter evidence where N28 requires it. The
existing L0 warehouse does not prove a Phase 6 medallion pipeline.

Kafka orders records within a partition, rather than globally across partitions.
Transactions do not by themselves prove exactly-once effects in an external
Postgres or Neo4j sink. N9 therefore requires idempotence evidence for each sink.
[Kafka 4.0 design](https://kafka.apache.org/40/design/design/), inspected
2026-10-08 UTC, supports this distinction.

PostgreSQL's `max_slot_wal_keep_size` can bound retained WAL but make required
history unavailable. N29's guard needs a recovery procedure as well as a limit.
[PostgreSQL 17 replication settings](https://www.postgresql.org/docs/17/runtime-config-replication.html),
inspected 2026-10-08 UTC, describes that trade-off. Debezium's snapshot and
delete/tombstone behavior supplies the INT-08 test cases.
[Debezium PostgreSQL connector 3.4](https://debezium.io/documentation/reference/3.4/connectors/postgresql.html)
was inspected on the same date. Research versions do not replace charter version gates.

Spark watermarks bound retained streaming state. Records outside the delay have
no processing guarantee. Keep Bronze for explicit historical recompute and choose
the delay against the actual outage workload.
[Spark 4.0.1 Structured Streaming](https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html),
inspected 2026-10-08 UTC, explains the limit. A checkpoint is not raw evidence or
a product correction policy.

## Register maintenance and unresolved fields

Before building an interface, add its selected schema/model version, source and
target deployment identifiers, owner, expected cadence or latency, retry limit,
checkpoint, retention, security identity, error categories, replay procedure,
and evidence links. Keep secrets outside this register. Record unknown values
as pending rather than fabricate an SLA or permission grant.

A registry/mapping change can require replay without a source-data change.
Keep the source record identity and record the new mapping version. If a source
key changes, preserve the old identity interval so historical joins remain
explainable. The independent review must check that every implemented interface
has one documented authority, capture boundary, and recovery test.

## Reference evidence

The reference repo was inspected at main commit
`01027a84be5d453cbb4e2ea091e4884729918b15` on 2026-10-08 UTC.
[PPC-007](https://github.com/aadehamid/pearland-petroleum-corporation/blob/01027a84be5d453cbb4e2ea091e4884729918b15/docs/PPC-007_Data_Integration_Event_and_Orchestration_Architecture.md)
provides the interface-field pattern and orchestration responsibilities.
[PPC-008](https://github.com/aadehamid/pearland-petroleum-corporation/blob/01027a84be5d453cbb4e2ea091e4884729918b15/docs/PPC-008_Data_Products_Medallion_and_KPI_Store_Architecture.md)
provides the product/maturity distinction. These are reference documentation
claims. No PPC runtime was executed for this register, and its industry sources
and KPI definitions are not inherited by LSC.

The [reuse assessment](LSC-REF-001_Technology_Roles_and_Reuse_Assessment.md)
owns candidate technology comparisons. This register does not independently
adopt Dagster, DuckLake, OpenLineage, or other reference components.
