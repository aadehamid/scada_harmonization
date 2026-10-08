# LSC-002. Domain narrative for Lagos Specialty Chemicals

Status: fictional domain narrative. The [charter](LSC-001_Problem_Statement_and_Project_Charter.md)
governs scope and architecture. This document explains why the sites have different
control systems, units, and tag names. It adds no company facts or technology decisions.

---

## The company

Lagos Specialty Chemicals (LSC) is a fictional mid-cap specialty-chemicals
manufacturer headquartered in Lagos, Nigeria. It began in the 1990s blending
industrial solvents and coatings additives for West Africa. Organic growth and
acquisitions made it a multinational producer of specialty intermediates and
polymer additives.

Its plants run continuous reaction, separation, and stripping using the Tennessee
Eastman process archetype. Reactants produce two liquid products and a byproduct.
Feed pumps, recycle compressors, agitator motors, and transfer pumps support the process.

The plants were built or acquired at different times. Their engineers chose
different control platforms, units, and tag conventions. Headquarters wants
enterprise analytics, predictive maintenance, and an AI copilot. The lab must
first reconcile four incompatible operational dialects.

The Unified Namespace (UNS) root is `lagos-chem`. The ISA-95 enterprise name is
Lagos Specialty Chemicals.

---

## How acquisitions created different site dialects

| Era | Event and site | Control heritage | Source of divergence |
| --- | --- | --- | --- |
| 1990s | Founding and first West African operations. Headquarters is not a lab site. | Solvents and coatings | Corporate origins and data culture |
| About 2005 | First US Gulf Coast plant, Beaumont, TX. The oldest asset is brownfield. | Allen-Bradley PLCs | Register tags such as `N7:20` and `FIC101_PV`, imperial units, and terse status codes. The lab uses real OpenPLC over Modbus TCP to teach how memory addresses acquire meaning. |
| About 2012 | Acquired Geismar, LA, built by a European licensor/EPC. | Siemens S7 | European engineering conventions explain addresses such as `DB10.DBD4` and `MW100`, metric units such as m³/h, kPa, and °C, and verbose statuses. The lab uses a real OPC-UA server through `asyncua`, per charter L1.1. |
| About 2018 | Greenfield expansion in Rotterdam, NL. | Ignition/MQTT | Nested semi-semantic names, metric units, and a site-specific status vocabulary. These still need enterprise harmonization. |
| About 2022 | Acquired a Corpus Christi, TX, midstream/feedstock terminal to secure raw materials. | CygNet from oil and gas | Flat names such as `CC_NORTH_U12_FIC101` encode hierarchy. Mixed units and oil-and-gas conventions come from the acquired SCADA system. |


The same physical reading, such as reactor feed flow, has four unrelated names
and status vocabularies across the SCADA lineages. Sites also use different units.
Harmonization gives consumers a common meaning while retaining the source identity.

Within a site, tag models also vary by system integrator. Engineers spend days
pulling historian extracts by hand, and sites treat real-time data as local assets.
The fictional corporate SAP ECC-to-S/4 migration adds business-record changes.
Headquarters needs governed, reusable metrics with owners, definitions, and lineage.
Sites retain local operating autonomy. The charter selects ERPNext for the lab's
enterprise-system lesson; this narrative does not add a SAP deployment.

The drawings have a similar reconciliation problem. Every site's P&IDs describe
the same Unit 100 equipment. Engineering records exist in authoring databases
and flat sheets. A sheet tag names an instrument but does not establish its
relationship to equipment. Crossing lines need evidence before they become a
pipe connection.

Engineers reconstruct connectivity by tracing paths across sheets. Brownfield
and acquired plants may hold only the sheets. The lab therefore extracts the
Unit 100 P&ID first, then scanned variants. The owner's related private project,
`aadehamid/Engineering_Drawing_to_Graph`, explores extraction from an
engineering-authoring backend.

---

## The cast of divergence (what the lab must reconcile)

| Dimension | Beaumont | Geismar | Rotterdam | Corpus Christi |
|-----------|----------|---------|-----------|----------------|
| SCADA lineage | Allen-Bradley | Siemens | Ignition-style | CygNet |
| Tag style | AB register (`N7:20`) | Siemens address (`DB10.DBD4`) | verbose semantic | compound hierarchy-encoding |
| Units | imperial | metric | metric | mixed |
| Status codes | terse | verbose | own vocabulary | O&G-style |
| PLC in lab | real OpenPLC (Modbus TCP) | real OPC-UA (`asyncua`) | Python-modeled | Python-modeled |

The roster exercises naming, units, status vocabulary, and addressing differences.
It also includes real-protocol and Python-modeled sites.

---

## The mission and the four planes

1. Harmonize the four dialects into one Unified Namespace through Sparkplug B and MQTT.
   Govern each metric with an owner, definition, and lineage.
2. Record curated operational events into ERPNext and reconcile them with the
   plant's transactional systems (MES/LIMS/CMMS/quality).
3. Contextualize assets, tags, events, lots, work orders, lab results, and engineering
   topology in Neo4j for cross-domain reasoning and a GraphRAG
   copilot.
4. Apply the data to traditional ML and a GenAI copilot. The flagship ML question is
   yield improvement and production leakage, with human-approved recommendations executed at the edge.

The lab must demonstrate these outcomes through the charter's phase exits.
The fictional business narrative is not evidence of a measured yield gain or a working copilot.
