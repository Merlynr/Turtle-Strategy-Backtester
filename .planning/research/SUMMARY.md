# Research Summary: 龟龟策略

**Date:** 2026-04-23

## Recommended v1 Direction

把项目收敛为一条可复现的研究流水线：

1. CLI 创建一次回测运行。
2. 用 AKShare / Tushare 生成每个调仓时点的标准快照。
3. 用 Gemini 把快照转换成 Schema 校验过的 JSON 决策。
4. 用自研调仓循环更新账本、净值和交易记录。
5. 输出 Markdown 报告和完整工件目录。

## Why This Direction

- 它与原始聊天记录中的三节点设计完全对齐。
- 它优先验证“数据是否正确、AI 输出是否稳定、回测是否可复查”这三个根问题。
- 它不会过早被 UI、实盘和高频需求拖离主线。

## Key Technical Choices

- **CLI**: Typer 适合 `run / replay / report` 型多命令应用。
- **Data**: AKShare 做默认入口，Tushare 做权限型补充与兜底。
- **Storage**: Parquet 保存快照和工件，DuckDB 负责本地分析和索引。
- **AI**: Gemini 只输出结构化 JSON，不直接驱动文本型流程。
- **Validation**: Pydantic 负责模型约束和执行前校验。
- **Simulation**: v1 采用自研调仓循环，先保证快照链路和工件链路正确。

## Biggest Risks

1. 点时点数据没有处理好，导致未来函数。
2. LLM 输出漂移，导致执行层脆弱。
3. 数据权限和模型成本在大规模回测时失控。
4. 只有结果没有工件，后续无法回放和定位问题。

## What The Roadmap Should Optimize For

- 先建脚手架和运行契约，再做数据、AI、执行、报告。
- 每个阶段都围绕“能否留下工件并复查”来验收。
- v1 不追求覆盖全部资产和策略类型，只追求一个可信闭环。
