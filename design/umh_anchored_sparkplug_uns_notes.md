# UMH-Anchored Sparkplug B UNS Notes

These notes describe a realistic home-lab architecture anchored on United Manufacturing Hub (UMH) Community, using Sparkplug B as the core industrial messaging and harmonization pattern, and floci as the local AWS-style IT/cloud emulation layer.[cite:80][cite:106][cite:112][cite:185] The goal is to build an end-to-end environment that feels production-like from Levels 1 through 4 while remaining based on open-source or free/community tools.[cite:3][cite:6][cite:68][cite:80][cite:185]

## Purpose

This architecture is meant to demonstrate how plant data can move from PLC-oriented OT systems into a Unified Namespace, then into historian, streaming, analytics, ML, and cloud-style IT services without requiring a real cloud account or paid software for the lab.[cite:80][cite:89][cite:182][cite:185] It is especially useful when the objective is to learn and prove the full data journey rather than just build a historian or dashboard.[cite:80][cite:83][cite:89]

UMH is the anchor because it provides an integrated open-source data infrastructure with MQTT, Kafka, historian/storage, visualization, and a management/data-model layer.[cite:80][cite:106][cite:112] floci extends that design by acting as a local AWS emulator for S3, Lambda, Kinesis, MSK, Athena, Glue, Step Functions, EventBridge, RDS, and other cloud-shaped services that many enterprise architectures expect downstream of the UNS.[cite:182][cite:184][cite:185]

## Why anchor on UMH

UMH Community is useful when the lab should move quickly toward a complete end-to-end story while still staying aligned with realistic industrial architecture.[cite:80][cite:106][cite:112] Instead of wiring every data-infrastructure component by hand, UMH gives a coherent stack with the kinds of interfaces and patterns commonly used in industrial IoT and UNS deployments.[cite:80][cite:112]

According to UMH’s architecture and product materials, UMH provides a data infrastructure centered around MQTT, Kafka, storage/historian, and modeling/visualization concepts suitable for industrial use.[cite:80][cite:106][cite:112] The Community License is free forever and can later be complemented with paid support or enterprise services without discarding the architecture developed in the lab.[cite:80]

## Architecture summary

A concise view of the architecture is:

1. **Level 0**: synthetic plus benchmark data representing sensors and actuators.[cite:145][cite:150]
2. **Level 1/2**: PLC-world representation through OpenPLC or PLC-style tags and addresses.[cite:21][cite:33][cite:167]
3. **Level 3 OT/UNS backbone**: UMH Community running MQTT, Kafka, historian/storage, dashboards, and plant data modeling.[cite:80][cite:106][cite:112]
4. **Level 3/4 SCADA and OT consumers**: Ignition Maker Edition or trial consuming Sparkplug B data and operating as an OT application on top of the UNS.[cite:3][cite:6][cite:81][cite:84]
5. **Level 4 IT/cloud emulation**: floci acting as local AWS for lake, eventing, orchestration, and analytics-style services.[cite:182][cite:184][cite:185]
6. **Cross-cutting**: Python services for data replay, synthetic generation, enrichment, ML training, and edge inference publishing via MQTT/Sparkplug.[cite:90][cite:92][cite:100][cite:104]

This creates a layered story that looks close to a production setup: OT systems and UNS on one side, IT/cloud consumers and pipelines on the other, with clear interfaces between them.[cite:80][cite:89][cite:185]

## Core OT and UNS roles

### Level 0: Synthetic and benchmark process reality

The intended design keeps only Level 0 synthetic.[cite:145][cite:150] Industrial benchmark datasets and Python-generated signals represent sensors, actuators, equipment states, and operational context.[cite:145][cite:150][cite:151] Those signals are then shaped to look like PLC memory or cryptic controller tags before being published upward.[cite:163][cite:167]

This matters because the project is not trying to show “clean analytics input.”[cite:150][cite:155] It is trying to show how messy controller-facing data becomes semantically harmonized through Sparkplug B and a Unified Namespace.[cite:162][cite:166][cite:168]

### Level 1/2: PLC-world representation

