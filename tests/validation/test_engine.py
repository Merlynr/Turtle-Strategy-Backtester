from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

import pytest

from guigui_strategy.validation.contracts import ValidationConfig, ValidationInput
from guigui_strategy.validation.engine import validate_run


FIXTURES = Path(__file__).parent / "fixtures"


def _materialize_fixture(source: Path, destination: Path) -> Path:
    shutil.copytree(source, destination)
    for path in destination.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            text = text.replace("__ARTIFACT_ROOT__", str(destination))
            path.write_text(text, encoding="utf-8")
    return destination


def _load_validation_input(run_root: Path, *, baseline_root: Path | None = None, check_golden_baseline: bool = False) -> ValidationInput:
    manifest = json.loads((run_root / "manifest.json").read_text(encoding="utf-8"))
    status = json.loads((run_root / "status.json").read_text(encoding="utf-8"))
    return ValidationInput(
        run_id=str(manifest["run_id"]),
        symbol=str(manifest["symbol"]),
        market=str(manifest["market"]),
        cadence=str(manifest["cadence"]),
        asof_date=date(2026, 4, 23),
        artifact_root=run_root,
        manifest=manifest,
        status=status,
        config=ValidationConfig(
            check_golden_baseline=check_golden_baseline,
            golden_baseline_root=baseline_root,
        ),
    )


def test_validate_run_passes_against_golden_fixture(tmp_path) -> None:
    run_root = _materialize_fixture(FIXTURES / "golden-run", tmp_path / "golden-run")
    input_ = _load_validation_input(run_root, baseline_root=run_root, check_golden_baseline=True)

    result = validate_run(input_)

    assert result.status == "passed"
    assert any(finding.code == "baseline-checked" for finding in result.findings)
    assert result.artifact_index.report_md_path == str(run_root / "report.md")
    assert result.checked_artifacts[0] == "manifest.json"


def test_validate_run_blocks_missing_report_artifact(tmp_path) -> None:
    run_root = _materialize_fixture(FIXTURES / "synthetic-run", tmp_path / "synthetic-run")
    input_ = _load_validation_input(run_root)

    result = validate_run(input_)

    assert result.status == "blocked"
    assert any(finding.code == "missing-artifact" for finding in result.findings)
    assert any("report.md" in finding.message or "report.md" in str(finding.details) for finding in result.findings)


def test_validate_run_rejects_mismatched_status_identity(tmp_path) -> None:
    run_root = _materialize_fixture(FIXTURES / "golden-run", tmp_path / "golden-run")
    status_path = run_root / "status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status["run_id"] = "run-002"
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    input_ = _load_validation_input(run_root)
    result = validate_run(input_)

    assert result.status == "blocked"
    assert any(finding.code == "status-run-id-mismatch" for finding in result.findings)
