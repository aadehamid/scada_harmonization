# LSC-REF-002. Downstream oil & gas operational-process ontologies — assessed search results

Status: **proposals, not adopted.** A filed search record so the downstream oil & gas
operational-process ontology question does not need to be re-searched from scratch. Every
adoption still goes through a separate decision and phase review; a row marked
"unverified" must be verified before any use.

Owner ask (2026-11-08): is there an ontology specific to downstream oil & gas operational
process; record the findings and recommendations so the search is not repeated.

## Scope of "downstream" here

Downstream oil & gas = refining (crude distillation, cracking, treating, blending), storage
and terminals, petrochemical plants, and product distribution — as opposed to upstream
(exploration, production wells, offshore platforms) and midstream (pipelines, gathering).
The lab's own domain is a specialty-chemicals process plant (§2), so it shares the refining
world's unit-operation vocabulary (distillation columns, heat exchangers, reactors, pumps,
valves) but is not a refinery. Candidates below are scored for how they describe
**operational process** — unit operation, procedures, phases, states, control, alarms,
production runs — not only equipment taxonomy.

## Where these slots into the project's already-decided anchors

- Plane 3 ontology vocabulary: **ISO 15926 / DEXPI-aligned** core, RDF/OWL TTL, SHACL-validated
  (pyshacl), loaded to Neo4j (rdflib → Cypher MERGE), cataloged in OpenMetadata 2.x
  (charter §12 #13).
- ISA-95 hierarchy for asset paths.
- Continuous-process accounting: lot-based production windows (N13); ISA-106 consulted for
  procedural automation, ISA-88 out for the continuous core.
- Alarm model: ISA-18.2 state machine (N20).
- SKOS match semantics: `identity_map.match_rule` = exactMatch / closeMatch (same referent),
  broadMatch / narrowMatch (hierarchy mismatch), unresolved — reconciliation rows only;
  class-level vocabulary alignment uses plain SKOS mapping relations outside `identity_map`.
- Units: UNECE Rec 20 now; QUDT quantity kinds later.
- Assessed already, excluded: Brick Schema, Project Haystack, RealEstateCore (buildings).

## Candidate table (proposals, not adopted)

Verified 2026-11-08 UTC from the cited primary sources.

| Candidate | Where | License + verified | Scope in one line | Downstream-process fit | Best role |
|---|---|---|---|---|---|
| **COPI — Core Ontology of Petroleum Installations** | github.com/INF-UFRGS-Ontologies/copi (IRI inf.ufrgs.br/ontologies/copi) | **CC-BY-4.0** (repo LICENSE file, read 2026-11-08; GitHub API reports NOASSERTION — LICENSE file wins, as with Brick). Active — pushed 2026-11-04; 1,090 commits | Domain-core OWL 2 DL ontology for **petroleum production plants**, specializing **BFO 2020 + IOF-Core**; states interoperability with **ISO 15926-4, ISO 14224, CFIHOS, and DEXPI** | Strongest structural fit: DEXPI/ISO 15926 alignment matches the lab's Plane 3 anchor directly; production-plant focus (upstream-leaning but refinery-relevant unit vocabulary) | **Crosswalk target** — the one with the clearest path into `config/ontology/*.ttl` |
| **O3PO — Offshore Petroleum Production Plant Ontology** | github.com/BDI-UFRGS/O3POntology | **MIT** (GitHub API, read); pushed 2025-12-19; paper: Santos et al., Expert Systems with Applications 238, 122104 (2024) | Bilingual (EN/PT), **BFO-aligned** domain ontology for **offshore** oil & gas production systems | Offshore/upstream-leaning; shares process vocabulary but not refining-specific | Pattern/domain reference (BFO-aligned teaching example) |
| **CFIHOS ontology** | github.com/tecnomod-um/cfihos | **No LICENSE file** — GitHub API reports no license → **unverified, treat as all-rights-reserved until proven otherwise**. Pushed 2026-08-06 | OWL ontology auto-generated from the **CFIHOS** (Capital Facilities Information HandOver Specification) Excel spec — the industry information-handover standard for O&G capital projects; standalone + **CFIHOS-IDO** (aligned with the Industrial Data Ontology) variants | Downstream-relevant asset-information vocabulary (equipment, systems, handover); covers the "what" more than the "how it runs" | Reference / crosswalk — **license must be cleared first** |
| **CFIHOS RDL v2.0** | posccaesar.org/ontologies/cfihos/v2.0 (POSC Caesar) | **License terms not found on-inspect — verified only as an RDL collection** (GUID identity scheme); same caveat as PCA RDL | The **official CFIHOS Reference Data Library**: standardized reference data within CFIHOS for O&G asset information | Same as CFIHOS ontology; the RDL form is the governed vocabulary | Reference — the governed sibling of the CFIHOS ontology |
| **ISO 15926-14 (HQDM)** | READI-JIP draft 2020-09; bioregistry.io/iso15926; gchq/HQDM | Draft is a WD (not a published standard); gchq/HQDM Apache-2.0 but stale (pushed 2022-07); final ISO publication status **unverified** | Title confirms the scope: *"process plants including oil and gas production facilities"*; 4D top-level ontology in OWL 2 DL | General process-plant (incl. O&G); not downstream-specific | Pattern reference only (upper-ontology alignment) |
| **PCA RDL (ISO 15926-4 reference data)** | rds.posccaesar.org/services/downloads/ | Formats verified (Turtle / RDF/XML / JSON-LD / Manchester); **license terms not found on-inspect — unverified** | The concrete ISO 15926-4 reference data for process plants incl. O&G | General process-plant vocabulary; strongest ISO 15926 instance | Crosswalk target (already recorded in LSC-REF-001) |
| **BioPortal ISO-15926-2_2003_oil** | bioportal.bioontology.org/ontologies/ISO-15926-2_2003 | **Unverified** — found via search snippet only (OWL, "gas and oil field process level descriptions"); the live page was bot-blocked on fetch | An ISO 15926-2 rendering on BioPortal | Unknown depth; flagged | Could not be assessed — re-check before use |
| **IBM ITOPS** | github.com/IBM/ITOPS-ontology | Apache-2.0; **archived 2024-07** | IT Operations ontology (Wikidata/DBpedia-derived) | **Not oil & gas** — the GitHub "oil-and-gas" topic listing is misleading | Excluded |
| **Refining-only operational ontology (e.g. crude distillation / FCC-specific)** | — | — | **Not found** in registries or targeted search | — | Negative (not found, not proven absent) |

## Recommendations

1. **COPI** is the strongest downstream-relevant crosswalk target found: CC-BY-4.0 license
   file, active maintenance, BFO 2020 + IOF-Core foundation, and it *states* interoperability
   with ISO 15926-4, ISO 14224, **CFIHOS, and DEXPI** — the exact Plane 3 anchors. Entry
   path: class crosswalk (`ConfigurationItem`, `Equipment`, `Process`, unit-operation terms)
   into `config/ontology/*.ttl` via plain SKOS mapping relations outside `identity_map`.
   Competency question it helps answer: *"Which equipment items and function locations belong
   to the crude-distillation system, and how do they connect operationally?"*
2. **CFIHOS (ontology + RDL v2.0)** is the standard to *align to* for downstream asset
   information handover — its vocabulary is the industry's own. **Verify the license first**:
   the GitHub ontology repo has no LICENSE file (all-rights-reserved until proven) and the
   POSC Caesar RDL page shows no license terms on-inspect. Competency question: *"Which
   tag/instrument maps to which CFIHOS equipment type for handover?"* — a natural Phase 5b.1
   (ET graph) alignment and a Phase 7 GraphRAG cross-domain demo.
3. **O3PO** — adopt as a *pattern*, not a dependency: a clean, MIT, BFO-aligned worked example
   of modeling a production plant; useful when authoring the lab's own plane-3 ontology
   classes, not as the vocabulary itself.

## What must be verified before any adoption

- **COPI:** exact release tag and SHA; BFO and IOF-Core dependency versions; SHACL shapes, if
  any; confirm which modules/file (`copi.ttl` vs `copi-full.ttl` vs `copi-simple.ttl`) match
  the lab's use; reproduce the claimed ISO 15926-4 / DEXPI alignment from the actual TTL, not
  the README.
- **CFIHOS ontology:** locate or request the license (nothing in the repo as of 2026-11-08);
  decide standalone vs CFIHOS-IDO variant; confirm OWL 2 DL conformance and SHACL rules.
- **CFIHOS RDL v2.0:** obtain the POSC Caesar license terms; confirm download format.
- **O3PO:** confirm ongoing maintenance (BSD/ESWA paper is 2024); check language scope.
- **PCA RDL / ISO 15926-14:** license terms (RDL) and final ISO publication status (15926-14)
  as flagged in LSC-REF-001.
- **BioPortal ISO-15926-2 oil:** re-fetch the live page (was bot-blocked); inspect
  actual content/license before assessing.

## Confidence notes

- The "not found" for a refining-only operational ontology is a **not-found result, not
  proof of absence**; service-companies (e.g. ontology consultancies serving refiners) may
  hold non-public models — out of scope for an open-license search.
- CFIHOS ontology license and CFIHOS RDL terms are the two biggest open items; both are
  **unverified**, exactly where a reviewer would check next.
- Structural fit of COPI (upstream-leaning "production plants") is inferred from its README
  and module names, not from reading the full TTL; re-verify coverage at adoption.
- The BioPortal entry is the only candidate whose primary page could not be read; it is
  flagged rather than dropped.

## Cross-references

- General (non-downstream) ontology candidates: [LSC-REF-001 section](LSC-REF-001_Technology_Roles_and_Reuse_Assessment.md#ontology-candidates-from-the-2026-11-08-search-proposals-not-adopted) —
  QUDT, PCA RDL, IDO, HQDM, IES↔HQDM crosswalk, pyDEXPI, B2MML; plus the
  [external reference vocabularies section](LSC-REF-001_Technology_Roles_and_Reuse_Assessment.md#external-reference-vocabularies-assessed-not-adopted) (Brick et al.).
- OT operational-process ontology candidates (PKO, IOF, P-PLAN, PSL, ISA-88/106/18.2 status)
  were surfaced in the same 2026-11-08 search session but **are not filed** — only the
  downstream O&G subset is recorded here, per the owner's request. Re-surface those before a
  downstream-only reading of this file is treated as the whole OT-process picture.
