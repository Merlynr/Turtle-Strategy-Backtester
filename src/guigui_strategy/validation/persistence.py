from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from .contracts import ValidationResult


def _serialize(value: Any) -> Any:
    if hasattr(value, "to_record"):
        return value.to_record()
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(val) for key, val in value.items()}
    if isinstance(value, Path):
        return str(value)
    return value


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as handle:
        handle.write(content)
        temp_name = handle.name
    Path(temp_name).replace(path)


def _write_json(path: Path, payload: Any) -> None:
    _atomic_write_text(path, json.dumps(_serialize(payload), ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def persist_validation_result(artifact_root: Path, result: ValidationResult) -> None:
    artifact_root = Path(artifact_root)
    (artifact_root / "meta").mkdir(parents=True, exist_ok=True)
    _write_json(artifact_root / "meta" / "validation.json", result.to_record())
