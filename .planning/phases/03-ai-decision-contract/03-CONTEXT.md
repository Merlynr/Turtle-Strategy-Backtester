# Phase 3: AI 决策契约与策略大脑 - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning
**Source:** Discuss checkpoint + existing Phase 1/2 contracts

<domain>
## Phase Boundary

本阶段交付 `brain-node` 的决策契约，把 Phase 2 产出的标准化快照稳定转换为可校验、可回放、可审计的方向型 JSON 决策。

本阶段只定义“研判输入、研判输出、版本记录、校验结果和失败路径”的契约，不负责仿真撮合、仓位演算、净值计算或报告生成。

Phase 4 会消费这里定义的决策记录，但不会反向修改这里的 schema 约束。

</domain>

<decisions>
## Implementation Decisions

### 决策输出边界
- **D-01:** `brain-node` 的主输出是最小可执行版本的方向型决策，重点是 `buy` / `sell` / `hold`，而不是位置大小或资金分配。
- **D-02:** 决策输出必须是 schema-validated JSON，不能依赖自由文本来驱动后续执行。
- **D-03:** 当模型输出缺字段、格式错误、语义不确定或校验失败时，系统必须严格 fail closed，不允许自动修复后继续。

### 决策记录边界
- **D-04:** AI 模型输出与运行审计记录分离：模型只生成决策 payload，运行时再把 `prompt_version`、`schema_version`、`model_label`、`input_summary` 和 `validation` 封装成可审计的决策记录。
- **D-05:** 每个调仓周期都必须保留输入摘要、决策 JSON 和校验结果，便于回放与对照 Phase 2 的快照工件。
- **D-06:** 决策记录属于 `{artifact_root}/decisions/` 下的正式工件，不能散落在临时文件或日志里。

### 版本与可追溯性
- **D-07:** 每次运行必须显式记录 `prompt_version`、`schema_version` 和 `model_label`，以支持同输入复现和版本对比。
- **D-08:** `schema_version` 必须作为显式协议字段存在，不能仅依赖文件名或目录名来判断。
- **D-09:** `prompt_version` 和 `model_label` 属于运行审计元数据，不属于模型应自由发挥的字段。

### 指令粒度
- **D-10:** 研判层不决定仓位大小，不决定手续费/滑点假设，不决定具体成交节奏；这些职责留给 Phase 4 的执行与仿真层。
- **D-11:** 研判层可以附带轻量诊断信息，但这些信息不能改变执行层的主决策语义。

### the agent's Discretion
- `decision` 记录里是否额外保留轻量诊断字段、信号标签或短理由，由实现阶段决定，只要不破坏最小可执行版本和 fail-closed 规则。
- `input_summary` 的内部结构可以按最小审计需要设计，只要能稳定标识本次快照、输入版本与决策上下文。

</decisions>

<protocol_schema>
## Formal JSON Schema Protocol Definition

**Contract split**

- `ai-decision-output.schema.json`: 模型实际返回的最小决策 payload
- `ai-decision-record.schema.json`: 运行时写入 `decisions/` 的审计记录

