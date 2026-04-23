---
phase: 01-run-contract
plan: 03
subsystem: infra
tags: [artifacts, replay, resume, state]
requires:
  - phase: 01-run-contract
    provides: skill topology and run identity contracts from plans 01 and 02
provides:
  - canonical run artifact layout
  - replay and resume contract
  - state routing to the fixed run container
affects: [phase-02, phase-03, phase-04, phase-05, phase-06]
tech-stack:
  added: []
  patterns:
    - fixed run container with reserved top-level files and directories
    - explicit split between read-write resume and read-only replay
key-files:
  created:
    - docs/contracts/run-artifact-layout.md
    - docs/contracts/replay-resume-contract.md
    - docs/examples/run-directory-example.md
  modified:
    - .planning/STATE.md
key-decisions:
  - "Every downstream phase must write inside the fixed run container instead of inventing ad hoc output paths."
  - "Resume mutates the same run through the existing artifact_root, while replay reads existing artifacts without changing identity."
  - "STATE.md should route future work through the artifact layout and replay or resume contracts."
patterns-established:
  - "Pattern 1: manifest.json, status.json, and report.md always live at the top level."
  - "Pattern 2: snapshots, decisions, execution, reports, and meta remain fixed directories across all later phases."
requirements-completed:
  - ORCH-02
duration: 3 min
completed: 2026-04-23
---

# Phase 01 Plan 03: Run Container Summary

**Canonical run container layout with explicit resume versus replay rules and project state routed to that baseline**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-23T11:36:06+08:00
- **Completed:** 2026-04-23T11:39:20+08:00
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Fixed the top-level run container shape around `manifest.json`, `status.json`, `report.md`, and the five reserved subdirectories.
- Defined `resume` as mutating the same run and `replay` as read-only inspection or regeneration against existing artifacts.
- Updated `STATE.md` so future phases are explicitly routed into the canonical artifact layout and replay or resume contract.

## Task Commits

Each task was committed atomically:

1. **Task 1: Define canonical artifact layout** - `c70ca5b` (docs)
2. **Task 2: Define replay and resume contract** - `6e350fe` (docs)
3. **Task 3: Route project state to artifact-driven execution** - `96676b5` (docs)

**Plan metadata:** `pending`

## Files Created/Modified

- `docs/contracts/run-artifact-layout.md` - Defines the fixed run container and what belongs in each directory.
- `docs/contracts/replay-resume-contract.md` - Defines preconditions, failure checks, and behavioral differences for replay and resume.
- `docs/examples/run-directory-example.md` - Shows one full run tree using `run_id + 短业务摘要`.
- `.planning/STATE.md` - Routes future phases to the canonical run container and replay/resume baseline.

## Decisions Made

- Declared the run container to be the only valid home for downstream artifacts.
- Separated replay from resume so later phases do not overwrite historical runs during inspection.
- Promoted the artifact layout and replay/resume docs into project state so they govern Phase 2 onward.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 2 can now write snapshots and metadata directly into the fixed run container without inventing new paths.
- Residual risk: Phase 1 still defines contracts only; a real `run_id` generation flow and user-facing resume/replay commands remain to be implemented.

---
*Phase: 01-run-contract*
*Completed: 2026-04-23*
