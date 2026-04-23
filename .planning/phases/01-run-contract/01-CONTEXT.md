# Phase 1: 项目脚手架与运行契约 - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning

<domain>
## Phase Boundary

本阶段聚焦定义“一个回测运行如何被发起、标识、暂停、续跑和落盘”的统一契约，用来支撑后续的数据、研判、执行和复盘子 skill。它只负责把运行单元和工件组织方式定稳，不扩展到数据抓取细节、AI 决策逻辑或回测公式本身。

</domain>

<decisions>
## Implementation Decisions

### Skill orchestration model
- **D-01:** 系统采用单一总入口的顶层 skill，用户默认从一个总控入口发起回测流程。
- **D-02:** 顶层 skill 是纯调度器，只负责接收任务、创建运行上下文、分发子 skill、汇总结果，不承担实际分析。
- **D-03:** 子 skill 按流水线节点拆分为四类：`数据`、`研判`、`执行`、`复盘`。

### Run identity and lifecycle
- **D-04:** 一个 `run` 表示一次完整回测，从接收运行参数开始，到报告输出或人工暂停为止。
- **D-05:** `run` 的核心业务语义绑定为 `策略 + 标的 + 时间区间 + cadence`。
- **D-06:** 顶层 skill 默认按全链路驱动运行，但允许在任意节点暂停，用于调试、人工介入和后续续跑。
- **D-07:** 如果运行停在中间节点，仍然属于同一个 `run`，只更新状态，不生成新的 `run`。

### Artifact directory contract
- **D-08:** 每个 `run` 使用一个独立目录，作为该次回测的唯一工件容器。
- **D-09:** `run` 目录顶层只放汇总文件，明细工件统一进入子目录，避免平铺混乱。
- **D-10:** 固定子目录为 `snapshots / decisions / execution / reports / meta`，分别承载快照、结构化决策、执行结果、复盘产物和元数据。
- **D-11:** `run` 目录命名采用 `run_id + 短业务摘要`，既保留唯一标识，也保留人工可读性。
- **D-12:** 顶层汇总文件固定为 `manifest.json`、`status.json`、`report.md`。

### the agent's Discretion
- 子 skill 的具体命名和调用参数风格，由后续规划阶段决定，但必须保持“总控 skill + 四类子 skill”的结构。
- `run_id` 的具体编码规则和短业务摘要格式，由后续规划阶段决定，但必须稳定、唯一且适合后续重放。
- `manifest.json`、`status.json` 与各子目录内文件的字段级 Schema，由后续规划阶段决定。
- 重放与续跑的精确命令形式可在规划阶段决定，但必须复用同一个 `run_id`，不能通过新建 `run` 实现续跑。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope and constraints
- `.planning/PROJECT.md` - 项目目标、核心价值、约束和总体方向
- `.planning/REQUIREMENTS.md` - `ORCH-01` 与 `ORCH-02` 所在的 v1 范围和需求映射
- `.planning/ROADMAP.md` - Phase 1 的边界、目标和成功标准
- `.planning/STATE.md` - 当前里程碑状态与下一步路由

### Discussion output
- `.planning/phases/01-run-contract/01-CONTEXT.md` - Phase 1 已锁定的运行契约与目录决策

### Additional specs
- No additional external specs yet - requirements are captured in the planning artifacts and decisions above

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- 目前仓库仍处于 planning-only 状态，没有现成代码、组件或工具函数可复用。

### Established Patterns
- 当前唯一已建立的模式是 GSD 风格的文档驱动流程：先通过 `PROJECT / REQUIREMENTS / ROADMAP / STATE` 明确边界，再进入计划与实现。
- 本项目已明确采用“总控 skill + 四类子 skill”的流水线模式，这会约束后续代码和 workflow 的组织方式。

### Integration Points
- 后续实现的首个集成点将是顶层总控 skill 的入口。
- 第二层集成点将是每个 `run` 的独立工件目录及其标准顶层文件和固定子目录。

</code_context>

<specifics>
## Specific Ideas

- 用户明确要求当前阶段通过 skill/workflow 的方式定义系统，而不是直接生成代码。
- 用户希望系统呈现出明显的“主控调度器 + 子节点流水线”结构，而不是零散命令集合。
- 目录契约需要同时支持机器读取和人工复盘，因此选择了 `run_id + 短业务摘要` 的混合命名方式。

</specifics>

<deferred>
## Deferred Ideas

- 重放与续跑的具体命令交互细节，留到后续规划时细化，但不能改变“续跑仍属于同一个 `run`”这个已定约束。
- 数据快照字段、决策 JSON Schema、执行账本结构和报告模板，属于后续 phase 的内容，不在本阶段展开。

</deferred>

---

*Phase: 01-run-contract*
*Context gathered: 2026-04-23*
