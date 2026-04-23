---
name: report-node
description: Generate report and summary artifacts from completed execution outputs.
---

# report-node

## Single Responsibility

Generate report and summary artifacts from completed execution outputs.

This node owns report generation and artifact packaging only.

## Forbidden Responsibilities

- creating new trading decisions
- mutating ledger state after execution
- rewriting run identity metadata

## Inputs

- run context
- execution artifacts
- report template inputs
- summary metadata

## Outputs

- report artifact
- summary artifact
- report index metadata

## Notes

`report-node` may read execution outputs, but it must not change trade or ledger records.
