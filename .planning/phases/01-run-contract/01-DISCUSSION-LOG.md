# Phase 1: 项目脚手架与运行契约 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `01-CONTEXT.md` - this log preserves the alternatives considered.

**Date:** 2026-04-23
**Phase:** 01-项目脚手架与运行契约
**Areas discussed:** Skill 入口形态, 运行单元定义, 工件目录契约

---

## Skill 入口形态

### Q1. 顶层 Skill 扮演什么角色？

| Option | Description | Selected |
|--------|-------------|----------|
| 纯调度器 | 只负责接收任务、创建运行上下文、分发子 skill、汇总结果，不自己做分析 | Yes |
| 调度 + 默认执行 | 平时负责调度，但在简单场景下也可以直接完成部分节点 | |
| 半调度半智能体 | 既调度又深度参与决策，子 skill 更像辅助工具 | |

**User's choice:** 纯调度器  
**Notes:** 顶层 skill 不承担分析职责，系统采用明确的主控调度器模式。

### Q2. 用户主要从哪个入口触发系统？

| Option | Description | Selected |
|--------|-------------|----------|
| 单一总入口 | 用户统一从一个总控 skill 进入，再由其决定调用哪些子 skill | Yes |
| 总入口 + 子入口并存 | 可以走总 skill，也可以直接调用某些子 skill | |
| 子入口优先 | 总 skill 只是包装层，平时更多直接调用子 skill | |

**User's choice:** 单一总入口  
**Notes:** 入口要统一，避免系统碎片化。

### Q3. 子 Skill 怎么分层最合适？

| Option | Description | Selected |
|--------|-------------|----------|
| 按流水线节点拆分 | 拆成数据 / 研判 / 执行 / 复盘四类子 skill | Yes |
| 按 GSD 阶段拆分 | 拆成准备 / 运行 / 验证 / 复盘 | |
| 混合拆分 | 既保留节点能力，也允许场景化包装 | |

**User's choice:** 按流水线节点拆分  
**Notes:** 采用四段式节点模型，呼应原始聊天记录中的流水线思路。

---

## 运行单元定义

### Q1. 一个 run 的边界是什么？

| Option | Description | Selected |
|--------|-------------|----------|
| 一次完整回测 | 从接收参数开始，到报告输出结束，算一个完整 run | Yes |
| 一次单周期决策 | 每个调仓周期单独算一个 run | |
| 一次阶段任务 | 只拉数据或只出报告也可以单独算 run | |

**User's choice:** 一次完整回测  
**Notes:** `run` 作为完整业务单元，而不是内部节点单元。

### Q2. run 的核心标识应该绑定什么？

| Option | Description | Selected |
|--------|-------------|----------|
| 策略 + 标的 + 时间区间 + cadence | 最符合回测语义，也方便比较 | Yes |
| 任务单号 | 更像 workflow job，不强调业务语义 | |
| 会话上下文 | 更偏 agent/session 视角 | |

**User's choice:** 策略 + 标的 + 时间区间 + cadence  
**Notes:** 运行标识优先围绕业务语义，而不是技术会话。

### Q3. 顶层 skill 每次启动后，默认要不要覆盖全链路？

| Option | Description | Selected |
|--------|-------------|----------|
| 总是全链路 | 默认就是 数据 -> 研判 -> 执行 -> 复盘 全跑完 | |
| 默认全链路，但允许停在某节点 | 适合重放、调试和人工介入 | Yes |
| 只做调度准备 | 真正执行要手动继续触发子 skill | |

**User's choice:** 默认全链路，但允许停在某节点  
**Notes:** 系统应默认闭环执行，但保留人工暂停点。

### Q4. run 如果停在中间节点，该算什么？

| Option | Description | Selected |
|--------|-------------|----------|
| 仍然是同一个 run | 只把状态标成 paused / partial，后续继续沿用该 run | Yes |
| 生成一个新的 run | 继续往下跑时新建 run | |
| 主 run + 子阶段记录 | 外面还是一个 run，但阶段实例单独记录 | |

**User's choice:** 仍然是同一个 run  
**Notes:** 续跑不能通过新建 run 来实现。

---

## 工件目录契约

### Q1. run 工件目录应该怎么组织？

| Option | Description | Selected |
|--------|-------------|----------|
| 每个 run 一个独立目录 | 最适合回放、审计和比较 | Yes |
| 按策略归档，再放 run | 更适合长期积累，但第一阶段更复杂 | |
| 按日期归档，再放 run | 更像日志系统 | |

**User's choice:** 每个 run 一个独立目录  
**Notes:** 工件归档以 run 为中心。

### Q2. 一个 run 目录里最上层该放什么？

| Option | Description | Selected |
|--------|-------------|----------|
| 只放汇总文件，细节分子目录 | 顶层保留汇总视图，明细归类进入子目录 | Yes |
| 所有文件平铺 | 简单但容易失控 | |
| 只有子目录 | 顶层不放任何业务文件 | |

**User's choice:** 只放汇总文件，细节分子目录  
**Notes:** 目录结构同时服务人工浏览和机器消费。

### Q3. 最少固定哪些子目录？

| Option | Description | Selected |
|--------|-------------|----------|
| snapshots / decisions / execution / reports / meta | 最贴合四段流水线和运行契约 | Yes |
| data / brain / ledger / output | 更贴近内部语义 | |
| inputs / process / outputs | 更抽象中性 | |

**User's choice:** `snapshots / decisions / execution / reports / meta`  
**Notes:** 子目录名称直接对齐系统节点与工件类型。

### Q4. run 目录命名更偏向哪种？

| Option | Description | Selected |
|--------|-------------|----------|
| run_id 为主 | 唯一性强，业务信息写进 manifest | |
| 可读业务名为主 | 肉眼友好，但容易过长 | |
| run_id + 短业务摘要 | 兼顾唯一性与人工可读性 | Yes |

**User's choice:** run_id + 短业务摘要  
**Notes:** 目录名既要稳，也要方便人工检索。

### Q5. 顶层汇总文件固定哪些？

| Option | Description | Selected |
|--------|-------------|----------|
| manifest.json + status.json + report.md | 兼顾元数据、运行状态和最终复盘 | Yes |
| manifest.json + summary.md | 更精简，但状态信息不足 | |
| manifest.yaml + status.yaml + report.md | 可读性强，但与前面 JSON 偏好不一致 | |

**User's choice:** `manifest.json + status.json + report.md`  
**Notes:** 顶层汇总文件采用 JSON + Markdown 组合。

---

## the agent's Discretion

- 子 skill 的具体命名
- `run_id` 的编码规则
- `manifest.json` 和 `status.json` 的字段设计
- 续跑与重放的具体命令语法

## Deferred Ideas

- 重放与续跑的具体交互细节留待规划阶段细化
- 数据、决策、执行和报告的内部 Schema 留待后续 phases 定义
