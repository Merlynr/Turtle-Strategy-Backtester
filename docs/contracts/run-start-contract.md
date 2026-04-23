# Run Start Contract

## Purpose

This contract defines how `backtest-orchestrator` starts a new run and materializes the first on-disk artifacts for that run.

## Required Start Inputs

- `symbol`
- `start`
- `end`
- `cadence`
- `strategy_profile`

## Ordered Workflow

1. Validate the incoming start request fields.
2. Generate a unique `run_id`.
3. Derive `artifact_root` from the run identity and short business summary.
4. Create the fixed run container at `artifact_root`.
5. Write `manifest.json` with the stable business identity and `entry_skill=backtest-orchestrator`.
6. Write initial `status.json` with the lifecycle state needed for orchestration.
7. Transition the run from `created` to `ready`.
8. Hand off the ready run to the next node boundary.

## Initial File Writes

### `manifest.json`

The orchestrator writes:

- `run_id`
- `strategy`
- `symbol`
- `market`
- `start`
- `end`
- `cadence`
- `entry_skill`
- `created_at`
- `artifact_root`

### `status.json`

The orchestrator writes:

- `run_id`
- `phase=01-run-contract`
- `current_node=orchestrator`
- `state=ready`
- `last_completed_node=null`
- `resume_from=data-node`
- `updated_at`
- `error_summary=null`

## Start Invariants

- The first persisted files are `manifest.json` and `status.json`.
- The generated `artifact_root` must match the run container layout contract.
- `resume_from=data-node` is the first safe continuation point once the run is ready.
- Starting a run creates a new identity; it must not overwrite an existing run with the same `run_id`.
