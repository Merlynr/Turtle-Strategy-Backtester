from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import pytest

from guigui_strategy.reporting.contracts import ReportConfig, ReportInput, ReportValidationError
from guigui_strategy.reporting.engine import generate_report


def _write_execution_artifacts(tmp_path):
    run_root = tmp_path / "runs" / "run-001"
    (run_root / "execution").mkdir(parents=True, exist_ok=True)
    (run_root / "snapshots").mkdir(parents=True, exist_ok=True)
    (run_root / "decisions").mkdir(parents=True, exist_ok=True)
    (run_root / "reports").mkdir(parents=True, exist_ok=True)
    (run_root / "meta").mkdir(parents=True, exist_ok=True)

    (run_root / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": "run-001",
                "strategy": "ma-cross",
                "symbol": "000001.SZ",
                "market": "CN-A",
                "start": "2026-04-01",
                "end": "2026-04-30",
                "cadence": "quarterly",
                "entry_skill": "backtest-orchestrator",
                "created_at": "2026-04-23T09:00:00+08:00",
                "artifact_root": str(run_root),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    (run_root / "status.json").write_text(
        json.dumps(
            {
                "run_id": "run-001",
                "phase": "05-reporting",
                "current_node": "report-node",
                "state": "partial",
                "last_completed_node": "execution-node",
                "resume_from": "report-node",
                "updated_at": "2026-04-23T09:40:00+08:00",
                "error_summary": None,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    (run_root / "execution" / "nav.json").write_text(
        json.dumps(
            [
                {"date": "2026-04-24", "nav": "100000", "cash": "100000", "shares": 0},
                {"date": "2026-04-25", "nav": "101000", "cash": "1000", "shares": 9900},
                {"date": "2026-04-26", "nav": "98000", "cash": "1000", "shares": 9900},
                {"date": "2026-04-27", "nav": "104000", "cash": "2000", "shares": 9800},
            ],
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    (run_root / "execution" / "fills.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "run_id": "run-001",
                        "symbol": "000001.SZ",
                        "asof_date": "2026-04-23",
                        "execution_date": "2026-04-24",
                        "decision_action": "buy",
                        "execution_action": "add",
                        "quantity": 9900,
                        "execution_price": "10",
                        "gross_value": "99000",
                        "commission": "99",
                        "slippage_cost": "99",
                        "cash_delta": "-99100",
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (run_root / "execution" / "ledger.jsonl").write_text(
        json.dumps(
            {
                "run_id": "run-001",
                "symbol": "000001.SZ",
                "asof_date": "2026-04-23",
                "execution_date": "2026-04-24",
                "decision_action": "buy",
                "execution_action": "add",
                "quantity": 9900,
                "cash": "900",
                "shares": 9900,
                "average_cost": "10.009999999999999786",
                "position_value": "99000",
                "realized_pnl": "0",
                "unrealized_pnl": "0",
                "nav": "100000",
                "mark_price": "10",
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return run_root


def test_generate_report_builds_five_sections(tmp_path) -> None:
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

    assert result.report_markdown.startswith("# Run Report: run-001")
    assert "## Summary" in result.report_markdown
    assert "## Metrics" in result.report_markdown
    assert "## Key Trades" in result.report_markdown
    assert "## Artifact Index" in result.report_markdown
    assert "## Notes" in result.report_markdown
    assert result.metrics.total_return == Decimal("0.04")
    assert result.metrics.max_drawdown == Decimal("-0.0297029702970297")
    assert result.key_trades[0].execution_action == "add"


def test_generate_report_rejects_missing_execution_inputs(tmp_path) -> None:
    run_root = tmp_path / "runs" / "run-001"
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "manifest.json").write_text(json.dumps({"run_id": "run-001"}), encoding="utf-8")
    (run_root / "status.json").write_text(json.dumps({"run_id": "run-001"}), encoding="utf-8")

    report_input = ReportInput(
        run_id="run-001",
        symbol="000001.SZ",
        market="CN-A",
        cadence="quarterly",
        asof_date=date(2026, 4, 23),
        artifact_root=run_root,
        manifest={"run_id": "run-001"},
        status={"run_id": "run-001"},
        config=ReportConfig(),
    )

    with pytest.raises(ReportValidationError):
        generate_report(report_input)

