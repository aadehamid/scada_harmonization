# Home Lab Notes for a Sparkplug B / UNS / SCADA Harmonization Project

> **⚠️ Archived vision note (pre-decision).** Options discussed here as open choices are now
> **DECIDED** in [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) §4/§12/§13 — e.g. the broker topology is
> **two-tier Mosquitto (edge) + EMQX (central)**, not either/or; the historian is **TimescaleDB**;
> **two** sites run real protocols (OpenPLC/Modbus + OPC-UA). Read this file only for narrative
> background and original rationale. The charter governs.

These notes frame the home lab as a **multi-site manufacturing data harmonization and contextualization problem**.[cite:78][cite:89][cite:234] The objective is to simulate plant sites where similar operational realities are represented differently across the manufacturing space, then harmonize those disparate OT data representations into a common enterprise language through a Unified Namespace, while also contextualizing the data so it is meaningful to OT, IT, analytics, ERP, and graph-based reasoning systems.[cite:89][cite:162][cite:166][cite:168][cite:227][cite:233][cite:234]

## Problem framing

The core problem is not simply collecting plant telemetry.[cite:89] It is that different sites, lines, and machines often represent similar underlying realities in different ways because of local PLC naming conventions, controller memory structures, brownfield integrations, differing tag taxonomies, and uneven operational modeling.[cite:163][cite:167][cite:168] As a result, what should be enterprise-comparable data often arrives as site-specific, cryptic, and inconsistent signals that are difficult to reuse consistently across plants.[cite:162][cite:168][cite:234]

The home lab is meant to simulate exactly that condition: multiple plant sites with disparate data representations at the source layer.[cite:21][cite:33][cite:167] The goal is to show how those local representations can be conformed to a common enterprise-facing language through Sparkplug B and a semantic UNS, so that downstream systems can consume the same industrial reality in a consistent way regardless of how each site originally named or structured its data.[cite:78][cite:89][cite:162][cite:166][cite:168]

A second goal is contextualization.[cite:234] Harmonization alone is not enough, because enterprise systems need more than normalized telemetry: they need data tied to assets, lines, sites, events, work orders, materials, maintenance actions, and business processes.[cite:227][cite:233][cite:234] That is why the aligned architecture now also includes ERPNext as the SAP-like enterprise application layer, Neo4j as the connected-context knowledge graph, and floci as local AWS-style IT/cloud emulation.[cite:185][cite:227][cite:233][cite:238]

## Project scope

The core project is to simulate a realistic industrial environment in which Level 0 is synthetic, Level 1/2 looks like a PLC world, and higher layers behave like a real OT/IT stack.[cite:21][cite:33][cite:89] The lab should therefore show not only historian and dashboard behavior, but also how harmonized and contextualized industrial data can feed analytics, ML, enterprise applications, and graph-based reasoning across an enterprise landscape.[cite:71][cite:73][cite:89][cite:227][cite:234]

A particularly realistic pattern is to simulate only Level 0 and keep the rest of the stack as real software: PLC-facing tag structures at Level 1/2, Sparkplug B or MQTT infrastructure at Level 3, historian/analytics/ML services above that, ERPNext as the SAP-like enterprise system, Neo4j as the connected-context knowledge graph spanning OT and enterprise relationships, and floci as the local AWS-shaped IT/cloud emulation layer.[cite:21][cite:33][cite:78][cite:89][cite:185][cite:227][cite:233][cite:234][cite:238]

## Three architecture notes

### Note 1: Hand-built Sparkplug B UNS

This option assembles the full stack manually without anchoring on UMH, using open-source or free tools throughout.[cite:21][cite:33][cite:68][cite:71] A realistic stack is OpenPLC for controller behavior, EMQX OSS or Mosquitto for MQTT, Sparkplug B as the payload/topic convention, Ignition Maker Edition or trial for SCADA, InfluxDB OSS or TimescaleDB Community for history, Grafana OSS for dashboards, Kafka plus DuckDB for downstream analytics, ERPNext for the SAP-like enterprise layer, Neo4j for the knowledge graph layer, and floci for cloud/IT emulation.[cite:3][cite:6][cite:35][cite:39][cite:40][cite:67][cite:68][cite:72][cite:78][cite:185][cite:227][cite:233][cite:238]

This path is useful for learning each moving part deeply, because every boundary is explicit and replaceable.[cite:68][cite:71][cite:78][cite:89] It also gives a clean migration path to paid versions later, since the core interfaces remain standard across controller tags, Sparkplug B and MQTT, historian/streaming systems, enterprise applications, graph context systems, and cloud-style services.[cite:39][cite:45][cite:68][cite:78][cite:89][cite:185][cite:227][cite:233][cite:238]

### Note 2: UMH-anchored Sparkplug B UNS

