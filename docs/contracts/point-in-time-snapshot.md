# Point-in-Time Snapshot Contract

## Purpose

This contract defines the manual snapshot input path for Phase 2. It lets an operator provide prices, indicators, and notes directly, then freezes that input into a normalized snapshot that `brain-node` can consume later.

## v1 Input Mode

v1 supports `provider=manual` as the primary path.

Required inputs:

- `provider=manual`
- `symbol`
- `market`
- `cadence`
- `asof_date`
- `prices.csv`
- operator-supplied `indicators`
- operator-supplied `notes`

## Canonical Files

### Raw price path

`prices.csv` is the operator-provided raw price series. It must be stored under:

`{artifact_root}/snapshots/prices.csv`

Required columns:

- `date`
- `open`
- `high`
- `low`
- `close`
- `volume`

### Normalized snapshot

Each snapshot is written as:

`{artifact_root}/snapshots/snapshot_{asof_date}.json`

Where `asof_date` uses `YYYY-MM-DD`.

## Normalized Snapshot Shape

The normalized snapshot must include:

- `provider`: always `manual` in Phase 2
- `symbol`
- `market`
- `cadence`
- `asof_date`
- `window_start`
- `window_end`
- `prices_csv_path`
- `indicator_payload`
- `notes`
- `built_at`
- `validation_status`

The exact internal layout of `indicator_payload` is implementation-defined, but it must preserve the operator-provided indicator values and their parameter notes.

## Consumption Boundary

`brain-node` consumes the normalized snapshot, not the raw CSV. The raw CSV remains available for audit and replay, but it is not the direct input to downstream decision making.

## Layout Rule

Every snapshot file produced by Phase 2 must live inside the fixed run container:

`{artifact_root}/snapshots/`

No alternate snapshot path is allowed.
