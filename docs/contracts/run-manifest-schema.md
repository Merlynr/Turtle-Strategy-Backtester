# Run Manifest Schema Contract

## Purpose

`manifest.json` is the stable business identity record for a run. It captures what the run is about, which entry skill created it, and where its artifact container lives.

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | string | Stable unique identifier for the run |
| `strategy` | string | Strategy profile, prompt profile, or strategy family label |
| `symbol` | string | Primary trading symbol for the backtest |
| `market` | string | Market or venue context, such as `CN-A` |
| `start` | string | Inclusive backtest start date |
| `end` | string | Inclusive backtest end date |
| `cadence` | string | Rebalance cadence such as `monthly` or `quarterly` |
| `entry_skill` | string | Entry skill that minted the run, normally `backtest-orchestrator` |
| `created_at` | string | ISO 8601 timestamp when the run identity was created |
| `artifact_root` | string | Absolute or project-relative root directory for this run's artifacts |

## Field Semantics

- `run_id` is the portable handle used by resume, replay, report lookup, and artifact inspection flows.
- `strategy`, `symbol`, `market`, `start`, `end`, and `cadence` define the business identity of the run.
- `entry_skill` records which top-level workflow entry created the run contract.
- `artifact_root` points to the single directory container for all artifacts belonging to this run.

## Example Shape

```json
{
  "run_id": "run-20260423-001_ma-cross-000001sz-qtr",
  "strategy": "ma-cross",
  "symbol": "000001.SZ",
  "market": "CN-A",
  "start": "2020-01-01",
  "end": "2023-12-31",
  "cadence": "quarterly",
  "entry_skill": "backtest-orchestrator",
  "created_at": "2026-04-23T11:35:00+08:00",
  "artifact_root": "runs/run-20260423-001_ma-cross-000001sz-qtr"
}
```

## Stability Rules

- `manifest.json` is written at creation time before node execution begins.
- Business identity fields are intended to remain stable for the life of the run.
- Mutating execution state belongs in `status.json`, not in the manifest.

## Invariants

- run_id is immutable after creation.
- manifest.json never changes business identity fields after creation.
- status.json is mutable and tracks execution progress.
- A resumed run reuses the same artifact_root.
- replay-ready means all required top-level files exist.
