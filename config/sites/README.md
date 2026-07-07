# sites — per-site divergence config

One folder per site of **Lagos Specialty Chemicals** (UNS root `lagos-chem`, charter §6).
Each will hold that site's divergence as data: naming-convention parameters, status-code
vocabulary, unit conventions, quality dialect, broker/endpoint settings. Same underlying
reality, four representations — the mess the lab exists to harmonize.

| Site | Heritage / SCADA | Divergence flavor | PLC realism |
|------|------------------|-------------------|-------------|
| `beaumont/` | Allen-Bradley (brownfield) | `N7:20`-style register tags, imperial units, raw ADC counts | real OpenPLC / Modbus TCP |
| `geismar/` | Siemens (acquired) | `DB10.DBD4` addresses, metric units | real OPC-UA (`asyncua`) |
| `rotterdam/` | Ignition-style (newer EU) | verbose nested names, metric units | Python-modeled |
| `corpus_christi/` | CygNet (acquired O&G) | compound flat tags encoding hierarchy, mixed units | Python-modeled |
