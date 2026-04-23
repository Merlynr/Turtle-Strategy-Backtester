# Project State: 龟龟策略

**Initialized:** 2026-04-23
**Current milestone:** M1 - 单标的可复现 AI 回测闭环
**Current phase:** Phase 1 - 项目脚手架与运行契约
**Next command:** /gsd-discuss-phase 1

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-23)

**Core value:** 在任意历史时点，系统都能基于当时可见的数据，产出可校验、可复现、可回放的 AI 决策与回测结果。  
**Current focus:** 先把 CLI、`run_id` 和工件目录契约做稳，再进入数据与 AI 细节。

## Phase Status

| Phase | Name | Status | Notes |
|-------|------|--------|-------|
| 1 | 项目脚手架与运行契约 | Pending | 初始化已完成，等待讨论实现方式 |
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

1. 明确 Phase 1 的仓库骨架、命令名和工件目录约定。
2. 再用 `/gsd-plan-phase 1` 把 Phase 1 拆成可执行计划。
