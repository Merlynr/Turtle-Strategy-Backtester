# AI Decision Output Example

## Valid Output

```json
{
  "action": "buy",
  "confidence": 0.74,
  "signal_tags": [
    "trend-confirmed",
    "volume-support"
  ]
}
```

## Invalid Output

```json
{
  "action": "buy",
  "confidence": 1.2,
  "notes": "increase size because momentum looks strong"
}
```

This invalid payload would be blocked because `confidence` is out of range and `notes` is not part of the schema.
