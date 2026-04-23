from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .contracts import ExecutionConfig, ExecutionInput, PortfolioState
from .engine import execute_execution
from .persistence import persist_execution_result


def run_execution_node(
    *,
    artifact_root: Path,
    run_id: str,
    symbol: str,
    market: str,
    cadence: str,
    asof_date,
    snapshot: Mapping[str, Any],
    decision_record: Mapping[str, Any],
    config: ExecutionConfig,
    starting_state: PortfolioState,
):
    execution_input = ExecutionInput(
        run_id=run_id,
        symbol=symbol,
        market=market,
        cadence=cadence,
        asof_date=asof_date,
        snapshot=snapshot,
        decision_record=decision_record,
        config=config,
        starting_state=starting_state,
    )
    result = execute_execution(execution_input)
    persist_execution_result(Path(artifact_root), result)
    return result

