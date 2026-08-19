# Unit 100 P&ID fixtures

Issued drawing + tag list for Lagos Specialty Chemicals Unit 100 (same TEP
unit). `data/**` is gitignored, so issued files live here.

| File | What |
|------|------|
| `LSC-U100-PID-001_revB.pdf` | Rev B one-pager (2026-08-18). SHA-256 `dd75cc078110e1f5b519dcf3024832d932d996daa14d0e4607d8ac6d2276179f`. Recovered from Hamid's upload. |
| `tag_schedule.csv` | 59 plant-data names. 1:1 `drawing_name` → `plant_data_name`. Controller bubbles (FC/LC/TC) are not rows. HOLD is a drawing cloud, not a row. |

`provenance=drawing` means the PDF prints it. `provenance=reconstructed` means
the row was rebuilt from the drawing + existing L0 names (TEP `xmeas_*` /
`xmv_*`, `P-101`/`K-201` machine points, `xv_feed`). The Grok Bot
`unit100_dexpi.json` / `tag_schedule.py` pack was not recovered.

Record: `design/UNIT100_PID.md`.
