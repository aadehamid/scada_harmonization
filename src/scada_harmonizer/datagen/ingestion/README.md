# ingestion (pipeline layer 1, Phase 1)

Full natives live on R2 (`lagos-chem-l0`) as wide Parquet. CI is the golden
slice. TEP sim-time is epoch + `i * 180s`. IIoT uses native UTC when present
(generated 1 s machine stream, or a snapshot file). Identity columns stay
metadata. See `design/PHASE1_L0_CONTRACT.md`.
