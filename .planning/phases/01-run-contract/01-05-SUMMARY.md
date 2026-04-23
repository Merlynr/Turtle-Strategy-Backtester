---
phase: 01-run-contract
requirements_completed:
  - ORCH-01
  - ORCH-02
plan: 05
subsystem: infra
tags: [gap-closure, run-id, resume, replay, orchestrator]
requires:
  - phase: 01-run-contract
    provides: corrected skill-first entry contract from plan 04
provides:
  - orchestrator run start workflow
  - lookup by run_id contract
  - operation matrix for resume and replay
  - end-to-end run operation sequences
affects: [phase-01, phase-02, phase-05]
tech-stack:
  added: []
  patterns:
    - run initialization through manifest and status writes
    - lookup before resume or replay
key-files:
  created:
    - docs/contracts/run-start-contract.md
    - docs/contracts/run-lookup-contract.md
    - docs/examples/run-operation-sequences.md
  modified:
    - .agents/skills/backtest-orchestrator/SKILL.md
    - docs/contracts/replay-resume-contract.md
key-decisions:
  - "Define run start as an ordered orchestrator workflow that mints run_id, derives artifact_root, and writes manifest/status before node dispatch."
  - "Require lookup by run_id before either resume or replay can proceed."
  - "Use a state operation matrix so paused, partial, completed, replay-ready, and failed runs have explicit allowed actions."
patterns-established:
  - "Pattern 1: Start, resume, and replay are all orchestrator-owned workflows, not ad hoc operator actions."
  - "Pattern 2: Resume is always same run_id plus same artifact_root, while replay remains read-only by default."
requirements-completed:
  - ORCH-02
duration: 2 min
completed: 2026-04-23
---

# Phase 01 Plan 05: Run Operations Summary

**Orchestrator-owned start, lookup, resume, and replay workflows anchored on run_id and artifact_root**

## Performance

- **Duration:** 2 min
- **Started:** 2026-04-23T12:58:49+08:00
- **Completed:** 2026-04-23T13:00:56+08:00
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Defined how `backtest-orchestrator` starts a run by validating inputs, minting `run_id`, deriving `artifact_root`, and writing the initial `manifest.json` and `status.json`.
- Added a dedicated `lookup by run_id` contract that decides whether `resume` or `replay` is legal for a given run state.
- Added one example document showing complete `start new run`, `resume paused run`, and `replay existing run` sequences.

## Task Commits

Each task was committed atomically:

1. **Task 1: Define the run start workflow in the orchestrator contract** - `8484845` (docs)
2. **Task 2: Define lookup-by-run_id and allowed operation selection** - `d9a311a` (docs)
3. **Task 3: Add end-to-end operation sequences for start, resume, and replay** - `ae421f4` (docs)

**Plan metadata:** `pending`

## Files Created/Modified

- `.agents/skills/backtest-orchestrator/SKILL.md` - Defines start order and points to operation sequences.
- `docs/contracts/run-start-contract.md` - Defines initial run creation and file writes.
- `docs/contracts/run-lookup-contract.md` - Defines how an existing run is resolved by `run_id`.
- `docs/contracts/replay-resume-contract.md` - Adds lookup dependency and state operation matrix.
- `docs/examples/run-operation-sequences.md` - Shows the end-to-end start, resume, and replay sequences.

## Decisions Made

- Elevated run initialization into an explicit orchestrator contract rather than leaving it implicit in schema docs.
- Required `lookup by run_id` before any replay or resume action.
- Wrote state-based operation rules so resume and replay have clear, non-overlapping safety boundaries.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 1 can now be re-verified against a skill-first entry contract plus explicit run operation workflows.
- If verification passes, Phase 2 can inherit a stable start, lookup, resume, and replay baseline for all run containers.

---
*Phase: 01-run-contract*
*Completed: 2026-04-23*
