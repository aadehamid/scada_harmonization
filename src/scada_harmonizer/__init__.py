"""scada_harmonizer — industrial data harmonization & contextualization home lab.

Simulates a multi-site specialty-chemicals manufacturer (Lagos Specialty Chemicals) whose
sites represent the same operational reality differently, then harmonizes that into one
Sparkplug B / MQTT Unified Namespace and contextualizes it into a Neo4j knowledge graph.

Package layout mirrors the charter's four planes plus the synthetic-data pipeline
(`datagen/`); each subpackage README states what lands there and in which build phase.
Authoritative definition: design/PROJECT_CHARTER.md.
"""