### 1) Model output schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "docs/contracts/ai-decision-output.schema.json",
  "title": "AI Decision Output v1",
  "type": "object",
  "additionalProperties": false,
  "required": ["action"],
  "properties": {
    "action": {
      "type": "string",
      "enum": ["buy", "sell", "hold"],
      "description": "Minimal executable direction chosen by brain-node."
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Optional confidence score for audit and diagnostics."
    },
    "signal_tags": {
      "type": "array",
      "items": { "type": "string" },
      "uniqueItems": true,
      "description": "Optional short tags for non-binding diagnostics."
    }
  }
}
```

### 2) Decision record schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "docs/contracts/ai-decision-record.schema.json",
  "title": "AI Decision Record v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "run_id",
    "symbol",
    "market",
    "cadence",
    "asof_date",
    "prompt_version",
    "schema_version",
    "model_label",
    "input_summary",
    "decision",
    "validation"
  ],
  "properties": {
    "run_id": { "type": "string", "minLength": 1 },
    "symbol": { "type": "string", "minLength": 1 },
    "market": { "type": "string", "minLength": 1 },
    "cadence": { "type": "string", "minLength": 1 },
    "asof_date": { "type": "string", "format": "date" },
    "prompt_version": { "type": "string", "minLength": 1 },
    "schema_version": { "type": "string", "minLength": 1 },
    "model_label": { "type": "string", "minLength": 1 },
    "input_summary": {
      "type": "object",
      "additionalProperties": false,
      "required": ["snapshot_ref", "snapshot_hash"],
      "properties": {
        "snapshot_ref": { "type": "string", "minLength": 1 },
        "snapshot_hash": { "type": "string", "minLength": 1 },
        "summary_text": { "type": "string" }
      }
    },
    "decision": {
      "$ref": "docs/contracts/ai-decision-output.schema.json"
    },
    "validation": {
      "type": "object",
      "additionalProperties": false,
      "required": ["status"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["passed", "blocked"]
        },
        "validated_at": {
          "type": "string",
          "format": "date-time"
        },
        "issues": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    }
  }
}
```

### Protocol notes

- The model only sees the output schema.
- The orchestrator writes the audit record after validation.
- A blocked record must remain blocked; it may be inspected, but it must not be silently promoted to an executable decision.
- The record schema is the authoritative contract for Phase 3 artifacts under `decisions/`.

</protocol_schema>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core project scope
- `.planning/PROJECT.md` - project goal, core value, and v1 scope
- `.planning/REQUIREMENTS.md` - `AI-01`, `AI-02`, `AI-03` and traceability context
- `.planning/ROADMAP.md` - Phase 3 goal and success criteria
- `.planning/STATE.md` - current milestone state and phase routing

### Upstream contracts
- `.planning/phases/01-run-contract/01-CONTEXT.md` - run identity, lifecycle, and artifact container boundaries
- `.planning/phases/02-point-in-time-snapshots/02-CONTEXT.md` - manual point-in-time snapshot contract
- `.planning/phases/03-ai-decision-contract/03-DISCUSS-CHECKPOINT.json` - locked decisions captured during discussion

### Runtime contracts
- `docs/contracts/skill-topology.md` - canonical node topology and boundary rule
- `docs/contracts/point-in-time-snapshot.md` - normalized snapshot shape consumed by `brain-node`
- `docs/contracts/snapshot-validation.md` - snapshot blocking and provenance rules
- `docs/contracts/run-artifact-layout.md` - `decisions/` directory and run container layout
- `docs/contracts/run-manifest-schema.md` - run identity and versioned artifact root context
- `docs/contracts/run-status-schema.md` - mutable status record and execution-state context

### Node skill contracts
- `.agents/skills/backtest-orchestrator/SKILL.md` - pure orchestrator boundary
- `.agents/skills/data-node/SKILL.md` - snapshot assembly boundary
- `.agents/skills/brain-node/SKILL.md` - schema-validated decision boundary

</canonical_refs>

<specifics>
## Specific Ideas

- 用户要求本阶段基于 1-1、2-1、3-1、4-1 决策生成上下文，并给出正式 JSON Schema 协议定义。
- 目标不是把 AI 输出做得更“聪明”，而是把输出变得更可校验、更可回放、更可追责。
- Phase 3 的成功标准必须能够直接支撑 Phase 4 的执行逻辑，但不能把执行职责提前塞进 brain-node。
- `AI-03` 的“输入摘要、决策 JSON 和校验结果”应该在决策记录里可以逐周期查看，而不是散落在日志里。

</specifics>

<deferred>
## Deferred Ideas

- 多模型并行投票或 ensemble 决策
- 复杂的仓位 sizing 或组合优化
- 自动策略评估指标与离线回测统计
- 面向 UI 的决策浏览器

</deferred>

---

*Phase: 03-ai-decision-contract*
*Context gathered: 2026-04-23*
