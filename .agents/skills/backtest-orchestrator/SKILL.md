---
name: backtest-orchestrator
description: The single entry skill for a backtest run. A pure orchestrator for the Turtle Strategy Backtester.
---
# backtest-orchestrator

## Role

`backtest-orchestrator` is the single entry skill for a backtest run.

It is a `纯调度器`:

- receives a backtest request
- creates or resolves a `run`
- dispatches work to `data-node`
- dispatches work to `brain-node`
- dispatches work to `execution-node`
- dispatches work to `report-node`
- aggregates run status and final outputs

It never performs strategy analysis, market data interpretation, execution math, or report writing by itself.

## Responsibility

- normalize entry arguments for a run
- allocate or resolve `run_id`
- derive `artifact_root`
- select next node based on lifecycle state
- persist orchestration progress into run metadata
- stop, resume, or replay the same run using the same identity

## Forbidden Responsibilities

- generating trading decisions directly
- assembling point-in-time market snapshots
- mutating ledger state
- writing final investment reports as a node substitute

## Inputs

- strategy_profile
- symbol
- market
- start
- end
- cadence
- optional `run_id`
- optional execution stop point

## Outputs

- resolved run context
- resolved `artifact_root`
- node dispatch order
- updated orchestration state
- final run completion status

## Run Start Workflow

When the operation is `start`, the orchestrator follows this order:

1. validate `symbol`, `start`, `end`, `cadence`, and `strategy_profile`
2. generate a unique `run_id`
3. derive `artifact_root` from the run identity
4. create the fixed run container
5. write initial `manifest.json`
6. write initial `status.json`
7. transition the run from `created` to `ready`
8. dispatch the ready run to `data-node`

## Dispatch Contract

Default node order:

1. `data-node`
2. `brain-node`
3. `execution-node`
4. `report-node`

The orchestrator may pause after any node, but it must preserve the same `run_id` and continue the same run on resume.

## Operation Sequences

See `docs/examples/run-operation-sequences.md` for the canonical `start new run`, `resume paused run`, and `replay existing run` sequences.
