# Replay And Resume Contract

## Purpose

This contract separates `resume` from `replay` so later phases do not accidentally overwrite an old run when they only mean to inspect it.

## Resume

`resume` means continuing an incomplete run.

Resume rules:

- Resume always uses the same run_id.
- Resume always reuses the existing artifact_root.
- Resume reads `status.json.resume_from` to determine the safe continuation point.
- Resume may mutate `status.json` and downstream artifacts that belong to the same run.
- Resume must not change business identity fields in `manifest.json`.

### Resume Preconditions

- `manifest.json` exists and its `run_id` matches `status.json.run_id`
- `status.json` exists
- `status.json.state` is `paused`, `partial`, or an operator-approved recovery from `failed`
- `status.json.resume_from` is present
- Fixed artifact directories exist: `snapshots/`, `decisions/`, `execution/`, `reports/`, and `meta/`

## Replay

`replay` means re-reading an existing run for inspection, comparison, audit, or report regeneration without changing its business identity.

Replay rules:

- Replay may target a `completed`, `paused`, or `replay-ready` run.
- Replay reads artifacts from the existing artifact_root.
- Replay does not mint a new run_id.
- Replay does not mutate business identity fields in `manifest.json`.
- Replay should prefer read-only regeneration of derived outputs when possible.

### Replay Preconditions

- `manifest.json` exists
- `status.json` exists
- `run_id` is internally consistent across required top-level files
- Required artifact directories exist: `snapshots/`, `decisions/`, `execution/`, `reports/`, and `meta/`
- The caller declares whether replay is inspection-only or report regeneration

## Error Checklist

Block the operation when any of these conditions are true:

- Missing `manifest.json`
- Missing `status.json`
- Mismatched `run_id` between `manifest.json` and `status.json`
- Missing required artifact directories
- Missing `resume_from` during `resume`
- Attempting `resume` from `completed` without an explicit repair path
- Attempting `replay` against a directory that is not the recorded artifact_root

## Decision Table

| Operation | Mutates current run | Requires same run_id | Reads resume_from | Primary use |
|-----------|----------------------|----------------------|-------------------|-------------|
| `resume` | Yes | Yes | Yes | Continue incomplete execution |
| `replay` | No | Yes | No | Inspect, compare, or regenerate derived outputs |
