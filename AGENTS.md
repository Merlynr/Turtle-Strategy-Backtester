# AGENTS.md

This project follows a GSD-style planning workflow.

## Always Read First

Before changing code, contracts, or plans, read these files in order:

1. `.planning/PROJECT.md`
2. `.planning/REQUIREMENTS.md`
3. `.planning/ROADMAP.md`
4. `.planning/STATE.md`
5. `docs/contracts/skill-topology.md`

If the task touches orchestration or run contracts, also read the relevant files under `.agents/skills/` and `docs/contracts/`.

## Project Guardrails

- Treat point-in-time correctness as non-negotiable.
- Never let provider-specific raw fields leak directly into the simulation engine.
- Never let free-form model text drive orders. Decision output must be schema-validated JSON.
- Preserve a strict separation between data acquisition, AI decision generation, simulation, and reporting.
- Keep v1 focused on a reproducible single-symbol backtest loop.
- Preserve the skill-first topology before adding command wrappers or code modules.

## Skill-First Topology

Phase 1 adopts a single orchestrator skill as the canonical entry to the system.

- The entry point lives at `.agents/skills/backtest-orchestrator/SKILL.md`.
- The backtest-orchestrator is a single orchestrator skill and a pure coordinator. It may create or resume a run, route work, and aggregate outputs, but it must not perform strategy analysis itself.
- Downstream work must preserve the four node boundaries defined in `.agents/skills/`:
  - `data-node`
  - `brain-node`
  - `execution-node`
  - `report-node`
- The canonical flow is `总控 -> 数据 -> 研判 -> 执行 -> 复盘`.
- Any future command surface, CLI entry, or code wrapper must remain subordinate to the contracts in `.agents/skills/` and `docs/contracts/skill-topology.md`.

## Repo Intent

This repo is currently skill-first and contract-first. Future code may grow into these areas, but those wrappers must reflect the orchestrator and node boundaries rather than replace them:

- `src/guigui_strategy/cli`
- `src/guigui_strategy/providers`
- `src/guigui_strategy/snapshots`
- `src/guigui_strategy/brain`
- `src/guigui_strategy/simulation`
- `src/guigui_strategy/reporting`
- `prompts/`
- `tests/`

## Workflow Expectations

- Use `/gsd-discuss-phase N` before planning a new phase when context is still fuzzy.
- Use `/gsd-plan-phase N` after the phase goal is clear.
- Use `/gsd-execute-phase N` to realize the approved plan through skill contracts, documentation, and later code wrappers.
- Update `.planning/STATE.md` and requirement traceability when a phase transitions.
- Record major scope or architecture shifts in `.planning/PROJECT.md`.
