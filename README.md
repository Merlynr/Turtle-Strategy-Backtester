# Turtle-Strategy-Backtester

龟龟策略量化回测系统。

这是一个 `skill-first`、`contract-first` 的单标的回测项目，核心目标是：

- 只使用历史时点可见的数据
- 把快照、AI 决策、执行、报告、验证全部落盘
- 保证同样输入能复现同样结果

## 项目描述

当前 v1.0 已完成并归档，覆盖完整闭环：

1. `backtest-orchestrator` 作为唯一总控入口
2. 手工或上游系统提供点时点快照
3. AI 节点输出结构化 JSON 决策
4. 执行节点按下一交易日开盘撮合
5. 报告节点生成可追溯复盘报告
6. 验证节点检查 run container 和黄金基线

项目不是“自由文本下单系统”，而是“契约驱动的回测工作流”。

## 当前能力边界

- 单标的 v1 闭环
- 日线/季度或月度等低频回测
- 手工快照输入
- schema 约束的 AI 决策记录
- 下一交易日开盘执行
- 报告与验证分离

不包含：

- 实盘交易
- 多标的组合回测
- 分钟级或 tick 级回测
- Web 仪表盘

## 安装

当前仓库没有打包成 `pip` 发布包，也没有 `pyproject.toml`。
最简单的方式是在仓库根目录直接运行，或把 `src/` 加入 `PYTHONPATH`。

### 1. 准备 Python

建议使用 Python 3.12 或更高版本。

### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. 让本地代码可导入

```bash
export PYTHONPATH="$PWD/src:$PYTHONPATH"
```

### 4. 安装测试依赖

项目代码本身只依赖标准库，测试需要 `pytest`。

```bash
python -m pip install pytest
```

## 运行前准备

你需要先准备一个 run 目录，例如：

```text
runs/run-20260423-001_ma-cross-000001sz-qtr/
├── manifest.json
├── status.json
├── report.md
├── snapshots/
│   ├── prices.csv
│   └── snapshot_2026-04-23.json
├── decisions/
│   └── decision_2026-04-23.json
├── execution/
├── reports/
└── meta/
    ├── manual-inputs/
    ├── snapshot-validation.json
    └── validation.json
```

### 关键文件说明

- `manifest.json`：运行身份，描述这次回测是什么
- `status.json`：运行状态，描述当前走到哪一节点
- `snapshots/prices.csv`：原始 K 线数据
- `snapshots/snapshot_YYYY-MM-DD.json`：规范化点时点快照
- `decisions/decision_YYYY-MM-DD.json`：AI 决策记录
- `execution/`：成交、账本、净值
- `report.md`：最终报告
- `reports/`：报告派生索引
- `meta/`：验证、审计和原始输入

## 两份最小样板

这里给出可以直接照着写的最小 JSON 样板。

### `manifest.json`

参考文件：

- [run-manifest-example.json](/home/projects/Turtle-Strategy-Backtester/docs/examples/run-manifest-example.json)

示例内容：

```json
{
  "run_id": "run-20260423-001_ma-cross-000001sz-qtr",
  "strategy": "ma-cross",
  "symbol": "000001.SZ",
  "market": "CN-A",
  "start": "2020-01-01",
  "end": "2023-12-31",
  "cadence": "quarterly",
  "entry_skill": "backtest-orchestrator",
  "created_at": "2026-04-23T11:35:00+08:00",
  "artifact_root": "runs/run-20260423-001_ma-cross-000001sz-qtr"
}
```

### `status.json`

参考文件：

- [run-status-example.json](/home/projects/Turtle-Strategy-Backtester/docs/examples/run-status-example.json)

示例内容：

```json
{
  "run_id": "run-20260423-001_ma-cross-000001sz-qtr",
  "phase": "01-run-contract",
  "current_node": "orchestrator",
  "state": "ready",
  "last_completed_node": null,
  "resume_from": "data-node",
  "updated_at": "2026-04-23T11:35:00+08:00",
  "error_summary": null
}
```

### 可直接使用的样例文件

下面这组文件可以直接作为手工回测的输入样板：

