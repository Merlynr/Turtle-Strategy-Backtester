# Run Identity Examples

The naming pattern is `run_id + short business summary`. The short summary stays human-readable, while the manifest keeps the full business identity.

run-20260423-001_ma-cross-000001sz-qtr
- Encodes: `run_id` sequence, `strategy=ma-cross`, `symbol=000001.SZ`, `cadence=quarterly`
- Not encoded directly: `market`, `start`, `end`, `entry_skill`, `artifact_root`, `created_at`

run-20260423-002_value-quality-600519sh-mon
- Encodes: `run_id` sequence, `strategy=value-quality`, `symbol=600519.SH`, `cadence=monthly`
- Not encoded directly: `market`, `start`, `end`, `entry_skill`, `artifact_root`, `created_at`

run-20260423-003_earnings-drift-300750sz-qtr
- Encodes: `run_id` sequence, `strategy=earnings-drift`, `symbol=300750.SZ`, `cadence=quarterly`
- Not encoded directly: `market`, `start`, `end`, `entry_skill`, `artifact_root`, `created_at`

## Mapping Guidance

- `run_id` must stay unique even if two runs share the same `strategy`, `symbol`, and `cadence`.
- The short business summary is a convenience label, not the authoritative source of identity.
- `manifest.json` remains the source of truth for exact dates, market, and creation metadata.
