# Hand-Built Sparkplug B UNS Notes

These notes describe a hand-built home-lab architecture for a Sparkplug B-centered Unified Namespace (UNS) using only open-source tools or free/community editions, with no dependency on United Manufacturing Hub as the backbone.[cite:3][cite:6][cite:21][cite:33][cite:68][cite:78][cite:185] The intent is to understand each architectural layer directly by assembling the components yourself, while still keeping the design realistic enough that paid or enterprise alternatives can later replace individual parts without invalidating the overall model.[cite:39][cite:45][cite:68][cite:80][cite:89]

## Purpose

The hand-built path is best when the goal is to learn the moving parts of a modern industrial data architecture rather than start from a platform bundle.[cite:68][cite:71][cite:78] Instead of inheriting MQTT, Kafka, storage, dashboards, and modeling from UMH, this architecture defines each role explicitly so you can understand what each component contributes to the final plant-to-cloud story.[cite:68][cite:71][cite:89]

This architecture is still intended to be realistic.[cite:89] It keeps only Level 0 synthetic, represents Level 1/2 through PLC-world structures, uses Sparkplug B to harmonize that data into an MQTT-based UNS, stores and analyzes it in OT and IT layers, and uses floci to emulate the AWS-shaped enterprise cloud side locally.[cite:21][cite:33][cite:78][cite:89][cite:182][cite:185]

## Architectural summary

A concise summary of the hand-built architecture is:

1. **Level 0**: benchmark datasets plus Python-generated signals represent sensors, actuators, and operating context.[cite:145][cite:150][cite:151]
2. **Level 1/2**: OpenPLC or a PLC-like memory/tag structure represents controller-facing integration.[cite:21][cite:33][cite:167]
3. **Level 3 transport and harmonization**: MQTT broker plus Sparkplug B structure create the UNS backbone.[cite:68][cite:78][cite:89]
4. **Level 3 OT systems**: Ignition Maker Edition or trial, historian/TSDB, and Grafana consume or store operational data.[cite:3][cite:6][cite:35][cite:40]
5. **Level 3/4 streaming and analytical infrastructure**: Kafka or equivalent plus Parquet/object storage and DuckDB build the IT analytics path.[cite:39][cite:45][cite:67][cite:72]
6. **Level 4 cloud/IT emulation**: floci emulates AWS-style object storage, streaming, orchestration, and analytics services locally.[cite:182][cite:184][cite:185]
7. **Cross-cutting**: Python services handle replay, synthetic generation, mapping, enrichment, analytics, and inference publishing.[cite:90][cite:92][cite:100][cite:104]

Unlike the UMH-anchored pattern, there is no platform that pre-bundles these roles.[cite:80][cite:112] Every service is selected and wired intentionally, which is both the main challenge and the main educational benefit.[cite:68][cite:71][cite:89]

## Why choose the hand-built path

The hand-built route is useful when the project needs transparency, portability, and deep understanding.[cite:68][cite:71] It makes the interfaces between controller data, MQTT/Sparkplug harmonization, storage, event streaming, analytics, and IT/cloud patterns visible rather than abstracted away.[cite:78][cite:89]

This matters because a Unified Namespace is easy to talk about conceptually but only becomes concrete when you explicitly decide:

- Where the semantic mapping happens.[cite:162][cite:166]
- What owns historian storage versus event streaming.[cite:35][cite:39][cite:45]
- How OT applications and IT applications each consume the same harmonized signals.[cite:84][cite:89]
- How cloud-style data products are fed from the industrial event backbone.[cite:73][cite:182][cite:185]

With a hand-built lab, each of those decisions becomes visible and testable.[cite:68][cite:89]

## Level 0: Synthetic and benchmark process reality

Only Level 0 should be synthetic in this design.[cite:145][cite:150] Benchmark datasets and Python-generated signals create realistic sensor, actuator, and equipment-state behavior, but everything above that point should behave like a real OT/IT stack.[cite:145][cite:150][cite:151][cite:167]