OpenPLC is a strong fit as a free/open-source controller stand-in because it behaves like a PLC runtime and can expose variables via industrial protocols such as Modbus TCP.[cite:21][cite:33] Even if some signals are produced directly by Python services, they should still be structured to resemble controller memory or cryptic tag names so the rest of the lab reflects real plant integration patterns.[cite:163][cite:167][cite:169]

This level exists to answer the real industrial problem: source systems often do not present clean semantic models.[cite:163][cite:167] Instead, they present address-based or cryptic names that later need to be mapped to enterprise-facing meanings.[cite:162][cite:168]

### Sparkplug B as the harmonization layer

Sparkplug B is the semantic and transport pattern that turns PLC-world structures into stable industrial MQTT messages.[cite:78][cite:166] Its node/device birth messages, metric definitions, aliases, and datatypes give a consistent model that downstream consumers can rely on.[cite:78][cite:110][cite:166]

In this UMH-anchored design, Sparkplug is the recommended way to move structured plant data into the UNS because it makes the relationship between source tags, asset identities, and semantic metrics explicit.[cite:162][cite:168][cite:89]

### UMH as the Level 3 UNS backbone

UMH acts as the core Level 3 data infrastructure.[cite:80][cite:106][cite:112] Based on its architecture and product pages, it provides a combination of MQTT, Kafka, historian/storage, visualization, and connector/data-model capabilities suitable for industrial data collection and harmonization.[cite:80][cite:106][cite:112]

The practical roles UMH can play in the lab are:

- **UNS event backbone** through MQTT and Kafka.[cite:80][cite:106]
- **Historian/time-series platform** through its bundled storage stack and integrated dashboards.[cite:80][cite:112]
- **Plant data modeling layer** for machine, line, and site structures that can align with Sparkplug identity choices.[cite:86][cite:106]
- **Operational management layer** for managing and observing the data infrastructure.[cite:80]

The advantage of anchoring on UMH is that many data-infrastructure concerns are already assembled, which lets more effort go into plant modeling, harmonization, and downstream analytics rather than infrastructure plumbing.[cite:80][cite:112]

## Ignition’s role in the UMH-anchored design

Ignition Maker Edition or trial is still valuable in a UMH-centered architecture because it acts as a realistic OT consumer of the UNS rather than as the owner of the data backbone.[cite:3][cite:6][cite:81][cite:84] This separation is useful because it mirrors how many real organizations operate: a common industrial data platform feeds multiple OT and IT applications.[cite:80][cite:89]

Ignition can be used for:

- HMI and dashboard views for operators or engineers.[cite:3][cite:6]
- Alarm visualization or basic control-room style views.
- Validation that Sparkplug-modeled assets can be consumed by SCADA tools in a way that is still practical for operations.[cite:81][cite:84]
- Demonstrating how an OT application subscribes to and consumes the same harmonized data that IT and ML tools use.[cite:84][cite:89]

Because Maker and trial are the same platform as licensed Ignition, the lab configuration is a realistic stepping stone to a future paid deployment.[cite:3][cite:6]

## Neo4j knowledge graph integration

### Why add Neo4j to the UMH-anchored architecture

Neo4j is a strong addition when the lab should include a **knowledge graph** that connects assets, tags, events, maintenance history, work orders, material flow, and enterprise context in a relationship-oriented model rather than relying only on time-series and relational stores.[cite:238][cite:242] Knowledge-graph approaches are increasingly used for digital-twin-style integration because they are well suited to connected industrial context spanning multiple systems.[cite:234]

In the UMH-anchored design, Neo4j should not replace UMH, the historian, or ERPNext.[cite:80][cite:89] Instead, it should sit beside them as a connected-context layer that preserves how physical assets, harmonized metrics, anomalies, maintenance actions, and enterprise objects relate to one another.[cite:234][cite:239]

### What Neo4j should model

A practical Neo4j model for this architecture should include nodes such as:

