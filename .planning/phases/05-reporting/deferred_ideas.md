# Phase 5 Deferred Ideas

This file records integration ideas that are intentionally out of scope for the Phase 5 reporting contract but should remain visible to Phase 6 planning and validation.

## Orchestrator Integration Requirements

The current Phase 5 scope is report generation only. The following orchestrator-related requirements are deferred so they are not lost:

1. `backtest-orchestrator` should be able to route a completed or replay-ready run directly into `report-node` without minting a new `run_id`.
2. A report-only continuation should preserve `artifact_root` and treat all execution artifacts as read-only inputs.
3. `resume` should continue from the last persisted safe node boundary, while `replay` should be able to regenerate derived report outputs from the same run identity.
4. The orchestrator should remain the owner of lifecycle transitions, but it must not write report content itself.
5. Report regeneration must be idempotent: if `report.md` or `reports/*` are rebuilt from the same execution inputs, the derived content should match the previous result.
6. If the report layer detects missing derived outputs, the repair path should prefer regeneration from existing artifacts rather than rerunning earlier phases.
7. Phase 6 should verify that report outputs can be recreated from the execution artifacts without mutating manifest, status, snapshot, decision, or execution identity fields.

## RTK Token Savings / Sequential Loop Notes

These ideas were previously raised and are intentionally deferred from Phase 5 proper:

1. A synchronous, order-driven backtest loop that steps node-by-node for easier debugging and human-in-the-loop pacing.
2. RTK token savings statistics integrated into session or run summaries so future work can measure orchestration overhead.
3. A run-level summary of token savings should not become part of the canonical report unless a later phase explicitly adds observability reporting.

## Phase 6 Reminder

Phase 6 should treat the following as verification targets:

- report generation remains downstream of execution
- report regeneration does not mutate execution-side state
- orchestrator routing still preserves `run_id` and `artifact_root`
- report artifacts remain deterministically reproducible from the same inputs