The recommended dataset strategy is:

- Use the **Industrial IoT Dataset (Synthetic)** for machine-oriented equipment behavior such as motors, compressors, conveyors, or predictive-maintenance style assets.[cite:145]
- Use the **Tennessee Eastman Process** dataset for process-oriented multivariable behavior such as tanks, reactors, loops, and fault scenarios.[cite:150][cite:155]
- Add Python-generated contextual signals such as valve state, run mode, counts, downtime, and OEE-style indicators that most benchmark datasets do not provide directly.[cite:151][cite:156]

This gives the lab both realistic process dynamics and operational context.[cite:145][cite:150][cite:151] It also supports a strong story: only the physical world is simulated, while the PLC, messaging, storage, analytics, and cloud-like layers are real software systems configured as a production-like stack.[cite:21][cite:33][cite:68][cite:185]

## Level 1/2: PLC-world representation

### OpenPLC and PLC-style tags

OpenPLC is a strong open-source stand-in for a PLC because it supports industrial controller concepts and can expose data over protocols such as Modbus TCP.[cite:21][cite:33] Even when values are generated in Python, they should be shaped to look like PLC memory addresses or cryptic controller tags before being published into the broader data stack.[cite:163][cite:167][cite:169]

Examples of this include:

- Address-based identifiers such as `N7:20`, `MW100`, or `DB10.DBD4`.[cite:167]
- Cryptic tag names such as `FIC101_PV`, `P201_RUNFB`, or `MTR04_AMP`.[cite:163][cite:169]

This level is important because many real plants do not expose a semantic model at the control layer.[cite:163][cite:167] They expose memory maps, sparse naming conventions, and controller-specific structures that later need harmonization.[cite:162][cite:168]

### Why this matters to the UNS story

If the lab skipped the PLC-world layer and sent friendly semantic names directly from Python into MQTT, it would lose one of the core educational lessons of a UNS: the transition from cryptic, source-system data to clean, enterprise-usable data.[cite:162][cite:166][cite:168] Keeping the PLC-world layer visible makes Sparkplug B and the harmonization process meaningful rather than cosmetic.[cite:78][cite:89][cite:162]

## Sparkplug B and MQTT as the backbone

### Broker choices

The recommended open-source MQTT broker choices are:

- **Mosquitto**, for a minimal, lightweight lab broker.[cite:68]
- **EMQX OSS**, for a more feature-rich industrial IoT broker with an easier path to enterprise editions later.[cite:68][cite:70]

Either broker can serve as the central MQTT transport layer for the UNS.[cite:68] EMQX OSS is often the better choice if the lab wants more broker-like features, while Mosquitto is easier when minimal footprint and simplicity matter more.[cite:68]

### Why Sparkplug B instead of plain MQTT JSON

Sparkplug B provides a consistent industrial topic and payload model with node and device births, metric aliases, datatypes, and lifecycle awareness.[cite:78][cite:166] That structure is what elevates MQTT from a generic pub/sub fabric to a real industrial messaging and harmonization layer.[cite:78][cite:89][cite:168]

In a hand-built architecture, Sparkplug B is especially useful because it prevents every publisher and consumer from inventing incompatible ad hoc conventions.[cite:78][cite:89] It gives a standard contract for how controller-derived values become reusable UNS metrics across SCADA, historian, analytics, and cloud-style consumers.[cite:84][cite:89][cite:166]

### Python Sparkplug services

Python should be the default implementation language for custom publishers and replay services in this architecture.[cite:90][cite:92][cite:100] The core Python transport stack is:

- **Paho MQTT** for MQTT connectivity.[cite:90][cite:99]
- **PySparkplug** for Sparkplug B publishing and metric modeling.[cite:100][cite:104][cite:105]

This lets the hand-built architecture remain highly flexible: Python can replay benchmark data, publish births and updates, consume UNS topics, enrich data, and later publish inference results back into the same semantic structure.[cite:92][cite:97][cite:100][cite:104]

## SCADA and OT consumers

