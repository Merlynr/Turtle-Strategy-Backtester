---
name: execution-node
description: Apply decisions to the current run-state and ledger model.
---

# execution-node

## Single Responsibility

Apply decisions to the current run-state and ledger model.

This node owns `run-state` transition and execution artifact mutation only.

## Forbidden Responsibilities

- generating strategy reasoning
- rebuilding historical snapshots
- producing final narrative reports

## Inputs

- run context
- current 状态 snapshot from status layer
- validated decision object
- execution assumptions

## Outputs

- updated run-state
- execution artifacts
- ledger and position artifacts

## Notes

`execution-node` is the only node allowed to mutate execution-side state.
