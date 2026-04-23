# Phase 5: 报告与可追溯复盘 - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning
**Source:** Phase 5 discussion + Phase 4 execution artifacts + run contracts

<domain>
## Phase Boundary

本阶段交付报告与可追溯复盘能力，把 Phase 4 产出的 execution 工件整理成一份人类可读、可回放、可追溯的报告入口。

本阶段只负责报告生成、报告索引、回放链接与摘要包装，不负责生成新的交易决策，不负责修改 execution 账本，也不负责重建 Phase 2/3/4 工件。

Phase 5 的输出必须建立在 Phase 4 已存在的 execution artifacts 之上，并保持与 `run_id` 和 `artifact_root` 的同一性。

</domain>

<decisions>
## Implementation Decisions

### 报告结构
- **D-01:** `report.md` 采用固定的五段式结构：`Summary`、`Metrics`、`Key Trades`、`Artifact Index`、`Notes`。
- **D-02:** `report.md` 作为 top-level canonical summary 保持简洁，正文只放可快速扫读的结论与指向；更长的表格、分解和补充说明放在 `reports/` 下的派生文件中。
- **D-03:** `reports/` 目录保留为派生报告与机器可读索引的扩展空间，但 Phase 5 的主入口仍然是 top-level `report.md`，不是另起一个入口页。

### 指标口径
- **D-04:** 所有绩效指标以单个 `run_id` 的完整执行周期为统计单元，不跨 run 聚合。
- **D-05:** 收益、回撤、波动等净值相关指标以 `execution/nav.json` 作为唯一权威曲线来源。
- **D-06:** 关键交易、持仓变化与手续费/滑点解释以 `execution/fills.jsonl` 和 `execution/ledger.jsonl` 为依据。
- **D-07:** 指标计算必须对 Phase 4 的费用和整手约束保持一致，不得在报告层重新解释成交规则。

### 工件跳转
- **D-08:** 报告中的工件索引必须直接链接 `manifest.json`、`status.json`、`snapshots/`、`decisions/`、`execution/` 和 `reports/`，不再额外制造第二套抽象索引层。
- **D-09:** 报告应明确指出每个关键结论来自哪个工件类别，方便复核者从 `report.md` 直接跳到对应证据。

### 报告生成与重建
- **D-10:** 报告生成是确定性的派生过程；同一组输入工件应产出同样的报告内容。
- **D-11:** 对于 `completed`、`paused`、`partial`、`replay-ready` 的 run，`report-node` 可以重新生成派生报告，但不得修改 execution 工件或业务身份字段。
- **D-12:** 如果 `report.md` 缺失或需要重建，系统优先基于现有 execution artifacts 做幂等恢复，而不是回退到数据节点或决策节点。

### 边界约束
- **D-13:** `report-node` 是唯一允许写报告派生工件的节点；orchestrator 只负责路由与状态推进，不负责报告内容生成。
- **D-14:** 报告层不得写入新的交易决策、不得补写 ledger、不得重算 Phase 2/3/4 的原始工件。

### the agent's Discretion
- 报告中的视觉排版、段落密度和是否增加 `reports/*.md` 的补充视图，由 planner 在不改变上述结构与口径的前提下决定。
- 如果后续需要增加机器可读摘要文件，优先放入 `reports/`，而不是改变 top-level `report.md` 的职责。

</decisions>

<specifics>
## Specific Ideas

- 用户希望 `report.md` 既能快速看懂一次回测结果，也能作为证据入口追溯配置、快照、决策、成交和报告工件。
- 报告层不应引入新的分析来源；它只做 Phase 4 结果的包装、引用和复盘。
- 关键交易应能让研究者快速定位“为什么这笔交易发生”，而不是再生成一套新的解释系统。

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and roadmap context
- `.planning/PROJECT.md` - project goal, validated decisions, and active focus
- `.planning/REQUIREMENTS.md` - `RPT-01`, `RPT-02` and traceability context
- `.planning/ROADMAP.md` - Phase 5 goal and success criteria
- `.planning/STATE.md` - current milestone state and phase routing

### Upstream phase contracts
- `.planning/phases/04-backtest-simulation/04-01-SUMMARY.md` - what Phase 4 actually delivered
- `.planning/phases/04-backtest-simulation/04-CONTEXT.md` - execution boundary and artifact assumptions
- `.planning/phases/03-ai-decision-contract/03-CONTEXT.md` - decision record shape and fail-closed semantics
- `.planning/phases/01-run-contract/01-CONTEXT.md` - run identity and artifact container contract

### Runtime contracts
- `docs/contracts/run-lifecycle.md` - run state model and lifecycle ownership
- `docs/contracts/replay-resume-contract.md` - resume/replay boundary and artifact prerequisites
- `docs/contracts/run-artifact-layout.md` - `report.md`, `reports/`, and top-level container rules
- `docs/contracts/skill-topology.md` - canonical node topology and boundary rule

### Node skill contracts
- `.agents/skills/report-node/SKILL.md` - report node boundary and allowed responsibilities
- `.agents/skills/backtest-orchestrator/SKILL.md` - orchestration and node routing constraints

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/contracts/run-artifact-layout.md` already defines `report.md` as the canonical top-level summary for the run.
- `docs/contracts/replay-resume-contract.md` already makes replay vs resume a stateful lookup problem rather than a content-generation problem.
- Phase 4 already persists `execution/nav.json`, `execution/fills.jsonl`, `execution/ledger.jsonl`, and `execution/rejections.jsonl`, which are sufficient to drive the reporting layer.

### Established Patterns
- The project is still contract-first: Phase 5 should define report contracts before any new reporting code is written.
- Earlier phases favored explicit auditability over hidden automation, which should carry into report linking and artifact indexing.

### Integration Points
- Phase 5 consumes the execution outputs created by Phase 4 and the fixed run container created by Phase 1.
- Phase 5 must write its derived outputs under the same run container so Phase 6 can verify them without alternate lookup paths.

</code_context>

<deferred>
## Deferred Ideas

- Report styling variations and richer Markdown formatting for future UX polish
- Additional derived reports under `reports/` for specialized audit views
- Cross-run analytics and portfolio-level comparisons

</deferred>

---

*Phase: 05-reporting*
*Context gathered: 2026-04-23*

