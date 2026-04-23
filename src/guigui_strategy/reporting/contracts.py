from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping


class ReportValidationError(ValueError):
    def __init__(self, reason: str, issues: list[str] | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.issues = issues or [reason]


def _require_mapping(value: Any, reason: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ReportValidationError(reason, [f"expected mapping, got {type(value).__name__}"])
    return value


def _decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ReportValidationError("invalid-decimal", [f"unable to parse decimal: {value!r}"]) from exc


def _decimal_str(value: Decimal) -> str:
    return format(value.normalize() if value == value.to_integral() else value, "f")


@dataclass(frozen=True)
class ReportConfig:
    annualization_factor: int = 252
    sharpe_risk_free_rate: Decimal = Decimal("0")
    report_sections: tuple[str, ...] = ("Summary", "Metrics", "Key Trades", "Artifact Index", "Notes")

    def __post_init__(self) -> None:
        if self.annualization_factor <= 0:
            raise ReportValidationError("invalid-annualization-factor", ["annualization_factor must be positive"])
        if len(self.report_sections) != 5:
            raise ReportValidationError("invalid-report-sections", ["report_sections must contain exactly five entries"])

    def to_record(self) -> dict[str, Any]:
        return {
            "annualization_factor": self.annualization_factor,
            "sharpe_risk_free_rate": _decimal_str(self.sharpe_risk_free_rate),
            "report_sections": list(self.report_sections),
        }


@dataclass(frozen=True)
class ReportInput:
    run_id: str
    symbol: str
    market: str
    cadence: str
    asof_date: date
    artifact_root: Path
    manifest: Mapping[str, Any]
    status: Mapping[str, Any]
    config: ReportConfig

    def to_record(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "symbol": self.symbol,
            "market": self.market,
            "cadence": self.cadence,
            "asof_date": self.asof_date.isoformat(),
            "artifact_root": str(self.artifact_root),
            "manifest": dict(self.manifest),
            "status": dict(self.status),
            "config": self.config.to_record(),
        }


@dataclass(frozen=True)
class ReportTrade:
    execution_date: date
    decision_action: str
    execution_action: str
    quantity: int
    execution_price: Decimal
    cash_delta: Decimal
    commission: Decimal
    slippage_cost: Decimal
    run_id: str
    symbol: str

    def to_record(self) -> dict[str, Any]:
        return {
            "execution_date": self.execution_date.isoformat(),
            "decision_action": self.decision_action,
            "execution_action": self.execution_action,
            "quantity": self.quantity,
            "execution_price": _decimal_str(self.execution_price),
            "cash_delta": _decimal_str(self.cash_delta),
            "commission": _decimal_str(self.commission),
            "slippage_cost": _decimal_str(self.slippage_cost),
            "run_id": self.run_id,
            "symbol": self.symbol,
        }


@dataclass(frozen=True)
class ReportMetrics:
    periods: int
    initial_nav: Decimal
    final_nav: Decimal
    total_return: Decimal
    max_drawdown: Decimal
    sharpe: Decimal
    annualized_return: Decimal
    volatility: Decimal

    def to_record(self) -> dict[str, Any]:
        return {
            "periods": self.periods,
            "initial_nav": _decimal_str(self.initial_nav),
            "final_nav": _decimal_str(self.final_nav),
            "total_return": _decimal_str(self.total_return),
            "max_drawdown": _decimal_str(self.max_drawdown),
            "sharpe": _decimal_str(self.sharpe),
            "annualized_return": _decimal_str(self.annualized_return),
            "volatility": _decimal_str(self.volatility),
        }


@dataclass(frozen=True)
class ReportIndex:
    report_md_path: str
    report_index_path: str
    manifest_path: str
    status_path: str
    snapshot_paths: tuple[str, ...]
    decision_paths: tuple[str, ...]
    execution_paths: tuple[str, ...]
    reports_paths: tuple[str, ...]

    def to_record(self) -> dict[str, Any]:
        return {
            "report_md_path": self.report_md_path,
            "report_index_path": self.report_index_path,
            "manifest_path": self.manifest_path,
            "status_path": self.status_path,
            "snapshot_paths": list(self.snapshot_paths),
            "decision_paths": list(self.decision_paths),
            "execution_paths": list(self.execution_paths),
            "reports_paths": list(self.reports_paths),
        }


@dataclass(frozen=True)
class ReportResult:
    run_id: str
    symbol: str
    market: str
    cadence: str
    asof_date: date
    report_markdown: str
    report_index: ReportIndex
    metrics: ReportMetrics
    key_trades: tuple[ReportTrade, ...]
    summary_lines: tuple[str, ...] = field(default_factory=tuple)

    def to_record(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "symbol": self.symbol,
            "market": self.market,
            "cadence": self.cadence,
            "asof_date": self.asof_date.isoformat(),
            "report_markdown": self.report_markdown,
            "report_index": self.report_index.to_record(),
            "metrics": self.metrics.to_record(),
            "key_trades": [trade.to_record() for trade in self.key_trades],
            "summary_lines": list(self.summary_lines),
        }

