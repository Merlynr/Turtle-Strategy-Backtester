# AGENTS.md

This project follows a GSD-style planning workflow.

## Always Read First

Before changing code or plans, read these files in order:

1. `.planning/PROJECT.md`
2. `.planning/REQUIREMENTS.md`
3. `.planning/ROADMAP.md`
4. `.planning/STATE.md`

## Project Guardrails

- Treat point-in-time correctness as non-negotiable.
- Never let provider-specific raw fields leak directly into the simulation engine.
- Never let free-form model text drive orders. Decision output must be schema-validated JSON.
- Preserve a strict separation between:
  - data acquisition
  - AI decision generation
  - simulation and reporting
- Keep v1 focused on a reproducible single-symbol backtest loop.

## Repo Intent

This repo is meant to become a CLI-first research system with these future areas:

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
- Update `.planning/STATE.md` and requirement traceability when a phase transitions.
- Record major scope or architecture shifts in `.planning/PROJECT.md`.

## Current Next Step

`/gsd-discuss-phase 1`
