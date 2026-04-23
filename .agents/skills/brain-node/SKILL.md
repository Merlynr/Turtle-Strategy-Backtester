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
- schema contract

## Outputs

- validated JSON decision object
- decision validation result
- decision generation metadata

## Notes

`brain-node` must return schema-safe JSON, not free-form execution text.