### Ignition’s role

Ignition Maker Edition or trial is a good fit as the main SCADA/HMI tool in the hand-built stack.[cite:3][cite:6] It is the same platform used commercially, which means any UDT structures, screens, or consumption patterns developed in the lab can carry forward into a paid deployment.[cite:3][cite:6]

In this architecture, Ignition should be treated as an OT consumer of the UNS rather than the owner of the UNS itself.[cite:84][cite:89] That means Sparkplug and MQTT define the industrial data backbone, while Ignition validates that an OT application can consume harmonized data for visualization, alarming, and operator-facing applications.[cite:81][cite:84]

### Historian choices

A hand-built architecture needs an explicit historian choice because no platform bundle is making that decision for you.[cite:35][cite:39][cite:40] Good free/open-source options include:

- **InfluxDB OSS** for a simple, strong time-series option with a clear cloud/enterprise path later.[cite:35][cite:40]
- **TimescaleDB Community** if PostgreSQL compatibility and relational joins matter.[cite:39][cite:48]
- **QuestDB OSS** if high-ingest, SQL-oriented time-series access is attractive.[cite:37][cite:45]

The choice depends on the rest of the lab. Timescale is especially appealing if you already use Postgres or want stronger SQL semantics; InfluxDB is convenient when the historian is primarily operational time-series storage.[cite:35][cite:39][cite:48]

### Grafana as visualization

Grafana OSS is a natural dashboard and trending layer for the hand-built architecture.[cite:40][cite:45] It can sit beside Ignition rather than replace it: Ignition provides SCADA-style views, while Grafana gives broader engineering and analytical trends across historian and IT-side data sources.[cite:40][cite:45]

## Streaming, batch, and analytics path

### Kafka or equivalent

A hand-built UNS architecture benefits from having an explicit streaming backbone on the IT side, even if MQTT remains the plant-side transport.[cite:39][cite:45][cite:73] Apache Kafka OSS is the most natural choice because it is widely used for streaming pipelines and has direct analogs in managed enterprise platforms.[cite:39][cite:45]

Kafka’s role here is not to replace MQTT or Sparkplug in OT.[cite:73][cite:89] Its role is to support downstream analytics, stream processing, lake ingestion, event replay, and enterprise integration once data leaves the immediate OT context.[cite:39][cite:45][cite:73]

### Batch and lakehouse pattern

A practical pattern is:

- MQTT/Sparkplug in OT for plant-side real-time semantics.[cite:78][cite:89]
- Historian/TSDB for operational time-series retention.[cite:35][cite:39][cite:40]
- Kafka for event streaming to IT.[cite:39][cite:45]
- Parquet files in object storage for batch analytics and ML feature creation.[cite:67][cite:72]
- DuckDB for developer-friendly analytical SQL over Parquet.[cite:67][cite:72]

This layered approach keeps operational and analytical needs separated while still allowing them to consume the same harmonized signals.[cite:39][cite:45][cite:72][cite:89]

### DuckDB’s role

DuckDB is a strong choice for IT-side analytics in a lab because it works extremely well with Parquet and local workflows.[cite:67][cite:72] It is especially useful for:

- Feature exploration and ad hoc analytical SQL.
- Joining historian exports with business context.
- Producing training datasets for ML.
- Prototyping data products before moving them to managed warehouse or lakehouse services.[cite:67][cite:72]

DuckDB is not the operational historian and not the MQTT backbone.[cite:67][cite:72] Its role is the analytical query engine that sits beside the streaming and storage layers.

## Neo4j knowledge graph integration

### Why add Neo4j in the hand-built stack

Neo4j is a strong addition when the lab should include a **knowledge graph** that captures relationships across assets, tags, events, maintenance history, production context, and enterprise objects rather than relying only on time-series and relational stores.[cite:238][cite:242] Knowledge-graph approaches are increasingly used for digital-twin-style data integration because they represent connected industrial context well across heterogeneous systems.[cite:234]

