from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from guigui_strategy.validation.contracts import (
    ValidationArtifactIndex,
    ValidationConfig,
    ValidationError,
    ValidationFinding,
    ValidationInput,
    ValidationResult,
)


def test_validation_config_records_golden_baseline() -> None:
    config = ValidationConfig(
        check_golden_baseline=True,
        golden_baseline_root=Path("/tmp/golden-run"),
        report_annualization_factor=252,
        report_sharpe_risk_free_rate=Decimal("0"),
    )

    assert config.to_record() == {
        "check_golden_baseline": True,
        "golden_baseline_root": "/tmp/golden-run",
        "report_annualization_factor": 252,
        "report_sharpe_risk_free_rate": "0",
        "allowed_runtime_metadata": ["validated_at"],
        "allowed_completed_states": ["completed", "replay-ready"],
    }


def test_validation_config_requires_golden_baseline_root_when_enabled() -> None:
    with pytest.raises(ValidationError):
        ValidationConfig(check_golden_baseline=True)


def test_validation_input_serializes_artifact_root_and_identity(tmp_path) -> None:
    config = ValidationConfig()
    validation_input = ValidationInput(
        run_id="run-001",
        symbol="000001.SZ",
        market="CN-A",
        cadence="quarterly",
        asof_date=date(2026, 4, 23),
        artifact_root=tmp_path,
        manifest={"run_id": "run-001", "artifact_root": str(tmp_path)},
        status={"run_id": "run-001"},
        config=config,
    )

    record = validation_input.to_record()
    assert record["artifact_root"] == str(tmp_path)
    assert record["config"]["check_golden_baseline"] is False


def test_validation_result_serializes_artifacts_and_findings(tmp_path) -> None:
    config = ValidationConfig()
    finding = ValidationFinding(code="layout-checked", severity="info", message="layout ok")
    artifact_index = ValidationArtifactIndex(
        validation_path=str(tmp_path / "meta" / "validation.json"),
        manifest_path=str(tmp_path / "manifest.json"),
        status_path=str(tmp_path / "status.json"),
        report_md_path=str(tmp_path / "report.md"),
        report_index_path=str(tmp_path / "reports" / "report-index.json"),
        report_summary_path=str(tmp_path / "reports" / "report-summary.json"),
        snapshot_paths=(str(tmp_path / "snapshots"),),
        decision_paths=(str(tmp_path / "decisions"),),
        execution_paths=(str(tmp_path / "execution"),),
        reports_paths=(str(tmp_path / "reports"),),
        meta_paths=(str(tmp_path / "meta"),),
    )
    result = ValidationResult(
        run_id="run-001",
        symbol="000001.SZ",
        market="CN-A",
        cadence="quarterly",
        artifact_root=tmp_path,
        status="passed",
        summary="passed",
        validated_at="2026-04-23T10:00:00+08:00",
        checked_artifacts=("manifest.json", "status.json"),
        findings=(finding,),
        artifact_index=artifact_index,
        config=config,
    )

    record = result.to_record()
    assert record["artifact_root"] == str(tmp_path)
    assert record["findings"][0]["severity"] == "info"
    assert record["artifact_index"]["validation_path"].endswith("meta/validation.json")