- **Site, area, line, cell, and asset** for physical hierarchy.
- **PLC or source tag** for brownfield identifiers.[cite:163][cite:167]
- **Sparkplug metric / semantic signal** for harmonized OT variables.[cite:166][cite:168]
- **Event** for faults, alarms, downtime, changeovers, and batches.
- **ERPNext business nodes** such as work orders, materials, assets, inventory movements, and maintenance actions.[cite:227][cite:233]

Important relationships include `PART_OF`, `HAS_METRIC`, `GENERATED_EVENT`, `RELATED_TO_WORK_ORDER`, `TRIGGERED_MAINTENANCE`, and `CONSUMED_MATERIAL`.[cite:234][cite:239] This structure makes cross-domain reasoning easier than relying on a historian alone.

### Where Neo4j sits in the UMH stack

Neo4j should sit on the **IT / knowledge / reasoning side** of the architecture, downstream of the harmonized UMH backbone and adjacent to ERP and analytical services.[cite:234][cite:239] A practical view is:

1. Level 0 replay and synthetic generation create plant behavior.[cite:145][cite:150][cite:151]
2. PLC-world structures or OpenPLC preserve source realism.[cite:21][cite:33][cite:163][cite:167]
3. Sparkplug B and UMH provide the harmonized OT/UNS backbone.[cite:78][cite:80][cite:106][cite:112]
4. OT applications such as Ignition and historian/dashboard services consume operational data.[cite:3][cite:6][cite:80][cite:112]
5. Integration services derive enterprise events and contextual relationships for ERPNext and Neo4j.[cite:227][cite:233][cite:238]
6. Neo4j becomes the graph layer connecting operational, semantic, and enterprise context.[cite:234][cite:239]

This means UMH remains the data backbone, while Neo4j adds relationship-rich context and advanced graph querying on top of that backbone.[cite:80][cite:234]

### How Neo4j integrates with UMH, Sparkplug, and ERPNext

Neo4j should consume from the **harmonized** side of the stack, using Sparkplug-structured data and UMH-managed downstream flows rather than raw disorganized source streams.[cite:78][cite:80][cite:89][cite:166] In practical terms, Python services or other integration processes can subscribe to UMH/Kafka or Sparkplug-derived streams and create graph nodes and relationships from them.[cite:80][cite:90][cite:238]

This can support patterns such as:

- Linking PLC/source tags to Sparkplug metric definitions and semantic asset nodes.[cite:163][cite:167][cite:168]
- Connecting events and anomalies to the assets and lines they affect.[cite:234]
- Linking ERPNext work orders and maintenance records to the equipment, batches, and events that produced them.[cite:227][cite:233]
- Building graph context for lineage, impact analysis, root-cause investigation, or future assistant workflows.[cite:239][cite:245]

This makes Neo4j a semantic extension of the UMH-anchored UNS rather than a competing backbone.[cite:80][cite:234]

### Python and Neo4j in the UMH-anchored design

Even though UMH provides the plant-side platform, Python remains the most practical implementation language for Neo4j integration because Neo4j provides an official Python driver and Python is already central to replay, enrichment, ML, and ERP integration across the architecture.[cite:90][cite:92][cite:238][cite:242] Python services can therefore create and update graph structures as a normal part of the overall data flow rather than as a disconnected side project.[cite:90][cite:97][cite:238]

### GraphRAG and future use cases

Neo4j also creates a path to GraphRAG and graph-assisted industrial copilots.[cite:239][cite:245] Neo4j’s GraphRAG Python tooling is intended for combining graph relationships with retrieval workflows, which could later support maintenance reasoning, fault-chain analysis, genealogy, and context-aware assistance in the lab.[cite:245]

### Neo4j resource links

- Neo4j Python driver GitHub: <https://github.com/neo4j/neo4j-python-driver> [cite:238]
- Neo4j Python driver on PyPI: <https://pypi.org/project/neo4j-driver/> [cite:242]
- Neo4j GraphRAG Python package: <https://github.com/neo4j/neo4j-graphrag-python> [cite:245]

## ERP / SAP-like integration with ERPNext

### Why ERPNext fits the UMH-anchored architecture

