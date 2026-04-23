# 手工回测操作手册

这份手册说明如何在当前仓库中手工准备一次回测 run，并运行执行、报告和验证。

## 1. 准备环境

先进入仓库根目录。

```bash
cd Turtle-Strategy-Backtester
```

建议使用 Python 3.12，并创建虚拟环境。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install pytest
export PYTHONPATH="$PWD/src:$PYTHONPATH"
```

## 2. 初始化 run 目录

用脚本生成一个手工回测模板：

```bash
bash scripts/init_manual_run.sh run-20260423-001_ma-cross-000001sz-qtr
```

默认会生成到：

```text
runs/run-20260423-001_ma-cross-000001sz-qtr/
```

如果你想指定别的目录，也可以：

```bash
bash scripts/init_manual_run.sh run-20260423-001_ma-cross-000001sz-qtr /tmp/my-run
```

## 3. 准备输入文件

模板里已经包含：

- `manifest.json`
- `status.json`
- `snapshots/prices.csv`
- `snapshots/snapshot_2026-04-23.json`
- `decisions/decision_2026-04-23.json`

你需要检查：

- `symbol`、`market`、`cadence` 是否正确
- `prices.csv` 是否只有历史时点数据
- `snapshot_2026-04-23.json` 的 `prices_csv_path` 是否指向当前 run 目录
- `decision_2026-04-23.json` 是否满足 AI 决策记录契约

## 4. 运行回测

运行脚本：

```bash
python run_backtest.py \
  --run-id run-20260423-001_ma-cross-000001sz-qtr \
  --asof-date 2026-04-23
```

如果你的 run 目录不在默认的 `runs/` 下，加上 `--artifact-root`：

```bash
python run_backtest.py \
  --run-id run-20260423-001_ma-cross-000001sz-qtr \
  --artifact-root /tmp/my-run \
  --asof-date 2026-04-23
```

## 5. 黄金基线回归

如果你想同时验证结果是否和仓库内的 golden run 一致：

```bash
python run_backtest.py \
  --run-id run-20260423-001_ma-cross-000001sz-qtr \
  --asof-date 2026-04-23 \
  --check-golden-baseline \
  --golden-baseline-root tests/validation/fixtures/golden-run
```

## 6. 结果查看

运行结束后，重点看这些文件：

- `report.md`
- `reports/report-index.json`
- `reports/report-summary.json`
- `meta/validation.json`

如果验证失败，先看 `meta/validation.json` 里的 `findings`。

## 7. 常见错误

- `prices.csv` 缺列
- `snapshot_*.json` 的 `prices_csv_path` 指错
- `decision_*.json` 不是合法决策记录
- `status.json` 没有更新到完成态
- `report.md` 还没生成就直接跑验证

## 8. 推荐顺序

1. 初始化 run 目录
2. 检查 `manifest.json` 和 `status.json`
3. 准备快照和决策
4. 跑 `run_backtest.py`
5. 看 `report.md`
6. 看 `meta/validation.json`

