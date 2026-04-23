from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Mapping

from .contracts import ReportConfig, ReportInput
from .engine import generate_report
from .persistence import persist_report_result


def run_reporting_node(
    *,
    artifact_root: Path,
    run_id: str,
    symbol: str,
    market: str,
    cadence: str,
    asof_date: date,
    manifest: Mapping[str, Any],
    status: Mapping[str, Any],
    config: ReportConfig | None = None,
):
    report_input = ReportInput(
        run_id=run_id,
        symbol=symbol,
        market=market,
        cadence=cadence,
        asof_date=asof_date,
        artifact_root=Path(artifact_root),
        manifest=manifest,
        status=status,
        config=config or ReportConfig(),
    )
    result = generate_report(report_input)
    persist_report_result(Path(artifact_root), result)
    return result

