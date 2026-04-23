# Report Generation Contract

## Purpose

This contract defines the Phase 5 reporting boundary.

The report node consumes Phase 4 execution artifacts and run identity metadata, then produces a deterministic human-readable `report.md` plus machine-readable report index artifacts.

It does not create new trading decisions, does not mutate execution ledgers, and does not rebuild earlier phase artifacts.

## Report Shape

Every completed report must follow the same five sections:

1. `Summary`
2. `Metrics`
3. `Key Trades`
4. `Artifact Index`
5. `Notes`

The top-level `report.md` is the canonical summary for the run. Additional derived material may live in `reports/`, but the top-level file remains the primary entry point.

## Source of Truth

Reporting may only read from:

- `manifest.json`
- `status.json`
- `execution/nav.json`
- `execution/fills.jsonl`
- `execution/ledger.jsonl`
- `execution/rejections.jsonl` when present
- the fixed run container paths that point to those artifacts

The report contract must not accept new market inputs or regenerate execution outputs.

## Metric Rules

All metrics are derived from the Phase 4 execution outputs:

- `nav.json` is the source for total return, drawdown, Sharpe, and related equity-curve metrics
- `fills.jsonl` and `ledger.jsonl` are the source for key trades and return decomposition

The metric formula choices must be explicit and stable so repeated report generation over the same inputs yields the same results.

## Artifact Linking

The report must include direct evidence-chain links to:

- `manifest.json`
- `status.json`
- `snapshots/`
- `decisions/`
- `execution/`
- `reports/`

The report should not invent a second index system. It should point directly to the run container artifacts that already exist.

## Determinism

Given the same input artifacts, report generation must produce the same Markdown output and the same machine-readable index.

That means:

- no wall-clock timestamps inside the rendered report body
- no hidden randomness
- no implicit reads from earlier phase inputs outside the run container

## Run Completion

Phase 5 completes the run through the `report-node` boundary.

When report generation succeeds:

- the top-level `report.md` exists
- the machine-readable report index exists under `reports/`
- `status.json` advances the run to `completed`

## Failure Handling

Invalid or incomplete report inputs must fail closed.

Examples:

- missing `execution/nav.json`
- malformed fill records
- missing run identity metadata
- partial report artifacts from a previous attempt

On failure, the reporting layer must preserve the existing run identity and leave a clear audit trail.

