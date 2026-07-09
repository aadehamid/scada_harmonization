# config — data, not code

Everything that varies is data (charter §9 "config over code"): site mappings, status maps,
unit factors, ontology vocabularies. Python reads these; it never hard-codes them.

| Folder | Contents |
|--------|----------|
| `mappings/` | ⭐ the three-stage mapping table — **the spine of the whole lab** (content pending, see its README) |
| `sites/` | per-site divergence config — one folder per charter §6 site |