In the hand-built architecture, Neo4j should be treated as a connected-context layer, not as a replacement for the MQTT broker, historian, or ERP.[cite:89] Its role is to preserve and query the relationships between physical assets, semantic metrics, anomalies, work orders, material flow, and maintenance actions in a way that complements the rest of the stack.[cite:234][cite:239]

### What Neo4j should model

A practical graph model for this lab should include nodes such as:

- **Site, area, line, cell, and asset** for physical hierarchy.
- **PLC tag / source tag** for cryptic controller-facing identifiers.[cite:163][cite:167]
- **Metric / signal** for Sparkplug or derived semantic variables.[cite:166][cite:168]
- **Event** for faults, downtime, alarms, batches, and maintenance-triggering conditions.
- **ERP objects** such as work orders, assets, materials, and stock movements once ERPNext is integrated.[cite:227][cite:233]

The graph should emphasize relationships such as `PART_OF`, `HAS_METRIC`, `GENERATED_EVENT`, `TRIGGERED_MAINTENANCE`, `FULFILLS_WORK_ORDER`, and `CONSUMED_MATERIAL`.[cite:234][cite:239] Those relationships make it easier to answer cross-domain questions that are awkward in a historian alone.

### Where Neo4j sits in the hand-built stack

Neo4j should sit on the **IT / context / reasoning side** of the hand-built architecture, downstream of Sparkplug-harmonized data and alongside ERP/integration services.[cite:234][cite:239] A good mental model is:

1. Level 0 replay/generation creates plant behavior.[cite:145][cite:150][cite:151]
2. PLC-world structures preserve source realism.[cite:21][cite:33][cite:163][cite:167]
3. MQTT + Sparkplug create the harmonized UNS backbone.[cite:68][cite:78][cite:166]
4. Historian and SCADA layers consume operational data.[cite:3][cite:6][cite:35][cite:39]
5. Integration services write selected context into ERPNext and Neo4j.[cite:227][cite:233][cite:238]
6. Neo4j ties OT structure, event history, and ERP context into a graph suitable for advanced querying and graph-assisted applications.[cite:234][cite:239]

This keeps concerns separated: the broker carries events, the historian stores time series, ERPNext owns business records, and Neo4j owns connected context.[cite:89][cite:227][cite:234]

### How Neo4j integrates with Sparkplug, OT data, and ERPNext

Neo4j should consume from the **harmonized** side of the architecture rather than from raw unstructured source values whenever possible.[cite:78][cite:89][cite:166] In practical terms, Python or other integration services should subscribe to Sparkplug topics or Kafka-fed derivatives and use those to populate graph entities and relationships.[cite:39][cite:45][cite:90][cite:238]

That allows the graph to preserve useful traceability such as:

- PLC/source tag to semantic metric mappings.[cite:163][cite:167][cite:168]
- Asset to event and event to downtime/fault relationships.[cite:234]
- Work order to line, machine, batch, and output relationships once ERPNext is connected.[cite:227][cite:233]
- Maintenance action to anomaly, runtime threshold, or failure event relationships.[cite:233][cite:234]

This is one of the most practical reasons to add Neo4j: it creates a connected layer spanning OT and enterprise records without forcing everything into one schema or one database style.[cite:234][cite:239]

### Python and Neo4j in the hand-built stack

Even though this note is architecture-centric rather than Python-centric, Python remains the most practical custom integration language for Neo4j because Neo4j provides an official Python driver and Python is already present elsewhere in the lab for replay, data preparation, and analytics.[cite:90][cite:92][cite:238][cite:242] That makes it straightforward to build graph-loading and graph-update services without introducing a separate integration language purely for the graph layer.

### GraphRAG and future use cases

Neo4j also creates an upgrade path toward GraphRAG or graph-assisted operational copilots.[cite:239][cite:245] Neo4j’s GraphRAG tooling for Python is meant to combine graph relationships with retrieval workflows, which could later support troubleshooting assistants, lineage queries, maintenance reasoning, and impact analysis across the industrial stack.[cite:245]

