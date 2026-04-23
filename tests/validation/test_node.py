from __future__ import annotations

import json
from datetime import datetime

from guigui_strategy.validation.engine import validate_run
from guigui_strategy.validation.node import run_validation

from .test_engine import FIXTURES, _materialize_fixture, _load_validation_input


def test_run_validation_persists_without_mutating_run_state(tmp_path, monkeypatch) -> None:
    run_root = _materialize_fixture(FIXTURES / "golden-run", tmp_path / "golden-run")
    before_manifest = (run_root / "manifest.json").read_text(encoding="utf-8")
    before_status = (run_root / "status.json").read_text(encoding="utf-8")

    class _FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            return cls(2026, 4, 23, 10, 50, 0, tzinfo=tz)

    monkeypatch.setattr("guigui_strategy.validation.engine.datetime", _FixedDatetime)
    result = run_validation(_load_validation_input(run_root, baseline_root=run_root, check_golden_baseline=True))

    after_manifest = (run_root / "manifest.json").read_text(encoding="utf-8")
    after_status = (run_root / "status.json").read_text(encoding="utf-8")
    validation_record = json.loads((run_root / "meta" / "validation.json").read_text(encoding="utf-8"))

    assert result.status == "passed"
    assert before_manifest == after_manifest
    assert before_status == after_status
    assert validation_record["status"] == "passed"
    assert validation_record["validated_at"] == "2026-04-23T10:50:00+00:00"
