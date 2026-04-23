# Skill Entry Examples

This project treats `backtest-orchestrator` as the canonical entry. Any future CLI wrapper is only a delegate to the same orchestrator contract.

## start

Intent: start a new run through `backtest-orchestrator`.

```text
entry_skill: backtest-orchestrator
operation: start
symbol: 000001.SZ
start: 2020-01-01
end: 2023-12-31
cadence: quarterly
strategy_profile: ma-cross-v1
```

Expected behavior:

- validate the request fields
- create a new `run_id`
- allocate the run container
- dispatch the run through the orchestrator workflow

## resume

Intent: continue an incomplete run through `backtest-orchestrator`.

```text
entry_skill: backtest-orchestrator
operation: resume
run_id: run-20260423-001_ma-cross-000001sz-qtr
```

Expected behavior:

- locate the existing run by `run_id`
- inspect current state and `resume_from`
- continue the same run instead of minting a new identity

## replay

Intent: inspect or regenerate derived outputs for an existing run through `backtest-orchestrator`.

```text
entry_skill: backtest-orchestrator
operation: replay
run_id: run-20260423-001_ma-cross-000001sz-qtr
```

Expected behavior:

- locate the existing run by `run_id`
- read its artifacts without changing business identity
- regenerate or inspect outputs according to replay rules
