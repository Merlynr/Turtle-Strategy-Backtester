# Run Directory Example

```text
runs/run-20260423-001_ma-cross-000001sz-qtr/
├── manifest.json
├── status.json
├── report.md
├── snapshots/
│   ├── prices.csv
│   └── snapshot_2026-04-23.json
├── decisions/
│   └── 2026-04-23-decision.json
├── execution/
│   ├── ledger.jsonl
│   └── nav.parquet
├── reports/
│   └── 2026q1-review.md
└── meta/
    ├── manual-inputs/
    │   └── 2026-04-23-source-note.md
    ├── validation.json
    └── sources.json
```

## Notes

- The directory name keeps the unique `run_id` and a short human-readable summary.
- `manifest.json`, `status.json`, and `report.md` stay at the top level for fast lookup.
- `snapshots/`, `decisions/`, `execution/`, `reports/`, and `meta/` remain fixed even when future phases add more file types.
- Raw operator input lives under `meta/manual-inputs/`; validation output lives in `meta/validation.json`.
