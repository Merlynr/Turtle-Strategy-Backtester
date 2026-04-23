# AI Decision Output Example

This example shows the only payload shape the model is allowed to emit on a successful pass.

## Valid Payload

```json
{
  "action": "buy",
  "confidence": 0.74,
  "signal_tags": ["trend-confirmation", "earnings-momentum"]
}
```

This is schema-valid because:

- `action` is present
- `action` is one of `buy`, `sell`, or `hold`
- optional diagnostics stay inside the allowed bounds

## Invalid Payload Rejected By Validation

```json
{
  "action": "add",
  "confidence": 1.2,
  "signal_tags": ["oversized"]
}
```

This payload must be blocked because:

- `action` is outside the allowed enum
- `confidence` exceeds the maximum of `1`
- the invalid payload must not be repaired into a valid trade instruction