- [prices.csv](/home/projects/Turtle-Strategy-Backtester/docs/examples/manual-run/prices.csv)
- [snapshot_2026-04-23.json](/home/projects/Turtle-Strategy-Backtester/docs/examples/manual-run/snapshot_2026-04-23.json)
- [decision_2026-04-23.json](/home/projects/Turtle-Strategy-Backtester/docs/examples/manual-run/decision_2026-04-23.json)

如果你想直接复制一个完整目录模板，可以用：

- [完整 run 模板](/home/projects/Turtle-Strategy-Backtester/docs/examples/manual-run/run-20260423-001_ma-cross-000001sz-qtr/)

## 使用方法

### 方法 1：按节点顺序手工编排

当前仓库提供的是节点函数，而不是完整 CLI。

可用节点函数：

- `run_execution_node(...)`
- `run_reporting_node(...)`
- `run_validation(...)`

推荐流程：

1. 准备 `manifest.json` 和 `status.json`
2. 准备 `snapshots/prices.csv`
3. 准备 `snapshots/snapshot_YYYY-MM-DD.json`
4. 准备 `decisions/decision_YYYY-MM-DD.json`
5. 调用 execution 节点
6. 重新读取最新 `status.json`
7. 调用 reporting 节点
8. 重新读取最新 `status.json`
9. 调用 validation 节点

### 方法 2：直接跑单元测试验证契约

```bash
pytest -q tests/execution tests/reporting tests/validation
```

这会验证：

- 执行契约
- 报告契约
- 验证契约

## 本地编排脚本示例

下面是一个与当前源码签名一致的最小示例。

```python
import json
import logging
from datetime import date
from decimal import Decimal
from pathlib import Path

from guigui_strategy.execution import ExecutionConfig, PortfolioState, run_execution_node
from guigui_strategy.reporting import ReportConfig, run_reporting_node
from guigui_strategy.validation import ValidationConfig, ValidationInput, run_validation


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    run_id = "run-20260423-001_ma-cross-000001sz-qtr"
    artifact_root = Path("runs") / run_id
    asof_date = date(2026, 4, 23)

    manifest = load_json(artifact_root / "manifest.json")
    status = load_json(artifact_root / "status.json")
    snapshot = load_json(artifact_root / "snapshots" / f"snapshot_{asof_date.isoformat()}.json")
    decision_record = load_json(artifact_root / "decisions" / f"decision_{asof_date.isoformat()}.json")

    logging.info("Running execution node...")
    run_execution_node(
        artifact_root=artifact_root,
        run_id=run_id,
        symbol=snapshot["symbol"],
        market=snapshot["market"],
        cadence=snapshot["cadence"],
        asof_date=asof_date,
        snapshot=snapshot,
        decision_record=decision_record,
        config=ExecutionConfig(
            initial_capital=Decimal("1000000"),
            commission_rate=Decimal("0.0003"),
            slippage_bps=Decimal("5"),
            position_limit=Decimal("1"),
            lot_size=100,
        ),
        starting_state=PortfolioState(
            cash=Decimal("1000000"),
            shares=0,
            average_cost=Decimal("0"),
            realized_pnl=Decimal("0"),
        ),
    )

    status = load_json(artifact_root / "status.json")

    logging.info("Running reporting node...")
    run_reporting_node(
        artifact_root=artifact_root,
        run_id=run_id,
        symbol=snapshot["symbol"],
        market=snapshot["market"],
        cadence=snapshot["cadence"],
        asof_date=asof_date,
        manifest=manifest,
        status=status,
        config=ReportConfig(),
    )

    status = load_json(artifact_root / "status.json")

    logging.info("Running validation node...")
    run_validation(
        ValidationInput(
            run_id=run_id,
            symbol=snapshot["symbol"],
            market=snapshot["market"],
            cadence=snapshot["cadence"],
            asof_date=asof_date,
            artifact_root=artifact_root,
            manifest=manifest,
            status=status,
            config=ValidationConfig(
                check_golden_baseline=False,
            ),
        )
    )

    logging.info("Done.")


if __name__ == "__main__":
    main()
```

### 直接使用脚本

