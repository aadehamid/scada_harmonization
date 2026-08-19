# data — local scratch (gitignored)

These folders are not the durable warehouse. Durable L0 lives on Cloudflare R2
bucket `lagos-chem-l0` (ENAM): four TEP `.RData` files, the IIoT zip, five wide
Parquet natives, notes. Hamid persist: persist on R2; keep raw on R2; warehouse
is wide Parquet; golden slice in git. Local `raw/` and `cache/` are scratch
only. Hamid's Mac holds no caches. Record:
`design/PHASE1_SYNTHETIC_DATA.md`. Datasheet: `design/PHASE1_DATASHEET.md`.

| Folder | Contents |
|--------|----------|
| `raw/` | optional local scratch copies of benchmark downloads. Not "keep raw" on the lab disk. |
| `cache/` | optional local derived frames. Regenerable. Not the warehouse. |

Later-phase stores do **not** live here: the medallion lakehouse (Bronze/Silver/Gold
Parquet) belongs to MinIO volumes (Phase 6), and databases own their own Docker volumes.