ERPNext is a strong open-source stand-in for SAP-like enterprise integration because it is positioned as open-source ERP software for manufacturing and can represent production, maintenance, logistics, and manufacturing-oriented business processes in one platform.[cite:227][cite:233] In the UMH-anchored design, that makes ERPNext a practical enterprise-side consumer of harmonized OT data.[cite:80][cite:227]

ERPNext should sit on the **enterprise / business application side** of the architecture, downstream of UMH and the Sparkplug-harmonized UNS.[cite:80][cite:89][cite:227] It should receive curated operational events and business-relevant state changes rather than every raw telemetry update.[cite:89][cite:227]

### What OT data should flow into ERPNext

Good ERPNext integration targets in the lab include:

- **Production / manufacturing**: work-order confirmations, completed counts, scrap counts, runtime/downtime summaries, batch completion, and machine or line state milestones.[cite:227]
- **Maintenance**: anomaly summaries, maintenance-triggering events, runtime thresholds, failure categories, and equipment condition indicators.[cite:233]
- **Logistics / inventory**: material consumption, inventory adjustments, finished-goods completion, WIP movement, and transfer-style business events inferred from harmonized line behavior.[cite:227][cite:233]

This reflects a realistic enterprise integration pattern because ERP systems generally consume aggregated events and transactions rather than high-frequency raw tags.[cite:89][cite:227]

### How ERPNext integrates into the UMH stack

A practical UMH-anchored ERPNext flow is:

1. Replay and synthetic services generate plant behavior.[cite:145][cite:150][cite:151]
2. PLC-world structures and Sparkplug publishers create harmonized OT data.[cite:21][cite:33][cite:78][cite:100]
3. UMH operates as the plant-side data backbone through MQTT, Kafka, storage, and dashboards.[cite:80][cite:106][cite:112]
4. Python or other integration services consume selected UMH/Kafka or Sparkplug-derived events and write curated business updates into ERPNext.[cite:80][cite:90][cite:227][cite:233]

In this role, ERPNext becomes the SAP-like system for work execution feedback, maintenance and asset actions, logistics/inventory context, and manufacturing business records beyond the OT layer.[cite:227][cite:233]

### Why ERPNext is useful here

Adding ERPNext strengthens the UMH-anchored architecture because it shows how a plant-side data platform feeds enterprise systems instead of ending at dashboards, historians, and cloud emulation alone.[cite:80][cite:89][cite:227] It gives the lab a realistic enterprise application destination for production, maintenance, and logistics signals that have already been harmonized in the UNS.[cite:227][cite:233]

### ERPNext resource links

- ERPNext manufacturing overview: <https://frappe.io/erpnext/open-source-manufacturing-erp-software> [cite:227]
- ERPNext GitHub repository: <https://github.com/frappe/erpnext> [cite:233]

## floci as the IT/cloud emulation layer

### What floci is

floci is a free, open-source local AWS emulator designed to expose AWS-shaped APIs for local development and testing.[cite:182][cite:184][cite:185] Its site and related materials describe support for a large set of AWS-like services through a local endpoint, including S3, DynamoDB, Kinesis, MSK, Lambda, Step Functions, EventBridge, RDS, Glue, Athena, OpenSearch, CloudWatch, and others.[cite:182][cite:184][cite:185]

That makes floci a strong fit for this lab because it lets the environment simulate an AWS-style enterprise landing zone without needing an actual AWS account.[cite:182][cite:185] In effect, UMH can represent the on-prem or plant-side data platform while floci represents the enterprise cloud platform that consumes and extends that data.[cite:80][cite:182][cite:185]

### Why floci fits this architecture

Many modern industrial architectures move data from OT and UNS systems into cloud-native services for lake storage, serverless processing, orchestration, analytics, and ML.[cite:73][cite:89] floci lets the lab imitate those target patterns locally, so the architecture can be designed in a cloud-compatible way from the beginning.[cite:182][cite:184][cite:185]

This is especially useful for learning and portability. Services developed against floci’s local AWS-like endpoints can later be pointed at actual AWS with much smaller changes than a full redesign would require.[cite:182][cite:184][cite:185]

### Specific roles floci can play

