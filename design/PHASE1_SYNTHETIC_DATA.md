# Phase 1 synthetic data record

**Status:** Polars + 1 s machine stream on `main` (`733cfec` after #32; generators `7b6cdd5` / #33). Warehouse is wide Parquet, compressed with zstd, on R2 `lagos-chem-l0`.
**Contract:** [`PHASE1_L0_CONTRACT.md`](PHASE1_L0_CONTRACT.md).  
**Datasheet:** [`PHASE1_DATASHEET.md`](PHASE1_DATASHEET.md) (why the files sit where they sit).  
**Reading copy:** [`PHASE1_SYNTHETIC_DATA.html`](PHASE1_SYNTHETIC_DATA.html).

![Lagos Specialty Chemicals plant, dawn](assets/hero-plant.png)

This file records what landed. It is not the L0 contract and it is not a dump of the session log. The contract still governs the record shape. This note records the land, the disk facts, and the persist rules Hamid set.

Phase 1 is replay-only. It does not assign physical meaning. It does not write Sparkplug. It does not open the mapping table. It does not treat L0 names as if a programmable logic controller (PLC) had issued them.

## What landed

PRs closed the Phase 1 L0 path on 18 August 2026, Central Time, then the 1 s stream the same day.

| PR | Merge | SHA | What it is |
|----|-------|-----|------------|
| [#28](https://github.com/aadehamid/scada_harmonization/pull/28) | 12:34 AM CT | `8564fed` | pandas as the first runtime dependency, empty Phase 1 package inits, ty in the dev group and CI |
| [#29](https://github.com/aadehamid/scada_harmonization/pull/29) | 12:56 AM CT | `3039710` | L0 record, ingestion, operational-technology (OT) extras, deterministic replay, golden fixtures, 21 tests at land |
| [#30](https://github.com/aadehamid/scada_harmonization/pull/30) | 18 Aug 2026 | `47883c7` | Phase 1 synthetic-data record (HTML twin + assets) |
| [#31](https://github.com/aadehamid/scada_harmonization/pull/31) | 18 Aug 2026 | `7da1621` | Polars replaces pandas for every tabular job |
| [#33](https://github.com/aadehamid/scada_harmonization/pull/33) | same day | `7b6cdd5` | seeded 1 s machine stream (P-101 / K-201); `friendly_name` is `{machine_id}/{pv}` |

Generator HEAD is `7b6cdd5`. `main` is `733cfec` after #32. Runtime deps are polars + pydantic. Pydantic validates the L0 boundary. Polars melts wide Parquet on read into long L0 rows.

CI stays golden-slice only. No full-dataset CI. No network in CI.

## Persist rules (Hamid)

Hamid owns keep versus delete. Agents do not invent a retention policy.

1. **Persist on R2.** Durable L0 lives in Cloudflare R2 bucket `lagos-chem-l0`, region ENAM (East North America).
2. **Keep raw on R2.** The four TEP `.RData` files and the IIoT zip stay on R2. Measured raw total: **1,419,880,076 bytes**. No csv.
3. **Warehouse is wide Parquet, not long JSONL.** Natives stay wide. Melt happens on read. Objects are compressed with zstd.
4. **Commit the golden slice, not the plant.** `tests/fixtures/datagen/golden_l0_slice.jsonl` is the identity pin (4 lines). `data/**` payloads stay gitignored and are local scratch only.

Those four rules are why a 58,661,861,866-byte history JSONL existed for one day and then did not. 96 GiB was an estimate, never the warehouse.

## Cloudflare R2 (durable store)

Cloudflare R2 is the durable source of truth for Phase 1 L0. Agents pull from this bucket when they need data and write durable results back here. Local `data/raw/` and `data/cache/` are scratch only. The warehouse is wide Parquet, compressed with zstd. Melt to long L0 rows happens on read, not as a stored file on R2.

The pattern is **one bucket per project**. This project's bucket is `lagos-chem-l0`. Do not invent a second bucket for this lab. Do not dump other projects into this bucket.

Connection settings are fixed for this Cloudflare account. They do not change per project. Only the bucket name does. The S3 client uses region `auto` and signature `s3v4`. The bucket itself still lives in ENAM, as the persist rules already say.

| Field | Value |
|-------|-------|
| Account ID | `011701390f6fee966f04b48182e37f9e` <!-- pragma: allowlist secret --> |
| Endpoint | `https://011701390f6fee966f04b48182e37f9e.r2.cloudflarestorage.com` <!-- pragma: allowlist secret --> |
| Region | `auto` |
| Signature | `s3v4` |
| Client | boto3 (S3 API). Not the AWS CLI. |
| Secrets | Access Key ID and Secret Access Key from an R2 API token, via a secret card. Never paste them in chat. |

The prefix tree inside `lagos-chem-l0` is locked as it exists today for this operational-technology (OT) / industrial-IoT warehouse:

```
lagos-chem-l0/
├── raw/
│   ├── tep/
│   └── iiot/
├── cache/
│   ├── native/          # wide Parquet by source_dataset=...
│   ├── extras/          # seeded OT extras Parquet
│   └── manifest.json    # when present
└── notes/
```

## Disk facts (18 August 2026)

| Artifact | Fate | Size / count |
|----------|------|----------------|
| History JSONL | Written, then deleted the same day | **330,920,000** rows, **58,661,861,866** bytes |
| Wide Parquet warehouse on R2 | Kept | **15,830,000** wide rows, **1,283,524,595** bytes |
| Raw on R2 | Kept | **1,419,880,076** bytes (four TEP `.RData` + IIoT zip, no csv) |
| 96 GiB long Faulty Testing estimate | Never the warehouse | Estimate only. The Faulty Testing Parquet exists. |
| TEP golden slice | Committed | 4 lines |
| Machine-stream golden | Committed (#33) | 2 machines × 20 s × 3 PVs |

TEP golden SHA-256 (unchanged):

```
f5b9d1cfdaf9f298d9cdcbcb926bc3486dfdac1cccff7816b34ac290e6d33516
```

Machine-stream golden SHA-256:

```
84b9f0885a8efc3c28c488beebefd47d2d9d6b5fd93dc6f7f681b5b2e52159f0
```

Pinned as `GOLDEN_SHA256` and `MACHINE_STREAM_GOLDEN_SHA256` in `tests/datagen/factories.py`. Hashes are of canonical UTF-8 JSONL, not of a raw download.

## Warehouse (R2 `lagos-chem-l0`, wide Parquet, zstd)

| Object | Bytes | Wide rows | Columns | SHA-256 |
|--------|------:|----------:|--------:|---------|
| `tep_faulty_testing` | 758,943,582 | 9,600,000 | 56 | `59a8c456088a96b2b8696a552edca945d99b121a3c6c5d45a18270b72a38e512` |
| `tep_faultfree_training` | 20,941,351 | 250,000 | 56 | `185db5cbe850d438329b0f39ef73f4ffcd0f9e4afd6fbccbc3c6325980cc66bf` |
| `tep_faultfree_testing` | 39,868,514 | 480,000 | 56 | `20938da894cebbbcb94136a7835ec17af0c376484126a7bc4d876b5f5b0246f1` |
| `tep_faulty_training` | 450,485,967 | 5,000,000 | 56 | `7bab727d6703fed5b9358c11f7f39d074d8888b8af95cabcb8902628dcdd8c01` |
| `iiot` | 13,285,181 | 500,000 | 18 | `3393ca3993175b5d4716eb2163c38bfbab42998ea58bd3116569a9a42b372073` |
| **Total** | **1,283,524,595** | **15,830,000** | | |

The warehouse includes the 9,600,000-row Faulty Testing native (758,943,582 bytes) and the rest of the warehouse (1,283,524,595 bytes). Hamid's Mac holds no caches. Local `data/raw/` and `data/cache/` are scratch, not the durable warehouse.

## TEP (the process layer)

Source: Rieth et al., Harvard Dataverse, [doi:10.7910/DVN/6C3JR1](https://doi.org/10.7910/DVN/6C3JR1).

Wide tables. Native cadence is a 3-minute sample index, not UTC. Ingestion assigns sim-time `1970-01-01T00:00:00Z + i * 180s`. Phase 1 does not interpolate TEP to 1 s.

| Split | Wide rows on R2 | In the warehouse? |
|-------|----------------:|-------------------|
| FaultFree Training | 250,000 | Yes |
| FaultFree Testing | 480,000 | Yes |
| Faulty Training | 5,000,000 | Yes. 20 faults for train. |
| Faulty Testing | 9,600,000 | Yes. Full published test. The Faulty Testing Parquet exists. |

Melt is `n_long = n_samples * n_value_columns`. Clean natives are quality Good. Seed 42 is run metadata, not a column. Polars melts on read from the wide Parquet.

NAB is skipped for Phase 1 exit.

## IIoT (snapshot per machine, not 1 s)

![Analog gauges and a strip-chart recorder](assets/instruments.png)

Source: [Industrial IoT Dataset (Synthetic)](https://www.kaggle.com/datasets/canozensoy/industrial-iot-dataset-synthetic).

The file is **one snapshot per machine**: 500,000 wide rows, 18 warehouse columns. It is not a historian export and it is not a 1-second time series. Earlier notes treated it as a replayable 1 Hz stream. That reading is wrong. This record corrects it.

The L0 contract still says: if an IIoT table has a UTC column, use it; otherwise fall back to `1970-01-01T00:00:00Z + i * 1s`. That fallback is a melt rule for a wide table that lacks time. It is not a claim that this Kaggle file is 1 Hz. Charter §14 N8 still names IIoT as the intended carrier of the fast scan class. The chosen file does not carry that class. The 1 s class is now a seeded generated machine stream (`generate_machine_stream`), ingested as `SourceDataset.IIOT`. Kaggle remains a snapshot. Python extras ride that 1 s host grid. This file does not rewrite N8.

Phase 1 must not mix TEP and IIoT on one stream.

## What the generators do

![Pipe elbow, the L0-to-PLC seam](assets/pipe-turn.png)

Code lives under `src/scada_harmonizer/datagen/`.

- **Generate.** Seeded 1 s rotating-equipment stream (`datagen/generation/`). Native UTC, string `machine_id` as metadata, a handful of fast PVs. Ingested as `iiot`.
- **Ingest.** Wide natives to long `L0Record` rows. TEP natives are float. IIoT natives keep bool/int/float. Identity columns are not melted. When `machine_id` is present, `friendly_name` is `{machine_id}/{pv}` and `source_column` stays the PV. Null/NaN is rejected; gaps are quality codes. Full natives are wide Parquet on R2. Melt is on read.
- **Augment.** Seeded operational-technology (OT) extras (`xv_feed`, `machine_state`, `cycle_count`, `ctrl_mode`, `comm_gap`, `noise_spike`, `stuck_pv`). Same seed, same extras. Natives are copied, then extras append. Quality on extras: Good, plus Bad/gap, Uncertain/spike, Stale/flatline. Lots, work orders, and material IDs stay Phase 5. Full extras are not persisted.
- **Replay.** Identity is `(sim_time_utc_ms, friendly_name, value, quality)`. Speed, pause/resume, and rebase change wall-clock spacing only. Backfill writes historical sim timestamps and is not live. Live pause blocks `emit()` until a cross-thread resume.

Physical meaning waits for the mapping table. `friendly_name` is what the L0 row stores. `source_column` is side metadata.

## Tests (golden-slice only)

`uv run pytest` is 41 passed (34 L0 goldens + Unit 100 P&ID). No `data/raw` or `data/cache` in CI. CI does not read R2.

Coverage matches the contract: L0 schema and frozen records, TEP 180 s deltas, melt row count, golden SHA-256, two-process cache hash, extras schema plus native-pin, IIoT time-column and no-time-column paths, mixed-cadence reject, replay identity, speed/pause/rebase, backfill versus live, naive rebase reject, generated 1 s machine stream (identity metadata, seed pin, extras on the 1 s grid).

## What this does not close

Phase 0 is still open. The mapping-table spine is unwritten. The Diagram 1 walkthrough is a parallel path and does not gate Phase 0 or Phase 1. The cursor is still `design/WALKTHROUGH_PROGRESS.md` §0.2. This record does not move that cursor. Charter §8.1 Phase 0 is unchanged.

Phase 1 exit is replay-only (deterministic sequence plus the N8 clock). The mapping table's `source_cadence` column stays on Phase 0. This record does not rewrite N8.

Phase 2 (PLC tag names, Sparkplug, edge Mosquitto) has not started.

## Pointers

| Path | Role |
|------|------|
| [`PHASE1_L0_CONTRACT.md`](PHASE1_L0_CONTRACT.md) | Authoritative L0 / replay identity |
| [`PHASE1_DATASHEET.md`](PHASE1_DATASHEET.md) | Local vs R2; why each dataset exists |
| [`synthetic_data_generation_notes.md`](synthetic_data_generation_notes.md) | 6-layer plan; persist facts are here and in the datasheet |
| [`LEARNING_LOG.md`](LEARNING_LOG.md) | Durable Phase 1 concepts |
| `tests/fixtures/datagen/` | Golden slice (4 lines) |
| R2 `lagos-chem-l0` | Durable raw + wide Parquet warehouse |
| `data/raw/`, `data/cache/` | Local scratch only. Not the durable warehouse. |
