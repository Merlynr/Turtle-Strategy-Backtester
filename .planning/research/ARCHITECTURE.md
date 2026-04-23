# Architecture Research: 龟龟策略

**Date:** 2026-04-23

## Recommended Component Boundaries

| Component | Responsibility | Inputs | Outputs |
|-----------|----------------|--------|---------|
| CLI Orchestrator | 解析命令、创建 run、驱动流程 | CLI args, config | run manifest, execution flow |
| Provider Adapters | 从 AKShare / Tushare 拉历史数据 | symbol, date, fields | raw provider payloads |
| Snapshot Builder | 把原始数据整理成点时点标准快照 | provider payloads | normalized snapshot |
| Prompt Registry | 管理提示词模板、策略版本、模型档位 | strategy profile, snapshot | model-ready prompt payload |
| Decision Engine | 调用 Gemini，获取结构化 JSON 决策 | prompt payload, schema | validated decision object |
| Simulation Engine | 解释决策并更新账本、持仓、净值 | decision object, price data | ledger, trades, equity curve |
| Reporting Layer | 生成指标、摘要和 Markdown 报告 | ledger, trades, run metadata | report, metrics |
| Artifact Store | 保存运行工件并提供索引 | all intermediate outputs | reproducible run directory |

## Data Flow

1. 用户通过 CLI 提交运行参数。
2. Orchestrator 创建 `run_id`，写入运行配置和目录结构。
3. 对每个调仓时点：
   - Provider Adapter 抓取历史行情与基本面数据。
   - Snapshot Builder 生成统一快照并落盘。
   - Prompt Registry 选择提示词模板和模型档位。
   - Decision Engine 调用 Gemini，并用 Schema 做校验。
   - Simulation Engine 根据 JSON 决策更新账本。
4. 所有周期结束后，Reporting Layer 计算指标并生成 Markdown 报告。
5. Artifact Store 保留本次运行的快照、决策、成交、报表和元数据，支持重放。

## Suggested Repository Layout

```text
.
|-- AGENTS.md
|-- prompts/
|-- src/
|   `-- guigui_strategy/
|       |-- cli/
|       |-- config/
|       |-- providers/
|       |-- snapshots/
|       |-- brain/
|       |-- simulation/
|       `-- reporting/
|-- tests/
`-- .planning/
```

## Build Order

1. **Phase 1**: 脚手架、CLI 入口、`run_id` 与工件目录契约
2. **Phase 2**: Provider Adapter 与点时点快照模型
3. **Phase 3**: Prompt Registry、Gemini 调用与 JSON 校验
4. **Phase 4**: 调仓循环、资金账本和收益计算
5. **Phase 5**: 报告、重放入口与运行索引
6. **Phase 6**: 自动校验、确定性检查和回归验证

## Architectural Rules

- 任何供应商字段都不能直接流入执行层，必须先进入标准快照模型。
- 任何模型输出都不能直接流入账本层，必须先通过 Schema 校验。
- 任何回测结果都不能只存在内存里，必须能落盘重放。
- 任何“解释性文本”都只能作为附加信息，不能代替结构化决策字段。

## Why Custom Simulation First

- 聊天记录里要跑的是“数据快照 -> AI 决策 -> 执行结算”的编排链路，而不是单纯技术指标回测。
- 自研调仓循环更容易把每一步的输入、输出和错误都落成工件。
- 这条链路稳定后，再接入通用框架做对照测试会更安全。
