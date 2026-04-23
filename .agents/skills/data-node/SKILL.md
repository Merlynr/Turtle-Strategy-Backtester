---
name: data-node
description: Build point-in-time snapshots for a run.
---

# data-node

## Single Responsibility

Build point-in-time snapshots for a run.

This node only assembles normalized snapshots from operator-provided manual inputs.

## Forbidden Responsibilities

- creating trading decisions
- updating run-state or ledger state
- generating report narratives

## Inputs

- run context
- `provider=manual`
- `symbol`
- `market`
- `cadence`
- `asof_date`
- `prices.csv`
- operator-supplied indicators
- operator-supplied notes

## Outputs

- normalized point-in-time snapshot
- `{artifact_root}/snapshots/snapshot_{asof_date}.json`
- snapshot metadata
- provider lineage metadata
- validation-ready provenance records

## Notes

The output of this node is consumed by `brain-node`. It must remain a snapshot assembler only.
