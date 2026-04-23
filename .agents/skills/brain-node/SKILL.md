---
name: brain-node
description: Convert snapshots into schema-validated JSON decisions.
---

# brain-node

## Single Responsibility

Convert snapshots into schema-validated JSON decisions.

This node owns decision generation only.

## Forbidden Responsibilities

- fetching raw provider data directly
- mutating run-state
- writing final report artifacts

## Inputs

- run context
- normalized snapshot payload
- prompt profile
- schema contract for the decision-output JSON
- decision-record contract used by the orchestrator for audit persistence

## Outputs

- schema-validated JSON decision object
- decision validation result
- decision-record metadata needed to persist the audit record separately

## Notes

`brain-node` must return schema-safe JSON, not free-form execution text.
If validation fails, the output stays blocked and the rejected payload is preserved only as audit data in the decision record.
