# Run Lifecycle Contract

## Run Definition

A `run` is one complete backtest instance. It begins when the orchestrator accepts a backtest request and ends when the run reaches `completed`, `failed`, or an intentionally persisted `paused` or `partial` state.

The run boundary is business-facing rather than node-facing:

- One backtest request maps to one run.
- A paused run is still the same run.
- A resumed run continues with the same run_id.
- A partial run is still the same run and records which node stopped last.

## Minimum States

| State | Meaning | Entered When | Exit Condition |
|-------|---------|--------------|----------------|
| `created` | Identity exists but execution has not started | The orchestrator allocates `run_id` and artifact root | Required inputs and metadata are persisted |
| `ready` | Run can start or resume safely | Manifest and initial status files are valid | The orchestrator dispatches the next node |
| `running` | A node is actively doing work for this run | A node starts processing | The node completes, pauses, or fails |
| `paused` | Execution stopped intentionally and may continue later | The orchestrator or a node stops after persisting state | Resume is requested with the same run_id |
| `partial` | Some outputs exist but the full flow is incomplete | A node finishes partially or stops before the next node begins | Resume or replay preparation clarifies next action |
| `completed` | The full backtest flow has finished | Reporting finishes and final artifacts are written | Terminal state |
| `failed` | The run cannot continue without intervention | A node or orchestrator records an unrecoverable error | Terminal until explicitly repaired |
| `replay-ready` | The run is not executing and all replay prerequisites exist | Required top-level artifacts are present and internally consistent | A replay or review operation consumes the artifacts |

## State Transition Rules

Canonical path:

`created -> ready -> running -> completed`

Allowed non-terminal transitions:

- `running -> paused`
- `running -> partial`
- `paused -> ready`
- `partial -> ready`
- `completed -> replay-ready`
- `failed -> ready` only after an explicit repair or operator override updates status safely

Forbidden transitions:

- `paused -> created`
- `partial -> created`
- `completed -> running`
- `replay-ready -> created`

## Resume Semantics

Resume never creates a second identity for the same business run.

- Resume must keep the same run_id.
- Resume must continue from the last persisted node boundary.
- Resume may update mutable execution fields in `status.json`.
- Resume must not rewrite business identity fields recorded at creation time.

## Lifecycle Ownership

- `backtest-orchestrator` creates the run and owns state transitions between nodes.
- Node skills may request `paused`, `partial`, or `failed`, but they do not mint new run identities.
- `status.json` is the canonical persisted execution state for the current lifecycle position.
