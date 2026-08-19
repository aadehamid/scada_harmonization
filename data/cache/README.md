# data/cache — local scratch (gitignored)

Not the durable warehouse. Full natives are wide Parquet on R2 `lagos-chem-l0`.
Polars melts on read. A 58,661,861,866-byte history JSONL was written then
deleted. 96 GiB was an estimate, never the warehouse. CI uses the committed
golden slice (4 lines) under `tests/fixtures/datagen/`. See
`design/PHASE1_SYNTHETIC_DATA.md` and `design/PHASE1_DATASHEET.md`.
