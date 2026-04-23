from __future__ import annotations

import json
import shutil
from datetime import datetime

from guigui_strategy.validation.contracts import ValidationConfig, ValidationInput
from guigui_strategy.validation.engine import validate_run
from guigui_strategy.validation.persistence import persist_validation_result

from .test_engine import FIXTURES, _materialize_fixture, _load_validation_input


def test_persist_validation_result_writes_meta_validation(tmp_path, monkeypatch) -> None:
    run_root = _materialize_fixture(FIXTURES / "golden-run", tmp_path / "golden-run")

    class _FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            return cls(2026, 4, 23, 10, 45, 0, tzinfo=tz)

    monkeypatch.setattr("guigui_strategy.validation.engine.datetime", _FixedDatetime)
    input_ = _load_validation_input(run_root, baseline_root=run_root, check_golden_baseline=True)
    result = validate_run(input_)
    persist_validation_result(run_root, result)

    validation_path = run_root / "meta" / "validation.json"
    assert validation_path.exists()

    record = json.loads(validation_path.read_text(encoding="utf-8"))
    assert record["status"] == "passed"
    assert record["validated_at"] == "2026-04-23T10:45:00+00:00"


def test_persist_validation_result_is_idempotent_with_fixed_timestamp(tmp_path, monkeypatch) -> None:
    run_root = _materialize_fixture(FIXTURES / "golden-run", tmp_path / "golden-run")

    class _FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            return cls(2026, 4, 23, 10, 45, 0, tzinfo=tz)

    monkeypatch.setattr("guigui_strategy.validation.engine.datetime", _FixedDatetime)
    input_ = _load_validation_input(run_root, baseline_root=run_root, check_golden_baseline=True)
    result = validate_run(input_)
    persist_validation_result(run_root, result)
    first = (run_root / "meta" / "validation.json").read_text(encoding="utf-8")
    persist_validation_result(run_root, result)
    second = (run_root / "meta" / "validation.json").read_text(encoding="utf-8")

    assert first == second
