# Phase 2: 点时点数据快照管线 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-23
**Phase:** 02 - 点时点数据快照管线
**Areas discussed:** manual data mode, snapshot format, schedule derivation, point-in-time invariants

---

## Manual Data Mode

| Option | Description | Selected |
|--------|-------------|----------|
| manual-first | 操作者手工提供 K 线/指标等输入，不依赖数据源凭证 | ✓ |
| provider-first | 以数据源适配器为主，手工仅作为调试辅助 | |
| hybrid | 两者并存，优先 provider，但允许 manual 覆盖 | |

**User's choice:** manual-first（用户明确“不需要数据源凭证/配置”）
**Notes:** 手工输入被标记为 provider=`manual`，要求溯源备注写入 `meta/`。

---

## Input Format And Persistence

| Option | Description | Selected |
|--------|-------------|----------|
| JSON-only snapshots | 所有输入与快照都用 JSON 表达与落盘 | |
| prices.csv + snapshots.json | 价格路径用 CSV，调仓快照用 JSON，便于后续仿真复用 | ✓ |
| parquet-first | 直接用 Parquet 作为主要格式 | |

**User's choice:** prices.csv + snapshots.json（根据“手工提供 K 线/指标”与后续仿真需求取默认推荐）
**Notes:** 落盘位置必须遵守 run container：`{artifact_root}/snapshots/` 与 `{artifact_root}/meta/`。

---

## Snapshot Schedule Derivation

| Option | Description | Selected |
|--------|-------------|----------|
| derive from prices.csv | 用 `cadence` + `prices.csv` 的可用交易日推导每期调仓日（取周期末最后交易日） | ✓ |
| operator-provided asof_dates | 完全由操作者提供 `asof_dates[]` 列表 | |
| fixed calendar | 依赖外部交易日历/节假日表 | |

**User's choice:** derive from prices.csv（满足“无凭证运行”且能复现）
**Notes:** 允许操作者覆盖：若提供 `asof_dates[]` 则以其为准。

---

## Point-In-Time Invariants

| Option | Description | Selected |
|--------|-------------|----------|
| strict validate | 强校验：任何 `candle.date > asof_date` 直接标记快照不可用并记录 | ✓ |
| warn only | 只告警，不阻断 | |
| trust operator | 完全信任操作者输入，不做校验 | |

**User's choice:** strict validate（防止未来函数污染后续决策与回测）
**Notes:** 违例写入 `{artifact_root}/meta/validation.json`，不能静默修复。

---

## Deferred Ideas

- 自动接入外部数据源适配器（AKShare/Tushare）
- 自动计算指标与复权规则（需要严控未来函数）
- 多标的与组合层面的快照对齐
