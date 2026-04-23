# data-node

## Single Responsibility

Build point-in-time snapshots for a run.

This node only owns `点时点` snapshot assembly from configured data providers.

## Forbidden Responsibilities

- creating trading decisions
- updating run-state or ledger state
- generating report narratives

## Inputs

- run context
- symbol
- market
- cadence
- snapshot timestamp
- provider configuration

## Outputs

- normalized point-in-time snapshot
- snapshot metadata
- provider lineage metadata

## Notes

The output of this node is consumed by `brain-node`.
