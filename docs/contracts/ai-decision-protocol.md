# AI Decision Protocol

## Purpose

This protocol defines how `brain-node` converts a normalized point-in-time snapshot into a replayable AI decision record.

The protocol is split into two layers:

- `ai-decision-output.schema.json` for the model's live output
- `ai-decision-record.schema.json` for the persisted audit record

## Live Model Output

The model is only allowed to emit the minimal executable decision payload.

Rules:

- `action` is required
- `action` must be one of `buy`, `sell`, or `hold`
- extra fields are rejected by schema validation unless explicitly added to the output schema
- the output must remain free of execution logic, ledger fields, or narrative prose

## Persisted Audit Record

The orchestrator writes a durable record after validation.

Required record fields:

- `run_id`
- `symbol`
- `market`
- `cadence`
- `asof_date`
- `prompt_version`
- `schema_version`
- `model_label`
- `input_summary`
- `decision`
- `validation`

`input_summary` ties the decision back to the normalized snapshot. `decision` stores the validated model payload. `validation` stores the result of schema checking and the blocked or passed outcome.

## Fail Closed

Invalid or uncertain output must fail closed.

That means:

- invalid JSON is blocked
- schema violations are blocked
- ambiguous or unparseable content is blocked
- blocked decisions are retained for audit but must not be promoted to execution

No auto-repair path is allowed in v1.

## Versioning Rules

Every persisted decision record must record:

- `prompt_version`
- `schema_version`
- `model_label`

These three values are part of the replay contract. A later run can only be considered equivalent if the same snapshot, prompt version, schema version, and model label are available.

## Storage Location

Decision records live under:

`{artifact_root}/decisions/`

Both passed and blocked records are retained there so the audit trail remains complete.

## Phase Boundary

Phase 3 owns decision contract definition only.

Phase 4 consumes the decision record and applies execution rules. Phase 3 does not decide position sizing, execution timing, or ledger mutation.
