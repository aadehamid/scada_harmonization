# plc_mapping (pipeline layer 3 — Phase 2)

Converts friendly source variables into **site-specific cryptic PLC representations**
(`N7:20`, `DB10.DBD4`, `FIC101_PV`, `CC_NORTH_U12_FIC101`) driven by the three-stage
mapping table in `config/mappings/`. This is the deliberate mess the lab exists to
harmonize — never publish clean semantic names straight from Python. No code until Phase 2.
