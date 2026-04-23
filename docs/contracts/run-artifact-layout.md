# Run Artifact Layout Contract

## Canonical Container

Each run owns one dedicated artifact container directory named with `run_id + short business summary`.

The top level must contain exactly these files and directories:

- `manifest.json`
- `status.json`
- `report.md`
- `snapshots/`
- `decisions/`
- `execution/`
- `reports/`
- `meta/`

No phase may invent a parallel top-level directory for run artifacts outside this container.

## Canonical Tree

```text
{artifact_root}/
├── manifest.json
├── status.json
├── report.md
├── snapshots/
├── decisions/
├── execution/
├── reports/
└── meta/
```

## Directory Responsibilities

### Top-Level Files

- `manifest.json`: stable business identity and creation metadata for the run
- `status.json`: mutable execution state, lifecycle position, and resume checkpoint
- `report.md`: canonical top-level summary for the run

### `snapshots/`

Stores point-in-time data artifacts that feed decision making.

- `snapshots/*.json`
- `snapshots/*.parquet`

### `decisions/`

Stores structured AI decision outputs and their validation results.

- `decisions/*.json`

### `execution/`

Stores execution-side ledgers and simulation outputs.

- `execution/ledger.*`
- `execution/fills.*`
- `execution/nav.*`

### `reports/`

Stores derived reports beyond the top-level summary report.

- `reports/*.md`
- `reports/*.json`

### `meta/`

Stores machine-readable metadata that supports auditing, provenance, and tooling.

- `meta/*.json`
- `meta/manual-inputs/`
- `meta/validation.json`

## Layout Rules

- Every artifact written by downstream phases must live under the run container.
- `artifact_root` in `manifest.json` points to this directory and nothing else.
- A resumed run reuses the same directory tree.
- A replay operation reads from this directory tree without inventing alternate lookup paths.
- `meta/manual-inputs/` stores raw operator-provided source payloads for Phase 2.
- `meta/validation.json` stores point-in-time validation results for snapshots.
