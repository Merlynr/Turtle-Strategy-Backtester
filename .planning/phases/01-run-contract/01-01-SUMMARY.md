---
phase: 01-run-contract
plan: 01
subsystem: infra
tags: [skills, workflow, orchestrator, contracts]
requires: []
provides:
  - 单一总入口 orchestrator skill 契约
  - 数据、研判、执行、复盘四类 node skill 边界文档
  - 项目级 skill-first 拓扑约束
affects: [phase-02, phase-03, phase-04, phase-05]
tech-stack:
  added: []
  patterns:
    - skill-first orchestration
    - pure orchestrator with delegated node execution
key-files:
  created:
    - .agents/skills/backtest-orchestrator/SKILL.md
    - .agents/skills/data-node/SKILL.md
    - .agents/skills/brain-node/SKILL.md
    - .agents/skills/execution-node/SKILL.md
    - .agents/skills/report-node/SKILL.md
    - docs/contracts/skill-topology.md
  modified:
    - AGENTS.md
key-decisions:
  - "Keep the top-level backtest-orchestrator as a pure coordinator that never performs strategy analysis."
  - "Split downstream work into data-node, brain-node, execution-node, and report-node with explicit forbidden responsibilities."
  - "Make .agents/skills/ and docs/contracts/skill-topology.md the canonical source for future command or code wrappers."
patterns-established:
  - "Pattern 1: Orchestrator owns run routing and aggregation, nodes own work inside their boundary."
  - "Pattern 2: Every node skill declares single responsibility, forbidden responsibilities, inputs, and outputs."
requirements-completed:
  - ORCH-01
duration: 5 min
completed: 2026-04-23
---

# Phase 01 Plan 01: Skill Topology Summary

**Single-entry orchestrator skill with four explicit node contracts for data, decision, execution, and reporting**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-23T11:19:43+08:00
- **Completed:** 2026-04-23T11:25:09+08:00
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments
- Defined `backtest-orchestrator` as the only user-facing entry and fixed its delegation order.
- Split `data-node`, `brain-node`, `execution-node`, and `report-node` into separate contract docs with boundary rules.
- Updated `AGENTS.md` so future command surfaces and code wrappers stay subordinate to the skill contracts.

## Task Commits

Each task was committed atomically:

1. **Task 1: Define orchestrator skill contract** - `824353a` (docs)
2. **Task 2: Add node skill boundary documents** - `5528a66` (docs)
3. **Task 3: Align AGENTS guidance to skill-first orchestration** - `cd9d928` (docs)

**Plan metadata:** `pending`

## Files Created/Modified

- `.agents/skills/backtest-orchestrator/SKILL.md` - Defines the single entry skill as a pure orchestrator.
- `.agents/skills/data-node/SKILL.md` - Captures point-in-time snapshot responsibilities and exclusions.
- `.agents/skills/brain-node/SKILL.md` - Captures schema-validated JSON decision responsibilities and exclusions.
- `.agents/skills/execution-node/SKILL.md` - Captures run-state and ledger mutation responsibilities and exclusions.
- `.agents/skills/report-node/SKILL.md` - Captures report artifact generation responsibilities and exclusions.
- `docs/contracts/skill-topology.md` - Records the canonical `总控 -> 数据 -> 研判 -> 执行 -> 复盘` flow.
- `AGENTS.md` - Locks the repo onto the skill-first orchestration path.

## Decisions Made

- Reserved analysis work for node skills so the orchestrator remains a pure coordinator.
- Required every node document to expose both allowed and forbidden responsibilities to prevent boundary drift.
- Declared `.agents/skills/` and `docs/contracts/skill-topology.md` as the upstream source for future wrappers and commands.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for `01-02` to define run lifecycle, manifest, and status contracts on top of the skill topology.
- Residual risk: this plan established orchestration contracts only, not the user-facing CLI behavior described in `ORCH-01`.

---
*Phase: 01-run-contract*
*Completed: 2026-04-23*
