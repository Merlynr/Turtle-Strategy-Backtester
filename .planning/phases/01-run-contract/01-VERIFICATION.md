---
phase: 01-run-contract
verified: 2026-04-23T11:42:52+08:00
status: gaps_found
score: 3/3 must-haves verified
---

# Phase 01: Run Contract Verification Report

**Phase Goal:** 把一次回测定义成可重复执行、可落盘、可重放的运行单元。  
**Verified:** 2026-04-23T11:42:52+08:00  
**Status:** gaps_found

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | 项目存在单一总入口 skill，且数据、研判、执行、复盘四类边界被明确拆开 | ✓ VERIFIED | `.agents/skills/backtest-orchestrator/SKILL.md` 与四个 node skill 文档已创建，`docs/contracts/skill-topology.md` 记录了 `总控 -> 数据 -> 研判 -> 执行 -> 复盘` |
| 2 | run 的身份、生命周期、manifest/status 字段与不变量已统一定义 | ✓ VERIFIED | `docs/contracts/run-lifecycle.md`、`docs/contracts/run-manifest-schema.md`、`docs/contracts/run-status-schema.md` 都包含相同的不变量与字段约束 |
| 3 | 每个 run 的固定 artifact layout、resume、replay 语义已被固化为统一契约 | ✓ VERIFIED | `docs/contracts/run-artifact-layout.md`、`docs/contracts/replay-resume-contract.md`、`docs/examples/run-directory-example.md` 与 `.planning/STATE.md` 已统一引用 run container 基线 |