### Neo4j resource links

- Neo4j Python driver GitHub: <https://github.com/neo4j/neo4j-python-driver> [cite:238]
- Neo4j Python driver on PyPI: <https://pypi.org/project/neo4j-driver/> [cite:242]
- Neo4j GraphRAG Python package: <https://github.com/neo4j/neo4j-graphrag-python> [cite:245]

## ERP / SAP-like integration with ERPNext

### Why ERPNext fits the hand-built architecture

ERPNext is a strong open-source stand-in for SAP-like enterprise integration because it is positioned as open-source ERP software for manufacturing and can represent manufacturing, inventory, and broader operational business context in one platform.[cite:227][cite:233] For the scope you identified—production, maintenance, logistics, and manufacturing—it is a practical enterprise-side destination for harmonized OT data in this lab.[cite:227][cite:233]

In the hand-built Sparkplug B UNS design, ERPNext should sit on the **enterprise / business application side** of the stack, downstream of the harmonized OT data backbone.[cite:89][cite:227] It should not receive every raw telemetry value; instead, it should receive curated operational events and business-relevant updates derived from the UNS.[cite:89][cite:227]

### What OT data should flow into ERPNext

Good ERPNext integration targets in the lab include:

- **Production / manufacturing**: work-order confirmations, completed counts, scrap counts, runtime and downtime summaries, batch completion, and line-state-based production milestones.[cite:227]
- **Maintenance**: maintenance-triggering events, anomaly summaries, runtime thresholds, equipment condition indicators, and failure/downtime classifications.[cite:233]
- **Logistics / inventory**: material consumption, finished-goods completion, inventory adjustments, WIP movement, and transfer-style events inferred from line activity.[cite:227][cite:233]

This is a realistic ERP integration pattern because enterprise systems like SAP or ERPNext usually consume curated transactions and events rather than high-frequency raw tag streams.[cite:89][cite:227]

### How ERPNext integrates into the hand-built stack

A practical hand-built ERPNext flow is:

1. Replay and synthetic services generate realistic plant behavior.[cite:145][cite:150][cite:151]
2. PLC-world structures preserve source-system realism.[cite:21][cite:33][cite:163][cite:167]
3. Sparkplug B and MQTT create the harmonized UNS layer.[cite:68][cite:78][cite:166]
4. SCADA and historian systems consume that data operationally.[cite:3][cite:6][cite:35][cite:39]
5. Python or other integration services consume selected harmonized events and write business-relevant updates into ERPNext.[cite:90][cite:227][cite:233]

In this role, ERPNext becomes the SAP-like enterprise system for work execution feedback, maintenance records, inventory/logistics context, and manufacturing state beyond the OT layer.[cite:227][cite:233]

### Why ERPNext is useful in this lab

Adding ERPNext makes the hand-built architecture more complete because it demonstrates how a UNS feeds enterprise systems rather than stopping at dashboards and historians.[cite:89][cite:227] It gives a realistic destination for production confirmations, maintenance workflows, and material/logistics events and therefore strengthens the plant-to-enterprise story of the lab.[cite:227][cite:233]

### ERPNext resource links

- ERPNext manufacturing overview: <https://frappe.io/erpnext/open-source-manufacturing-erp-software> [cite:227]
- ERPNext GitHub repository: <https://github.com/frappe/erpnext> [cite:233]

## floci as the cloud/IT emulation layer

### Why include floci in a hand-built design

floci is a free, open-source local AWS emulator with support for a broad set of AWS-shaped APIs and services, including S3, Lambda, Kinesis, MSK, Glue, Athena, EventBridge, Step Functions, RDS, and more.[cite:182][cite:184][cite:185] In the hand-built architecture, floci becomes the cloud-side landing zone that makes the lab look like it feeds enterprise cloud patterns without needing an actual AWS account.[cite:182][cite:185]

This matters because the hand-built path is not only about OT basics.[cite:89] It is also about showing a full plant-to-enterprise pattern where the UNS can drive cloud-style data lake, analytics, orchestration, and ML workflows.[cite:73][cite:182][cite:185]

