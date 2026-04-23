from __future__ import annotations

import csv
from dataclasses import replace
from datetime import date
from decimal import Decimal, ROUND_DOWN
from pathlib import Path
from typing import Any, Iterable

from .contracts import (
    BlockedExecutionRecord,
    ExecutionInput,
    ExecutionResult,
    FillRecord,
    LedgerRow,
    PortfolioState,
    PriceBar,
    ValidatedDecisionRecord,
    ExecutionValidationError,
    validate_decision_record,
)


def _floor_to_lot(quantity: Decimal, lot_size: int) -> int:
    if quantity <= 0:
        return 0
    lots = (quantity // Decimal(lot_size)) * Decimal(lot_size)
    return int(lots)


def _read_price_bars(prices_csv_path: Path) -> list[PriceBar]:
    if not prices_csv_path.exists():
        raise ExecutionValidationError("missing-prices-csv", [f"{prices_csv_path} does not exist"])
    bars: list[PriceBar] = []
    with prices_csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"date", "open", "high", "low", "close", "volume"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ExecutionValidationError("invalid-prices-csv", ["prices.csv is missing required columns"])
        for row in reader:
            bars.append(PriceBar.from_mapping(row))
    bars.sort(key=lambda item: item.date)
    return bars


def _next_trading_open(bars: Iterable[PriceBar], asof_date: date) -> PriceBar | None:
    for bar in bars:
        if bar.date > asof_date:
            return bar
    return None


def _blocked_result(
    input_: ExecutionInput,
    reason: str,
    issues: list[str],
    validated_decision: ValidatedDecisionRecord | None = None,
) -> ExecutionResult:
    blocked = BlockedExecutionRecord(
        reason=reason,
        issues=tuple(issues),
        decision_action=validated_decision.decision_action if validated_decision else None,
        execution_action=validated_decision.execution_action if validated_decision else None,
    )
    return ExecutionResult(
        run_id=input_.run_id,
        symbol=input_.symbol,
        market=input_.market,
        cadence=input_.cadence,
        asof_date=input_.asof_date,
        status="blocked",
        execution_date=None,
        config=input_.config,
        starting_state=input_.starting_state,
        ending_state=input_.starting_state,
        validated_decision=validated_decision,
        fills=(),
        ledger_rows=(),
        nav_curve=(),
        blocked_record=blocked,
    )


def execute_execution(input_: ExecutionInput) -> ExecutionResult:
    try:
        validated_decision = validate_decision_record(input_.decision_record)
    except ExecutionValidationError as exc:
        return _blocked_result(input_, exc.reason, exc.issues)

    if validated_decision.run_id != input_.run_id:
        return _blocked_result(
            input_,
            "run-id-mismatch",
            [f"decision run_id {validated_decision.run_id!r} does not match execution run_id {input_.run_id!r}"],
            validated_decision,
        )
    if validated_decision.symbol != input_.symbol:
        return _blocked_result(input_, "symbol-mismatch", ["decision symbol does not match execution symbol"], validated_decision)

    snapshot = input_.snapshot
    if not isinstance(snapshot, dict):
        snapshot = dict(snapshot)
    if snapshot.get("validation_status") != "passed":
        return _blocked_result(input_, "snapshot-not-passed", ["snapshot validation_status must be passed"], validated_decision)
    prices_csv_path = snapshot.get("prices_csv_path")
    if not prices_csv_path:
        return _blocked_result(input_, "missing-prices-path", ["snapshot missing prices_csv_path"], validated_decision)

    try:
        bars = _read_price_bars(Path(prices_csv_path))
    except ExecutionValidationError as exc:
        return _blocked_result(input_, exc.reason, exc.issues, validated_decision)

    execution_bar = _next_trading_open(bars, input_.asof_date)
    if execution_bar is None:
        return _blocked_result(
            input_,
            "missing-next-open",
            [f"no trading-day open found strictly after {input_.asof_date.isoformat()}"],
            validated_decision,
        )

    mark_price = execution_bar.open
    cash = input_.starting_state.cash
    shares = input_.starting_state.shares
    average_cost = input_.starting_state.average_cost
    realized_pnl = input_.starting_state.realized_pnl
    config = input_.config

    fills: list[FillRecord] = []
    quantity = 0
    execution_action = validated_decision.execution_action

    if execution_action == "hold":
        next_state = PortfolioState(cash=cash, shares=shares, average_cost=average_cost, realized_pnl=realized_pnl)
        row = LedgerRow(
            run_id=input_.run_id,
            symbol=input_.symbol,
            asof_date=input_.asof_date,
            execution_date=execution_bar.date,
            decision_action=validated_decision.decision_action,
            execution_action=execution_action,
            quantity=0,
            cash=next_state.cash,
            shares=next_state.shares,
            average_cost=next_state.average_cost,
            position_value=next_state.position_value(mark_price),
            realized_pnl=next_state.realized_pnl,
            unrealized_pnl=next_state.position_value(mark_price) - (Decimal(next_state.shares) * next_state.average_cost),
            nav=next_state.equity(mark_price),
            mark_price=mark_price,
        )
        return ExecutionResult(
            run_id=input_.run_id,
            symbol=input_.symbol,
            market=input_.market,
            cadence=input_.cadence,
            asof_date=input_.asof_date,
            status="passed",
            execution_date=execution_bar.date,
            config=config,
            starting_state=input_.starting_state,
            ending_state=next_state,
            validated_decision=validated_decision,
            fills=(),
            ledger_rows=(row,),
            nav_curve=(row,),
            blocked_record=None,
        )

    trade_price = mark_price * (Decimal("1") + config.slippage_rate) if execution_action == "add" else mark_price * (Decimal("1") - config.slippage_rate)
    if execution_action == "add":
        affordable_shares = _floor_to_lot(cash / (trade_price * (Decimal("1") + config.commission_rate)), config.lot_size)
        position_cap = config.initial_capital * config.position_limit
        position_value = Decimal(shares) * mark_price
        room_value = position_cap - position_value
        if room_value <= 0:
            return _blocked_result(input_, "position-limit-breach", ["position limit leaves no room for additional long exposure"], validated_decision)
        limit_shares = _floor_to_lot(room_value / trade_price, config.lot_size)
        quantity = min(affordable_shares, limit_shares)
        if quantity <= 0:
            if affordable_shares <= 0:
                return _blocked_result(input_, "zero-buyable-lot", ["available cash cannot fund one 100-share lot"], validated_decision)
            return _blocked_result(input_, "position-limit-breach", ["position limit blocks an additional 100-share lot"], validated_decision)
        gross_value = trade_price * Decimal(quantity)
        commission = gross_value * config.commission_rate
        slippage_cost = mark_price * config.slippage_rate * Decimal(quantity)
        cash_after = cash - gross_value - commission
        total_cost_basis = (Decimal(shares) * average_cost) + gross_value + commission
        shares_after = shares + quantity
        average_cost_after = total_cost_basis / Decimal(shares_after)
        realized_after = realized_pnl
    else:
        sellable_shares = (shares // config.lot_size) * config.lot_size
        if sellable_shares <= 0:
            return _blocked_result(input_, "zero-sellable-lot", ["current holdings do not contain a sellable 100-share lot"], validated_decision)
        quantity = sellable_shares
        gross_value = trade_price * Decimal(quantity)
        commission = gross_value * config.commission_rate
        slippage_cost = mark_price * config.slippage_rate * Decimal(quantity)
        cash_after = cash + gross_value - commission
        realized_increment = gross_value - commission - (Decimal(quantity) * average_cost)
        shares_after = shares - quantity
        average_cost_after = Decimal("0") if shares_after == 0 else average_cost
        realized_after = realized_pnl + realized_increment

    next_state = PortfolioState(
        cash=cash_after,
        shares=shares_after,
        average_cost=average_cost_after,
        realized_pnl=realized_after,
    )
    position_value = next_state.position_value(mark_price)
    unrealized_pnl = position_value - (Decimal(next_state.shares) * next_state.average_cost)
    nav = next_state.equity(mark_price)

    fill = FillRecord(
        run_id=input_.run_id,
        symbol=input_.symbol,
        asof_date=input_.asof_date,
        execution_date=execution_bar.date,
        decision_action=validated_decision.decision_action,
        execution_action=execution_action,
        quantity=quantity,
        execution_price=trade_price,
        gross_value=gross_value,
        commission=commission,
        slippage_cost=slippage_cost,
        cash_delta=(cash_after - cash) if execution_action == "add" else (cash_after - cash),
    )
    row = LedgerRow(
        run_id=input_.run_id,
        symbol=input_.symbol,
        asof_date=input_.asof_date,
        execution_date=execution_bar.date,
        decision_action=validated_decision.decision_action,
        execution_action=execution_action,
        quantity=quantity,
        cash=next_state.cash,
        shares=next_state.shares,
        average_cost=next_state.average_cost,
        position_value=position_value,
        realized_pnl=next_state.realized_pnl,
        unrealized_pnl=unrealized_pnl,
        nav=nav,
        mark_price=mark_price,
    )
    return ExecutionResult(
        run_id=input_.run_id,
        symbol=input_.symbol,
        market=input_.market,
        cadence=input_.cadence,
        asof_date=input_.asof_date,
        status="passed",
        execution_date=execution_bar.date,
        config=config,
        starting_state=input_.starting_state,
        ending_state=next_state,
        validated_decision=validated_decision,
        fills=(fill,),
        ledger_rows=(row,),
        nav_curve=(row,),
        blocked_record=None,
    )
