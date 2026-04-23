---
phase: 01-run-contract
plan: 02
subsystem: infra
tags: [run-contract, manifest, status, lifecycle]
requires: []
provides:
  - run 生命周期状态机
  - manifest.json 字段契约
  - status.json 字段契约
  - run_id 命名与身份示例
affects: [phase-02, phase-03, phase-04, phase-05, phase-06]
tech-stack:
  added: []
  patterns:
    - immutable run identity with mutable status tracking
    - shared invariants across lifecycle and schema docs
key-files:
  created:
    - docs/contracts/run-lifecycle.md
    - docs/contracts/run-manifest-schema.md
    - docs/contracts/run-status-schema.md
    - docs/examples/run-identity-examples.md
  modified: []
key-decisions:
  - "Define one run as one complete backtest, even when it pauses or becomes partial."
  - "Keep business identity in manifest.json and mutable execution progress in status.json."
  - "Mirror the same invariants across lifecycle, manifest, and status docs so downstream phases can validate against one vocabulary."
patterns-established:
  - "Pattern 1: A resumed run always keeps the same run_id and artifact_root."
  - "Pattern 2: Manifest is stable identity, status is mutable execution state."
requirements-completed:
  - ORCH-01
  - ORCH-02
duration: 4 min
completed: 2026-04-23
---

# Phase 01 Plan 02: Run Identity Summary

**Run lifecycle, manifest, and status contracts that define one backtest as one stable identity with resumable state**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-23T11:29:25+08:00
- **Completed:** 2026-04-23T11:33:28+08:00
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Defined the minimum lifecycle states from `created` through `replay-ready`, including paused and partial continuation rules.
- Split stable business identity into `manifest.json` and mutable execution progress into `status.json`.
- Added naming examples and shared invariants so later phases can reuse the same `run_id`, `artifact_root`, and replay vocabulary.

## Task Commits

Each task was committed atomically:

1. **Task 1: Define run lifecycle and state transitions** - `a3a6792` (docs)
2. **Task 2: Define manifest schema and business identity fields** - `c91e9c2` (docs)
3. **Task 3: Cross-check lifecycle, manifest, and status consistency** - `f7bf110` (docs)

**Plan metadata:** `pending`

## Files Created/Modified

- `docs/contracts/run-lifecycle.md` - Defines run states, transitions, resume semantics, and lifecycle invariants.
- `docs/contracts/run-manifest-schema.md` - Defines stable business identity fields for `manifest.json`.
- `docs/contracts/run-status-schema.md` - Defines mutable execution tracking fields for `status.json`.
- `docs/examples/run-identity-examples.md` - Provides concrete `run_id + 短业务摘要` examples and mapping notes.

## Decisions Made

- Treated `paused` and `partial` as states of the same run rather than reasons to mint a new run.
- Assigned immutable business identity to `manifest.json` and execution progress to `status.json`.
- Repeated the same invariants across all three contract docs to keep later implementation and verification aligned.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for `01-03` to define the run directory layout and the concrete replay or resume contract on top of these schemas.
- Residual risk: these contracts still do not provide the CLI entry promised by `ORCH-01`; they only define the shape that later execution must obey.

---
*Phase: 01-run-contract*
*Completed: 2026-04-23*
