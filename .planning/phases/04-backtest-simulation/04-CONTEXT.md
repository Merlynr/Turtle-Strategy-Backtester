# Phase 4: 回测仿真内核 - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning
**Source:** Phase 4 discussion + Phase 1/2/3 contracts

<domain>
## Phase Boundary

本阶段交付回测仿真内核，把 Phase 3 的 schema-validated AI 决策记录和 Phase 2 的点时点快照转成可复现的执行结果、账本变更和净值曲线。

本阶段只负责调仓执行、仓位与现金更新、手续费与滑点计入、以及执行工件落盘，不负责报告叙述、不负责新的决策生成，也不负责重建历史快照。

Phase 5 会消费本阶段输出的 execution 工件，但不会反向改变执行规则。

</domain>

<decisions>
## Implementation Decisions

### 成交时点
- **D-01:** 执行时点使用决策对应 `asof_date` 之后的下一可用交易日开盘价，而不是当日收盘价。
- **D-02:** 下一可用交易日以 Phase 2 的 `prices.csv` / 标准化快照所提供的价格序列为准，不额外引入外部交易日历。
- **D-03:** 如果决策日期之后不存在可用价格行，则该笔执行不得凭空成交，必须进入显式阻断或待处理状态并记录原因。

### 仓位规则
- **D-04:** Phase 4 采用方向型执行模型：`buy` 表示建立或增持多头，`sell` 表示减持或清空多头，`hold` 表示不改变仓位。
- **D-05:** 本阶段的默认执行策略是“尽量向目标方向完全执行”，即买入时在仓位上限约束内尽可能部署可用现金，卖出时尽可能清空可卖持仓。
- **D-06:** `reduce` / `add` 保持为执行层可理解的扩展语义，但 v1 的核心链路以 Phase 3 当前输出的 `buy` / `sell` / `hold` 为主，不要求 AI 在本阶段新增自由文本指令。

### 数量与整手规则
- **D-07:** A 股执行按 100 股整手处理；买入时向下取整到可买整手，卖出时按可卖整手处理。
- **D-08:** 不使用 fractional share；如果按整手计算后买卖数量为 0，则该笔订单视为不可执行并记录原因。

### 成本与约束
- **D-09:** 初始资金、手续费、滑点和仓位上限都是显式配置项，必须随 run 记录并参与每一期结算。
- **D-10:** 手续费与滑点进入净值和现金结算，不得被当作“事后指标”省略。
- **D-11:** 仓位上限是强约束，超限订单不得自动扩大到上限之外。

### 失败处理
- **D-12:** 不合法订单必须被拒绝并留下清晰诊断，不允许静默修正为另一笔交易。
- **D-13:** 失败执行记录要保留在 `execution/` 目录下，作为可审计工件，而不是只写日志。

### the agent's Discretion
- 手续费和滑点的具体公式参数、默认值和分段规则由 planner 决定，只要不破坏 fail-closed 和可复现原则。
- `reduce` / `add` 在 v1 中是否作为显式对外可配置的扩展开关，由 planner 决定；但不能让它们改变 Phase 3 当前的 schema-locked 决策边界。
- 当价格序列末尾缺少下一交易日时，是否将该期标记为终止、部分完成或失败，由 planner 在不破坏审计的前提下细化。

</decisions>

<specifics>
## Specific Ideas

- 用户明确选择了下一交易日开盘成交、全额方向执行、100 股整手执行。
- Phase 4 需要对齐 Phase 3 的“direction-only”决策契约，而不是再引入一个新的自由文本指令层。
- 账本必须能解释为什么一笔看起来“应该能买”的决策会因为整手、费用或仓位上限而失败。

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and roadmap context
- `.planning/PROJECT.md` - project goal, validated decisions, and active focus
- `.planning/REQUIREMENTS.md` - `SIM-01`, `SIM-02`, `SIM-03` and traceability context
- `.planning/ROADMAP.md` - Phase 4 goal and success criteria
- `.planning/STATE.md` - current milestone state and phase routing

### Upstream phase contracts
- `.planning/phases/03-ai-decision-contract/03-01-SUMMARY.md` - locked AI decision protocol decisions
- `.planning/phases/03-ai-decision-contract/03-CONTEXT.md` - decision boundary and what Phase 4 may consume
- `.planning/phases/02-point-in-time-snapshots/02-CONTEXT.md` - normalized point-in-time snapshot shape
- `.planning/phases/01-run-contract/01-CONTEXT.md` - run identity and artifact container contract

### Runtime contracts
- `docs/contracts/run-lifecycle.md` - run state model and lifecycle ownership
- `docs/contracts/replay-resume-contract.md` - resume/replay boundary and artifact prerequisites
- `docs/contracts/run-artifact-layout.md` - `execution/` subtree and artifact storage rules
- `docs/contracts/ai-decision-protocol.md` - execution may only consume validated decision records
- `docs/contracts/skill-topology.md` - canonical node topology and boundary rule

### Node skill contracts
- `.agents/skills/execution-node/SKILL.md` - execution node boundary and allowed responsibilities
- `.agents/skills/brain-node/SKILL.md` - input contract for the validated decision object

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.agents/skills/execution-node/SKILL.md` already defines the execution node as the sole owner of run-state and ledger mutation.
- `docs/contracts/run-artifact-layout.md` already reserves `execution/` for ledger, fills, and NAV outputs.

### Established Patterns
- The project is still contract-first: phase work is specified as documents before any implementation code exists.
- Earlier phases favored explicit auditability over hidden automation, which should carry into execution and cost accounting.

### Integration Points
- Phase 4 consumes `docs/contracts/ai-decision-record.schema.json` and the normalized snapshot outputs from Phase 2.
- Phase 4 must write execution artifacts under the fixed run container so Phase 5 can report from them without alternate lookup paths.

</code_context>

<deferred>
## Deferred Ideas

- Partial-fill engine with broker-style order matching
- Intraday or minute-level execution timing
- Multi-asset portfolio allocation
- Real broker integration
- Advanced order types beyond the current direction-based loop

</deferred>

---

*Phase: 04-backtest-simulation*
*Context gathered: 2026-04-23*
