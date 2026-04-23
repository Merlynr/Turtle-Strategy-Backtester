# Run Lookup Contract

## Purpose

This contract defines lookup by run_id so the orchestrator can resolve an existing run before deciding whether `resume` or `replay` is legal.

## Lookup By Run_ID

Ordered lookup algorithm:

1. Accept `run_id` as the lookup key.
2. Resolve `artifact_root` from the run index or the recorded run directory naming convention.
3. Load `manifest.json` from the resolved `artifact_root`.
4. Load `status.json` from the resolved `artifact_root`.
5. Verify that `manifest.json.run_id` and `status.json.run_id` both match the requested `run_id`.
6. Inspect `status.json.state`.
7. Return the resolved run context plus the allowed operation set for that state.

## Required Reads

- `artifact_root`
- `manifest.json`
- `status.json`

## Allowed Operation Selection

| State | Allowed Operation | Notes |
|-------|-------------------|-------|
| `ready` | `resume` | Continue the same run from the recorded boundary |
| `paused` | `resume`, `replay` | `resume` requires `resume_from`; `replay` stays read-only |
| `partial` | `resume`, `replay` | `resume` requires `resume_from`; `replay` may inspect partial artifacts |
| `completed` | `replay` | Resume is blocked unless an explicit repair path exists |
| `replay-ready` | `replay` | Preferred read-only review state |
| `failed` | `resume` only under an explicit repair policy, otherwise blocked | Requires operator-approved recovery |

## Blocking Conditions

- `artifact_root` cannot be resolved
- `manifest.json` is missing
- `status.json` is missing
- requested `run_id` does not match both files
- the resolved directory is not the recorded `artifact_root`
