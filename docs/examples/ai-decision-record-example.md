# AI Decision Record Example

## Passed Record

```json
{
  "run_id": "run-20260423-001_ma-cross-000001sz-qtr",
  "symbol": "000001.SZ",
  "market": "CN-A",
  "cadence": "quarterly",
  "asof_date": "2026-04-23",
  "prompt_version": "brain-v1.0",
  "schema_version": "ai-decision-output.v1",
  "model_label": "gemini-2.5-flash",
  "input_summary": {
    "snapshot_ref": "snapshots/snapshot_2026-04-23.json",
    "snapshot_hash": "sha256:7d4a1d0b4d0df3f4e4b6a1f3f0b8c1fd9d6c6c8d5f4b8e3a2f1c0b9a8d7e6c5b",
    "summary_text": "Quarterly snapshot with price trend support and stable fundamentals."
  },
  "decision": {
    "action": "buy",
    "confidence": 0.74,
    "signal_tags": [
      "trend-confirmed",
      "volume-support"
    ]
  },
  "validation": {
    "status": "passed",
    "validated_at": "2026-04-23T11:35:00+08:00",
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
  "asof_date": "2026-04-23",
  "prompt_version": "brain-v1.0",
  "schema_version": "ai-decision-output.v1",
  "model_label": "gemini-2.5-flash",
  "input_summary": {
    "snapshot_ref": "snapshots/snapshot_2026-04-23.json",
    "snapshot_hash": "sha256:7d4a1d0b4d0df3f4e4b6a1f3f0b8c1fd9d6c6c8d5f4b8e3a2f1c0b9a8d7e6c5b",
    "summary_text": "Model emitted extra free-form text and out-of-range confidence."
  },
  "decision": {
    "action": "buy",
    "confidence": 1.2,
    "signal_tags": [
      "trend-confirmed"
    ]
  },
  "validation": {
    "status": "blocked",
    "validated_at": "2026-04-23T11:36:00+08:00",
    "issues": [
      "confidence exceeds maximum",
      "unexpected free-form field detected in model response"
    ]
  }
}
```

Blocked records remain in `decisions/` for audit, but they must not be forwarded to execution.