仓库根目录已经提供了 [run_backtest.py](/home/projects/Turtle-Strategy-Backtester/run_backtest.py)。

最小运行方式：

```bash
export PYTHONPATH="$PWD/src:$PYTHONPATH"
python run_backtest.py \
  --run-id run-20260423-001_ma-cross-000001sz-qtr \
  --asof-date 2026-04-23
```

启用黄金基线回归：

```bash
python run_backtest.py \
  --run-id run-20260423-001_ma-cross-000001sz-qtr \
  --asof-date 2026-04-23 \
  --check-golden-baseline \
  --golden-baseline-root tests/validation/fixtures/golden-run
```

默认情况下，脚本从 `runs/<run-id>/` 读取文件；你也可以通过 `--artifact-root` 指定其他目录。

### 黄金基线回归

如果你要做回归验证，把 validation 配置改成：

```python
ValidationConfig(
    check_golden_baseline=True,
    golden_baseline_root=Path("tests/validation/fixtures/golden-run"),
)
```

## 使用案例

### 案例 1：手工输入 000001.SZ 的季度回测

1. 准备 [prices.csv](/home/projects/Turtle-Strategy-Backtester/docs/examples/manual-run/prices.csv)
2. 复制 [snapshot_2026-04-23.json](/home/projects/Turtle-Strategy-Backtester/docs/examples/manual-run/snapshot_2026-04-23.json) 到 run 目录并按你的目录修正 `prices_csv_path`
3. 复制 [decision_2026-04-23.json](/home/projects/Turtle-Strategy-Backtester/docs/examples/manual-run/decision_2026-04-23.json) 到 `decisions/`
4. 运行 execution
5. 生成 report
6. 运行 validation

### 案例 2：复盘一个已完成 run

1. 根据 `run_id` 找到对应目录
2. 读取 `manifest.json` 和 `status.json`
3. 检查 `report.md`、`reports/`、`execution/`
4. 运行 validation 检查一致性

### 案例 3：做契约回归测试

```bash
pytest -q tests/execution tests/reporting tests/validation
```

适合在改动执行、报告或验证逻辑后确认没有破坏既有契约。

### 案例 4：用脚本初始化一份新的手工回测目录

```bash
bash scripts/init_manual_run.sh run-20260423-001_ma-cross-000001sz-qtr
```

初始化完成后，再运行：

```bash
python run_backtest.py \
  --run-id run-20260423-001_ma-cross-000001sz-qtr \
  --asof-date 2026-04-23
```

## 重要约束

- `brain-node` 只能输出 schema 合法的决策记录
- `execution` 只接受通过验证的决策记录
- `report.md` 只能由 report node 生成
- `validation` 只能检查已完成的 run container
- Phase 2 的快照校验写到 `meta/snapshot-validation.json`
- Phase 6 的质量验证写到 `meta/validation.json`

## 参考文档

- [Skill Topology](/home/projects/Turtle-Strategy-Backtester/docs/contracts/skill-topology.md)
- [Run Start Contract](/home/projects/Turtle-Strategy-Backtester/docs/contracts/run-start-contract.md)
- [Run Manifest Schema](/home/projects/Turtle-Strategy-Backtester/docs/contracts/run-manifest-schema.md)
- [Run Status Schema](/home/projects/Turtle-Strategy-Backtester/docs/contracts/run-status-schema.md)
- [Point-in-Time Snapshot Contract](/home/projects/Turtle-Strategy-Backtester/docs/contracts/point-in-time-snapshot.md)
- [AI Decision Record Example](/home/projects/Turtle-Strategy-Backtester/docs/examples/ai-decision-record-example.md)
- [Report Generation Contract](/home/projects/Turtle-Strategy-Backtester/docs/contracts/report-generation-contract.md)
- [Quality Validation Contract](/home/projects/Turtle-Strategy-Backtester/docs/contracts/quality-validation-contract.md)
- [手工回测操作手册](/home/projects/Turtle-Strategy-Backtester/docs/manual-run-guide.md)

## 备注

如果你希望把这个项目真正“命令化”，下一步应该补一个正式 CLI，再把这些节点调用封装成 `start` / `resume` / `replay` / `report` / `validate` 子命令。
