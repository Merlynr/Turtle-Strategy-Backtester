from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from guigui_strategy.reporting.contracts import ReportConfig, ReportInput, ReportValidationError


def test_report_config_locks_five_sections() -> None:
    config = ReportConfig(annualization_factor=252, sharpe_risk_free_rate=Decimal("0"))
    assert config.to_record() == {
        "annualization_factor": 252,
        "sharpe_risk_free_rate": "0",
        "report_sections": ["Summary", "Metrics", "Key Trades", "Artifact Index", "Notes"],
    }


def test_report_config_rejects_wrong_section_count() -> None:
    with pytest.raises(ReportValidationError):
        ReportConfig(report_sections=("Summary", "Metrics"))


def test_report_input_serializes_artifact_root_and_identity(tmp_path) -> None:
    config = ReportConfig()
    report_input = ReportInput(
        run_id="run-001",
        symbol="000001.SZ",
        market="CN-A",
        cadence="quarterly",
        asof_date=date(2026, 4, 23),
        artifact_root=tmp_path,
        manifest={"run_id": "run-001"},
        status={"run_id": "run-001"},
        config=config,
    )

    record = report_input.to_record()
    assert record["artifact_root"] == str(tmp_path)
    assert record["run_id"] == "run-001"
    assert record["config"]["annualization_factor"] == 252

