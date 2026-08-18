# Synthetic Data Generation Notes for the UNS / Sparkplug B Home Lab

> **Living data-strategy note.** The 6-layer pipeline shape here is still the plan. Decided
> items live in [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md): production is **lot-based**
> (ISA-106, not ISA-88 batches — §14 N13); **PySparkplug is a candidate**, not a decided
> dependency (§4.1); mapping-table columns include the §14 set. The charter governs.
>
> **Phase 1 (2026-08-18):** L0 generators are on `main` (PRs #28/#29). Land, persist, and
> disk facts: [`PHASE1_SYNTHETIC_DATA.md`](PHASE1_SYNTHETIC_DATA.md). Contract:
> [`PHASE1_L0_CONTRACT.md`](PHASE1_L0_CONTRACT.md). **IIoT correction:** the Kaggle file is
> snapshot-per-machine, not a 1-second time series (see below).

These notes describe how to build a realistic, high-volume synthetic data layer for a home lab whose purpose is to simulate **multiple plant sites with disparate OT data representations**, then harmonize those site-specific representations into a common enterprise language through Sparkplug B and a Unified Namespace. The synthetic-data layer therefore has to do more than generate believable sensor values: it also has to support downstream contextualization so the harmonized data can feed OT applications, ERPNext as the SAP-like enterprise application layer, Neo4j as the connected-context knowledge graph, analytics/ML pipelines, and floci-based cloud/IT workflows.

## Design goal

The synthetic data layer should not look like a clean academic CSV flowing directly into analytics. It should look like real plant data from multiple sites: multiple sensors per asset, correlated variables, drift, operating modes, state changes, occasional missing points, and realistic controller-facing tags that later need semantic harmonization. Just as importantly, the same underlying operational reality should be allowed to appear differently across sites so the lab can demonstrate the true harmonization problem rather than a single perfectly standardized source.

The best way to achieve that is to combine two data sources:

- **Benchmark datasets** that already contain realistic multivariate behavior, faults, and temporal structure.
- **Python-generated signals** that fill gaps common in real plants, such as valve positions, machine states, manual/auto modes, counters, production context, maintenance triggers, work-order references, lot identifiers, and material/logistics events.

This blended approach gives both realism and flexibility. The benchmark data supplies believable process dynamics, while Python fills in the operational and enterprise-relevant context and lets the lab scale to more assets, more lines, more sites, and more event types than any one dataset offers by itself.

## Data philosophy

### Only Level 0 is synthetic

The intended model is that only the physical world is synthetic. The rest of the chain should feel real: a PLC layer or PLC-like structure, Sparkplug B edge publishing, MQTT broker, historian, stream processing, analytics, ERP integration, graph-context services, and edge inference services.

That means the data generation layer should represent:

- Sensors, such as temperature, flow, pressure, vibration, current, level, and humidity.
- Actuator-related signals, such as valve position, drive speed, command outputs, and run permissives.
- Equipment state, such as idle, running, faulted, setup, starved, or blocked states.
- Production context, such as counts, scrap, good units, lot IDs, machine mode transitions, work-order references, and completed-lot events.
- Maintenance context, such as anomaly flags, runtime thresholds, asset-condition summaries, and maintenance-triggering events.
- Logistics or material context, such as material identifiers, consumption events, transfer-style events, and finished-goods completions.

### Why not just use a dedicated sensor simulator?

A separate GUI tool can still be useful, but it is not required. In this lab, Python dataset replayers and Python generators can effectively *be* the Level 0 world. From the UNS, historian, ERP, or graph side, there is no functional difference between a hardware sensor chain and a Python service that emits the same time-ordered values through the same interfaces.

This makes Python especially attractive because it lets the same language handle:

- Dataset loading and cleaning.
- Time-series generation and augmentation.
- Mapping to PLC-style structures.
- Publishing to MQTT and Sparkplug B.
- Creating ERP-relevant events and contextual identifiers.
- Creating graph-relevant identifiers and relationship hints for Neo4j.
- ML training and later inference deployment.

## Benchmark datasets to use

The recommended baseline is to use one machine-oriented dataset and one process-oriented dataset. This gives both discrete equipment behavior and continuous multivariable process behavior in the same lab. It also provides a good foundation for modeling how comparable industrial realities can be represented differently across different sites, lines, or assets while still being harmonized later.

### 1) Industrial IoT Dataset (Synthetic) – Kaggle

**Link:** [Industrial IoT Dataset (Synthetic)](https://www.kaggle.com/datasets/canozensoy/industrial-iot-dataset-synthetic)

This dataset is synthetic, designed around industrial predictive-maintenance style signals, and useful for machine-centered equipment data. **Correction (2026-08-18):** the published file (`factory_sensor_simulator_2040.csv`) is **one snapshot per machine** (about 500,000 rows, 22 columns). It is **not** a 1-second historian export and must not be replayed as a 1 Hz stream. The L0 contract's `epoch + i * 1s` rule is a melt fallback for a wide table that lacks a time column, not a description of this file. Charter §14 N8 still names IIoT as the intended fast-class carrier; this file does not carry that class. Python extras and a later machine stream cover the gap. N8 itself is not rewritten here.

Good uses in the lab include:

- Creating one or more machine families with repeated sensor patterns (as snapshots, then cloned).
- Training ML models for failure prediction or anomaly scoring on per-machine features.
- Showing multiple lines or sites by binding the same snapshot schema to different site tags later.

This dataset is not a literal plant historian export. TEP remains the time-ordered process layer. Do not mix TEP and IIoT on one Phase 1 stream.

### 2) Tennessee Eastman Process (TEP)

**Link:** [Harvard Dataverse TEP data](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi%3A10.7910%2FDVN%2F6C3JR1)  
**Overview:** [The Tennessee Eastman Process: an Open Source Benchmark](https://keepfloyding.github.io/posts/Ten-East-Proc-Intro/)

TEP is a classic process-control benchmark with measured variables, manipulated variables, and fault scenarios over time. It is ideal for demonstrating process industries or any scenario where multiple variables move together because of physics, control loops, and process disturbances.

Good uses in the lab include:

- Reactor or mixing process simulations.
- Complex multivariate analytics and process anomaly detection.
- Demonstrating why harmonized, semantically named variables matter when hundreds of raw variables must be interpreted.
- Demonstrating how site-specific naming and controller structures can still be conformed to common enterprise semantics after harmonization.

TEP is simulated rather than collected from a live plant, but the dynamic model and long-standing use in process-control research make it a strong proxy for realistic process historian data.

### 3) Optional anomaly and augmentation datasets

**Numenta Anomaly Benchmark overview:** [NAB overview](https://www.emergentmind.com/topics/numenta-anomaly-benchmark-nab)

NAB is optional but useful when the lab needs extra anomaly-rich time series for experimentation or ML comparison. It is not the primary source for the lab, but it can add diversity when testing spike detection, drift detection, or alerting workflows.

## What “realistic enough” means

The benchmark datasets are not literally raw exports from a live operating plant, but they are realistic enough for the project’s goals when used correctly. The right mental model is not “are these exact historian dumps,” but rather “do these streams have enough structure, cross-correlation, drift, fault behavior, and contextual richness to behave like real plant data after they pass through site-specific PLC-world representations and later enter a harmonized enterprise-facing model.”

To preserve realism:

- Replay records in time order, not shuffled.
- Preserve or intentionally resample the original cadence in a controlled way.
- Keep variable relationships intact when injecting noise or missingness.
- Avoid generating fully independent random signals for every sensor; real equipment variables usually move together.
- Allow site-level naming, controller conventions, and event labeling to vary while preserving a path to later harmonization.

## Python libraries for generation and replay

### Core data and replay libraries

| Library | Role | Link |
|---------|------|------|
| pandas | Load CSVs, align timestamps, merge benchmark and synthetic signals. | [pandas](https://pandas.pydata.org/) |
| paho-mqtt | MQTT connectivity from Python. | [PyPI](https://pypi.org/project/paho-mqtt/) |
| PySparkplug | Sparkplug B publishing from Python (*candidate* — charter §4.1). | [GitHub](https://github.com/matteosox/pysparkplug) |
| DuckDB Python package | Fast analytical SQL over replayed datasets and Parquet. | [DuckDB](https://duckdb.org/) |
| Neo4j Python driver | Optional graph-loading/query support for downstream context flows. | [PyPI](https://pypi.org/project/neo4j-driver/) |

Pandas is the workhorse for dataset loading and transformation, even though it was not the focus of the earlier tool discussion. Paho MQTT is the standard open-source Python MQTT client and should be the default transport library for the project. PySparkplug is the *candidate* Python-native path for Sparkplug B publishing (Pre-Alpha — verify in Phase 2; fallback is hand-rolled `spBv1.0` protobuf over paho-mqtt, charter §4.1). The lab is Sparkplug-centric rather than plain JSON-over-MQTT.

DuckDB is useful for local analytical preparation, while the Neo4j Python driver becomes useful when the synthetic data flow needs to emit contextual entities and relationships for downstream graph use cases. ERPNext does not change the core synthetic-data tooling directly, but it does increase the importance of generating meaningful business-facing events and identifiers such as work orders, lots, materials, and maintenance triggers.

### Synthetic signal generation libraries

| Library or approach | Role | Link |
|---------------------|------|------|
| timeseries-generator | Generate analog signals with trend, seasonality, and noise. | [Article and examples](https://blog.devgenius.io/customize-your-synthetic-time-series-data-by-timeseries-generator-9a6669e393bc) |
| Custom Python state machines | Generate valve states, machine modes, and event-driven operational changes. | Use standard Python and pandas workflows. |
| ML4ITS synthetic-data | Optional deep-learning-based synthetic time-series generation. | [GitHub](https://github.com/ML4ITS/synthetic-data) |
| SynTiSeD | Optional research-oriented synthetic time-series generator. | [Paper](https://www.dfki.de/fileadmin/user_upload/import/13272_SynTiSeD_paper.pdf) |

The most practical default is **timeseries-generator + custom Python** rather than more complex generative models. That keeps the lab understandable and controllable, especially when the goal is to show traceable relationships between sensors, states, process behavior, enterprise events, and graph context rather than just maximize data novelty.

## Data generation pattern

### Step 1: Load benchmark data as the base process layer

TEP is the continuous process base layer (time-ordered, 3-minute samples). The Kaggle IIoT file is a **per-machine snapshot** layer, not a second time series to align. Load both with pandas; do not pretend the IIoT rows are 1 s samples and do not mix the two on one Phase 1 stream.

A useful pattern is:

- Use Industrial IoT data for pumps, motors, conveyors, packers, or condition-based equipment.
- Use TEP for tanks, reactors, lines, utility loops, or other process-oriented equipment.
- Treat each replay stream as an asset template that can be cloned across lines, units, or sites.
- Let cloned site variants preserve the same underlying operational meaning while using different local tags, naming conventions, or controller structures.

### Step 2: Map dataset variables to physical assets

Before any MQTT or Sparkplug work begins, each dataset column should be assigned a physical meaning in the plant model. For example, a process variable may become a reactor inlet temperature, while a machine signal may become motor current on a filler or compressor.

A mapping table should exist with at least these fields:

- Source dataset name.
- Source column name.
- Physical meaning.
- Asset name.
- Equipment class.
- Site / line / cell context.
- Unit of measure.
- Expected range.
- Sampling cadence.
- Optional enterprise/context IDs such as work-order ID, lot ID, material ID, maintenance event type, or graph entity key where relevant.

This mapping becomes the foundation for both PLC-world representation and later semantic harmonization.

### Step 3: Add synthetic signals for missing Level 0 context

Realistic plant stories need more than analog process values. They also need discrete and contextual tags that datasets rarely provide directly. Python should generate these additional signals.

Typical added signals include:

- Valve positions, open/closed states, and commanded setpoints.
- Drive state, machine run state, permissives, and interlocks.
- Lot IDs, work-order references, order numbers, product grades, and current SKU.
- OEE-style counters: total count, good count, reject count, runtime, downtime, changeover time.
- Maintenance and operator events such as manual mode, maintenance bypass, runtime threshold crossing, or anomaly flags.
- Material consumption, WIP movement hints, finished-good completion events, and transfer-style events that can later drive ERP or graph context.

For analog additions, use timeseries-generator or simple Python functions with noise and drift. For discrete additions, use Python state machines driven by rules tied to the benchmark signals, such as opening a valve when flow rises, incrementing count only while machine state is running, or generating a completion event when a lot window closes.

### Step 4: Inject realistic messiness

A small amount of messiness should be intentionally added before the data reaches the PLC-facing structure. This is important because real plants rarely provide perfectly clean signals all the way through the stack.

Recommended messiness to include:

- **Missing samples:** random drops, burst drops, or communication gaps.
- **Short spikes:** one-off outliers from noise, sensor issues, or bad reads.
- **Flatlines:** sensor freezes or stuck values, especially on analog channels.
- **Operational interruptions:** setup, maintenance, cleaning cycles, or off-shift states.
- **Manual-mode behavior:** operator overrides that cause values to behave differently from closed-loop control.
- **Site-level variation:** different naming conventions, event labels, and controller-facing structures across sites even when the underlying operational pattern is similar.

The key is moderation. Enough messiness should exist to make the data believable, but not so much that the underlying benchmark relationships disappear.

## PLC-world representation

### Why PLC structure matters

The lab is meant to look like data moving through an actual OT stack, not directly from Python into analytics. That means the generated data should be transformed into PLC-facing addresses or cryptic tags before the UNS sees it.

This is important for two reasons:

- It makes the lab much closer to real brownfield integration, where the source is often a memory map or non-semantic controller naming.
- It gives a clear role to Sparkplug B and the UNS as the harmonization layer, rather than just another message transport.

### How to structure it

Every variable should pass through a two-stage or three-stage name mapping:

1. **Friendly source variable** from the dataset or Python generator.
2. **Site-specific PLC-world representation** such as `N7:20`, `MW100`, `DB10.DBD4`, or a cryptic tag like `FIC101_PV`.
3. **Sparkplug metric name / enterprise semantic representation** such as `Reactor1/FeedFlow` or `Line2/Filler/MotorCurrent`.

This lets the lab tell a realistic story: Level 0 values exist, different sites or controllers store or expose them in non-semantic forms, and the edge/UNS layer harmonizes them into clean enterprise-facing names.

### OpenPLC option

If you want the lab to look even more PLC-like, OpenPLC can act as the Level 1/2 stand-in controller and expose variables over Modbus TCP. Python services can write synthetic values into an OpenPLC-facing structure or directly model controller tags before those values are read by the Sparkplug edge publisher.

This is optional for the note itself, but it aligns with the stated goal that everything above Level 0 should feel real and PLC-oriented.

## Sparkplug B mapping

### Why Sparkplug is the harmonization layer

Sparkplug B provides a standard MQTT topic and payload model for industrial devices, including edge nodes, devices, births, data messages, aliases, and datatypes. That structure is what turns PLC-side chaos into a stable semantic model consumable by SCADA, historian, ERP, graph, and IT systems.

### Mapping pattern

A good mapping table should contain:

- PLC tag or PLC address.
- Sparkplug group ID.
- Edge node ID.
- Device ID.
- Metric name.
- Alias.
- Datatype.
- Engineering unit.
- Semantic asset path.
- Site identifier.
- Optional downstream context IDs for lot, work order, material, asset, or event type where useful.

At runtime, the Python publisher should:

1. Read the replayed and augmented signal set.
2. Translate each signal into its PLC-world identifier.
3. Build or reference the Sparkplug metric definition.
4. Publish NBIRTH or DBIRTH messages for device structure.
5. Publish NDATA or DDATA messages carrying current values and quality.

This creates the exact pattern you want to demonstrate: semantic structure on top of cryptic controller sources, and a path from site-specific representations into a common enterprise language.

## Recommended volume strategy

A convincing home lab needs enough volume to show historians, dashboards, UNS flows, ERP integrations, graph context, and ML pipelines working across multiple assets and sites. Volume should come from replication, time scaling, site variation, and signal expansion rather than only from one very large source dataset.

Recommended scaling tactics:

- Clone each base asset template across multiple lines or sites.
- Apply offset parameters so the cloned assets are not identical.
- Replay multiple runs at different speeds for backfill and historian population.
- Add synthetic auxiliary tags for every base asset, such as mode, state, valve, count, setpoint, quality tags, work-order references, and lot IDs.
- Generate different fault calendars and event labels per asset or per site to avoid synchronized behavior and to simulate local representation differences.

This allows a modest raw dataset to grow into a realistic multi-line, multi-site environment with dozens or hundreds of tags per asset and a believable mix of analog, discrete, event, and stateful data.

## Python implementation outline

The Python implementation should be split into clear layers so the project remains maintainable.

### 1) Ingestion layer

This layer loads benchmark datasets, validates schema, standardizes timestamps, and caches normalized forms for replay.

### 2) Augmentation layer

This layer adds synthetic analog and discrete signals, computes operational states, injects controlled messiness, and generates enterprise-relevant context such as work orders, lots, material IDs, or maintenance triggers where needed.

### 3) PLC mapping layer

This layer converts friendly asset variables into site-specific PLC addresses or cryptic PLC tags according to a configurable mapping table.

### 4) Sparkplug layer

This layer maps PLC-facing values to Sparkplug group IDs, node IDs, device IDs, aliases, metric names, and datatypes, then publishes via Paho (PySparkplug *candidate* — charter §4.1).

### 5) Context export layer

This layer prepares selected business-relevant events and contextual identifiers for downstream ERPNext and Neo4j flows, even if those systems are populated by separate integration services later.

### 6) Replay/orchestration layer

This layer controls cadence, clock speed, pause/resume behavior, backfill mode, and live simulation mode.

This separation will make it easier later to swap in real PLCs, real edge gateways, UMH-based infrastructure, ERP integrations, or graph services without rewriting the core synthetic-data model.

## Practical tool links

### Datasets

- Industrial IoT Dataset (Synthetic): <https://www.kaggle.com/datasets/canozensoy/industrial-iot-dataset-synthetic>
- Tennessee Eastman Process data: <https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi%3A10.7910%2FDVN%2F6C3JR1>
- Tennessee Eastman overview: <https://keepfloyding.github.io/posts/Ten-East-Proc-Intro/>
- NAB overview: <https://www.emergentmind.com/topics/numenta-anomaly-benchmark-nab>

### Python tools

- Paho MQTT PyPI: <https://pypi.org/project/paho-mqtt/>
- Eclipse Paho Python docs: <https://eclipse.dev/paho/clients/python/>
- PySparkplug GitHub: <https://github.com/matteosox/pysparkplug>
- PySparkplug docs: <https://pysparkplug.mattefay.com>
- timeseries-generator article/examples: <https://blog.devgenius.io/customize-your-synthetic-time-series-data-by-timeseries-generator-9a6669e393bc>
- DuckDB: <https://duckdb.org/>
- Neo4j Python driver: <https://pypi.org/project/neo4j-driver/>
- ERPNext manufacturing overview: <https://frappe.io/erpnext/open-source-manufacturing-erp-software>
- ERPNext GitHub: <https://github.com/frappe/erpnext>
- ML4ITS synthetic-data: <https://github.com/ML4ITS/synthetic-data>
- SynTiSeD paper: <https://www.dfki.de/fileadmin/user_upload/import/13272_SynTiSeD_paper.pdf>

## Working conclusion

The right synthetic data strategy for this lab is not “random fake sensor numbers.” It is a layered process: start with benchmark datasets that already have realistic temporal and multivariate behavior, enrich them in Python with operational, enterprise, and contextual signals, inject modest messiness and site-level representation differences, map them into PLC-style structures, and only then publish them into Sparkplug B and the UNS.

That approach gives the home lab enough realism to support SCADA, historian, UNS, ERPNext, Neo4j, IT/cloud emulation, and ML demonstrations while still being deterministic, reproducible, and fully under your control.
