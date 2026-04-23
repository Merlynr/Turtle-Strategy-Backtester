# Run Status Schema Contract

## Purpose

`status.json` is the mutable execution record for a run. It tracks where the run is now, what completed last, and what is required to resume safely.

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | string | Stable unique identifier allocated at run creation |
| `phase` | string | High-level execution stage or milestone label for the current run contract |
| `current_node` | string | Node currently active or next to run: `orchestrator`, `data-node`, `brain-node`, `execution-node`, `report-node` |
| `state` | string | Current lifecycle state: `created`, `ready`, `running`, `paused`, `partial`, `completed`, `failed`, `replay-ready` |
| `last_completed_node` | string or null | Most recent node that finished successfully |
| `resume_from` | string or null | Node or checkpoint where the orchestrator should continue |
| `updated_at` | string | ISO 8601 timestamp for the last persisted status change |
| `error_summary` | object or null | Structured error digest for failures or partial states |

## Field Notes

- `run_id` is used to join status with `manifest.json` and all downstream artifacts.
- `phase` is allowed to reflect the active workflow phase or equivalent contract stage, but it must be explicit and machine-readable.
- `current_node` and `resume_from` may differ during a pause. `resume_from` points to the safe continuation point.
- `error_summary` should stay `null` when the run is healthy.

## Example Shape

```json
{
  "run_id": "run-20260423-001_ma-cross-000001sz-qtr",
  "phase": "01-run-contract",
  "current_node": "brain-node",
  "state": "paused",
  "last_completed_node": "data-node",
  "resume_from": "brain-node",
  "updated_at": "2026-04-23T11:30:00+08:00",
  "error_summary": null
}
```

## Persistence Rules

- `status.json` changes over time as the run progresses.
- A paused or partial run remains attached to the same run_id.
- The file must always describe the latest known safe continuation point.
- `error_summary` must be written before a run enters `failed`.
