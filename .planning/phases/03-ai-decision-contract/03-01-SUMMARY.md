---
phase: 03-ai-decision-contract
requirements_completed:
  - AI-01
  - AI-02
  - AI-03
plan: 01
subsystem: ai-contracts
tags:
  - json-schema
  - audit
  - replay
  - fail-closed
  - brain-node

# Dependency graph
requires:
  - phase: 02-point-in-time-snapshots
    provides: normalized point-in-time snapshot payload and validation boundary
provides:
  - formal JSON Schema split between model output and persisted audit record
  - fail-closed decision protocol for blocked outputs
  - versioned decision records under the run container
affects:
  - phase-04
  - execution-node
  - report-node

# Tech tracking
tech-stack:
  added:
    - json-schema draft 2020-12
  patterns:
    - minimal executable model payload
    - blocked audit envelope for invalid output
    - prompt/schema/model version trio for replayability

key-files:
  created:
    - docs/contracts/ai-decision-output.schema.json
    - docs/contracts/ai-decision-record.schema.json
    - docs/contracts/ai-decision-protocol.md
    - docs/examples/ai-decision-output-example.md
    - docs/examples/ai-decision-record-example.md
  modified:
    - .agents/skills/brain-node/SKILL.md
    - docs/contracts/run-artifact-layout.md

key-decisions:
  - "Keep the model-facing payload minimal: action plus optional diagnostics only."
  - "Persist blocked outputs as audit envelopes instead of repairing or promoting them."
  - "Record prompt_version, schema_version, and model_label on every decision record."
  - "Keep decision records under decisions/ so replay and audit remain localized to the run container."

patterns-established:
  - "Pattern 1: schema-validated JSON only, with buy/sell/hold as the executable decision surface."
  - "Pattern 2: fail-closed blocked records retain the rejected response and schema violations for audit."
  - "Pattern 3: the orchestrator persists decision-record metadata separately from the brain-node output."

requirements-completed: [AI-01, AI-02, AI-03]

# Metrics
duration: 33min
completed: 2026-04-23
---

# Phase 3: AI Decision Contract Summary

**Versioned AI decision output and audit record schemas with fail-closed blocked-output retention**

## Performance

- **Duration:** 33 min
- **Started:** 2026-04-23T08:24:00Z
- **Completed:** 2026-04-23T08:57:30Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Defined `ai-decision-output.schema.json` as the minimal executable model payload with `buy`, `sell`, and `hold` only.
- Defined `ai-decision-record.schema.json` as the persisted audit record with input summary, version metadata, validated decision, and blocked audit-envelope support.
- Documented the protocol split, fail-closed behavior, and replayability rules in `ai-decision-protocol.md`.
- Aligned `brain-node` and the run artifact layout to keep decision records under `decisions/` and outside execution logic.
- Added examples that show both a valid decision payload and a blocked record that preserves the rejected response for audit.

## Task Commits

Each task was committed atomically:

1. **Task 1: Define the AI decision protocol and JSON Schemas** - `83c1f2c` (feat)
2. **Task 2: Align brain-node and artifact layout to the protocol** - `af73721` (feat)
3. **Task 3: Add examples that prove the fail-closed flow** - `27d8314` (feat)

## Files Created/Modified

- `docs/contracts/ai-decision-output.schema.json` - minimal model output schema
- `docs/contracts/ai-decision-record.schema.json` - persisted decision audit schema
- `docs/contracts/ai-decision-protocol.md` - protocol split, fail-closed rules, versioning rules
- `docs/contracts/run-artifact-layout.md` - `decisions/` layout and blocked-record retention rule
- `.agents/skills/brain-node/SKILL.md` - node boundary aligned to schema-validated JSON output
- `docs/examples/ai-decision-output-example.md` - valid and invalid output examples
- `docs/examples/ai-decision-record-example.md` - passed and blocked decision record examples

## Decisions Made

- Kept the decision payload intentionally small so Phase 4 can interpret a stable executable surface.
- Treated invalid model output as an audit artifact, not as something to auto-correct into a valid action.
- Stored the prompt/schema/model version trio alongside every record so later replay can reproduce the exact contract context.
- Localized all decision records under the run container to preserve auditability and avoid parallel artifact paths.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The first commit attempt hit a read-only `.git/index.lock` error in the sandbox, so the task commits were written with escalated filesystem access.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 4 can consume the persisted decision records without inferring missing metadata.
- The schema boundary now makes blocked AI output inspectable without letting it escape into execution.

## PLAN COMPLETE

Phase 3 plan 01 delivered the versioned AI decision contract and fail-closed audit path required for the execution phase.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/03-ai-decision-contract/03-01-SUMMARY.md`
- Task commit hashes exist in git history: `83c1f2c`, `af73721`, `27d8314`
- Contract files, examples, and aligned skill/layout docs are present on disk

---
*Phase: 03-ai-decision-contract*
*Completed: 2026-04-23*
