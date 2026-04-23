from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from guigui_strategy.execution.contracts import (
    ExecutionConfig,
    ExecutionValidationError,
    PortfolioState,
    validate_decision_record,
)


def test_execution_config_persists_assumptions() -> None:
    config = ExecutionConfig(
        initial_capital=Decimal("100000"),
        commission_rate=Decimal("0.001"),
        slippage_bps=Decimal("10"),
        position_limit=Decimal("1"),
        lot_size=100,
    )

    assert config.slippage_rate == Decimal("0.001")
    assert config.to_record() == {
        "initial_capital": "100000",
        "commission_rate": "0.001",
        "slippage_bps": "10",
        "slippage_rate": "0.001",
        "position_limit": "1",
        "lot_size": 100,
    }


def test_portfolio_state_rejects_negative_cash() -> None:
    with pytest.raises(ExecutionValidationError):
        PortfolioState(cash=Decimal("-1"), shares=0, average_cost=Decimal("0"))


def test_validate_decision_record_accepts_phase3_buy() -> None:
    record = {
        "run_id": "run-001",
        "symbol": "000001.SZ",
        "market": "CN-A",
        "cadence": "quarterly",
        "asof_date": "2026-04-23",
        "prompt_version": "brain-v1.0",
        "schema_version": "ai-decision-output.v1",
        "model_label": "gemini-2.5-flash",
        "input_summary": {"snapshot_ref": "snapshots/snapshot_2026-04-23.json"},
        "decision": {"action": "buy", "confidence": 0.72, "signal_tags": ["trend-confirmed"]},
        "validation": {"status": "passed", "issues": []},
    }

    validated = validate_decision_record(record)

    assert validated.decision_action == "buy"
    assert validated.execution_action == "add"
    assert validated.asof_date == date(2026, 4, 23)
    assert validated.signal_tags == ("trend-confirmed",)


def test_validate_decision_record_blocks_invalid_action() -> None:
    record = {
        "run_id": "run-001",
        "symbol": "000001.SZ",
        "market": "CN-A",
        "cadence": "quarterly",
        "asof_date": "2026-04-23",
        "prompt_version": "brain-v1.0",
        "schema_version": "ai-decision-output.v1",
        "model_label": "gemini-2.5-flash",
        "input_summary": {},
        "decision": {"action": "wait"},
        "validation": {"status": "passed", "issues": []},
    }

    with pytest.raises(ExecutionValidationError) as exc_info:
        validate_decision_record(record)

    assert exc_info.value.reason == "unsupported-decision-action"


def test_validate_decision_record_requires_passed_validation() -> None:
    record = {
        "run_id": "run-001",
        "symbol": "000001.SZ",
        "market": "CN-A",
        "cadence": "quarterly",
        "asof_date": "2026-04-23",
        "prompt_version": "brain-v1.0",
        "schema_version": "ai-decision-output.v1",
        "model_label": "gemini-2.5-flash",
        "input_summary": {},
        "decision": {"action": "sell"},
        "validation": {"status": "blocked", "issues": ["schema failed"]},
    }

    with pytest.raises(ExecutionValidationError) as exc_info:
        validate_decision_record(record)

    assert exc_info.value.reason == "decision-not-passed"

