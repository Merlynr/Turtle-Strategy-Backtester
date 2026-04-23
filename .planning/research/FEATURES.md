# Feature Research: 龟龟策略

**Date:** 2026-04-23

## Table Stakes

| Feature | Why it matters | Complexity | Depends on |
|---------|----------------|------------|------------|
| CLI 回测入口 | 没有统一入口就无法自动化运行和复盘 | Medium | Project scaffold |
| 点时点数据快照 | 这是避免未来函数的底线能力 | High | Provider adapter |
| 本地缓存与元数据 | 回放、提速和审计都依赖它 | Medium | Snapshot model |
| JSON 决策契约 | AI 输出必须稳定可解析 | High | Prompt + schema |
| 调仓循环与资金账本 | 回测系统的执行核心 | High | Decision interpreter |
| 指标与 Markdown 报告 | 没有结果总结就很难比较策略价值 | Medium | Simulation outputs |
| 运行工件目录 | 没有工件链路就无法定位问题与复核结果 | Medium | Run manifest |

## Differentiators

| Feature | Why it helps | Complexity | Depends on |
|---------|--------------|------------|------------|
| 双数据源适配器 | 数据可用性和覆盖率更高 | Medium | Snapshot model |
| 提示词与模型版本化 | 能清楚比较“模型变了”还是“策略变了” | Medium | CLI + config |
| 运行重放与差异对比 | 方便做 regression 与策略回顾 | Medium | Artifact lineage |
| D1-D6 分析协议 | 让 AI 节点内部逻辑更可控 | Medium | Prompt contract |
| 成本档位切换 | 批量回测用低成本模型，基准运行用高质量模型 | Low | Gemini adapter |

## Anti-Features

| Feature | Why not in v1 |
|---------|----------------|
| 实盘交易 | 风险高，且会掩盖回测正确性问题 |
| 分钟级或 tick 级回测 | 数据权限、撮合假设和性能要求明显上升 |
| Dashboard 优先 | 会把注意力从可复现闭环转到展示层 |
| 不保留工件的“一次性回测” | 无法审计、无法复核、无法比较 |
| 自由文本 AI 输出 | 一旦解析漂移，执行层会变得脆弱 |
| 全市场自动选股引擎 | v1 范围过大，会拖慢核心闭环验证 |

## Suggested v1 Product Shape

1. 一个 `backtest run` 命令。
2. 一个统一的快照模型，屏蔽供应商差异。
3. 一个严格的 JSON 决策模型，限定动作枚举和风险字段。
4. 一个可配置的调仓与资金账本内核。
5. 一份自动生成的 Markdown 复盘报告。
6. 一个围绕 `run_id` 组织的工件目录。

## Feature Implications For Requirements

- v1 必须覆盖“启动运行、拉快照、出 JSON、做回测、出报告、可追溯”这六个闭环。
- 差异化功能可以先做成接口或占位，不要在第一轮实现里追求全部完成。
- Anti-feature 应该直接写入 Out of Scope，防止路线图被 UI、实盘或高频需求带偏。
