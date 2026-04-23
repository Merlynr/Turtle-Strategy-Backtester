# 龟龟策略：AI 驱动量化回测系统

## What This Is

这是一个面向策略研究者的 CLI 优先量化回测系统，用来把历史点时点数据、AI 研判和回测执行串成一条可复现的流水线。v1 聚焦单标的 A 股回测，强调数据快照、结构化决策和结果复盘三件事必须打通。

## Core Value

在任意历史时点，系统都能基于当时可见的数据，产出可校验、可复现、可回放的 AI 决策与回测结果。

## Requirements

### Validated

(None yet - ship to validate)

### Active

- [ ] 通过命令行发起一次完整的 AI 回测运行
- [ ] 用点时点数据快照约束 AI 输入，避免未来函数
- [ ] 用结构化 JSON 决策驱动回测执行与报告
- [ ] 为每次运行保留完整工件，支持重放与对比

### Out of Scope

- 实盘交易接入 - v1 先验证研究闭环与回测正确性
- 高频或分钟级撮合 - 数据成本和执行复杂度过高
- Web 仪表盘 - 先以 CLI 和 Markdown 报告验证需求
- 多标的组合优化 - 先把单标的、单策略闭环做扎实

## Context

- 想法来源于一段关于“AI 驱动的量化回测系统”的聊天记录，核心建议是把系统拆成三类节点：
  - Node 1：数据聚合节点，负责在历史时点抓取市场和财务数据。
  - Node 2：逻辑研判节点，负责把快照喂给 Gemini，并强约束为结构化 JSON 决策。
  - Node 3：结算与执行节点，负责解释决策、模拟交易并记录 PnL。
- 编排方式采用 GSD 风格的工作流：先初始化项目上下文，再做研究、需求、路线图，后续逐阶段执行。
- 目标用户首先是策略研究者本人，因此系统优先服务“可跑、可查、可复盘”，而不是做成面向外部用户的产品。
- 预期主命令形态类似 `backtest run --symbol 000001.SZ --start 2020-01-01 --end 2023-12-31 --cadence quarterly`。
- 回测输出至少要包含运行工件目录、决策日志、净值曲线、夏普比率、最大回撤和 Markdown 复盘报告。

## Constraints

- **市场范围**: v1 仅覆盖 A 股日线与季度或月度节奏，先降低噪声和实现复杂度
- **交互方式**: 以 CLI 为主，便于自动化、批量运行和后续脚本集成
- **AI 契约**: Node 2 只允许输出结构化 JSON，禁止自由文本直接驱动执行
- **可复现性**: 每次运行都必须落盘输入、输出和元数据，支持审计与复盘
- **数据源**: 兼容 AKShare 与 Tushare，不把引擎绑死到单一供应商
- **风险控制**: v1 只做回测与分析，不做实盘下单

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 采用 Python + CLI 优先架构 | 数据生态成熟，最贴近 GSD 编排方式 | Pending |
| 把点时点数据快照设为一级工件 | 这是避免未来函数和支持复盘的核心防线 | Pending |
| 让 Gemini 只返回 Schema 校验后的 JSON | 降低提示漂移导致的执行风险 | Pending |
| 使用 Parquet + DuckDB 保存运行数据 | 兼顾可追溯性、查询效率和本地复用 | Pending |
| v1 聚焦单标的闭环 | 先验证核心价值，再扩展到组合与更复杂策略 | Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition**:
1. Requirements invalidated? Move them to Out of Scope with reason.
2. Requirements validated? Move them to Validated with phase reference.
3. New requirements emerged? Add them to Active.
4. Decisions to log? Add them to Key Decisions.
5. "What This Is" still accurate? Update it if the project has drifted.

**After each milestone**:
1. Review all sections end to end.
2. Re-check whether Core Value is still the top priority.
3. Audit Out of Scope items and confirm the reasons still hold.
4. Refresh Context with the latest architecture, users, and validation learnings.

---
*Last updated: 2026-04-23 after initialization*
