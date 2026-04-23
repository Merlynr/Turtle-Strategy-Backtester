# Phase 6: 质量护栏与验证闭环 - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning
**Source:** Phase 6 discussion + Phase 5 reporting artifacts + run contracts

<domain>
## Phase Boundary

本阶段只负责质量护栏与验证闭环，验证 Phase 1 到 Phase 5 已交付的运行契约、点时点数据、AI 决策、仿真执行与报告产物是否可校验、可复跑、可回归。

本阶段不新增新的交易能力，不改写 execution 账本，不改变报告生成职责，也不扩展到多标的、实盘或更高频率。质量验证必须围绕现有 run container、执行工件与报告工件展开。

</domain>

<decisions>
## Implementation Decisions

### 验证入口
- **D-01:** Phase 6 的正式入口是一个独立的 `validate` 流程，作为明确的质量检查命令存在，而不是只靠零散测试和文档约定来承载验证职责。
- **D-02:** `pytest` 仍然是实现 `validate` 的主要技术手段之一，但它不再是用户视角下的唯一验证接口。
- **D-03:** 验证流程应能串起 schema 校验、点时点完整性检查和回测结果一致性检查，并给出单一的成败结论。

### 确定性标准
- **D-04:** 相同输入下，整个 run container 需要保持一致，允许变化的只有显式时间字段和其他明确声明为运行时元数据的字段。
- **D-05:** 质量验证必须覆盖 `manifest.json`、`status.json`、`execution/`、`reports/` 与 phase-specific validation 产物之间的一致性。
- **D-06:** 对于报告与复跑输出，验证要检查语义和结构是否保持一致，而不是只接受“看起来差不多”。

### 最小回归集
- **D-07:** 最小回归集必须同时包含合成 fixture 和一份仓库内的 golden run 工件。
- **D-08:** 合成 fixture 用于稳定覆盖边界条件和失败路径，golden run 用于覆盖真实端到端路径和已知良好输出。
- **D-09:** golden run 工件应作为版本化回归基线保留在仓库内，便于后续 Phase 6 及更晚阶段复用。

### the agent's Discretion
- 验证命令的具体命名、输出格式和日志密度由 planner 决定，只要它能稳定实现上述三类校验目标。
- 可把 `validate` 设计成组合式检查入口，由多个子校验步骤构成，但用户视角应该看到一个清晰的质量结论。

</decisions>

<specifics>
## Specific Ideas

- 用户明确希望 Phase 6 不只是“写测试”，而是提供一个正式的质量入口。
- 用户接受用一份仓库内的 golden run 作为回归锚点，而不是完全依赖临时生成的数据。
- 用户更偏向于严格确定性：整个 run container 应尽量稳定，只把显式时间字段视为可变因素。

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and roadmap context
- `.planning/PROJECT.md` - project goal, validated decisions, and active focus
- `.planning/REQUIREMENTS.md` - `QA-01`, `QA-02` and traceability context
- `.planning/ROADMAP.md` - Phase 6 goal and success criteria
- `.planning/STATE.md` - current milestone state and phase routing

### Upstream phase contracts
- `.planning/phases/05-reporting/05-CONTEXT.md` - reporting boundary, artifact index, and deferred ideas
- `.planning/phases/05-reporting/05-01-SUMMARY.md` - what Phase 5 actually delivered
- `.planning/phases/04-backtest-simulation/04-CONTEXT.md` - execution boundary and artifact assumptions
- `.planning/phases/04-backtest-simulation/04-01-SUMMARY.md` - deterministic execution core and persistence behavior
- `.planning/phases/03-ai-decision-contract/03-CONTEXT.md` - decision record shape and fail-closed semantics
- `.planning/phases/02-point-in-time-snapshots/02-CONTEXT.md` - point-in-time validation boundary
- `.planning/phases/01-run-contract/01-CONTEXT.md` - run identity and artifact container contract

### Runtime contracts
- `docs/contracts/run-lifecycle.md` - run state model and lifecycle ownership
- `docs/contracts/replay-resume-contract.md` - resume/replay boundary and artifact prerequisites
- `docs/contracts/run-artifact-layout.md` - `report.md`, `reports/`, and top-level container rules
- `docs/contracts/snapshot-validation.md` - point-in-time snapshot validation contract
- `docs/contracts/skill-topology.md` - canonical node topology and boundary rule
- `docs/contracts/report-generation-contract.md` - deterministic report generation and report artifact rules
- `docs/contracts/backtest-execution-contract.md` - deterministic execution boundary and persistence rules

### Node skill contracts
- `.agents/skills/report-node/SKILL.md` - report node boundary and allowed responsibilities
- `.agents/skills/execution-node/SKILL.md` - execution node boundary and allowed responsibilities
- `.agents/skills/brain-node/SKILL.md` - schema-validated decision boundary
- `.agents/skills/data-node/SKILL.md` - point-in-time snapshot boundary
- `.agents/skills/backtest-orchestrator/SKILL.md` - orchestration and node routing constraints

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/execution/` already covers deterministic execution contracts and can serve as the starting point for validation scenarios.
- `tests/reporting/` already covers deterministic report synthesis and provides a strong pattern for future report consistency checks.
- `docs/contracts/report-generation-contract.md` and `docs/contracts/backtest-execution-contract.md` already encode the phase boundaries that validation should assert.
- `docs/contracts/replay-resume-contract.md` already separates replay from resume, which is important for validation flows that must not mutate identity fields.

### Established Patterns
- The repo is contract-first and artifact-first: validation should assert against concrete files under the run container rather than against hidden in-memory state.
- Existing phases use strict fail-closed behavior. Phase 6 should preserve that pattern for validation failures.
- Phase 5 introduced deterministic report synthesis, so Phase 6 can validate reproducibility against those derived outputs without redefining report content.

### Integration Points
- Phase 6 consumes the full run container emitted by Phases 1 through 5.
- The validation entry point should integrate with the same artifact root and `run_id` model used by `resume` and `replay`.
- The golden run fixture should live in a stable repo location that downstream tests and planners can reference directly.

</code_context>

<deferred>
## Deferred Ideas

- RTK token savings statistics for orchestration summaries remain deferred.
- A synchronous, order-driven backtest loop remains deferred.
- Cross-run analytics, portfolio-level comparisons, and richer observability remain outside Phase 6.

</deferred>

---

*Phase: 06-quality*
*Context gathered: 2026-04-23*
