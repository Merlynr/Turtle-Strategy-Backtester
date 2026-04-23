# Stack Research: 龟龟策略

**Date:** 2026-04-23
**Scope:** v1 单标的、CLI 优先、可复现 AI 回测闭环

## Recommended v1 Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Runtime | Python 3.x | 量化、数据处理和 CLI 生态成熟，适合快速搭建研究工具 |
| CLI | Typer | 官方文档支持多命令 CLI，适合 `backtest run/replay/report` 这种结构 |
| Market data | AKShare as default provider | 文档完整、接入成本低，适合快速拉起 A 股历史数据与常见数据接口 |
| Premium data fallback | Tushare Pro adapter | 官方文档明确存在权限与积分分层，适合作为高质量或补充数据源 |
| Artifact storage | Parquet | 列式存储适合快照缓存、后续分析和重放 |
| Local analytics store | DuckDB | 官方文档显示可直接读取 Parquet，适合本地查询运行工件 |
| AI contract | Gemini structured output | 官方文档支持用 JSON Schema 约束输出，适合“JSON only”决策接口 |
| Schema validation | Pydantic 2 | 官方文档支持从模型生成 JSON Schema，并做输入输出校验 |
| Simulation kernel | Custom rebalance loop | 比直接绑定通用回测框架更容易保证点时点快照、工件落盘和 AI 决策契约 |
| Benchmark adapter | backtesting.py as optional reference | 官方文档说明其订单和持仓语义清晰，可用于后续基准验证，但不建议做 v1 主内核 |

## Stack Notes

### 1. 数据层

- 采用“Provider Adapter + 标准化快照”设计。
- AKShare 负责快速可用的数据入口。
- Tushare Pro 作为可选增强源，特别适合需要更稳定字段或更多权限型接口时使用。
- 由适配器把不同供应商字段统一成内部快照模型，避免执行层直接依赖供应商列名。

### 2. 工件层

- 原始抓取结果按运行和时点落到 Parquet 或 JSON。
- DuckDB 用于在本地把快照、决策、成交和报告索引起来。
- 每次运行都保留 `run_id`、输入参数、数据源、策略版本和模型版本。

### 3. AI 层

- Gemini 只承担“把快照转成结构化决策”的职责。
- 决策输出必须先通过 Pydantic 模型或 JSON Schema 校验，再允许进入执行层。
- 需要把模型档位与提示词模板版本化，保证可重放和可对比。

### 4. 回测层

- v1 不建议一开始就把核心流程绑到通用策略框架。
- 自研调仓循环更容易明确每一步：
  - 取快照
  - 调用 AI
  - 校验 JSON
  - 解释订单
  - 更新账本
  - 落盘工件
- 可在后续阶段引入 `backtesting.py` 做交叉验证，而不是作为第一天的主依赖。

## What Not To Use In v1

- 不要使用自由文本或 Markdown 直接驱动交易逻辑。
- 不要把 CSV 当成唯一工件格式，后续查询和对比成本太高。
- 不要把执行层直接耦合到 AKShare 或 Tushare 的原始字段名。
- 不要先做 Web UI，再补 CLI 和工件链路。
- 不要一上来做多标的组合、分钟级或实盘联动。

## References

- [Typer Commands](https://typer.tiangolo.com/tutorial/commands/)
- [Gemini Structured Outputs](https://ai.google.dev/gemini-api/docs/structured-output)
- [Pydantic JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/)
- [DuckDB Parquet Overview](https://duckdb.org/docs/lts/data/parquet/overview.html)
- [AKShare 文档首页](https://akshare.akfamily.xyz/)
- [AKShare 股票数据文档](https://akshare.akfamily.xyz/data/stock/stock.html)
- [Tushare 权限说明](https://tushare.pro/document/1?doc_id=108)
- [Tushare 数据索引](https://tushare.pro/document/2?doc_id=209)
- [backtesting.py 文档](https://kernc.github.io/backtesting.py/)
- [backtesting.py API](https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html)

## Inference Notes

- 由 Tushare 官方权限说明可推断：数据源必须抽象成可切换适配器，不能把 v1 的可用性绑定到某个积分档位。
- 由 Gemini 结构化输出文档可推断：Node 2 的目标不是“写长分析”，而是“返回可验证决策对象”。
- 由 DuckDB 与 Parquet 文档可推断：本地重放和批量分析不需要先引入独立数据库服务。
