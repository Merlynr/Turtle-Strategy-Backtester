# Run Template

This directory is a copyable manual backtest boilerplate.

It already includes:

- `manifest.json`
- `status.json`
- `snapshots/prices.csv`
- `snapshots/snapshot_2026-04-23.json`
- `decisions/decision_2026-04-23.json`
- empty `execution/`
- empty `reports/`
- empty `meta/manual-inputs/`

Before running `run_backtest.py`, copy this directory to `runs/<run-id>/` or point `--artifact-root` at it.

After execution and reporting, the system will create:

- `report.md`
- `reports/report-index.json`
- `reports/report-summary.json`
- `meta/validation.json`