This option uses United Manufacturing Hub Community as the central data infrastructure while keeping the rest of the lab open source or free.[cite:80][cite:106][cite:112] UMH Community includes an open-source stack with MQTT, Kafka, historian/storage, visualization, and a management/data-model layer, and its community license is free forever with a path to paid support later.[cite:80][cite:106][cite:112]

In this version, UMH becomes the backbone for the UNS and historian, while OpenPLC, simulated data, Ignition, Python ML services, ERPNext, Neo4j, and floci attach to it as producers, consumers, or downstream contextual and enterprise layers.[cite:80][cite:83][cite:86][cite:112][cite:185][cite:227][cite:233][cite:238] This is the faster route to an end-to-end demo because it reduces assembly effort while still preserving realistic interfaces and future portability.[cite:80][cite:89][cite:106]

### Note 3: Python-centric implementation

This option keeps the same overall architecture but uses Python in most places where it is practical and mature to do so.[cite:90][cite:92][cite:100][cite:104] Python becomes the primary implementation language for dataset replay, synthetic signal generation, Sparkplug publishing, data cleaning, enrichment, feature engineering, analytics, edge inference services, ERPNext integration services, and Neo4j graph-loading or graph-query services.[cite:92][cite:97][cite:100][cite:104][cite:105][cite:227][cite:233][cite:238][cite:242]

The core Python transport tools are Eclipse Paho MQTT for broker connectivity and PySparkplug or another Sparkplug wrapper for Sparkplug B semantics.[cite:90][cite:99][cite:100][cite:104][cite:105] Python can also act as the bridge from the harmonized UNS into ERPNext on the enterprise side and into Neo4j on the graph/context side, making it not just a glue language but a first-class participant across OT, IT, and contextual reasoning layers.[cite:68][cite:89][cite:97][cite:227][cite:233][cite:238][cite:242]

## Synthetic data strategy

### Why synthetic plus benchmark data is the right fit

The recommended approach is to combine one or two benchmark datasets with Python-generated synthetic signals.[cite:145][cite:150][cite:151] This produces realistic multivariate behavior while also letting the lab include tags that real datasets usually do not provide directly, such as valve states, operating modes, OEE-style counters, work-order references, batch identifiers, maintenance-related events, and material/logistics context.[cite:145][cite:150][cite:151][cite:156][cite:227][cite:233]

This is also the best way to make the lab look like a PLC world while keeping Level 0 synthetic.[cite:21][cite:33][cite:167] The benchmark and synthetic values act as the underlying process reality, but what the PLC and upstream systems see are PLC-style addresses and cryptic tags that later get harmonized into Sparkplug B metrics and a semantic namespace usable across sites by OT, IT, ERP, and graph-context systems.[cite:162][cite:166][cite:167][cite:227][cite:234]

### Base datasets to replay

