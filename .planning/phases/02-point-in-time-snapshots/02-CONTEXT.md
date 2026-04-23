# Phase 2: 点时点数据快照管线 - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning

<domain>
## Phase Boundary

交付“点时点数据快照管线”，让 `data-node` 能在不依赖外部数据源凭证的前提下，把操作者手工提供的 K 线/指标等信息，固化为可复现、可审计的快照工件，并写入 Phase 1 定义的固定 run container（`{artifact_root}/snapshots/` 与 `{artifact_root}/meta/`）。

本阶段不负责生成买卖决策（Phase 3），不负责成交/账本与净值仿真（Phase 4），不负责报告生成（Phase 5）。

</domain>

<decisions>
## Implementation Decisions

### 手工数据模式（manual provider）
- **D-01:** v1 支持“手工输入数据模式”作为主路径：不要求 AKShare/Tushare 等数据源凭证。
- **D-02:** 手工输入被视为 provider=`manual`，必须在快照与元数据中记录最小溯源信息（由操作者提供的来源说明/备注）。
- **D-03:** 后续如果接入数据源，属于扩展能力；本阶段先把“无凭证也能跑”的链路打通。

### 快照输入与落盘格式
- **D-04:** 回测价格路径（用于后续仿真/对齐调仓日）由操作者提供，首选 CSV（`date,open,high,low,close,volume`），作为 run 工件落盘在 `{artifact_root}/snapshots/prices.csv`。
- **D-05:** 每个调仓时点的快照以 JSON 形式落盘，文件命名固定为 `{artifact_root}/snapshots/snapshot_{asof_date}.json`（`asof_date` 使用 `YYYY-MM-DD`）。
- **D-06:** “原始输入”与“标准化快照”分离：标准化快照用于喂给 `brain-node`；原始输入（如果存在多段来源或非结构化说明）落在 `{artifact_root}/meta/manual-inputs/`，用于审计与复核。

### 调仓时点（snapshot schedule）
- **D-07:** 默认调仓时点由 `cadence` + `prices.csv` 推导：每个周期取该周期内“最后一个可用交易日”（不依赖外部交易日历）。
- **D-08:** 允许操作者覆盖默认调仓时点：在 run 的 `meta/` 中显式提供 `asof_dates[]`，则以该列表为准。

### 点时点约束（避免未来函数）
- **D-09:** 快照内任何蜡烛数据必须满足 `candle.date <= asof_date`；若检测到违例，必须把违例记录写入 `{artifact_root}/meta/snapshot-validation.json`，并把该快照标记为不可用（不允许静默吞掉）。
- **D-10:** 快照必须显式记录本次快照使用的价格窗口范围（例如 `window_start`/`window_end`）与构建时间 `built_at`，以支持回放。

### 指标与特征（features）
- **D-11:** v1 优先接受操作者“直接提供”的指标/特征（RSI/MA/ATR 等），不强制在本阶段实现指标计算器；后续如需统一计算属于扩展。
- **D-12:** 快照中的 `indicators` 字段允许同时包含数值与计算备注（例如周期参数、是否复权、是否去极值）。

### the agent's Discretion
- 在不改变外部契约（文件路径与文件名规则）的前提下，快照 JSON 的内部字段组织与冗余程度（例如是否同时冗余一段 K 线窗口）由实现阶段决定，以最小化 Phase 3 的接入复杂度。

</decisions>

<specifics>
## Specific Ideas

- 用户工作流设想：选出股票 -> 手工提供 K 线/指标/备注 -> 系统给出买入/卖出决策并落盘 -> 累积决策形成回测 -> 根据回测迭代调整（决策与回测属于后续 Phase 3/4/5）。
- 不引入外部数据源凭证；数据完全由操作者提供并被系统固化为可复现工件。

</specifics>

<canonical_refs>
## Canonical References

### Phase 1 契约（Phase 2 必须遵守）
- `docs/contracts/run-artifact-layout.md` - run container 的顶层结构与 `snapshots/`、`meta/` 的归属
- `.agents/skills/backtest-orchestrator/SKILL.md` - 统一入口与调度边界
- `.agents/skills/data-node/SKILL.md` - data-node 的职责边界
- `docs/contracts/run-start-contract.md` - start 的必填输入
- `docs/contracts/run-manifest-schema.md` - `manifest.json` 的业务身份字段
- `docs/contracts/run-status-schema.md` - `status.json` 的运行状态字段
- `docs/contracts/skill-topology.md` - orchestrator 与四个 node 的拓扑

### 示例（用于对齐落盘语义）
- `docs/examples/run-directory-example.md` - run container 示例树
- `docs/examples/skill-entry-examples.md` - start/resume/replay 的入口示例

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.agents/skills/data-node/SKILL.md`: 已存在 data-node 的职责声明，可在 Phase 2 中扩展为“手工输入 provider”与快照 schema 的落盘契约。

### Established Patterns
- 目前以“文档契约优先”的方式推进：先锁定快照 schema 与落盘位置，再进入实现。

### Integration Points
- `backtest-orchestrator` 在 `start` 后默认分发给 `data-node`；Phase 2 的产物必须能够被 `brain-node` 消费。

</code_context>

<deferred>
## Deferred Ideas

- 自动对接 AKShare/Tushare 等数据源（需要凭证与数据对齐策略）
- 自动计算技术指标与复权/复原规则（可能引入未来函数风险，需要更严格的点时点校验）
- 多标的组合快照与对齐（v2）

</deferred>

---

*Phase: 02-point-in-time-snapshots*
*Context gathered: 2026-04-23*