### Specific roles floci can play

#### 1) S3-style data lake

floci’s S3 emulation can receive Parquet or CSV snapshots exported from Kafka consumers, historian exports, or Python pipelines.[cite:182][cite:185] This gives the lab a cloud-shaped data lake for long-term analytical storage and lakehouse-style workflows.[cite:185]

#### 2) Kinesis/MSK-style streaming destination

floci can emulate Kinesis and MSK, making it possible to test how UNS-derived streams might be forwarded into AWS-style enterprise eventing patterns.[cite:185] This is especially useful if the long-term target architecture includes managed streaming or cloud-native data products.

#### 3) Lambda and Step Functions

floci’s Lambda and Step Functions support can emulate event-driven processing, scheduled transformations, and orchestration workflows.[cite:182][cite:185] This is useful for:

- Triggering feature calculations on new data drops.
- Running enrichment or alerting functions.
- Orchestrating model training, scoring, or backfill routines.

#### 4) Glue and Athena

Glue and Athena emulation make it possible to catalog and query object-store data in an AWS-shaped way.[cite:185] This complements DuckDB: DuckDB is ideal for local development and fast iteration, while floci emulates the cloud service interfaces an enterprise data team may later adopt.[cite:67][cite:72][cite:185]

#### 5) RDS and OpenSearch

floci’s RDS and OpenSearch endpoints can be used for downstream application patterns such as metadata storage, curated marts, or searchable event logs.[cite:185] These are optional but useful when the lab should show that a UNS can feed not just historians and dashboards, but many application and platform services.[cite:89][cite:185]

### Where floci sits in the stack

In the hand-built architecture, floci should sit clearly on the IT/cloud side, not in the OT transport path.[cite:182][cite:185] A clean separation looks like this:

- **OT side**: OpenPLC, Python replay/generation, MQTT broker, Sparkplug B, Ignition, historian.[cite:21][cite:33][cite:68][cite:78]
- **Bridge layer**: Kafka consumers, historian exports, Python ETL or stream processors.[cite:39][cite:45][cite:72]
- **IT/cloud side**: floci S3, Athena, Lambda, EventBridge, Kinesis, RDS, and related services.[cite:182][cite:185]

This makes the cloud side a consumer and processor of harmonized industrial data rather than a replacement for the OT messaging model.[cite:89][cite:185]

## Python’s role across the stack

Python is the best language to standardize on in this hand-built architecture because it can span nearly every custom part of the system.[cite:90][cite:92][cite:100] Useful Python roles include:

- Replaying benchmark datasets in time order.[cite:145][cite:150][cite:151]
- Generating additional analog and discrete signals.[cite:151][cite:156]
- Injecting realistic messiness such as spikes, missing points, and state transitions.[cite:136][cite:141][cite:156]
- Mapping benchmark variables to PLC tags and PLC tags to Sparkplug metrics.[cite:163][cite:167][cite:100]
- Publishing and consuming MQTT/Sparkplug streams.[cite:90][cite:99][cite:100][cite:104]
- Consuming Kafka and writing Parquet or cloud-emulated outputs.[cite:39][cite:67][cite:72][cite:185]
- Training models and deploying inference services that publish predictions back into the UNS.[cite:71][cite:97][cite:101]

This makes the hand-built design highly coherent: infrastructure components are open-source services, and Python is the implementation layer that ties them together.[cite:68][cite:90][cite:100]

## Recommended end-to-end flow

A practical end-to-end sequence for the hand-built lab is:

