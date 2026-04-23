# Point-in-Time Snapshot Example

This example shows the manual input path for Phase 2.

## Raw prices.csv

```csv
date,open,high,low,close,volume
2026-04-21,10.00,10.20,9.90,10.10,1200000
2026-04-22,10.08,10.30,10.02,10.25,1325000
2026-04-23,10.24,10.40,10.18,10.36,1410000
```

## Normalized snapshot

`snapshot_2026-04-23.json`

```json
{
  "provider": "manual",
  "symbol": "000001.SZ",
  "market": "A-share",
  "cadence": "quarterly",
  "asof_date": "2026-04-23",
  "window_start": "2026-04-21",
  "window_end": "2026-04-23",
  "prices_csv_path": "runs/run-20260423-001_ma-cross-000001sz-qtr/snapshots/prices.csv",
  "indicator_payload": {
    "ma20": 10.18,
    "rsi14": 62.4,
    "atr14": 0.26
  },
  "notes": "Operator provided a bullish setup after earnings stabilization.",
  "built_at": "2026-04-23T15:30:00+08:00",
  "validation_status": "passed"
}
```

## Rejected example

This row must be rejected because it violates the point-in-time rule:

```csv
date,open,high,low,close,volume
2026-04-24,10.40,10.55,10.32,10.50,1500000
```

The validation contract blocks any `candle.date > asof_date`.
