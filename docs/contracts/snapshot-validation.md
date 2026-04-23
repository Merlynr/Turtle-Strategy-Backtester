# Snapshot Validation Contract

## Purpose

This contract defines how Phase 2 validates point-in-time snapshots and records the results for audit and replay.

## Point-in-Time Rule

The key validation rule is:

`candle.date <= asof_date`

If any candle in the input window violates this rule, the snapshot must be blocked.

## Validation Outcomes

- `passed`: the snapshot satisfies point-in-time visibility
- `blocked`: the snapshot contains a post-dated candle or another invalid condition

Blocked snapshots must not be handed to `brain-node`.

## Validation Record

Validation results must be written to:

`{artifact_root}/meta/validation.json`

The record must include:

- `run_id`
- `asof_date`
- `provider`
- `input_hash`
- `validation_status`
- `violations`
- `validated_at`

## Manual Input Provenance

Raw operator-provided inputs and notes must be retained under:

`{artifact_root}/meta/manual-inputs/`

This subtree is the audit trail for the original human input used to produce a normalized snapshot.

## Cache Reuse

Snapshot reuse is allowed only when all of the following match:

- the raw input payload
- the versioned parameters
- the `asof_date`
- the `symbol`
- the `market`
- the `cadence`

If any of these change, the snapshot must be rebuilt rather than reused.

## Blocking Conditions

Block the snapshot when:

- any `candle.date > asof_date`
- the raw price series is missing required columns
- the operator input cannot be normalized into the required snapshot shape
- the validation record cannot be written to `meta/validation.json`
