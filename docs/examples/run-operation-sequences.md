# Run Operation Sequences

## start new run

Inputs:

- `symbol`
- `start`
- `end`
- `cadence`
- `strategy_profile`

Sequence:

1. `backtest-orchestrator` validates the start inputs.
2. The orchestrator generates `run_id`.
3. The orchestrator derives `artifact_root`.
4. The orchestrator creates the fixed run container.
5. The orchestrator writes `manifest.json`.
6. The orchestrator writes `status.json` with `current_node=orchestrator` and `resume_from=data-node`.
7. The orchestrator marks the run `ready`.

Expected outcome:

- a new `run_id` exists
- `artifact_root` exists
- `manifest.json` and `status.json` exist in the run container

## resume paused run

Inputs:

- `run_id`

Sequence:

1. `backtest-orchestrator` looks up the run by `run_id`.
2. The orchestrator resolves `artifact_root`.
3. The orchestrator reads `manifest.json`.
4. The orchestrator reads `status.json`.
5. The orchestrator verifies the requested `run_id` matches both files.
6. The orchestrator reads `resume_from`.
7. The orchestrator resumes the same run from the recorded node boundary.

Expected outcome:

- the same `run_id` is reused
- the same `artifact_root` is reused
- `status.json` advances without changing business identity

## replay existing run

Inputs:

- `run_id`

Sequence:

1. `backtest-orchestrator` looks up the run by `run_id`.
2. The orchestrator resolves `artifact_root`.
3. The orchestrator reads `manifest.json`.
4. The orchestrator reads `status.json`.
5. The orchestrator confirms replay is legal for the current state.
6. The orchestrator reads `report.md` and any other required artifacts.
7. The orchestrator inspects or regenerates derived outputs without changing identity.

Expected outcome:

- the same `run_id` remains authoritative
- `artifact_root` is treated as read-only input for replay
- `report.md` and related artifacts can be inspected or regenerated safely
