# AI-driven Quantitative Backtest System

## What This Is

This is a skill-first quantitative backtesting system for a single-symbol v1 loop. The system is designed around point-in-time snapshots, schema-locked AI decisions, deterministic execution, and auditable local artifacts.

The primary workflow is:

1. collect the data that was visible at a specific `asof_date`
2. normalize it into a snapshot
3. ask the AI node for a structured buy/sell/hold decision
4. simulate the result locally
5. write every artifact to disk for replay and review

## Core Value

At any historical timestamp, the system should be able to produce verifiable AI decisions and backtest results from contemporaneous inputs only.

## Validated

- Phase 1 validated `backtest-orchestrator` as the canonical entry for starting, resuming, and replaying runs.
- Phase 1 validated the run contract around `run_id`, `artifact_root`, `manifest.json`, `status.json`, and the fixed run container.
- Phase 2 validated the manual point-in-time snapshot model for v1.
- Phase 2 validated that snapshots are normalized from manual operator input and blocked if they violate point-in-time rules.
- Phase 2 validated the fixed metadata subtree for raw manual inputs and validation records.
- Phase 3 validated the AI decision protocol, versioned prompt contract, and schema-locked JSON decision boundary.
- Phase 3 validated fail-closed decision handling and auditable decision records under `decisions/`.
- Phase 4 validated deterministic next-open execution, lot-aware sizing, explicit run-scoped costs, and auditable execution artifacts.
- Phase 5 validated deterministic report generation, artifact indexing, and terminal run completion from execution outputs.
- Phase 6 validated the quality entry, run-container consistency checks, golden-run regression coverage, and `meta/validation.json` persistence.

## Active

- Prepare milestone audit and cleanup now that Phase 6 has validated the full v1 loop.
- Keep validated execution, reporting, and validation artifacts intact for audit and replay.
- Preserve strict separation between report generation, validation, and any future wrappers.

## Out of Scope for v1

- Live trading integration
- Minute-level or tick-level backtesting
- Web UI
- Multi-symbol portfolio optimization

## Context

- Phase 1 established a single top-level orchestrator skill with four node boundaries: data, brain, execution, and report.
- Phase 1 also established the `start / resume / replay` lifecycle and the fixed run container.
- Phase 2 made manual point-in-time snapshots the primary v1 input path, which means the project does not require external data-source credentials to begin with.
- The intended user flow is a researcher manually supplying stock information, indicators, and candles, then receiving a structured buy/sell decision that is stored locally and reused for backtesting.
- Phase 4 added deterministic next-open simulation, lot-aware sizing, and run-scoped execution persistence.
- Phase 5 added deterministic report synthesis, direct artifact links, and run completion handoff.

## Current State

v1.0 has shipped and been archived. The system now has a complete skill-first backtest loop, a dedicated validation entry, and a milestone audit record.

### Shipped Scope

- canonical `backtest-orchestrator` entry
- manual point-in-time snapshot flow
- schema-locked AI decision protocol
- deterministic next-open execution core
- traceable report synthesis
- dedicated validation entry with golden-run regression

### Next Milestone Goals

- expand toward orchestration and analysis improvements without breaking the existing run contract
- preserve strict separation between snapshot assembly, AI decisioning, execution, reporting, and validation
- keep the v1 artifacts stable as the historical baseline

## Constraints

- v1 focuses on single-symbol A-share daily candles and quarter/month rebalance cadence.
- `backtest-orchestrator` remains the single canonical entry point.
- The AI node may only emit structured JSON.
- Each run must retain inputs, outputs, and metadata for auditability and replay.
- The system should stay data-source agnostic so manual input can work without Tushare or Gemini credentials.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use a skill-first orchestrator architecture | Keeps the workflow aligned with GSD and leaves room for wrappers later | Accepted |
| Treat point-in-time snapshot assembly as a first-class node | This is the core anti-lookahead boundary | Accepted |
| Require schema-validated AI JSON decisions | Reduces prompt drift and makes execution deterministic | Accepted |
| Store run artifacts in a fixed local layout | Preserves replayability and auditability | Accepted |
| Start with a single-symbol closed loop | Validates the core value before widening scope | Accepted |
| Use explicit execution costs and lot-aware sizing for Phase 4 | Keeps the simulation deterministic and replayable | Accepted |
| Derive reports only from execution artifacts for Phase 5 | Keeps reporting reproducible and auditable | Accepted |
| Add a dedicated validation entry with golden-run regression for Phase 6 | Ensures completed runs are checkable, replayable, and regression-safe | Accepted |

## Archived Milestone

- [v1.0 milestone audit](.planning/v1.0-MILESTONE-AUDIT.md)
- [v1.0 milestone roadmap archive](.planning/milestones/v1.0-ROADMAP.md)
- [v1.0 milestone requirements archive](.planning/milestones/v1.0-REQUIREMENTS.md)

## Evolution

This document evolves at phase transitions and milestone boundaries.

After each phase transition:

1. move validated requirements to the Validated section
2. move obsolete requirements to Out of Scope
3. add new requirements to Active
4. record new architectural decisions
5. confirm the Core Value still matches the project goal

---
*Last updated: 2026-04-23 after v1.0 archive*
