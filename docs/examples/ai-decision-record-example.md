# AI Decision Record Example

This example shows how the persisted audit record separates the input summary, decision payload, and validation result.

## Passed Record

```json
{
  "run_id": "run-20260423-001_ma-cross-000001sz-qtr",
  "symbol": "000001.SZ",
  "market": "CN-A",
  "cadence": "quarterly",
  "asof_date": "2026-03-31",
  "prompt_version": "brain-v1.0.0",
  "schema_version": "ai-decision-output@1",
  "model_label": "gemini-2.5-pro",
  "input_summary": {
    "snapshot_ref": "snapshots/snapshot_2026-03-31.json",
    "snapshot_hash": "sha256:9d8c3d7a6e7f5c0d9e4b2f6c1a3b7e8f0d4c2b1a9e6f5d4c3b2a1f0e9d8c7b6a",
    "summary_text": "Manual point-in-time snapshot with quarterly cadence and normalized price/indicator payload."
  },
  "decision": {
    "action": "buy",
    "confidence": 0.74,
    "signal_tags": ["trend-confirmation", "earnings-momentum"]
  },
  "validation": {
    "status": "passed",
    "validated_at": "2026-04-23T08:12:34Z",
    "issues": []
  }
}
```

## Blocked Record

```json
{
  "run_id": "run-20260423-001_ma-cross-000001sz-qtr",
  "symbol": "000001.SZ",
  "market": "CN-A",
  "cadence": "quarterly",
  "asof_date": "2026-03-31",
  "prompt_version": "brain-v1.0.0",
  "schema_version": "ai-decision-output@1",
  "model_label": "gemini-2.5-pro",
  "input_summary": {
    "snapshot_ref": "snapshots/snapshot_2026-03-31.json",
    "snapshot_hash": "sha256:9d8c3d7a6e7f5c0d9e4b2f6c1a3b7e8f0d4c2b1a9e6f5d4c3b2a1f0e9d8c7b6a",
    "summary_text": "Manual point-in-time snapshot with quarterly cadence and normalized price/indicator payload."
  },
  "decision": {
    "status": "blocked",
    "raw_output": {
      "action": "add",
      "confidence": 1.2,
      "signal_tags": ["oversized"]
    },
    "blocked_reason": "Model output failed schema validation.",
    "schema_violations": [
      "decision.action must be one of buy, sell, hold",
      "decision.confidence must be less than or equal to 1"
    ]
  },
  "validation": {
    "status": "blocked",
    "validated_at": "2026-04-23T08:13:01Z",
    "issues": [
      "Unsupported action value: add",
      "Confidence score out of range: 1.2"
    ]
  }
}
```

The blocked record is retained for audit, but it is not promoted into an executable decision.
