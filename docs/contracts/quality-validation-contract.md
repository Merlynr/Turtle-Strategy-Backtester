# Quality Validation Contract

## Purpose

This contract defines the Phase 6 quality entry for the Turtle Strategy backtester.

`validate` inspects an existing run container and produces a single pass/blocked quality result. It does not mint a new `run_id`, it does not repair the run, and it does not mutate manifest or execution-side artifacts.

## Scope

Phase 6 validation checks the outputs from Phases 1 through 5:

- run identity and artifact-root consistency
- required top-level run layout
- report presence and report determinism
- execution artifact presence and consistency
- deterministic replay expectations

The validation boundary reads the existing run container only. It may compare current outputs against a checked-in golden baseline when configured to do so.

## Inputs

The validation entry expects:

- `run_id`
- `symbol`
- `market`
- `cadence`
- `artifact_root`
- the current manifest and status records
- a `ValidationConfig`

## Validation Config

The config keeps the validation scope explicit:

- whether to compare against a golden baseline
- where that golden baseline lives
- which status values are considered valid for a completed run
- which timestamps are runtime metadata and may change between validations
- which report assumptions should be used when regenerating the report for comparison

## Output

Validation results are written to:

`{artifact_root}/meta/validation.json`

The record includes:

- the run identity
- the artifact root
- the validation status
- the checked artifacts
- the findings
- the validation summary
- the validation timestamp

## Pass / Blocked Rules

- `passed`: the run container is internally consistent and the regenerated report matches the stored report outputs
- `blocked`: one or more required artifacts are missing, inconsistent, or non-deterministic

Blocked runs must not be repaired automatically. They are evidence, not input for silent correction.

## Determinism

The same run inputs should produce the same validation summary and findings.

The only allowed variation across repeated validations is explicit runtime metadata such as `validated_at`.

## Evidence Chain

Validation must directly reference the run container and its core artifacts:

- `manifest.json`
- `status.json`
- `report.md`
- `snapshots/`
- `decisions/`
- `execution/`
- `reports/`
- `meta/validation.json`

## Boundary Rules

- Validation may inspect artifacts, but it must not rewrite manifest or execution-side records.
- Validation may write `meta/validation.json`, but it must not create a second business identity.
- Validation must fail closed when the run container is incomplete or mismatched.

