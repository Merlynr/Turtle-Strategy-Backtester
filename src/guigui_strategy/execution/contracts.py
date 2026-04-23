from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

ALLOWED_DECISION_ACTIONS = {"buy", "sell", "hold"}
EXECUTION_ACTION_ALIASES = {"buy": "add", "sell": "reduce", "hold": "hold"}


class ExecutionValidationError(ValueError):
    def __init__(self, reason: str, issues: list[str] | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.issues = issues or [reason]


def _decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ExecutionValidationError("invalid-decimal", [f"unable to parse decimal: {value!r}"]) from exc


def _require_mapping(value: Any, reason: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ExecutionValidationError(reason, [f"expected mapping, got {type(value).__name__}"])
    return value


def _require_date(value: Any, reason: str) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ExecutionValidationError(reason, [f"invalid ISO date: {value!r}"]) from exc
    raise ExecutionValidationError(reason, [f"expected ISO date string, got {type(value).__name__}"])


def _decimal_str(value: Decimal) -> str:
    return format(value.normalize() if value == value.to_integral() else value, "f")


@dataclass(frozen=True)
class ExecutionConfig:
    initial_capital: Decimal
    commission_rate: Decimal
    slippage_bps: Decimal
    position_limit: Decimal
    lot_size: int = 100

    def __post_init__(self) -> None:
        if self.initial_capital <= 0:
            raise ExecutionValidationError("invalid-initial-capital", ["initial_capital must be positive"])
        if self.commission_rate < 0:
            raise ExecutionValidationError("invalid-commission-rate", ["commission_rate must be non-negative"])
        if self.slippage_bps < 0:
            raise ExecutionValidationError("invalid-slippage-bps", ["slippage_bps must be non-negative"])
        if self.position_limit <= 0:
            raise ExecutionValidationError("invalid-position-limit", ["position_limit must be positive"])
        if self.lot_size <= 0:
            raise ExecutionValidationError("invalid-lot-size", ["lot_size must be positive"])

    @property
    def slippage_rate(self) -> Decimal:
        return self.slippage_bps / Decimal("10000")

    def to_record(self) -> dict[str, Any]:
        return {
            "initial_capital": _decimal_str(self.initial_capital),
            "commission_rate": _decimal_str(self.commission_rate),
            "slippage_bps": _decimal_str(self.slippage_bps),
            "slippage_rate": _decimal_str(self.slippage_rate),
            "position_limit": _decimal_str(self.position_limit),
            "lot_size": self.lot_size,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ExecutionConfig":
        mapping = _require_mapping(data, "invalid-execution-config")
        return cls(
            initial_capital=_decimal(mapping["initial_capital"]),
            commission_rate=_decimal(mapping["commission_rate"]),
            slippage_bps=_decimal(mapping["slippage_bps"]),
            position_limit=_decimal(mapping["position_limit"]),
            lot_size=int(mapping.get("lot_size", 100)),
        )


@dataclass(frozen=True)
class PortfolioState:
    cash: Decimal
    shares: int
    average_cost: Decimal
    realized_pnl: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if self.cash < 0:
            raise ExecutionValidationError("invalid-cash", ["cash cannot be negative"])
        if self.shares < 0:
            raise ExecutionValidationError("invalid-shares", ["shares cannot be negative"])
        if self.average_cost < 0:
            raise ExecutionValidationError("invalid-average-cost", ["average_cost cannot be negative"])

    def equity(self, mark_price: Decimal) -> Decimal:
        return self.cash + (Decimal(self.shares) * mark_price)

    def position_value(self, mark_price: Decimal) -> Decimal:
        return Decimal(self.shares) * mark_price

    def to_record(self) -> dict[str, Any]:
        return {
            "cash": _decimal_str(self.cash),
            "shares": self.shares,
            "average_cost": _decimal_str(self.average_cost),
            "realized_pnl": _decimal_str(self.realized_pnl),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "PortfolioState":
        mapping = _require_mapping(data, "invalid-portfolio-state")
        return cls(
            cash=_decimal(mapping["cash"]),
            shares=int(mapping.get("shares", 0)),
            average_cost=_decimal(mapping.get("average_cost", 0)),
            realized_pnl=_decimal(mapping.get("realized_pnl", 0)),
        )


@dataclass(frozen=True)
class PriceBar:
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "PriceBar":
        mapping = _require_mapping(data, "invalid-price-bar")
        return cls(
            date=_require_date(mapping["date"], "invalid-price-bar-date"),
            open=_decimal(mapping["open"]),
            high=_decimal(mapping["high"]),
            low=_decimal(mapping["low"]),
            close=_decimal(mapping["close"]),
            volume=int(mapping["volume"]),
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "open": _decimal_str(self.open),
            "high": _decimal_str(self.high),
            "low": _decimal_str(self.low),
            "close": _decimal_str(self.close),
            "volume": self.volume,
        }


@dataclass(frozen=True)
class ValidatedDecisionRecord:
    run_id: str
    symbol: str
    market: str
    cadence: str
    asof_date: date
    prompt_version: str
    schema_version: str
    model_label: str
    input_summary: Mapping[str, Any]
    decision_action: str
    execution_action: str
    confidence: Decimal | None
    signal_tags: tuple[str, ...]
    validation_status: str
    validation_issues: tuple[str, ...] = ()
    validated_at: str | None = None

    def to_record(self) -> dict[str, Any]:
        decision: dict[str, Any] = {"action": self.decision_action}
        if self.confidence is not None:
            decision["confidence"] = _decimal_str(self.confidence)
        if self.signal_tags:
            decision["signal_tags"] = list(self.signal_tags)
        validation_record = {
            "status": self.validation_status,
            "issues": list(self.validation_issues),
        }
        if self.validated_at is not None:
            validation_record["validated_at"] = self.validated_at
        return {
            "run_id": self.run_id,
            "symbol": self.symbol,
            "market": self.market,
            "cadence": self.cadence,
            "asof_date": self.asof_date.isoformat(),
            "prompt_version": self.prompt_version,
            "schema_version": self.schema_version,
            "model_label": self.model_label,
            "input_summary": dict(self.input_summary),
            "decision": decision,
            "validation": validation_record,
        }


@dataclass(frozen=True)
class BlockedExecutionRecord:
    reason: str
    issues: tuple[str, ...]
    decision_action: str | None = None
    execution_action: str | None = None
    execution_date: date | None = None
    details: Mapping[str, Any] = field(default_factory=dict)

    def to_record(self) -> dict[str, Any]:
        record = {
            "reason": self.reason,
            "issues": list(self.issues),
            "decision_action": self.decision_action,
            "execution_action": self.execution_action,
            "details": dict(self.details),
        }
        if self.execution_date is not None:
            record["execution_date"] = self.execution_date.isoformat()
        return record


@dataclass(frozen=True)
class FillRecord:
    run_id: str
    symbol: str
    asof_date: date
    execution_date: date
    decision_action: str
    execution_action: str
    quantity: int
    execution_price: Decimal
    gross_value: Decimal
    commission: Decimal
    slippage_cost: Decimal
    cash_delta: Decimal

    def to_record(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "symbol": self.symbol,
            "asof_date": self.asof_date.isoformat(),
            "execution_date": self.execution_date.isoformat(),
            "decision_action": self.decision_action,
            "execution_action": self.execution_action,
            "quantity": self.quantity,
            "execution_price": _decimal_str(self.execution_price),
            "gross_value": _decimal_str(self.gross_value),
            "commission": _decimal_str(self.commission),
            "slippage_cost": _decimal_str(self.slippage_cost),
            "cash_delta": _decimal_str(self.cash_delta),
        }


@dataclass(frozen=True)
class LedgerRow:
    run_id: str
    symbol: str
    asof_date: date
    execution_date: date
    decision_action: str
    execution_action: str
    quantity: int
    cash: Decimal
    shares: int
    average_cost: Decimal
    position_value: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    nav: Decimal
    mark_price: Decimal

    def to_record(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "symbol": self.symbol,
            "asof_date": self.asof_date.isoformat(),
            "execution_date": self.execution_date.isoformat(),
            "decision_action": self.decision_action,
            "execution_action": self.execution_action,
            "quantity": self.quantity,
            "cash": _decimal_str(self.cash),
            "shares": self.shares,
            "average_cost": _decimal_str(self.average_cost),
            "position_value": _decimal_str(self.position_value),
            "realized_pnl": _decimal_str(self.realized_pnl),
            "unrealized_pnl": _decimal_str(self.unrealized_pnl),
            "nav": _decimal_str(self.nav),
            "mark_price": _decimal_str(self.mark_price),
        }


@dataclass(frozen=True)
class ExecutionInput:
    run_id: str
    symbol: str
    market: str
    cadence: str
    asof_date: date
    snapshot: Mapping[str, Any]
    decision_record: Mapping[str, Any]
    config: ExecutionConfig
    starting_state: PortfolioState


@dataclass(frozen=True)
class ExecutionResult:
    run_id: str
    symbol: str
    market: str
    cadence: str
    asof_date: date
    status: str
    execution_date: date | None
    config: ExecutionConfig
    starting_state: PortfolioState
    ending_state: PortfolioState
    validated_decision: ValidatedDecisionRecord | None
    fills: tuple[FillRecord, ...]
    ledger_rows: tuple[LedgerRow, ...]
    nav_curve: tuple[LedgerRow, ...]
    blocked_record: BlockedExecutionRecord | None = None

    def to_record(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "symbol": self.symbol,
            "market": self.market,
            "cadence": self.cadence,
            "asof_date": self.asof_date.isoformat(),
            "status": self.status,
            "execution_date": self.execution_date.isoformat() if self.execution_date else None,
            "config": self.config.to_record(),
            "starting_state": self.starting_state.to_record(),
            "ending_state": self.ending_state.to_record(),
            "validated_decision": self.validated_decision.to_record() if self.validated_decision else None,
            "fills": [fill.to_record() for fill in self.fills],
            "ledger_rows": [row.to_record() for row in self.ledger_rows],
            "nav_curve": [row.to_record() for row in self.nav_curve],
            "blocked_record": self.blocked_record.to_record() if self.blocked_record else None,
        }


def validate_decision_record(record: Mapping[str, Any]) -> ValidatedDecisionRecord:
    mapping = _require_mapping(record, "invalid-decision-record")
    required = {
        "run_id",
        "symbol",
        "market",
        "cadence",
        "asof_date",
        "prompt_version",
        "schema_version",
        "model_label",
        "input_summary",
        "decision",
        "validation",
    }
    missing = sorted(required - set(mapping))
    if missing:
        raise ExecutionValidationError("missing-decision-fields", [f"missing fields: {', '.join(missing)}"])
    decision = _require_mapping(mapping["decision"], "invalid-decision-payload")
    if set(decision) - {"action", "confidence", "signal_tags"}:
        extras = sorted(set(decision) - {"action", "confidence", "signal_tags"})
        raise ExecutionValidationError("unexpected-decision-fields", [f"unexpected fields: {', '.join(extras)}"])
    action = decision.get("action")
    if action not in ALLOWED_DECISION_ACTIONS:
        raise ExecutionValidationError("unsupported-decision-action", [f"action must be one of {sorted(ALLOWED_DECISION_ACTIONS)}"])
    validation = _require_mapping(mapping["validation"], "invalid-validation-payload")
    if validation.get("status") != "passed":
        issues = validation.get("issues") or ["validation.status must be passed"]
        raise ExecutionValidationError("decision-not-passed", [str(issue) for issue in issues])
    confidence_value = decision.get("confidence")
    confidence = _decimal(confidence_value) if confidence_value is not None else None
    if confidence is not None and not (Decimal("0") <= confidence <= Decimal("1")):
        raise ExecutionValidationError("confidence-out-of-range", ["confidence must be between 0 and 1"])
    signal_tags = tuple(decision.get("signal_tags") or ())
    if len(signal_tags) != len(set(signal_tags)):
        raise ExecutionValidationError("duplicate-signal-tags", ["signal_tags must be unique"])
    asof_date = _require_date(mapping["asof_date"], "invalid-decision-asof-date")
    validation_issues = tuple(str(issue) for issue in (validation.get("issues") or ()))
    return ValidatedDecisionRecord(
        run_id=str(mapping["run_id"]),
        symbol=str(mapping["symbol"]),
        market=str(mapping["market"]),
        cadence=str(mapping["cadence"]),
        asof_date=asof_date,
        prompt_version=str(mapping["prompt_version"]),
        schema_version=str(mapping["schema_version"]),
        model_label=str(mapping["model_label"]),
        input_summary=_require_mapping(mapping["input_summary"], "invalid-input-summary"),
        decision_action=str(action),
        execution_action=EXECUTION_ACTION_ALIASES[str(action)],
        confidence=confidence,
        signal_tags=signal_tags,
        validation_status=str(validation.get("status")),
        validation_issues=validation_issues,
        validated_at=str(validation["validated_at"]) if validation.get("validated_at") is not None else None,
    )
