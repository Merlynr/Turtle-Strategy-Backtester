# Phase 2: 点时点数据快照管线 - Summary

**Plan:** 02-02
**Wave:** 1
**Status:** complete

## Outcome

Extended the run container metadata rules and defined snapshot validation behavior.

## Files Changed

- `docs/contracts/run-artifact-layout.md`
- `docs/contracts/snapshot-validation.md`

## Verification

- `meta/manual-inputs/` is explicitly part of the run container metadata subtree.
- `meta/validation.json` stores validation results.
- `candle.date <= asof_date` is the blocking validation rule.
- Cache reuse is only allowed when payloads and versioned parameters match.

## Notes

This plan ensures the snapshot layer can be audited and rejected cleanly before `brain-node` consumes it.