#### 1) Data lake and archival target

floci’s S3 emulation can act as the object-store landing zone for industrial data exported from UMH or Kafka pipelines.[cite:182][cite:185] This is useful for:

- Storing Parquet or CSV snapshots of historian or Kafka data.[cite:182][cite:185]
- Maintaining long-term analytical history separate from the operational historian.
- Feeding local AWS-style lakehouse patterns such as Glue catalog plus Athena querying.[cite:185]

This role matters because it separates operational storage from analytical storage in a way that resembles many real enterprise designs.[cite:80][cite:185]

#### 2) Streaming and eventing destination

floci supports AWS-shaped streaming and eventing services such as Kinesis, MSK, SQS, SNS, and EventBridge.[cite:185] Those can be used to emulate how industrial events leave the UMH backbone and enter broader enterprise integration patterns.

Examples include:

- UMH Kafka topics mirrored or transformed into floci MSK/Kinesis streams.[cite:80][cite:185]
- Operational alerts or state changes sent through EventBridge or SNS-style patterns.[cite:185]
- Queue-based decoupling for downstream batch or serverless jobs with SQS.[cite:185]

This helps demonstrate that the UNS is not only an OT construct; it is also a clean upstream source for enterprise event-driven architecture.[cite:89][cite:185]

#### 3) Serverless processing and orchestration

floci supports Lambda and Step Functions, which lets the lab simulate cloud-style batch and event-driven processing locally.[cite:182][cite:185] That opens several useful patterns:

- Trigger a Lambda-like function when a file lands in S3-floci.[cite:185]
- Use Step Functions to orchestrate replay backfills, feature computation, or model-scoring pipelines.[cite:185]
- Use EventBridge to schedule recurring analytics or data-quality checks.[cite:185]

This is a very practical way to demonstrate how harmonized industrial data could feed automated business and analytics workflows in a cloud platform without leaving the local lab.[cite:182][cite:185]

#### 4) Analytics catalog and query layer

floci includes Glue and Athena emulation as part of its AWS-shaped offering.[cite:185] These can be used to:

- Register datasets written to S3-floci into a catalog.
- Query historical Parquet data with Athena-like semantics.
- Demonstrate cloud-warehouse or lakehouse consumption of UNS-origin data in a way that is familiar to enterprise teams.[cite:185]

This complements DuckDB well: DuckDB is ideal for local developer-first analytics, while floci emulates the AWS-facing interfaces and workflows an enterprise data team may later expect.[cite:67][cite:72][cite:185]

#### 5) Relational and search endpoints

floci’s RDS and OpenSearch emulation can stand in for downstream application storage and search systems.[cite:185] For example:

- Store curated analytical outputs or asset metadata in RDS-like Postgres or MySQL.[cite:185]
- Index event logs or enriched equipment timelines into OpenSearch-like endpoints.[cite:185]

These are optional, but they make the lab more complete when the goal is to show that a UNS can feed many enterprise data products, not only dashboards and ML notebooks.[cite:89][cite:185]

#### 6) Cloud-style observability

floci’s CloudWatch-style metrics and logging can help emulate how platform teams observe applications and pipelines on the IT side.[cite:185] Python services that consume from UMH or floci can emit logs and metrics into CloudWatch-like endpoints to show how operational and cloud observability might coexist.[cite:185]

## Python services in the UMH-anchored design

Even though UMH anchors the infrastructure, Python still plays a major role in this architecture.[cite:90][cite:92][cite:100] Python is a natural fit for:

- Replaying benchmark datasets as time-ordered plant signals.[cite:145][cite:150][cite:151]
- Generating additional analog and discrete synthetic signals.[cite:151][cite:156]
- Injecting realistic data messiness such as missing points or spikes.[cite:136][cite:141][cite:156]
- Mapping PLC-style variables into Sparkplug metrics.[cite:163][cite:167][cite:100]
- Consuming Kafka or S3-style data on the IT side and running ML or feature pipelines.[cite:67][cite:72][cite:185]
- Publishing edge inference results back into the UNS via MQTT/Sparkplug.[cite:97][cite:100][cite:104][cite:105]

