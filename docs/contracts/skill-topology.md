# Skill Topology

## Canonical Flow

This project uses one total entry skill and four node skills.

`总控 -> 数据 -> 研判 -> 执行 -> 复盘`

## Entry Skill

- `backtest-orchestrator`
  - single user-facing entry
  - pure orchestrator
  - owns routing, run creation, resume, replay, and final aggregation

## Node Skills

### 数据

- `data-node`
- builds point-in-time snapshots from configured providers

### 研判

- `brain-node`
- turns snapshots into schema-validated JSON decisions

### 执行

- `execution-node`
- interprets decisions and mutates run-state, positions, and ledger artifacts

### 复盘

- `report-node`
- generates report outputs and summary artifacts from completed execution data

## Boundary Rule

No node may absorb another node's primary responsibility.

The orchestrator coordinates nodes.
Nodes do the work inside their own boundary.
