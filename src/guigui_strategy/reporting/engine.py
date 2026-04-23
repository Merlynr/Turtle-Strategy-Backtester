from __future__ import annotations

import json
from dataclasses import replace
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable

from .contracts import (
    ReportConfig,
    ReportIndex,
    ReportInput,
    ReportMetrics,
    ReportResult,
    ReportTrade,
    ReportValidationError,
)


def _decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ReportValidationError("invalid-decimal", [f"unable to parse decimal: {value!r}"]) from exc


def _decimal_str(value: Decimal) -> str:
    return format(value.normalize() if value == value.to_integral() else value, "f")


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.0000000000000001"))


def _require_file(path: Path, reason: str) -> Path:
    if not path.exists():
        raise ReportValidationError(reason, [f"missing file: {path}"])
    return path


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _parse_nav_rows(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        raise ReportValidationError("invalid-nav-data", ["execution/nav.json must contain a non-empty list"])
    rows: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ReportValidationError("invalid-nav-row", ["nav rows must be objects"])
        if "nav" not in item:
            raise ReportValidationError("missing-nav-field", ["nav row missing nav field"])
        rows.append(item)
    return rows


def _as_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise ReportValidationError("invalid-date", [f"expected ISO date string, got {type(value).__name__}"])


def _compute_metrics(nav_rows: list[dict[str, Any]], annualization_factor: int, rf_rate: Decimal) -> ReportMetrics:
    nav_values = [_decimal(row["nav"]) for row in nav_rows]
    initial_nav = nav_values[0]
    final_nav = nav_values[-1]
    total_return = _quantize((final_nav / initial_nav) - Decimal("1"))

    peak = nav_values[0]
    max_drawdown = Decimal("0")
    for value in nav_values:
        if value > peak:
            peak = value
        drawdown = (value / peak) - Decimal("1")
        if drawdown < max_drawdown:
            max_drawdown = drawdown

    period_returns: list[Decimal] = []
    for prev, curr in zip(nav_values, nav_values[1:]):
        if prev == 0:
            continue
        period_returns.append((curr / prev) - Decimal("1"))

    if period_returns:
        avg_return = mean([float(value) for value in period_returns])
        volatility = pstdev([float(value) for value in period_returns]) if len(period_returns) > 1 else 0.0
        excess = [float(value - rf_rate) for value in period_returns]
        excess_mean = mean(excess)
        sharpe = Decimal("0")
        if volatility != 0:
            sharpe = Decimal(str((excess_mean / volatility) * (annualization_factor ** 0.5)))
        annualized_return = Decimal(str((1 + avg_return) ** annualization_factor - 1))
        volatility_dec = Decimal(str(volatility))
    else:
        sharpe = Decimal("0")
        annualized_return = Decimal("0")
        volatility_dec = Decimal("0")

    return ReportMetrics(
        periods=max(len(nav_values) - 1, 0),
        initial_nav=initial_nav,
        final_nav=final_nav,
        total_return=total_return,
        max_drawdown=_quantize(max_drawdown),
        sharpe=_quantize(sharpe),
        annualized_return=_quantize(annualized_return),
        volatility=_quantize(volatility_dec),
    )


def _build_key_trades(fills: list[dict[str, Any]]) -> tuple[ReportTrade, ...]:
    trades: list[ReportTrade] = []
    for fill in fills:
        if not isinstance(fill, dict):
            raise ReportValidationError("invalid-fill-record", ["fill records must be objects"])
        for field in ("execution_date", "decision_action", "execution_action", "quantity", "execution_price", "cash_delta", "commission", "slippage_cost", "run_id", "symbol"):
            if field not in fill:
                raise ReportValidationError("missing-fill-field", [f"fill record missing {field}"])
        trades.append(
            ReportTrade(
                execution_date=_as_date(fill["execution_date"]),
                decision_action=str(fill["decision_action"]),
                execution_action=str(fill["execution_action"]),
                quantity=int(fill["quantity"]),
                execution_price=_decimal(fill["execution_price"]),
                cash_delta=_decimal(fill["cash_delta"]),
                commission=_decimal(fill["commission"]),
                slippage_cost=_decimal(fill["slippage_cost"]),
                run_id=str(fill["run_id"]),
                symbol=str(fill["symbol"]),
            )
        )
    trades.sort(key=lambda trade: (trade.execution_date, trade.decision_action, trade.quantity, trade.execution_price))
    return tuple(trades)


def _artifact_links(artifact_root: Path) -> ReportIndex:
    return ReportIndex(
        report_md_path=str(artifact_root / "report.md"),
        report_index_path=str(artifact_root / "reports" / "report-index.json"),
        manifest_path=str(artifact_root / "manifest.json"),
        status_path=str(artifact_root / "status.json"),
        snapshot_paths=(str(artifact_root / "snapshots"),),
        decision_paths=(str(artifact_root / "decisions"),),
        execution_paths=(str(artifact_root / "execution"),),
        reports_paths=(str(artifact_root / "reports"),),
    )


def _render_report(input_: ReportInput, metrics: ReportMetrics, key_trades: tuple[ReportTrade, ...], report_index: ReportIndex) -> str:
    summary_lines = [
        f"# Run Report: {input_.run_id}",
        "",
        "## Summary",
        f"- Symbol: `{input_.symbol}`",
        f"- Market: `{input_.market}`",
        f"- Cadence: `{input_.cadence}`",
        f"- As of: `{input_.asof_date.isoformat()}`",
        f"- Final NAV: `{_decimal_str(metrics.final_nav)}`",
        f"- Total Return: `{_decimal_str(metrics.total_return)}`",
        f"- Max Drawdown: `{_decimal_str(metrics.max_drawdown)}`",
        f"- Sharpe: `{_decimal_str(metrics.sharpe)}`",
        "",
        "## Metrics",
        "| Metric | Value |",
        "|---|---:|",
        f"| Periods | {metrics.periods} |",
        f"| Initial NAV | `{_decimal_str(metrics.initial_nav)}` |",
        f"| Final NAV | `{_decimal_str(metrics.final_nav)}` |",
        f"| Total Return | `{_decimal_str(metrics.total_return)}` |",
        f"| Annualized Return | `{_decimal_str(metrics.annualized_return)}` |",
        f"| Max Drawdown | `{_decimal_str(metrics.max_drawdown)}` |",
        f"| Sharpe | `{_decimal_str(metrics.sharpe)}` |",
        f"| Volatility | `{_decimal_str(metrics.volatility)}` |",
        "",
        "## Key Trades",
    ]
    if key_trades:
        summary_lines.extend([
            "| Execution Date | Decision | Execution | Qty | Price | Cash Delta |",
            "|---|---|---|---:|---:|---:|",
        ])
        for trade in key_trades:
            summary_lines.append(
                f"| {trade.execution_date.isoformat()} | `{trade.decision_action}` | `{trade.execution_action}` | "
                f"{trade.quantity} | `{_decimal_str(trade.execution_price)}` | `{_decimal_str(trade.cash_delta)}` |"
            )
    else:
        summary_lines.append("No executable trades were recorded for this run.")

    summary_lines.extend([
        "",
        "## Artifact Index",
        f"- [manifest.json]({report_index.manifest_path})",
        f"- [status.json]({report_index.status_path})",
        f"- [snapshots/]({report_index.snapshot_paths[0]})",
        f"- [decisions/]({report_index.decision_paths[0]})",
        f"- [execution/]({report_index.execution_paths[0]})",
        f"- [reports/]({report_index.reports_paths[0]})",
        "",
        "## Notes",
        "- Metrics are derived only from execution artifacts inside this run container.",
        "- The report is deterministic for identical input artifacts.",
        "- Report regeneration does not mutate execution-side state.",
    ])
    return "\n".join(summary_lines) + "\n"


def generate_report(input_: ReportInput) -> ReportResult:
    artifact_root = Path(input_.artifact_root)
    manifest_path = _require_file(artifact_root / "manifest.json", "missing-manifest")
    status_path = _require_file(artifact_root / "status.json", "missing-status")
    nav_path = _require_file(artifact_root / "execution" / "nav.json", "missing-nav")
    fills_path = _require_file(artifact_root / "execution" / "fills.jsonl", "missing-fills")
    ledger_path = _require_file(artifact_root / "execution" / "ledger.jsonl", "missing-ledger")

    manifest = _read_json(manifest_path)
    status = _read_json(status_path)
    nav_rows = _parse_nav_rows(_read_json(nav_path))
    fills = _read_jsonl(fills_path)
    _ = _read_jsonl(ledger_path)

    if str(manifest.get("run_id")) != input_.run_id:
        raise ReportValidationError("run-id-mismatch", ["manifest run_id does not match report input"])
    if str(status.get("run_id")) != input_.run_id:
        raise ReportValidationError("status-run-id-mismatch", ["status run_id does not match report input"])

    metrics = _compute_metrics(nav_rows, input_.config.annualization_factor, input_.config.sharpe_risk_free_rate)
    key_trades = _build_key_trades(fills)
    report_index = _artifact_links(artifact_root)
    report_markdown = _render_report(input_, metrics, key_trades, report_index)

    return ReportResult(
        run_id=input_.run_id,
        symbol=input_.symbol,
        market=input_.market,
        cadence=input_.cadence,
        asof_date=input_.asof_date,
        report_markdown=report_markdown,
        report_index=report_index,
        metrics=metrics,
        key_trades=key_trades,
        summary_lines=tuple(report_markdown.splitlines()),
    )