| Dataset | Role in lab | Why it is useful | Link |
|---------|-------------|------------------|------|
| Industrial IoT Dataset (Synthetic) | Equipment/machine-level sensor behavior | Provides realistic industrial sensor and failure-style patterns for predictive maintenance demonstrations.[cite:145] | [Kaggle](https://www.kaggle.com/datasets/canozensoy/industrial-iot-dataset-synthetic) [cite:145] |
| Tennessee Eastman Process (TEP) | Process-plant multivariate behavior | Provides long-running, correlated process variables and fault scenarios that resemble real process control behavior.[cite:150][cite:155] | [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi%3A10.7910%2FDVN%2F6C3JR1) [cite:150] |
| Numenta Anomaly Benchmark (optional) | Extra anomaly-rich streams | Adds anomaly patterns useful for testing historian, alerting, and ML behavior.[cite:137][cite:142] | [Overview](https://www.emergentmind.com/topics/numenta-anomaly-benchmark-nab) [cite:142] |

### Adding realism and messiness

To make the lab believable, the synthetic layer should include correlated variables, state changes, drift, faults, missingness, and operational context instead of fully independent random signals.[cite:136][cite:141][cite:145][cite:156] It should also include identifiers and event types that matter downstream, such as batches, machine states, downtime categories, production counts, and maintenance-relevant conditions, because those are the kinds of signals that later feed ERPNext records and graph relationships in Neo4j.[cite:143][cite:151][cite:156][cite:227][cite:233][cite:234]

## PLC-style tag structure and harmonization

### Simulating cryptic PLC memory or tag names

An important design choice is to make the synthetic data look like it came from real controllers rather than clean semantic APIs.[cite:163][cite:167] This means values should first appear as memory addresses or cryptic PLC tags such as `N7:20`, `MW100`, `DB10.DBD4`, or controller-style names like `FIC101_PV`, and only later be mapped to semantic Sparkplug B metrics.[cite:163][cite:167][cite:169]

This matters because the problem being simulated is precisely that different plants and systems expose their data differently.[cite:163][cite:167][cite:168] The harmonization challenge is to take those local, controller-specific representations and conform them into a common enterprise language without losing traceability back to the original source semantics.[cite:162][cite:168][cite:234]

### Mapping from PLC tags to Sparkplug B and UNS

The harmonization layer should explicitly map PLC-facing structures to Sparkplug B metrics and asset paths.[cite:78][cite:162][cite:166][cite:168] That mapping is what turns controller chaos into a coherent UNS that can serve SCADA, historian, analytics, ERP, and graph-context use cases at the same time.[cite:84][cite:89][cite:227][cite:234]

A good mapping table should therefore include not only source tag and target metric names, but also engineering units, asset class, line/site context, and, where relevant, IDs that help tie the data to enterprise records or graph entities such as work orders, assets, materials, and event types.[cite:162][cite:168][cite:227][cite:233][cite:234]

## Python libraries and modules

### Core Python modules for the project

The core Python stack should center on Pandas for data shaping, Paho MQTT for MQTT transport, PySparkplug for Sparkplug B publishing, and DuckDB for developer-friendly analytical SQL over Parquet and replayed datasets.[cite:67][cite:90][cite:100][cite:151] If ERPNext and Neo4j are part of the lab, Python should also be used for enterprise integration services and graph-loading or graph-query services because that keeps the custom implementation surface consistent across the architecture.[cite:90][cite:92][cite:97][cite:227][cite:233][cite:238][cite:242]

This keeps Python at the center of the implementation while still allowing the stack to remain architecturally realistic.[cite:68][cite:89][cite:90] Brokers, historians, ERP systems, graph databases, and cloud emulators still run as dedicated services, but Python ties the flows together in a maintainable way.[cite:35][cite:39][cite:68][cite:185][cite:227][cite:233][cite:238]

### Optional Python-friendly advanced generators

There are also optional synthetic-data libraries such as timeseries-generator, ML4ITS synthetic-data, and SynTiSeD if the lab needs more advanced generation patterns beyond benchmark replay and simple augmentation.[cite:133][cite:151][cite:152] These are useful when you want more variety or more controlled augmentation, but the simpler replay-plus-augmentation pattern is usually the most transparent for a home-lab architecture that also needs to feed Sparkplug, ERP, and graph context flows.[cite:151][cite:156][cite:227][cite:234]

## Recommended execution pattern

A useful execution pattern is to start with one or two benchmark datasets, replay them through Python as if they were plant signals, map them into PLC-style tags, publish them via MQTT or Sparkplug B, store them in a historian or time-series backend, and then use the same harmonized streams for analytics, ML experiments, ERPNext enterprise integration, Neo4j knowledge-graph enrichment, and floci-based IT/cloud emulation.[cite:145][cite:150][cite:151][cite:90][cite:92][cite:100][cite:35][cite:39][cite:67][cite:185][cite:227][cite:233][cite:238]

One practical sequence is:

1. Load and replay benchmark datasets through Python.[cite:145][cite:150][cite:151]
2. Add synthetic operational and actuator context.[cite:151][cite:156]
3. Convert the values into PLC-like tags or OpenPLC-facing structures.[cite:21][cite:33][cite:167]
4. Publish them into MQTT / Sparkplug B.[cite:78][cite:90][cite:100][cite:104]
5. Consume them in SCADA, historian, and dashboard layers.[cite:3][cite:6][cite:35][cite:39][cite:40]
6. Feed selected business-relevant events into ERPNext.[cite:227][cite:233]
7. Feed selected semantic and event relationships into Neo4j.[cite:234][cite:238][cite:242]
8. Reuse the same data for ML training, edge inference, and cloud-style workflows through floci.[cite:71][cite:73][cite:97][cite:101][cite:185]

## Practical conclusion

The aligned direction is to build a realistic PLC-world-to-UNS lab that demonstrates a multi-site enterprise harmonization problem, not just a telemetry demo.[cite:21][cite:33][cite:78][cite:89] The lab should show how disparate site-level OT representations can be conformed to a common enterprise language and then contextualized so they can support OT applications, analytics, ML, ERP-style enterprise processes through ERPNext, connected-context reasoning through Neo4j, and cloud-style IT workflows through floci.[cite:89][cite:185][cite:227][cite:233][cite:234][cite:238]

That combination makes the home lab stronger as both a learning environment and an architecture prototype, because it demonstrates not only how to collect industrial data but how to harmonize, contextualize, and operationalize it across SCADA, historian, analytics, enterprise, graph, and cloud-style domains with largely open-source or free tools.[cite:3][cite:6][cite:35][cite:39][cite:68][cite:80][cite:185][cite:227][cite:233][cite:238]
