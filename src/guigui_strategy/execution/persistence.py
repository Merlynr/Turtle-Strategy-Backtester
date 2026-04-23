from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from .contracts import ExecutionConfig, ExecutionResult


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


def _write_jsonl(path: Path, rows: Iterable[Any]) -> None:
    lines = [json.dumps(_serialize(row), ensure_ascii=False, sort_keys=True) for row in rows]
    _atomic_write_text(path, "\n".join(lines) + ("\n" if lines else ""))


def persist_execution_result(artifact_root: Path, result: ExecutionResult) -> None:
    artifact_root = Path(artifact_root)
    artifact_root.mkdir(parents=True, exist_ok=True)
    (artifact_root / "execution").mkdir(parents=True, exist_ok=True)
    (artifact_root / "meta").mkdir(parents=True, exist_ok=True)
    (artifact_root / "snapshots").mkdir(parents=True, exist_ok=True)
    (artifact_root / "decisions").mkdir(parents=True, exist_ok=True)
    (artifact_root / "reports").mkdir(parents=True, exist_ok=True)
    report_path = artifact_root / "report.md"
    if not report_path.exists():
        _atomic_write_text(report_path, "")

    _write_json(artifact_root / "meta" / "execution-config.json", result.config.to_record())
    _write_jsonl(artifact_root / "execution" / "ledger.jsonl", result.ledger_rows)
    _write_jsonl(artifact_root / "execution" / "fills.jsonl", result.fills)
    _write_json(artifact_root / "execution" / "nav.json", [row.to_record() for row in result.nav_curve])
    _write_jsonl(
        artifact_root / "execution" / "rejections.jsonl",
        [result.blocked_record] if result.blocked_record is not None else [],
    )

    status_path = artifact_root / "status.json"
    status_payload = {
        "run_id": result.run_id,
        "phase": "04-backtest-simulation",
        "current_node": "report-node",
        "state": "partial",
        "last_completed_node": "execution-node",
        "resume_from": "report-node",
        "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "error_summary": None,
    }
    _write_json(status_path, status_payload)