**Score:** 3/3 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.agents/skills/backtest-orchestrator/SKILL.md` | 单一总入口且为纯调度器 | ✓ EXISTS + SUBSTANTIVE | 明确声明 pure orchestrator，并委派到四个 node skills |
| `.agents/skills/data-node/SKILL.md` | 点时点快照边界 | ✓ EXISTS + SUBSTANTIVE | 包含 single responsibility、forbidden responsibilities、inputs、outputs |
| `.agents/skills/brain-node/SKILL.md` | JSON 决策边界 | ✓ EXISTS + SUBSTANTIVE | 明确 schema-validated JSON 输出 |
| `.agents/skills/execution-node/SKILL.md` | run-state 与账本边界 | ✓ EXISTS + SUBSTANTIVE | 明确状态迁移与 ledger mutation |
| `.agents/skills/report-node/SKILL.md` | 报告工件边界 | ✓ EXISTS + SUBSTANTIVE | 明确 report artifact generation |
| `docs/contracts/skill-topology.md` | 总控与四节点拓扑 | ✓ EXISTS + SUBSTANTIVE | 记录 canonical flow |
| `docs/contracts/run-lifecycle.md` | 生命周期状态机 | ✓ EXISTS + SUBSTANTIVE | 覆盖 `created` 到 `replay-ready` |
| `docs/contracts/run-manifest-schema.md` | manifest.json 契约 | ✓ EXISTS + SUBSTANTIVE | 定义业务身份字段与 `artifact_root` |
| `docs/contracts/run-status-schema.md` | status.json 契约 | ✓ EXISTS + SUBSTANTIVE | 定义 `resume_from`、`current_node`、`error_summary` |
| `docs/contracts/run-artifact-layout.md` | 固定 run container | ✓ EXISTS + SUBSTANTIVE | 固定三类顶层文件和五个子目录 |
| `docs/contracts/replay-resume-contract.md` | replay/resume 规则 | ✓ EXISTS + SUBSTANTIVE | 区分 read-write `resume` 与 read-only `replay` |

**Artifacts:** 11/11 verified

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `docs/contracts/skill-topology.md` | `AGENTS.md` | 项目级协作约束 | ✓ WIRED | `AGENTS.md` 明确要求未来 wrapper 从属于 `.agents/skills/` 与 topology contract |
| `docs/contracts/run-lifecycle.md` | `docs/contracts/run-status-schema.md` | 状态枚举与 resume 语义 | ✓ WIRED | 两者共享 `paused`、`partial`、`replay-ready`、`resume_from` 语义 |
| `docs/contracts/run-manifest-schema.md` | `docs/contracts/run-artifact-layout.md` | `artifact_root` 指向固定 run container | ✓ WIRED | manifest 约束与 artifact layout 目录树一致 |
| `docs/contracts/run-artifact-layout.md` | `docs/contracts/replay-resume-contract.md` | resume/replay 依赖同一容器 | ✓ WIRED | replay/resume 前置检查都要求固定顶层文件和五个目录 |

**Wiring:** 4/4 connections verified

## Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| `ORCH-01`: 通过命令行指定 `symbol`、`start`、`end`、`cadence` 和 `strategy_profile` 启动一次回测 | ✗ BLOCKED | 当前只定义了 skill-first 合同和未来入口约束，没有可执行的 CLI 或等价的用户触发面 |
| `ORCH-02`: 为一次回测生成唯一 `run_id`，并按 `run_id` 重放或复核该次运行 | ✗ BLOCKED | 已定义 `run_id`、artifact_root、resume/replay 合同，但没有真正执行 run 创建、run 定位或 replay/resume 操作的工作流 |

**Coverage:** 0/2 requirements satisfied

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `.planning/ROADMAP.md` | Phase 1 success criteria | CLI-first success criteria vs skill-first execution scope | 🛑 Blocker | 当前 phase 产物是 contract docs，不足以宣称满足 `ORCH-01` |
| `.planning/REQUIREMENTS.md` | Orchestration section | User-facing behavior still requires runnable entry and run lookup | 🛑 Blocker | `ORCH-01` 与 `ORCH-02` 仍然缺少可执行路径 |
| `src/` | - | No executable wrapper or runnable flow yet | ⚠️ Warning | 合同已齐，但没有把 `run_id` 创建、resume、replay 变成可操作行为 |

**Anti-patterns:** 3 found (2 blockers, 1 warning)

## Human Verification Required

None — automated verification found specification gaps before any human-run workflow could be tested.

## Gaps Summary

### Critical Gaps (Block Progress)

1. **Entry surface does not satisfy ORCH-01**
   - Missing: A runnable user-facing entry or a revised requirement that formally adopts skill-first entry instead of CLI-only wording
   - Impact: The roadmap still expects `backtest run`, so Phase 1 cannot be marked complete against its current success criteria
   - Fix: Either align the requirement and roadmap to skill-first orchestration, or add a thin executable wrapper that calls the orchestrator contract

2. **No run creation flow mints real run_id and artifact_root**
   - Missing: An operation that takes inputs and actually creates the run container defined by the contracts
   - Impact: `ORCH-02` remains theoretical; nothing proves unique run generation or directory materialization
   - Fix: Add a follow-up plan for run creation and artifact-root materialization based on the manifest and status contracts

3. **No runnable replay or resume operation**
   - Missing: A concrete workflow that resolves an existing run by `run_id` and executes replay or resume behavior
   - Impact: Replay and resume are documented but not yet usable
   - Fix: Add a follow-up plan for run lookup, state validation, and replay/resume invocation rules

## Recommended Fix Plans

### 01-04-PLAN.md: Reconcile Entry Surface With Skill-First Intent

**Objective:** Resolve the mismatch between current CLI-first requirements and the user's chosen skill-first delivery path.

**Tasks:**
1. Update `PROJECT.md`, `REQUIREMENTS.md`, and `ROADMAP.md` so orchestration requirements match the intended skill-first entry model.
2. Add explicit user-facing examples for starting a run through `backtest-orchestrator`.
3. Verify Phase 1 success criteria against the revised entry contract.

**Estimated scope:** Small

---

### 01-05-PLAN.md: Define Executable Run Operations

**Objective:** Turn the documented run contract into an operational start, resume, and replay workflow without widening scope into full simulation logic.

**Tasks:**
1. Define the concrete sequence that mints `run_id`, creates `artifact_root`, and writes initial `manifest.json` and `status.json`.
2. Define the operator flow that locates an existing run by `run_id` and chooses replay or resume safely.
3. Verify that the documented flow satisfies `ORCH-02` at the workflow level.

**Estimated scope:** Medium

## Verification Metadata

**Verification approach:** Goal-backward using the current roadmap success criteria plus plan must-haves  
**Must-haves source:** Aggregated from `01-01-PLAN.md`, `01-02-PLAN.md`, and `01-03-PLAN.md`  
**Automated checks:** 18 passed, 2 failed  
**Human checks required:** 0  
**Total verification time:** 4 min

---
*Verified: 2026-04-23T11:42:52+08:00*
*Verifier: the agent*
