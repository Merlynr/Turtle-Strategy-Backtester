#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  cat >&2 <<'EOF'
Usage:
  scripts/init_manual_run.sh RUN_ID [ARTIFACT_ROOT]

Examples:
  scripts/init_manual_run.sh run-20260423-001_ma-cross-000001sz-qtr
  scripts/init_manual_run.sh run-20260423-001_ma-cross-000001sz-qtr runs/run-20260423-001_ma-cross-000001sz-qtr
EOF
  exit 1
fi

RUN_ID="$1"
ARTIFACT_ROOT="${2:-runs/$RUN_ID}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_ROOT="$PROJECT_ROOT/docs/examples/manual-run"
TEMPLATE_RUN="$TEMPLATE_ROOT/run-20260423-001_ma-cross-000001sz-qtr"

if [[ ! -d "$TEMPLATE_RUN" ]]; then
  echo "Template directory not found: $TEMPLATE_RUN" >&2
  exit 1
fi

if [[ -e "$ARTIFACT_ROOT" ]]; then
  echo "Target already exists: $ARTIFACT_ROOT" >&2
  exit 1
fi

mkdir -p "$(dirname "$ARTIFACT_ROOT")"
cp -R "$TEMPLATE_RUN" "$ARTIFACT_ROOT"

python3 - "$RUN_ID" "$ARTIFACT_ROOT" <<'PY'
from __future__ import annotations

import json
from pathlib import Path
import sys

run_id = sys.argv[1]
artifact_root = Path(sys.argv[2])

manifest_path = artifact_root / "manifest.json"
status_path = artifact_root / "status.json"
snapshot_path = artifact_root / "snapshots" / "snapshot_2026-04-23.json"
decision_path = artifact_root / "decisions" / "decision_2026-04-23.json"
run_root_ref = artifact_root.as_posix()

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["run_id"] = run_id
manifest["artifact_root"] = run_root_ref
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

status = json.loads(status_path.read_text(encoding="utf-8"))
status["run_id"] = run_id
status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
snapshot["prices_csv_path"] = f"{run_root_ref}/snapshots/prices.csv"
snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

decision = json.loads(decision_path.read_text(encoding="utf-8"))
decision["run_id"] = run_id
decision["input_summary"]["snapshot_ref"] = "snapshots/snapshot_2026-04-23.json"
decision_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

echo "Initialized manual run template at: $ARTIFACT_ROOT"
