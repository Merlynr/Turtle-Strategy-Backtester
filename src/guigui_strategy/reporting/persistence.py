from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from .contracts import ReportResult


def _serialize(value: Any) -> Any:
    if hasattr(value, "to_record"):
        return value.to_record()
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(val) for key, val in value.items()}
    return value


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as handle:
        handle.write(content)
        temp_name = handle.name
    Path(temp_name).replace(path)


def _write_json(path: Path, payload: Any) -> None:
    _atomic_write_text(path, json.dumps(_serialize(payload), ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def persist_report_result(artifact_root: Path, result: ReportResult) -> None:
    artifact_root = Path(artifact_root)
    artifact_root.mkdir(parents=True, exist_ok=True)
    (artifact_root / "reports").mkdir(parents=True, exist_ok=True)

    _atomic_write_text(artifact_root / "report.md", result.report_markdown)
    _write_json(artifact_root / "reports" / "report-index.json", result.report_index)
    _write_json(artifact_root / "reports" / "report-summary.json", result.to_record())

    status_payload = {
        "run_id": result.run_id,
        "phase": "05-reporting",
        "current_node": "report-node",
        "state": "completed",
        "last_completed_node": "report-node",
        "resume_from": None,
        "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "error_summary": None,
    }
    _write_json(artifact_root / "status.json", status_payload)

