# Project State: 龟龟策略

**Initialized:** 2026-04-23
**Current milestone:** M1 - 单标的可复现 AI 回测闭环
**Current phase:** Phase 1 - 项目脚手架与运行契约
**Next command:** /gsd-plan-phase 1

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-23)

**Core value:** 在任意历史时点，系统都能基于当时可见的数据，产出可校验、可复现、可回放的 AI 决策与回测结果。  
**Current focus:** Phase 1 的上下文已经收敛，下一步进入计划阶段，把总控 skill、run 生命周期和工件目录契约拆成可执行计划。

## Phase Status

| Phase | Name | Status | Notes |
|-------|------|--------|-------|
| 1 | 项目脚手架与运行契约 | Context Ready | 已生成 `01-CONTEXT.md`，等待计划拆解 |
| 2 | 点时点数据快照管线 | Pending | 依赖 Phase 1 的运行目录与配置契约 |
| 3 | AI 决策契约与策略大脑 | Pending | 依赖标准快照模型 |
| 4 | 回测仿真内核 | Pending | 依赖 JSON 决策对象 |
| 5 | 报告与可追溯复盘 | Pending | 依赖账本和工件链路 |
| 6 | 质量护栏与验证闭环 | Pending | 收口阶段，验证可信度与复现性 |

## Working Assumptions

- v1 只做单标的 A 股回测。
- 调仓节奏优先支持季度，必要时扩展到月度。
- AI 节点输出必须是结构化 JSON。
- 实盘、Web UI 和高频数据不进入当前里程碑。

## Immediate Next Step

1. 读取 `.planning/phases/01-run-contract/01-CONTEXT.md`。
2. 运行 `/gsd-plan-phase 1`，把总控 skill、run 契约和工件结构拆成执行计划。
