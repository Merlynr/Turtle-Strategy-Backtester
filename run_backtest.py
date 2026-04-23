from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from guigui_strategy.execution import ExecutionConfig, PortfolioState, run_execution_node
from guigui_strategy.reporting import ReportConfig, run_reporting_node
from guigui_strategy.validation import ValidationConfig, ValidationInput, run_validation


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def parse_decimal(value: str) -> Decimal:
    return Decimal(value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a manual Turtle Strategy backtest from an existing run directory.",
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="Run identifier, e.g. run-20260423-001_ma-cross-000001sz-qtr",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=None,
        help="Run artifact directory. Defaults to runs/<run-id>.",
    )
    parser.add_argument(
        "--asof-date",
        required=True,
        help="As-of date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--initial-capital",
        type=parse_decimal,
        default=Decimal("1000000"),
        help="Initial capital for execution.",
    )
    parser.add_argument(
        "--commission-rate",
        type=parse_decimal,
        default=Decimal("0.0003"),
        help="Commission rate as a decimal fraction.",
    )
    parser.add_argument(
        "--slippage-bps",
        type=parse_decimal,
        default=Decimal("5"),
        help="Slippage in basis points.",
    )
    parser.add_argument(
        "--position-limit",
        type=parse_decimal,
        default=Decimal("1"),
        help="Maximum long exposure as a fraction of initial capital.",
    )
    parser.add_argument(
        "--lot-size",
        type=int,
        default=100,
        help="Trading lot size, usually 100 for A-share daily execution.",
    )
    parser.add_argument(
        "--check-golden-baseline",
        action="store_true",
        help="Enable golden-run validation.",
    )
    parser.add_argument(
        "--golden-baseline-root",
        type=Path,
        default=None,
        help="Golden baseline run directory used when --check-golden-baseline is enabled.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Logging level.",
    )
    return parser.parse_args()


def refresh_json(path: Path) -> dict[str, Any]:
    return load_json(path)


def main() -> int:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(asctime)s - %(levelname)s - %(message)s")

    artifact_root = args.artifact_root or (PROJECT_ROOT / "runs" / args.run_id)
    asof_date = date.fromisoformat(args.asof_date)

    manifest_path = artifact_root / "manifest.json"
    status_path = artifact_root / "status.json"
    snapshot_path = artifact_root / "snapshots" / f"snapshot_{asof_date.isoformat()}.json"
    decision_path = artifact_root / "decisions" / f"decision_{asof_date.isoformat()}.json"

    for path in (manifest_path, status_path, snapshot_path, decision_path):
        if not path.exists():
            logging.error("Missing required file: %s", path)
            return 1

    manifest = load_json(manifest_path)
    status = load_json(status_path)
    snapshot = load_json(snapshot_path)
    decision_record = load_json(decision_path)

    symbol = str(snapshot["symbol"])
    market = str(snapshot["market"])
    cadence = str(snapshot["cadence"])

    logging.info("Running execution node for %s", args.run_id)
    execution_result = run_execution_node(
        artifact_root=artifact_root,
        run_id=args.run_id,
        symbol=symbol,
        market=market,
        cadence=cadence,
        asof_date=asof_date,
        snapshot=snapshot,
        decision_record=decision_record,
        config=ExecutionConfig(
            initial_capital=args.initial_capital,
            commission_rate=args.commission_rate,
            slippage_bps=args.slippage_bps,
            position_limit=args.position_limit,
            lot_size=args.lot_size,
        ),
        starting_state=PortfolioState(
            cash=args.initial_capital,
            shares=0,
            average_cost=Decimal("0"),
            realized_pnl=Decimal("0"),
        ),
    )
    logging.info("Execution status: %s", execution_result.status)

    status = refresh_json(status_path)

    logging.info("Running reporting node for %s", args.run_id)
    report_result = run_reporting_node(
        artifact_root=artifact_root,
        run_id=args.run_id,
        symbol=symbol,
        market=market,
        cadence=cadence,
        asof_date=asof_date,
        manifest=manifest,
        status=status,
        config=ReportConfig(),
    )
    logging.info("Report status: %s", getattr(report_result, "status", "completed"))

    status = refresh_json(status_path)

    validation_config = ValidationConfig(
        check_golden_baseline=args.check_golden_baseline,
        golden_baseline_root=args.golden_baseline_root,
    )
    logging.info("Running validation node for %s", args.run_id)
    validation_result = run_validation(
        ValidationInput(
            run_id=args.run_id,
            symbol=symbol,
            market=market,
            cadence=cadence,
            asof_date=asof_date,
            artifact_root=artifact_root,
            manifest=manifest,
            status=status,
            config=validation_config,
        )
    )
    logging.info("Validation status: %s", validation_result.status)
    logging.info("Done. Report written to %s", artifact_root / "report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
