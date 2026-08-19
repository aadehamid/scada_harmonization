# Phase 1 datasheet

**Status:** Polars on `main` `7da1621` (2026-08-18).  
**Record:** [`PHASE1_SYNTHETIC_DATA.md`](PHASE1_SYNTHETIC_DATA.md) records what landed.  
**Reading copy:** [`PHASE1_DATASHEET.html`](PHASE1_DATASHEET.html).

This datasheet is why the files sit where they sit. Hamid owns persist. Agents do not invent a retention policy.

## Local vs R2

Three places, three jobs.

**R2 `lagos-chem-l0` is durable.** Region ENAM (East North America). First use of this bucket and of Parquet compressed with zstd. It holds:

- four TEP `.RData` files
- the IIoT zip
- five wide Parquet natives
- notes / manifest

It does not hold csv. It does not hold the 58,661,861,866-byte history JSONL. It does not hold full operational-technology (OT) extras.

**Git is the pin, not the plant.** Generators, the L0 contract, the golden slice (4 lines), the 21 tests, and these docs. Payloads stay out.

**Local is scratch only.** `data/raw/` and `data/cache/` are not the durable warehouse. Hamid's Mac holds no caches.

## Raw on R2 (1,419,880,076 bytes, no csv)

| Object | Bytes |
|--------|------:|
| `TEP_FaultFree_Training.RData` | 24,678,017 |
| `TEP_FaultFree_Testing.RData` | 47,327,663 |
| `TEP_Faulty_Training.RData` | 494,063,194 |
| `TEP_Faulty_Testing.RData` | 836,882,037 |
| IIoT zip | 16,929,165 |
| **Total** | **1,419,880,076** |

Rebuild source. Not replay input. The warehouse is wide Parquet, not these files.

## Warehouse on R2 (wide Parquet, zstd)

| Object | Bytes | Wide rows | Columns | SHA-256 |
|--------|------:|----------:|--------:|---------|
| `tep_faulty_testing` | 758,943,582 | 9,600,000 | 56 | `59a8c456088a96b2b8696a552edca945d99b121a3c6c5d45a18270b72a38e512` |
| `tep_faultfree_training` | 20,941,351 | 250,000 | 56 | `185db5cbe850d438329b0f39ef73f4ffcd0f9e4afd6fbccbc3c6325980cc66bf` |
| `tep_faultfree_testing` | 39,868,514 | 480,000 | 56 | `20938da894cebbbcb94136a7835ec17af0c376484126a7bc4d876b5f5b0246f1` |
| `tep_faulty_training` | 450,485,967 | 5,000,000 | 56 | `7bab727d6703fed5b9358c11f7f39d074d8888b8af95cabcb8902628dcdd8c01` |
| `iiot` | 13,285,181 | 500,000 | 18 | `3393ca3993175b5d4716eb2163c38bfbab42998ea58bd3116569a9a42b372073` |
| **Total** | **1,283,524,595** | **15,830,000** | | |

Polars melts on read. The 9,600,000-row Faulty Testing native (758,943,582 bytes) and the rest of the warehouse (1,283,524,595 bytes) are on R2. 96 GiB was an estimate, never the warehouse. The Faulty Testing Parquet exists.

## Why each dataset

1. **TEP FaultFree Training (250,000 wide rows).** Healthy baseline.
2. **TEP FaultFree Testing (480,000 wide rows).** Longer healthy holdout.
3. **TEP Faulty Training (5,000,000 wide rows).** 20 faults for train.
4. **TEP Faulty Testing (9,600,000 wide rows).** Full published test, now on R2.
5. **IIoT (500,000 wide rows).** Snapshot per machine, not 1 s.
6. **Raw TEP `.RData`.** Rebuild source.
7. **Raw IIoT zip.** Rebuild source. No csv on R2.
8. **Golden slice.** CI pin. 4 lines. SHA-256 `f5b9d1cfdaf9f298d9cdcbcb926bc3486dfdac1cccff7816b34ac290e6d33516`.
9. **Notes / manifest.** What is on the bucket.
10. **Not created.** Full long JSONL. Full extras. NAB. Mapping YAML. Sparkplug.

## Git versus scratch

| Place | What lives there |
|-------|------------------|
| Git | Generators, [`PHASE1_L0_CONTRACT.md`](PHASE1_L0_CONTRACT.md), golden slice (4 lines), 21 tests, this datasheet, the land record |
| R2 `lagos-chem-l0` | Four TEP `.RData`, IIoT zip, five Parquets, notes |
| Local `data/` | Scratch only. Hamid's Mac holds no caches. |

Phase 1 does not treat L0 names as if a programmable logic controller (PLC) had issued them. PLC tag names wait for Phase 2. This datasheet does not rewrite N8. The walkthrough is a parallel path and does not gate. The cursor stays at `design/WALKTHROUGH_PROGRESS.md` §0.2.
