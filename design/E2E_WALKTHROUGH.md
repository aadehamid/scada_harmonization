# End-to-End Walkthrough Guide — Physical Process ⇄ Enterprise (and Back)

**Purpose:** the narrative script for walking the *entire* loop — physical process → enterprise →
back to the actuator — after the Diagram 1 review. It combines Diagram 1, the charter, and an
external reference deck ("Enterprise IT vs Manufacturing OT", `reference/enterprise_it_ot_deck/`,
local-only) into **three threads plus cross-cutting narratives**. The goal is to describe **industry
best practice completely — including systems this lab consciously omits** (each omission is
acknowledged, described, and mapped to its lab analog), and then go deeper where the lab exceeds the
deck.

> The deck supplies Thread A (the order/transaction flow) and the systems vocabulary. Threads B and
> C — the telemetry flow up and the decision/control flow back down — are **not in the deck**; they
> are this lab's core and must be narrated from Diagram 1 + charter §14.

---

## 0. Opening primer — the three architecture lenses: ISA-95 · Purdue · IEC 62443 (do this FIRST, owner-requested 2026-07-06)

Before any thread: high-level descriptions of the **three standards/models every industrial
architecture diagram silently mixes** — ISA-95 (the deepest, since everything in the lab hangs off
it), then Purdue and IEC 62443 at the same high-level treatment. The core lesson: they answer three
*different* questions — **what function runs where** (ISA-95), **how the network is layered**
(Purdue), and **how it is secured** (IEC 62443) — and one diagram element carries all three at once.

*(Naming crosswalk, worth 30 seconds: many ISA standards have IEC twins — same content, US vs
international designation: ISA-95 = IEC 62264 · ISA-99 = IEC 62443 · ISA-88 = IEC 61512 ·
ISA-18.2 = IEC 62682.)*

### 0.1 ISA-95 / IEC 62264 — the function & data lens (the lab's spine)

1. **What it is** — the enterprise–control-system integration standard: a *functional and data*
   model for how manufacturing operations and business systems exchange information. It is **not**
   a network architecture and **not** a security standard.
2. **The functional hierarchy (Levels 0–4)** — physical process → sensing/actuation → supervisory
   control → manufacturing operations (MES/LIMS/CMMS live at L3) → business planning (ERP at L4).
3. **The equipment hierarchy** — enterprise → site → area → **production unit** (the
   continuous-process branch; "line/cell" is the discrete branch) → equipment. This is literally the
   lab's UNS topic path (`lagos-chem/<site>/<area>/<production-unit>/...`, §14 N19) and the
   `asset_master` shape.
