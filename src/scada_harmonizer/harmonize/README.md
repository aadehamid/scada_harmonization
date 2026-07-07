# harmonize — Plane 1 (Phases 2–4)

OT → Sparkplug B UNS. The harmonization machinery itself: canonical Pydantic models
(the semantic target of the mapping table), transform primitives (unit conversion, status
normalization, UTC timestamp coercion), per-field lineage, and the **Python site-forwarders**
(store-and-forward, Sparkplug session contract, cross-site conforming → central EMQX).
Cross-source equivalence — same physical event from different sites → identical canonical
output — is the proof, encoded in `tests/` at Phase 4a. No code until Phase 2.
