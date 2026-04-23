from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

from guigui_strategy.reporting.contracts import ReportConfig, ReportInput
from guigui_strategy.reporting.engine import generate_report
from guigui_strategy.reporting.persistence import persist_report_result

from .test_engine import _write_execution_artifacts


def test_persist_report_result_writes_report_and_summary(tmp_path) -> None:
    run_root = _write_execution_artifacts(tmp_path)
    report_input = ReportInput(
        run_id="run-001",
        symbol="000001.SZ",
        market="CN-A",
        cadence="quarterly",
        asof_date=date(2026, 4, 23),
        artifact_root=run_root,
        manifest={"run_id": "run-001"},
        status={"run_id": "run-001"},
        config=ReportConfig(annualization_factor=252, sharpe_risk_free_rate=Decimal("0")),
    )

    result = generate_report(report_input)
    persist_report_result(run_root, result)

    assert (run_root / "report.md").exists()
    assert (run_root / "reports" / "report-index.json").exists()
    assert (run_root / "reports" / "report-summary.json").exists()

    status = json.loads((run_root / "status.json").read_text(encoding="utf-8"))
    assert status["state"] == "completed"
    assert status["current_node"] == "report-node"
    assert status["last_completed_node"] == "report-node"
    assert status["resume_from"] is None


def test_persist_report_result_is_idempotent(tmp_path) -> None:
    run_root = _write_execution_artifacts(tmp_path)
    report_input = ReportInput(
        run_id="run-001",
        symbol="000001.SZ",
        market="CN-A",
        cadence="quarterly",
        asof_date=date(2026, 4, 23),
        artifact_root=run_root,
        manifest={"run_id": "run-001"},
        status={"run_id": "run-001"},
        config=ReportConfig(annualization_factor=252, sharpe_risk_free_rate=Decimal("0")),
    )

    result = generate_report(report_input)
    persist_report_result(run_root, result)
    first = (run_root / "reports" / "report-summary.json").read_text(encoding="utf-8")
    persist_report_result(run_root, result)
    second = (run_root / "reports" / "report-summary.json").read_text(encoding="utf-8")

    assert first == second

