from __future__ import annotations

from datetime import date
from decimal import Decimal

from guigui_strategy.execution.contracts import ExecutionConfig, ExecutionInput, PortfolioState
from guigui_strategy.execution.engine import execute_execution


def _write_prices(tmp_path, rows: str):
    path = tmp_path / "prices.csv"
    path.write_text(rows, encoding="utf-8")
    return path


def _base_record(action: str, asof_date: str = "2026-04-23"):
    return {
        "run_id": "run-001",
        "symbol": "000001.SZ",
        "market": "CN-A",
        "cadence": "quarterly",
        "asof_date": asof_date,
        "prompt_version": "brain-v1.0",
        "schema_version": "ai-decision-output.v1",
        "model_label": "gemini-2.5-flash",
        "input_summary": {"snapshot_ref": "snapshots/snapshot_2026-04-23.json"},
        "decision": {"action": action, "confidence": 0.7, "signal_tags": ["trend-confirmed"]},
        "validation": {"status": "passed", "issues": []},
    }


def test_execute_buy_uses_next_open_and_lot_rounding(tmp_path) -> None:
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

    assert result.status == "passed"
    assert result.execution_date == date(2026, 4, 24)
    assert result.fills[0].quantity == 9700
    assert result.ledger_rows[0].shares == 9700
    assert result.ledger_rows[0].nav == result.ending_state.equity(Decimal("10.20"))
    assert result.ledger_rows[0].nav < Decimal("100000")


def test_execute_hold_is_noop_but_marks_to_market(tmp_path) -> None:
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

    assert result.status == "passed"
    assert result.fills == ()
    assert result.ledger_rows[0].nav == Decimal("100000")
    assert result.ledger_rows[0].execution_action == "hold"


def test_execute_sell_reduces_all_sellable_lots(tmp_path) -> None:
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
        decision_record=_base_record("sell"),
        config=config,
        starting_state=PortfolioState(cash=Decimal("0"), shares=250, average_cost=Decimal("9.00")),
    )

    result = execute_execution(execution_input)

    assert result.status == "passed"
    assert result.fills[0].quantity == 200
    assert result.ending_state.shares == 50
    assert result.ending_state.realized_pnl > Decimal("0")


def test_execute_blocks_missing_next_open(tmp_path) -> None:
    prices = _write_prices(
        tmp_path,
        "date,open,high,low,close,volume\n"
        "2026-04-23,10.00,10.10,9.95,10.05,100\n",
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

    assert result.status == "blocked"
    assert result.blocked_record is not None
    assert result.blocked_record.reason == "missing-next-open"


def test_execute_blocks_zero_buyable_lot(tmp_path) -> None:
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
        starting_state=PortfolioState(cash=Decimal("500"), shares=0, average_cost=Decimal("0")),
    )

    result = execute_execution(execution_input)

    assert result.status == "blocked"
    assert result.blocked_record is not None
    assert result.blocked_record.reason == "zero-buyable-lot"

