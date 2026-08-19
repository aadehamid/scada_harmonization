# Diagram 1 v2 Walkthrough — Progress Tracker

**Purpose:** a surface-independent bookmark for the end-to-end teaching walkthrough, so it can be
resumed from *any* agent/surface (CLI, web, another terminal) without losing position. This file is
the cursor; `design/E2E_WALKTHROUGH.md` is the script; `design/LEARNING_LOG.md` is where the durable
teaching notes land.

**Last updated:** 2026-08-19

---

## Where we are

| Step | Section | Status |
|------|---------|--------|
| Primer §0.1 | ISA-95 / IEC 62264 — function & data lens | ✅ **DONE** (notes in LEARNING_LOG → Concepts) |
| Primer §0.2 | Purdue model (PERA) — network lens | ⬜ **NEXT** |
| Primer §0.3 | IEC 62443 (ISA-99) — security lens | ⬜ pending |
| Thread B | Telemetry UP (physics → sensor → PLC → Sparkplug → forwarder → EMQX → historian → lake → graph) | ⬜ pending |
| Thread C | Control BACK DOWN (features → model → HITL → DCMD → actuator) | ⬜ pending |
| Thread A | Order thread (ERPNext SO → MRP → WO → lot → ship → invoice) | ⬜ pending |
| — | Cross-cutting narratives + "consciously omitted" systems | ⬜ pending |

**Walkthrough is parallel.** Completing the steps above still **locks Diagram 1**
as the template for Diagrams 2 & 3. It does **not** block the mapping table or
later build work (owner lock 2026-08-19). Hamid runs this pass independently.

**Diagram under walkthrough (v2, the lock target):**
https://app.eraser.io/workspace/MgnB91QGOhX8xWiKeaAK?diagram=133RhOiN_-G6Ko5kaTj8&layout=canvas

---

## The teaching method (five-beat cadence, repeated per lens / per diagram block)

1. **Problem tie-in** — which real pain (days-to-data, site divergence, governance, identity, yield/HITL) it addresses.
2. **Mechanism** — what it is, plainly; inputs/outputs, protocols, which plane/zone.
3. **External research** — web-search current ISA/IEC/CISA best practice; note where the lab aligns vs deliberately diverges. Cite sources.
4. **Gap check** — does Diagram 1 v2 match? If not, fix in Eraser (`manually_update_diagram` when arrow direction matters). Light for the conceptual primer; primary for the diagram blocks.
5. **One-line teach-back** — a sentence the owner can reuse verbatim in a presentation.

After each step: pause for the owner's questions before moving on. Log glossary terms to `LEARNING_LOG.md` as they appear.

---

## Kickoff prompt to resume (paste into a fresh session on any surface)

> Read `design/E2E_WALKTHROUGH.md` (the script), `design/WALKTHROUGH_PROGRESS.md` (this cursor), and
> `design/LEARNING_LOG.md` (notes so far). We are running the Diagram 1 v2 end-to-end teaching
> walkthrough. §0.1 ISA-95 is done. **Continue from §0.2 — the Purdue model** using the five-beat
> cadence (problem tie-in → mechanism → web research with cited sources → gap check against Diagram 1
> v2 → one-line teach-back), pausing for my questions between steps, and logging glossary terms to
> `design/LEARNING_LOG.md`. After Purdue, do §0.3 IEC 62443, then Threads B → C → A.

**Optional parallel cross-check** — hand the *current* lens to a separate web-search agent (no repo
access) and diff its answer against ours. Example prompt lives in the CLI session that taught §0.1;
the reusable shape is: *"Teach me <lens> from scratch for a technical presentation; use cited web
sources; cover what-it-is / what-it-is-NOT, its core concepts, real-world examples, and one
presentation-ready sentence per concept; end with a glossary."*

---

## Conventions reminder (so a fresh agent doesn't drift)

- **Owns during the walkthrough:** this session owns `WALKTHROUGH_PROGRESS.md` and
  walkthrough notes in `LEARNING_LOG.md`. Build agents update `HANDOFF.md` / status
  docs. Neither side waits on the other.
- **Diagram edits → Eraser only** (`scada_harmonization` workspace); use `manually_update_diagram`
  when arrow direction matters (the AI edit path reverses arrows).
- **Git:** branch → PR → owner merges (direct-to-`main` only for small doc/housekeeping when the owner
  says so). Commit trailer names the assisting model.
