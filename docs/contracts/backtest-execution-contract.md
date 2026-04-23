# Backtest Execution Contract

## Purpose

This contract defines the execution-node boundary for Phase 4.

The execution node consumes two upstream inputs only:

- the Phase 3 AI decision record
- the Phase 2 normalized snapshot and price series

Its job is to turn those inputs into deterministic fills, ledger rows, and NAV rows.
It does not generate strategy reasoning, rebuild snapshots, or write narrative reports.

## Execution Assumptions

Phase 4 uses explicit run-scoped assumptions that must be persisted with the run:

- `initial_capital`
- `commission_rate`
- `slippage_bps`
- `position_limit`
- `lot_size`

The execution layer treats these values as configuration, not hidden defaults.
They must be written to `meta/execution-config.json` so replay can reuse the same assumptions.

## Accepted Decision Boundary

The execution boundary accepts only validated Phase 3 decision records.

The persisted AI decision record must already satisfy the AI schema contract:

- `action` is one of `buy`, `sell`, or `hold`
- invalid JSON is blocked upstream
- schema failures are blocked upstream

The execution layer normalizes the accepted actions into internal long-direction semantics:

- `buy` maps to `add`
- `sell` maps to `reduce`
- `hold` remains `hold`

`reduce` and `add` are execution-layer aliases only.
They are not required to appear in the AI output boundary.

## Timing Rule

Execution always happens on the first available trading-day open strictly after `asof_date`.

If the price series does not contain a later trading-day open, the order cannot be fabricated.
The engine must return a blocked execution record with a clear reason.

## Quantity Rule

The engine uses A-share 100-share lots.

For long entry:

- deploy as much cash as allowed by available cash
- respect lot-size rounding
- respect the configured position limit

For long exit:

- release as much sellable exposure as allowed by current holdings
- respect lot-size rounding

If the computed quantity is zero, the engine must block the order and record why.

## Cost Rule

Commission and slippage both affect cash and NAV.

The engine must not treat costs as a post-hoc note.
Costs must be applied when computing:

- fill cash delta
- average cost basis
- realized PnL
- unrealized PnL
- NAV

## Fail Closed Rule

Invalid, missing, or constraint-breaching orders fail closed.

Examples:

- missing next open
- missing or malformed snapshot price series
- zero buyable lot
- zero sellable lot
- position-limit breach
- invalid decision record

Blocked decisions are retained in the run container for audit.
They are not rewritten into a different trade.

## Output Artifacts

The execution node writes only machine-readable artifacts under the run container:

- `meta/execution-config.json`
- `execution/ledger.jsonl`
- `execution/fills.jsonl`
- `execution/nav.json`
- `execution/rejections.jsonl`
- `status.json`

The execution node does not create report prose.
It only advances the run to the safe continuation point for the next node.

## Status Handoff

When execution completes, the run remains attached to the same `run_id` and `artifact_root`.

The execution boundary updates the mutable run state so the next node can continue safely.
For v1 this handoff is:

- `current_node = report-node`
- `state = partial`
- `last_completed_node = execution-node`
- `resume_from = report-node`

This keeps the execution boundary separate from report generation.

