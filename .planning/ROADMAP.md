# Roadmap: 龟龟策略

**Created:** 2026-04-23
**Mode:** YOLO
**Granularity:** Standard
**Execution:** Parallel where safe
**Coverage:** 16 of 16 v1 requirements mapped

## Milestone 1: 单标的可复现 AI 回测闭环

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | 项目脚手架与运行契约 | 建立 CLI 入口、`run_id` 规则和工件目录结构 | ORCH-01, ORCH-02 | 3 |
| 2 | 点时点数据快照管线 | 建立数据适配器、标准快照模型和缓存 | DATA-01, DATA-02, DATA-03, DATA-04 | 4 |
| 3 | AI 决策契约与策略大脑 | 建立提示词版本化、Gemini 调用与 JSON 校验 | AI-01, AI-02, AI-03 | 4 |
| 4 | 回测仿真内核 | 建立调仓执行、资金账本和净值计算 | SIM-01, SIM-02, SIM-03 | 4 |
| 5 | 报告与可追溯复盘 | 建立报告生成、运行索引与工件回放 | RPT-01, RPT-02 | 3 |
| 6 | 质量护栏与验证闭环 | 建立自动校验、确定性检查和回归验证 | QA-01, QA-02 | 3 |

## Phase Details

### Phase 1: 项目脚手架与运行契约

**Goal:** 把一次回测定义成可重复执行、可落盘、可重放的运行单元。  
**Requirements:** ORCH-01, ORCH-02  
**Depends on:** None  
**UI hint:** no

**Success criteria**
1. CLI 暴露 `backtest run` 的核心参数入口。
2. 每次运行都会生成唯一 `run_id` 和工件目录。
3. 用户可以通过 `run_id` 定位一次既有运行并准备重放。

### Phase 2: 点时点数据快照管线

**Goal:** 为每个调仓时点构建统一、可缓存、可审计的数据快照。  
**Requirements:** DATA-01, DATA-02, DATA-03, DATA-04  
**Depends on:** Phase 1  
**UI hint:** no

**Success criteria**
1. 给定标的和调仓日期，系统能拉取对应行情快照。
2. 给定调仓日期，系统只暴露“当时已披露”的财务或基本面信息。
3. 快照能被标准化并缓存复用。
4. 每份快照都携带数据源、抓取时间、参数和版本信息。

### Phase 3: AI 决策契约与策略大脑

**Goal:** 把历史快照稳定地转换成结构化决策对象。  
**Requirements:** AI-01, AI-02, AI-03  
**Depends on:** Phase 2  
**UI hint:** no

**Success criteria**
1. 提示词模板、模型档位和策略版本具备显式配置。
2. Gemini 返回结果在进入执行层前通过 Schema 校验。
3. 每个调仓周期都保留输入摘要、决策 JSON 和校验状态。
4. 校验失败时，系统有明确错误路径而不是静默继续。

### Phase 4: 回测仿真内核

**Goal:** 用显式交易和资金假设驱动净值变化。  
**Requirements:** SIM-01, SIM-02, SIM-03  
**Depends on:** Phase 3  
**UI hint:** no

**Success criteria**
1. 系统能解释 `buy`、`sell`、`hold`、`reduce`、`add` 指令。
2. 初始资金、手续费、滑点和仓位上限都可配置。
3. 每一期都会更新持仓、现金、盈亏和净值曲线。
4. 不合法订单会被拒绝并留下清晰诊断。

### Phase 5: 报告与可追溯复盘

**Goal:** 让一次运行既有结果摘要，也有完整证据链。  
**Requirements:** RPT-01, RPT-02  
**Depends on:** Phase 4  
**UI hint:** no

**Success criteria**
1. 系统自动生成包含核心指标和关键交易的 Markdown 报告。
2. 报告能链接回配置、快照、决策和执行工件。
3. 用户可以基于 `run_id` 重建或查看既有报告。

### Phase 6: 质量护栏与验证闭环

**Goal:** 确保结果可信、可复跑、可回归。  
**Requirements:** QA-01, QA-02  
**Depends on:** Phase 5  
**UI hint:** no

**Success criteria**
1. 自动校验覆盖 Schema、点时点完整性和核心回测计算。
2. 相同输入工件下的重复运行结果一致，或差异被明确解释。
3. 项目具备执行前的本地验证命令和最小回归集。

## Next Recommended Command

`/gsd-execute-phase 1 --gaps-only`

---
*Roadmap created: 2026-04-23*