4. **Part 2 object models** — material (definition/lot — the lab's N14 tables), equipment
   (class vs instance — P6 templates), personnel, process segments.
5. **The L3↔L4 exchange pattern** — *schedule down, performance up* (B2MML is the XML binding):
   the lab's order-to-cash conduit C6 down, production confirmations up (§12 #18).
6. **Sidebar** — ISA-88 (batch) vs ISA-106 (continuous): why LSC is lot-based, not batch (§14 N13).

### 0.2 Purdue model (PERA) — the network lens

1. **What it is** — the Purdue Enterprise Reference Architecture (Theodore Williams, early 1990s):
   the reference for **segmenting the plant network into numbered levels** (0–5). ISA-95 borrowed
   its level numbering, which is why the two get conflated — but Purdue is about *where wires and
   subnets go*, not what functions do.
2. **The shape** — cell/area zones at L0–2, site operations L3, the **DMZ between 3 and 4** (the
   "Level 3.5" everyone cites — a Purdue/security construct, *not* an ISA-95 level), enterprise
   L4–5. The lab's diagram *is* this shape: OT zone left, iDMZ middle, IT right.
3. **The modern debate** — cloud, edge computing, and the UNS blur strict level-by-level traversal
   ("data no longer climbs one level at a time"); the lab's answer is the industry's current
   consensus: **keep Purdue for network segmentation, let data flow hub-and-spoke through the UNS,
   with the broker in the DMZ as the conduit** (worth a web-research stop — the "is Purdue dead?"
   literature vs. the CISA/vendor guidance that still mandates it for segmentation).

### 0.3 IEC 62443 (ISA-99) — the security lens

1. **What it is** — *the* industrial-cybersecurity standard family (asset owners, integrators, and
   product vendors each get their own parts). Where Purdue says "layer the network," 62443 says
   "now govern what crosses the layers."
2. **Core concepts, each with its lab artifact** — **zones** (groupings of assets with common
   security requirements → the diagram's three zones + Docker networks + `lab.zone` labels, L1.3);
   **conduits** (the *only* sanctioned paths between zones, each documented with initiator/protocol
   → the C1–C6 conduit inventory, N21, and the no-IT-initiated-into-OT rule); **defense in depth**
   (→ P2 safety layers, broker ACLs N22, TLS N23, command audit N24); **security levels SL1–4**
   (target vs achieved — the lab doesn't claim an SL, but can *describe* what SL2 would demand).
3. **Boundary note** — functional safety is a *different* standard (IEC 61511/SIS, consciously not
   modeled — N25); 62443 is security, not safety, and the two onions are independent.

**Teach-back target:** the owner can place any lab component on the ISA-95 hierarchy, name which of
the three lenses a given diagram element belongs to, and explain compound sentences like: *"MES is a
Level 3 **function** (ISA-95), on the OT side of the **network** (Purdue), below the **security**
boundary (62443 Z3)"* — and *"the iDMZ broker is a Purdue/62443 construct that ISA-95 doesn't even
know about."*

Use web research to ground all three (ISA/IEC/CISA sources preferred). Log glossary terms to
`LEARNING_LOG.md` as they appear (ISA-95, IEC 62264, Purdue/PERA, DMZ, zone, conduit, SL, B2MML,
production unit, equipment class…).

---

## Thread A — The transaction thread (order-to-cash, top-down then confirmations up)

*Source: deck slides 3 & 5 (ten handoffs). Lab: ERPNext + role-A schemas + CDC (charter §12 #18).*

| # | Deck step (system) | Lab home | Notes / conscious omissions to describe |
|---|--------------------|----------|------------------------------------------|
| 1 | Customer order → sales order (CRM/ERP) | ERPNext **Sales Order** | **CRM described-only** (§13.1 L3.1): in industry, CRM owns the pipeline and hands the order to ERP |
| 2 | MRP run → production order + material needs (ERP/MRP) | ERPNext **Production Plan / Material Request → Work Order** | narrate MRP logic: demand → BOM explosion → net requirements |
| 3 | Pick request → materials staged (WMS) | ERPNext **stock entry** + `mes.material_lot` staging event | **WMS described-only** (§12 #19): in industry a WMS owns bins/waves/pick paths; lab represents the *events*, not the system |
| 4 | Work order received → dispatched (MES) | `mes.production_order` (synced from ERPNext — still the plant's own key space, deliberately misaligned) | the identity-reconciliation hook: ERP order ID ≠ MES key |
| 5 | Job start recorded (MES; barcode scan) | `mes.production_lot` start event (operator-event analog) | continuous-plant contrast: **lot window opens**, no barcoded discrete job (§14 N13) |
| 6 | Process monitored → deviation alarm (SCADA) | UNS → ISA-18.2 alerting node (§14 N20) → Ignition/console | this is where Thread B is *live* underneath Thread A |
| 7 | Inspection → results linked to lot (QMS) | `lims.sample → lab_result → disposition` + `quality.*` | genealogy join: lot ↔ lab result (§14 N13/N14) |
| 8 | Job complete → actuals to ERP (MES→ERP) | production confirmation → ERPNext (Plane 2's original direction) | ISA-95 L3↔L4: *performance up* |
| 9 | Pick, pack, ship → traceability (WMS) | ERPNext **Delivery Note** + genealogy trace ("which lots ship?") | the recall query: *which finished lots contain feedstock lot X?* |
| 10 | Customer invoiced → order-to-cash complete (ERP) | ERPNext **Sales Invoice** | **AR/AP beyond the single invoice described-only** — ERPNext has full accounting; lab closes one thread, not the ledger |

**Teach-back:** *"Every handoff is an integration point — and each one is where plants fail"* (deck's
key insight). The lab's answer: one namespace + CDC + contracts + dead-letter/redrive instead of ten
point-to-point interfaces.

## Thread B — The telemetry/data thread (physical process → insight; the deck only names the boxes)

*Source: Diagram 1 + charter §4/§6/§14. Follow ONE measurement — a reactor feed flow — uphill.*

1. **Physics** — TEP process dynamics (the only synthetic layer). Scan rate must match process
   physics (P1).
2. **Sensor → PLC** — 4–20 mA → **raw ADC counts** in `N7:20` at Beaumont (§14 N17); the
   "memory-address world."
3. **Protocol** — Modbus TCP (Beaumont), OPC-UA (Geismar), modeled (Rotterdam, Corpus Christi):
   four dialects, one reality.
4. **Edge publish** — mapping stages 2→3: cryptic tag → Sparkplug metric (aliases, birth
   certificates, RBE); site Mosquitto = local autonomy.
5. **Harmonization** — the site-forwarder (a compliant Edge Node, §14 N3): cross-site conforming,
   store-and-forward, STATE; **where "same reality, different names" becomes one namespace.**
6. **Enterprise UNS (iDMZ)** — EMQX: Sparkplug in, **retained ISA-95 topics** out (§14 N1/N2);
   the browsable current state of the whole enterprise.
7. **OT consumption** — TimescaleDB historian (quality codes, gap-fill, rollups — §14 N10/N11),
   Grafana, Ignition, alerting.
8. **Into IT** — UNS→Kafka bridge (decodes protobuf, holds BIRTH state, §14 N6); CDC joins the
   transactional leg (Debezium, dual-homed conduit).
9. **Lakehouse** — Bronze (immutable raw) → Silver (validated vs `metric_registry`) → Gold
   (features); DuckDB for analysis.
10. **Context** — Neo4j: asset ↔ tag ↔ event ↔ lot ↔ work order ↔ lab result; GraphRAG on top.

**Weave in per hop:** which slide-6/7 pain this hop kills (silos → one namespace; latency →
seconds not days; no-history → historian+lake; Excel → governed registry with owners).

## Thread C — The decision/control thread (insight → actuator; absent from the deck)

*Source: charter §13.5, §13.7 P2–P4, §14 N5/N24/N30–N35. This is "and back" — industry closed-loop
practice the deck never shows.*

1. **Features** — offline gold + online Redis (single-sourced definitions, §14 N35).
2. **Model** — trained centrally, registered in MLflow (dataset version + model card, §14 N34),
   deployed to edge + cloud.
3. **Shadow first** — L0: scores live data, surfaces nothing; promotion gates (§14 N30).
4. **Detection** — two-level SPC: EWMA/CUSUM + PCA T²/SPE with contribution plots (§14 N33).
5. **Recommendation** — setpoint + confidence + SHAP attribution + TTL/input-snapshot (§14 N31/N32).
6. **Human gate** — HITL console (graded L0–L3); approve / edit / reject; alarm-fatigue awareness.
7. **Command** — approved → EMQX (iDMZ crossing) → site-forwarder issues **DCMD** on the site
   broker (§14 N5).
8. **Defense-in-depth** — model envelope → **PLC-side clamp** → independent BPCS-level guard —
   and describe the layer the lab does *not* model: a certified **SIS** (IEC 61511) sits below all
   of this in a real plant (§14 N25).
9. **Actuation + proof** — controller writes; **DDATA read-back** confirms; `command_audit` records
   who/what/when (§14 N24).
10. **Loop closes** — the effect shows up back in Thread B telemetry, and later in LIMS results
    (delayed-label evaluation, §14 N31): OT→IT→OT, operator-governed.

## Cross-cutting narratives (weave through all three threads)

- **Multi-site divergence & harmonization** — the deck is single-plant; LSC's four dialects are the
  enterprise-scale version of its integration problem.
- **Governance as data products** — `metric_registry` owners/definitions/lineage; "creators as
  gatekeepers"; local autonomy + central standards.
- **Identity reconciliation** — the mechanism behind the deck's "multiple versions of truth":
  `identity_map`, match rules, survivorship, golden record (§14 N15).
- **Security zoning** — Purdue/IEC 62443, iDMZ, five conduits, no-IT-into-OT, per-branch ACLs, TLS,
  command ACL (§13.8, §14 N21–N23) — the deck's thin "CYBER" bar, done properly.
- **Time & quality semantics** — event time at the edge, idempotent sinks, Good/Uncertain/Bad/Stale,
  STALE-on-NDEATH, clock skew (§14 N9/N10).
- **People & red flags** — deck slide 7 mapped to antidotes: paper/Excel → governed registry +
  automated pipelines; swivel-chair → CDC/UNS; IT/OT divide → zoning *plus* shared namespace;
  no-history → historian + lakehouse.

## Consciously omitted — acknowledge, describe, point at the analog

| Industry system (deck) | Role in industry (describe it) | Why the lab omits it | Lab analog to point at |
|---|---|---|---|
| CRM | owns customers/pipeline; hands sales orders to ERP | §13.1 L3.1 — no customer domain in a 4-site process lab | ERPNext Sales Order is the entry point |
| WMS | bins, waves, pick paths, dock scheduling | §12 #19 — warehouse *events* suffice for the lessons | ERPNext stock moves + `material_lot` staging |
| PLM | product/BOM lifecycle, engineering change | §7 — ET topology is synthesized directly | ISO 15926/DEXPI ontology + Neo4j topology |
| EAM (vs CMMS) | enterprise-wide asset registry/finance view | lab's asset scope is 4 sites | `asset_master` + CMMS + ERPNext assets |
| EMS/BMS | energy/building management | §13 L3.2-adjacent; no building domain | 30 s "environmental" scan class + TEP utility loops |
| Batch execution (ISA-88) | recipes/phases for batch plants | §14 N13 — LSC is continuous (ISA-106) | lot windows; golden operating window |
| Robotics / AGV / vision | discrete-floor automation & QC | §13.7 Tier 3 — no discrete floor, no CV modality | IIoT rotating machines; time-series QC (SPC) |
| SIS (GuardLogix et al.) | certified independent safety layer | §14 N25 — cannot be meaningfully simulated | described in Thread C step 8; optional OpenPLC hard-trip "stand-in" |
| Low-code app layer (Mendix) | persona apps over many systems | not needed for the lessons | HITL console + Grafana + (Phase 7) copilot |
| Middleware (MuleSoft/Boomi) | managed integration hub | the lab *builds* the hub instead | UNS + Kafka + CDC (+ UMH Core later) |

**Definition of success for the walkthrough:** the owner can narrate Threads A, B, and C without
notes, name each deck system at its correct layer, explain each omission *and* its industry role,
and answer "where would X fail in a real plant, and what in this architecture prevents it?"
