from __future__ import annotations

from datetime import date
from decimal import Decimal

from guigui_strategy.execution.contracts import ExecutionConfig, ExecutionInput, PortfolioState
from guigui_strategy.execution.engine import execute_execution
from guigui_strategy.execution.persistence import persist_execution_result


def _write_prices(tmp_path, rows: str):
    path = tmp_path / "prices.csv"
    path.write_text(rows, encoding="utf-8")
    return path


def _base_record(action: str):
    return {
        "run_id": "run-001",
        "symbol": "000001.SZ",
        "market": "CN-A",
        "cadence": "quarterly",
        "asof_date": "2026-04-23",
        "prompt_version": "brain-v1.0",
        "schema_version": "ai-decision-output.v1",
        "model_label": "gemini-2.5-flash",
        "input_summary": {"snapshot_ref": "snapshots/snapshot_2026-04-23.json"},
        "decision": {"action": action, "confidence": 0.7, "signal_tags": ["trend-confirmed"]},
        "validation": {"status": "passed", "issues": []},
    }


def test_persist_execution_result_writes_auditable_artifacts(tmp_path) -> None:
    prices = _write_prices(
        tmp_path,
        "date,open,high,low,close,volume\n"
        "2026-04-23,10.00,10.10,9.95,10.05,100\n"
        "2026-04-24,10.20,10.30,10.10,10.25,100\n",
    )
    config = ExecutionConfig(
        initial_capital=Decimal("100000"),
        commission_rate=Decimal("0.001"),
        slippage_bps=Decimal("10"),
        position_limit=Decimal("1"),
        lot_size=100,
    )
    execution_input = ExecutionInput(
        run_id="run-001",
        symbol="000001.SZ",
        market="CN-A",
        cadence="quarterly",
        asof_date=date(2026, 4, 23),
        snapshot={"validation_status": "passed", "prices_csv_path": str(prices)},
        decision_record=_base_record("buy"),
        config=config,
        starting_state=PortfolioState(cash=Decimal("100000"), shares=0, average_cost=Decimal("0")),
    )
    result = execute_execution(execution_input)

    artifact_root = tmp_path / "runs" / "run-001"
    persist_execution_result(artifact_root, result)

    assert (artifact_root / "meta" / "execution-config.json").exists()
    assert (artifact_root / "execution" / "ledger.jsonl").exists()
    assert (artifact_root / "execution" / "fills.jsonl").exists()
    assert (artifact_root / "execution" / "nav.json").exists()
    assert (artifact_root / "execution" / "rejections.jsonl").exists()

    status_text = (artifact_root / "status.json").read_text(encoding="utf-8")
    assert '"current_node": "report-node"' in status_text
    assert '"resume_from": "report-node"' in status_text

    ledger_text = (artifact_root / "execution" / "ledger.jsonl").read_text(encoding="utf-8").strip()
    assert ledger_text
    assert '"decision_action": "buy"' in ledger_text


def test_persist_execution_result_is_deterministic(tmp_path) -> None:
    prices = _write_prices(
        tmp_path,
        "date,open,high,low,close,volume\n"
        "2026-04-23,10.00,10.10,9.95,10.05,100\n"
        "2026-04-24,10.20,10.30,10.10,10.25,100\n",
    )
    config = ExecutionConfig(
        initial_capital=Decimal("100000"),
        commission_rate=Decimal("0.001"),
        slippage_bps=Decimal("10"),
        position_limit=Decimal("1"),
        lot_size=100,
    )
    execution_input = ExecutionInput(
        run_id="run-001",
        symbol="000001.SZ",
        market="CN-A",
        cadence="quarterly",
        asof_date=date(2026, 4, 23),
        snapshot={"validation_status": "passed", "prices_csv_path": str(prices)},
        decision_record=_base_record("hold"),
        config=config,
        starting_state=PortfolioState(cash=Decimal("100000"), shares=0, average_cost=Decimal("0")),
    )
    result = execute_execution(execution_input)

    artifact_root = tmp_path / "runs" / "run-001"
    persist_execution_result(artifact_root, result)
    first = (artifact_root / "execution" / "ledger.jsonl").read_text(encoding="utf-8")
    persist_execution_result(artifact_root, result)
    second = (artifact_root / "execution" / "ledger.jsonl").read_text(encoding="utf-8")

    assert first == second