The key Python transport libraries remain Paho MQTT and PySparkplug.[cite:90][cite:99][cite:100][cite:104] This keeps the lab aligned with your preference for Python while still benefiting from UMH as a platform layer.[cite:90][cite:100]

## Recommended end-to-end flow

A practical end-to-end pattern for the UMH-anchored lab is:

1. Load and augment benchmark datasets in Python.[cite:145][cite:150][cite:151]
2. Translate them into PLC-style tags or controller-facing structures.[cite:163][cite:167]
3. Publish harmonized Sparkplug B data into UMH’s MQTT backbone.[cite:78][cite:80][cite:106]
4. Let UMH fan that data into historian, dashboards, and Kafka-based downstream paths.[cite:80][cite:112]
5. Use Ignition as an OT consumer of the harmonized Sparkplug/UNS data.[cite:81][cite:84]
6. Bridge or export selected data into floci services such as S3, Athena, Lambda, Kinesis, or EventBridge.[cite:182][cite:185]
7. Run analytics and ML processes on the floci side or in Python services using floci as the cloud-shaped API layer.[cite:182][cite:185]
8. Publish inference or enriched outputs back into the UNS through Sparkplug B, where they become visible to both OT and IT consumers.[cite:97][cite:100][cite:104]

This round-trip is what makes the lab especially valuable: it shows not only OT-to-IT flow, but also IT-to-edge feedback, which is necessary for demonstrating ML deployment and operationalization.[cite:71][cite:73][cite:101]

## Why this is a strong educational architecture

This architecture is strong for education because it stays close to real-world industrial patterns while remaining accessible and reproducible.[cite:80][cite:89][cite:185] It teaches the distinction between source-system tags, semantic harmonization, operational storage, event streaming, and enterprise cloud consumption without requiring a large production environment.[cite:162][cite:168][cite:185]

It is also upgrade-friendly. The same overall design can later move from:

- Ignition Maker/trial to licensed Ignition.[cite:3][cite:6]
- UMH Community to UMH with support or enterprise deployment practices.[cite:80][cite:106]
- floci endpoints to actual AWS services.[cite:182][cite:184][cite:185]
- Python replay/generation code to real plant data sources or vendor gateways.[cite:90][cite:100][cite:167]

That means the architecture is not a throwaway lab. It is a learning environment that can gradually evolve toward something operationally serious.[cite:80][cite:89][cite:185]

## Practical links

### UMH

- UMH docs: <https://umh.docs.umh.app/docs/> [cite:112]
- UMH architecture: <https://umh.docs.umh.app/docs/architecture/> [cite:106]
- UMH data infrastructure: <https://umh.docs.umh.app/docs/architecture/data-infrastructure/> [cite:80]

### floci

- floci site: <https://floci.io/floci/> [cite:185]
- floci GitHub: <https://github.com/floci-io/floci> [cite:180]

### Supporting components

- Ignition Maker Edition docs: <https://www.docs.inductiveautomation.com/docs/8.1/other-editions/ignition-maker-edition> [cite:6]
- Paho MQTT: <https://pypi.org/project/paho-mqtt/> [cite:90]
- PySparkplug: <https://github.com/matteosox/pysparkplug> [cite:100]
- OpenPLC references: [cite:21][cite:33]

## Working conclusion

In a UMH-anchored Sparkplug B UNS architecture, UMH should be treated as the plant-side data backbone, Sparkplug B should be treated as the harmonization and messaging contract, Ignition should be treated as a realistic OT consumer, and floci should be treated as the local AWS-style enterprise platform that receives, stores, analyzes, and operationalizes industrial data.[cite:80][cite:84][cite:89][cite:182][cite:185]

That combination gives a powerful lab setup: realistic OT and UNS behavior on one side, realistic cloud and enterprise patterns on the other, and a clear migration path to paid or production-grade systems later without invalidating the structure you build now.[cite:3][cite:6][cite:80][cite:106][cite:182][cite:185]
DOCEOF && ls -l output/umh_anchored_sparkplug_uns_notes.md
