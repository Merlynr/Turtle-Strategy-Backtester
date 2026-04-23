# Run Directory Example

```text
runs/run-20260423-001_ma-cross-000001sz-qtr/
├── manifest.json
├── status.json
├── report.md
├── snapshots/
│   ├── 2020-03-31-market.json
│   └── 2020-03-31-fundamentals.parquet
├── decisions/
│   └── 2020-03-31-decision.json
├── execution/
│   ├── ledger.jsonl
│   └── nav.parquet
├── reports/
│   └── 2020q1-review.md
└── meta/
    ├── sources.json
    └── validation.json
```

## Notes

- The directory name keeps the unique `run_id` and a short human-readable summary.
- `manifest.json`, `status.json`, and `report.md` stay at the top level for fast lookup.
- `snapshots/`, `decisions/`, `execution/`, `reports/`, and `meta/` remain fixed even when future phases add more file types.
