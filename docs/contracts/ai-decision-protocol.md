# AI Decision Protocol

## Purpose

Phase 3 converts the normalized Phase 2 snapshot into a small, replayable decision contract. The goal is not to make the model freer or richer. The goal is to make the output harder to misuse.

## Contract Split

The protocol has two distinct JSON surfaces:

- `ai-decision-output.schema.json`: the model-facing payload
- `ai-decision-record.schema.json`: the persisted audit record written under `decisions/`

The model may only return the output payload. The orchestrator writes the audit record after validation.

## Model Output

The model output is intentionally minimal:

- `action` is required
- valid values are `buy`, `sell`, and `hold`
- `confidence` and `signal_tags` are optional diagnostics only

No position sizing, execution routing, or reporting fields belong in the model output. Those responsibilities stay outside `brain-node`.

## Audit Record

Each decision cycle must persist a record with:

- run identity: `run_id`, `symbol`, `market`, `cadence`, `asof_date`
- versioning metadata: `prompt_version`, `schema_version`, `model_label`
- input audit: `input_summary`
- decision payload: `decision`
- validation result: `validation`

`schema_version` identifies the decision-output schema version used for validation. `prompt_version` identifies the prompt template version. `model_label` records the concrete model identifier used for the run.

## Fail Closed

Validation must fail closed.

If the model output is missing required fields, contains unsupported values, cannot be parsed, or otherwise fails schema validation, the system must not coerce it into an executable action. The blocked response is retained as an audit artifact, but it remains blocked.

That means:

- no silent repair
- no automatic fallback to a different action
- no promotion of invalid output into a valid decision

## Replayability

Replayability depends on freezing the decision context at the time of generation.

The persisted record must preserve:

- the exact snapshot reference and hash used as input
- the prompt version
- the schema version
- the model label

Those fields allow a later reviewer to understand what the model saw, what contract it was held to, and why a record passed or blocked.

## Storage Rule

Decision records live under:

`{artifact_root}/decisions/`

Blocked validations stay in the same audit subtree. They are not rewritten into a clean executable result, and they are not moved to a side channel.

## Phase Boundary

This protocol ends at the decision boundary.

Phase 3 defines the schema-checked decision contract. Phase 4 may consume the persisted decision record, but it must not reinterpret the meaning of the fields or widen the contract.
