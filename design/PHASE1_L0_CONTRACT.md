# Phase 1 L0 contract

L0 is the long-form measurement record Phase 1 stores. This file is authoritative for ingestion, augmentation, and replay. Charter §8.1 Phase 1 exit is replay-only. Mapping-table `source_cadence` stays on Phase 0. It is not an L0 field.

## L0 record

One row per measurement (long form). Fields:

- `ts_utc`: UTC datetime
- `friendly_name`: string; the stored L0 name
- `source_column`: string; dataset-native column; side metadata
- `source_dataset`: `tep` or `iiot`
- `value`: float, int, or bool
- `quality`: Good, Uncertain, Bad, or Stale (charter §14 N10). Always present. Clean benchmark rows are Good.
- `quality_reason`: string or null

Seed is run metadata, not a per-row field. Default seed is 42. Physical meaning waits for the mapping table. Lots, work-order, and material IDs stay Phase 5.

## Time

Tennessee Eastman Process (TEP) is a 3-minute sample index, not UTC. Sim-time is the simulated clock, not wall-clock. Pre-rebase sim-time for sample `i` is `1970-01-01T00:00:00Z + i * 180s`. Industrial Internet of Things (IIoT) uses native UTC timestamps when present; otherwise `1970-01-01T00:00:00Z + i * 1s`. The ~1 s fast class is a seeded generated machine stream ingested as `iiot` (native UTC). The Kaggle IIoT file remains a snapshot and is not a 1 Hz historian. N8 rebase adds a single offset at replay start so the first event meets wall-clock-now. Cadence tests use sim-time deltas (TEP 180s; machine stream 1s). Do not interpolate TEP to 1s.

## Melt

Melt means wide table to long rows. TEP arrives wide. Ingestion melts to long L0 rows: one output row per (sample, column). `n_long = n_samples * n_value_columns`. Identity columns (`machine_id` / `Machine_ID`, `machine_type`, TEP `faultNumber` / `simulationRun`) are stream metadata, not L0 PVs. When `machine_id` is present, `friendly_name` is `{machine_id}/{pv}` and `source_column` stays the PV.

## Serialization and fixtures

Canonical form is JSONL, one object per line, keys in the field order above, `ts_utc` as ISO-8601 with `Z`. Cache hash is SHA-256 of that UTF-8 file. The golden-slice JSONL remains the CI pin. Full natives are wide Parquet on R2 `lagos-chem-l0` (melt on read). The golden slice is a tiny committed JSONL under `tests/fixtures/datagen/` (hand-authored or trimmed). CI hashes canonical records, not raw downloads. No network in CI.

## Replay identity

The sequence is the ordered list of `(sim_time_utc_ms, friendly_name, value, quality)`. Same cache + seed + clock settings must reproduce that list. Speed factor and pause/resume change wall-clock spacing only. Rebase changes the wall-clock mapping, not order or sim-time deltas. Backfill writes historical sim timestamps and is not live. Phase 1 has no Sparkplug payload; the clock type is this record plus `sim_time_utc_ms`.

Do not mix TEP and IIoT on one stream.

## Tests (blocking)

- L0 schema: required fields present; quality always present
- TEP cadence: consecutive same-name sim deltas are 180s
- Melt: wide shape maps to long row count
- Golden-slice SHA-256 is stable
- Two-process: same raw + seed → same cache hash
- Augmentation: extras have a declared schema; same seed → same extras; TEP native columns are unchanged (hash of that subset is identical)
- Mixed cadence: combining TEP and IIoT on one stream fails
- Replay: same seed → identical identity list
- Speed factor, pause/resume, and rebase do not change the identity list or sim-time deltas
- Backfill vs live: same identity list; backfill is not live
- Machine stream: generate → ingest as `iiot` → cache → augment → replay; two machines at the same tick have distinct `{machine_id}/{pv}` names; raw same-name deltas are 1s; machine identity is not an L0 PV; same seed → identical frame and extras; mixed TEP+stream raises MixedCadenceError; machine-stream golden SHA-256 is stable. Kaggle snapshot and TEP 180s tests stay green.

## Sources

- TEP: doi:10.7910/DVN/6C3JR1
- IIoT: https://www.kaggle.com/datasets/canozensoy/industrial-iot-dataset-synthetic
- Numenta Anomaly Benchmark (NAB): skip for Phase 1 exit
