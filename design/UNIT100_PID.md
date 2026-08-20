# Unit 100 P&ID — Rev B one-pager

**Status:** one-pager landed 2026-08-19. Extra pages (index, analyzer, legend,
area sheets) are not in the repo.
**Drawing:** `tests/fixtures/datagen/pid/LSC-U100-PID-001_revB.pdf`
**Tag list:** `tests/fixtures/datagen/pid/tag_schedule.csv`

This is Lagos Specialty Chemicals **Unit 100** — the same Tennessee Eastman
Process unit the L0 generators already replay. One plant. Later lots / work
orders / materials must use these names. No site copies. No mapping table.
No Sparkplug this lap.

## What is issued vs reconstructed

**Recovered (Hamid upload):** the Rev B PDF (`LSC-U100-PID-001`, sheet 1 of 1,
2026-08-18). SHA-256
`dd75cc078110e1f5b519dcf3024832d932d996daa14d0e4607d8ac6d2276179f`.

**Printed on the sheet (do not rename):**

- Equipment: R-101 reactor, E-101 product condenser, V-101 product separator,
  K-201 recycle compressor, T-101 product stripper, P-101 A+C feed pump, XV-101
- Pipes: `2"-P-1001` … `4"-P-1012`, `3"-CW-1101`, `3"-CW-1102`
- HOLD cloud on **T-101 OVH'D**
- Note 1: analyzers AT-201..AT-219 = L0 `xmeas_23`..`xmeas_41`, off-sheet
- Note 2: L0 join mentioned as `data/tag_schedule.parquet` (file not recovered;
  issued join is the CSV in fixtures)
- Note 4: drawn from `models/unit100_dexpi.json` (not recovered)

**Reconstructed:** the 59-row `drawing_name` → `plant_data_name` schedule. The
Grok Bot model / `tag_schedule.py` / book pack is not in this repo. Rows use
the L0 names that already exist (`xmeas_1`–`xmeas_41`, `xmv_1`–`xmv_11`,
`P-101`/`K-201` machine points, `xv_feed`). Instrument-to-TEP pairing for
`xmeas_1`–`xmeas_22` and the eleven valves follows Downs & Vogel stream
numbering plus what the one-pager actually draws. Do not treat reconstructed
pipe/stream cells as a second naming system.

**Not a graph node:** pipe numbers, HOLD, controller bubbles (FC/LC/TC).

## Plant-data names (59)

| Count | Names |
|------:|-------|
| 41 | `xmeas_1` … `xmeas_41` |
| 11 | `xmv_1` … `xmv_11` |
| 6 | `P-101/{vibration_rms,motor_current_a,shaft_speed_rpm}` and the same three on `K-201` |
| 1 | `xv_feed` |

That is the L0 join. TEP stays 180 s. The 1 s class is the generated machine
stream on P-101 and K-201. Kaggle stays a snapshot.

## Domain locks on this sheet

- **Stream 12** is T-101 overhead → reactor feed **with the recycle compressor**,
  not to the condenser. HOLD stays on that overhead until the next revision.
- Materials A–H are a drawing note only. No lots, no company hierarchy.
- 1:1 drawing name → plant-data name. Stream and pipe are list columns.

## Extra pages (not this PR)

Architect lock: index + analyzer page (print AT-201..AT-219) + legend
**before** more process pages. Titles say sheet N of N, not “1 of 1” on a book.
Say “1 second machine stream on P-101 and K-201”.

**When we return (owner-triggered drawing lap — not the default next build).**
The 59-row CSV is enough for the mapping table. Extra pages do not unlock
Phase 0/2. DEXPI / `book.py` wait for Phase 5b; do not rebuild them here.
Kickoff prompt lives in `HANDOFF.md` §3. One plant. Do not change L0 names.
If the book hash changes, update `tests/test_unit100_pid.py` and this file.
