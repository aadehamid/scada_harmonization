# Phase 1 synthetic data record

**Status:** generators on `main` (2026-08-18). Full L0 cache written, then deleted.  
**Contract:** [`PHASE1_L0_CONTRACT.md`](PHASE1_L0_CONTRACT.md).  
**Reading copy:** [`PHASE1_SYNTHETIC_DATA.html`](PHASE1_SYNTHETIC_DATA.html).

![Lagos Specialty Chemicals plant, dawn](assets/hero-plant.png)

This file is the durable record of what Phase 1 actually did. It is not the L0 contract and it is not a dump of the session log. The contract still governs the record shape. This note records the land, the disk facts, and the persist rules Hamid set.

Phase 1 is replay-only. It does not assign physical meaning. It does not write Sparkplug. It does not open the mapping table.

## What landed

Two PRs closed the code path on 18 August 2026, Central Time.

| PR | Merge | SHA | What it is |
|----|-------|-----|------------|
| [#28](https://github.com/aadehamid/scada_harmonization/pull/28) | 12:34 AM CT | `8564fed` | pandas as the first runtime dependency, empty Phase 1 package inits, ty in the dev group and CI |
| [#29](https://github.com/aadehamid/scada_harmonization/pull/29) | 12:56 AM CT | `3039710` | L0 record, ingestion, OT extras, deterministic replay, golden fixtures, 21 tests |

The merge commit for #29 is `3039710`. The last commit on that branch is `8b83fa6`.

Runtime dependencies on `main` are now pandas and pydantic. Pydantic validates the L0 boundary. Pandas melts wide TEP (and IIoT tables that look wide) into long L0 rows.

CI stays golden-slice only. No full-dataset CI. No network in CI.

## Persist rules (Hamid)

Hamid owns keep versus delete. Agents do not invent a retention policy.

1. **Keep raw.** Benchmark downloads stay in `data/raw/` (gitignored). Measured size after Phase 1: **1.35 GiB**.
2. **Cache is regenerable.** A full L0 JSONL in `data/cache/` is a derived product of raw plus seed. It is safe to delete. Hamid deleted the one that was written.
3. **Do not persist Full Faulty Testing as L0.** That split was never written. At 200 B/rec it would have been about **96 GiB**.
4. **Commit the golden slice, not the plant.** `tests/fixtures/datagen/golden_l0_slice.jsonl` is the identity pin. `data/**` payloads stay gitignored.

Those four rules are why a 54.63 GiB file existed for one day and then did not.

## Disk facts (18 August 2026)

| Artifact | Fate | Size / count |
|----------|------|----------------|
| L0 cache JSONL | Written, then deleted the same day | **330,920,000** rows, **54.63 GiB** |
| Full Faulty Testing L0 | Never written | ~96 GiB at 200 B/rec |
| Raw downloads | Kept | **1.35 GiB** |
| Golden slice | Committed | 4 rows, 700 bytes |

SHA-256 of the committed golden file:

```
f5b9d1cfdaf9f298d9cdcbcb926bc3486dfdac1cccff7816b34ac290e6d33516
```

Pinned as `GOLDEN_SHA256` in `tests/datagen/factories.py`. The hash is of canonical UTF-8 JSONL, not of a raw download.

## TEP (the process layer)

Source: Rieth et al., Harvard Dataverse, [doi:10.7910/DVN/6C3JR1](https://doi.org/10.7910/DVN/6C3JR1).

Wide tables. Three metadata columns (`faultNumber`, `simulationRun`, `sample`) plus 52 process variables. Native cadence is a 3-minute sample index, not UTC. Ingestion assigns sim-time `1970-01-01T00:00:00Z + i * 180s`. Phase 1 does not interpolate TEP to 1 s.

| Split | Wide shape (published) | L0 written? |
|-------|------------------------|-------------|
| FaultFree Training | 500 runs × 500 samples = 250,000 | Part of the 330,920,000-row cache |
| FaultFree Testing | 500 runs × 960 samples = 480,000 | Part of the 330,920,000-row cache |
| Faulty Training | 20 faults × 500 runs × 500 samples = 10,000,000 | Part of the 330,920,000-row cache |
| Faulty Testing | 20 faults × 500 runs × 960 samples = 19,200,000 | **No.** Hamid skipped it. |

Melt is `n_long = n_samples * n_value_columns`. Clean natives are quality Good. Seed 42 is run metadata, not a column.

NAB is skipped for Phase 1 exit.

## IIoT (snapshot per machine, not 1 s)

![Analog gauges and a strip-chart recorder](assets/instruments.png)

Source: [Industrial IoT Dataset (Synthetic)](https://www.kaggle.com/datasets/canozensoy/industrial-iot-dataset-synthetic) (`factory_sensor_simulator_2040.csv`).

The file is **one snapshot per machine**: about 500,000 rows, 22 columns. It is not a historian export and it is not a 1-second time series. Earlier notes treated it as a replayable 1 Hz stream. That reading is wrong. This record corrects it.

The L0 contract still says: if an IIoT table has a UTC column, use it; otherwise fall back to `1970-01-01T00:00:00Z + i * 1s`. That fallback is a melt rule for a wide table that lacks time. It is not a claim that this Kaggle file is 1 Hz. Charter §14 N8 still names IIoT as the intended carrier of the fast scan class. The chosen file does not carry that class. Python extras and a later machine stream have to do that work. This file does not rewrite N8.

Phase 1 must not mix TEP and IIoT on one stream.

## What the generators do

![Pipe elbow, the L0-to-PLC seam](assets/pipe-turn.png)

Code lives under `src/scada_harmonizer/datagen/`.

- **Ingest.** Wide CSV to long `L0Record` rows. TEP natives are float. IIoT natives keep bool/int/float. Null/NaN is rejected; gaps are quality codes.
- **Augment.** Seeded OT extras (`xv_feed`, `machine_state`, `cycle_count`, `ctrl_mode`, `comm_gap`, `noise_spike`, `stuck_pv`). Same seed, same extras. Natives are copied, then extras append. Quality on extras: Good, plus Bad/gap, Uncertain/spike, Stale/flatline. Lots, work orders, and material IDs stay Phase 5.
- **Replay.** Identity is `(sim_time_utc_ms, friendly_name, value, quality)`. Speed, pause/resume, and rebase change wall-clock spacing only. Backfill writes historical sim timestamps and is not live. Live pause blocks `emit()` until a cross-thread resume.

Physical meaning waits for the mapping table. `friendly_name` is what the cache stores. `source_column` is side metadata.

## Tests (21, all golden-slice)

`uv run pytest` is 21 passed. No `data/raw` or `data/cache` in CI.

Coverage matches the contract: L0 schema and frozen records, TEP 180 s deltas, melt row count, golden SHA-256, two-process cache hash, extras schema plus native-pin, IIoT time-column and no-time-column paths, mixed-cadence reject, replay identity, speed/pause/rebase, backfill versus live, naive rebase reject.

## What this does not close

Phase 0 is still open. The mapping-table spine is still gated on the Diagram 1 walkthrough (`design/WALKTHROUGH_PROGRESS.md`). Charter §8.1 Phase 0 is unchanged.

Phase 1 exit is replay-only (deterministic sequence plus the N8 clock). The mapping table's `source_cadence` column stays on Phase 0. This record does not rewrite N8.

Phase 2 (PLC disguise, Sparkplug, edge Mosquitto) has not started.

## Pointers

| Path | Role |
|------|------|
| [`PHASE1_L0_CONTRACT.md`](PHASE1_L0_CONTRACT.md) | Authoritative L0 / replay identity |
| [`synthetic_data_generation_notes.md`](synthetic_data_generation_notes.md) | 6-layer plan; IIoT banner corrected here |
| [`LEARNING_LOG.md`](LEARNING_LOG.md) | Durable Phase 1 concepts |
| `tests/fixtures/datagen/` | Golden slice |
| `data/raw/`, `data/cache/` | Gitignored payloads; READMEs track Hamid's persist rules |