1. Load the Industrial IoT and TEP datasets in Python.[cite:145][cite:150]
2. Generate missing operational context such as valve state, machine mode, counts, and OEE-related signals.[cite:151][cite:156]
3. Inject modest realism issues such as missing points, spikes, and manual-mode behavior.[cite:136][cite:141][cite:156]
4. Map those values into PLC-style addresses or cryptic controller tags.[cite:163][cite:167]
5. Publish them as Sparkplug B node and device metrics via MQTT.[cite:78][cite:100][cite:104]
6. Consume the harmonized signals in Ignition and write history into a TSDB.[cite:3][cite:6][cite:35][cite:39]
7. Forward selected streams into Kafka and write analytical copies to Parquet/object storage.[cite:39][cite:45][cite:67][cite:72]
8. Use DuckDB and/or floci services such as Athena, Lambda, or S3 for IT/cloud-style analytics and orchestration.[cite:67][cite:72][cite:182][cite:185]
9. Train ML models and deploy Python scoring services that publish enriched or predictive metrics back into the Sparkplug B UNS.[cite:71][cite:97][cite:100][cite:101]

This loop demonstrates both OT-to-IT data flow and IT-to-edge feedback, which is critical if the lab is meant to show actual operationalization of analytics and ML rather than just passive dashboards.[cite:71][cite:73][cite:101]

## Upgrade path and realism

One reason this hand-built design is valuable is that it is upgrade-friendly.[cite:68][cite:89] Each open-source or free component has an obvious replacement path later if the project moves toward production:

- Mosquitto or EMQX OSS can be replaced by EMQX Enterprise, HiveMQ, or cloud MQTT brokers while preserving MQTT/Sparkplug contracts.[cite:68][cite:89]
- Ignition Maker/trial can be replaced by licensed Ignition without changing the application model.[cite:3][cite:6]
- InfluxDB OSS or Timescale Community can be replaced by cloud or enterprise offerings.[cite:35][cite:39]
- Kafka OSS can move to Confluent or managed Kafka services.[cite:39][cite:45]
- floci endpoints can move to actual AWS services later with much smaller changes than a redesign would require.[cite:182][cite:184][cite:185]

That means the hand-built lab is not just educational; it is also a prototype architecture with a credible path toward real deployment patterns.[cite:68][cite:89][cite:185]

## Practical links

### Data and core tools

- Industrial IoT Dataset (Synthetic): <https://www.kaggle.com/datasets/canozensoy/industrial-iot-dataset-synthetic> [cite:145]
- Tennessee Eastman Process data: <https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi%3A10.7910%2FDVN%2F6C3JR1> [cite:150]
- OpenPLC references: [cite:21][cite:33]
- Paho MQTT: <https://pypi.org/project/paho-mqtt/> [cite:90]
- PySparkplug: <https://github.com/matteosox/pysparkplug> [cite:100]

### OT and UNS infrastructure

- Ignition Maker Edition docs: <https://www.docs.inductiveautomation.com/docs/8.1/other-editions/ignition-maker-edition> [cite:6]
- EMQX open-source info: [cite:68]
- Sparkplug specification: [cite:78]
- Grafana OSS references: [cite:40][cite:45]
- Timescale and historian references: [cite:39][cite:48]
- InfluxDB historian references: [cite:35][cite:40]
- DuckDB: <https://duckdb.org/> [cite:67]

### Cloud/IT emulation

- floci site: <https://floci.io/floci/> [cite:185]
- floci GitHub: <https://github.com/floci-io/floci> [cite:180]

## Working conclusion

The hand-built Sparkplug B UNS scenario is the right option when the goal is to assemble and understand the full industrial data architecture yourself: synthetic Level 0 reality, PLC-world source structures, Sparkplug B harmonization, explicit MQTT and historian choices, explicit OT and IT consumption paths, and a local cloud emulation layer through floci.[cite:21][cite:33][cite:68][cite:78][cite:89][cite:185]

It is more work than a UMH-anchored design, but it gives deeper understanding of where each concern belongs and makes every integration surface visible.[cite:68][cite:71][cite:89] That makes it especially valuable for learning, for architecture experimentation, and for building a stack that can later swap individual components for paid or enterprise equivalents without losing the design principles established in the lab.[cite:39][cite:45][cite:68][cite:182][cite:185]
DOCEOF && ls -l output/hand_built_sparkplug_uns_notes.md
