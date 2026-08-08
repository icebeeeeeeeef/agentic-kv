# Agentic KV Agent Instructions

本仓库是一个面向秋招的 AI Infra / KV Cache runtime engineering 项目。所有工作必须同时服务于两件事：

1. 把共享 KV Pool 的 L3 写入准入做成证据可复核的工程项目。
2. 保持面试口径诚实、可追问、不过度包装。

## 先读什么

任何新对话或 agent 在修改本仓库前，必须依次完整阅读：

1. [README.md](README.md)
2. [PROJECT_EVALUATION_SOP.md](docs/project/PROJECT_EVALUATION_SOP.md)
3. [STATUS.md](STATUS.md)
4. [PROJECT_PLAN.md](docs/project/PROJECT_PLAN.md)
5. [Documentation map](docs/README.md)
6. 与当前任务直接相关的 implementation evidence、research evidence 或 historical review

不要用旧评审或 source material 覆盖 canonical plan。

## 权威顺序

1. [PROJECT_EVALUATION_SOP.md](docs/project/PROJECT_EVALUATION_SOP.md)：选题、能力信号、证据、主张与叙事的方法论宪法
2. [PROJECT_PLAN.md](docs/project/PROJECT_PLAN.md)：当前项目的 Gate、STOP 与实验合同；方法论上必须服从 SOP
3. [STATUS.md](STATUS.md)：实际完成状态
4. [TASKS.md](TASKS.md)：用户明确授权的近期工作
5. [docs/implementation](docs/implementation/)：固定版本源码与运行时证据
6. [INTERVIEW_QA.md](docs/project/INTERVIEW_QA.md)：由上述证据派生的面试防守集合
7. [JOB_MARKET_FIT.md](docs/research/JOB_MARKET_FIT.md) 与 [PROJECT_SELECTION_REVIEW.md](docs/research/PROJECT_SELECTION_REVIEW.md)
8. research evidence、historical reviews 与 source material

低层文件不得反向升级高层 claim state。任务清单和面试集合也不得修改项目宪法；若发现冲突，先停止并提出需要裁决的差异。SOP 解决的是方法论冲突；STATUS 对实际运行、实现和验证状态保持事实权威，不能被任何计划或叙事文件改写。

## 工作方式

### 第一性原理

- 回答问题、设计方案或解释代码时，先从目标、约束、输入输出、核心不变量和失败模式出发。
- 不因用户表述或行业惯例直接接受某个方向；如果固定版本源码、实验或约束不支持，要明确指出。
- 如果一个功能、逻辑或抽象对当前问题没有实际作用，或属于过度优化，应拒绝实现并说明理由。
- 默认寻找最简单、最直接、可验证的做法；复杂方案必须证明它比简单方案多解决了当前真实问题。
- 如果结论来自推测，必须标明推测依据和仍需获得的证据。

### 方案设计

- 实现前先确认边界、状态归属、数据流、不变量、失败路径和归因口径。
- 优先复用 pinned upstream 机制；能做窄 hook 或增量改造时，不重造 SGLang、Mooncake 或缓存框架。
- 不为远期可能性增加通用框架、插件系统、动态策略服务或平台组件，除非它直接提高当前证据质量、实验真实性或面试防御性。
- 对需要权衡的设计，必须说明代价、反例、停止条件和可回滚的最小实现。
- 新增或扩展功能前，至少审核 [PROJECT_PLAN.md](docs/project/PROJECT_PLAN.md)、[STATUS.md](STATUS.md) 及与当前 Gate 相关的 implementation evidence。
- 如果局部方案破坏已有 claim state、项目边界、实验公平性或面试口径，应停止实现，先提出冲突和需要用户确认的新决策。

### 调研原则

- 上游能力不确定、存在重要权衡或可能重复造轮子时，优先核对真实做法。
- 优先使用一手来源：论文、官方文档、固定版本源码、上游 issue/PR、可运行示例和本仓库实验结果。
- 调研结论必须映射回当前问题：解决什么、不能解决什么、是否改变 ownership、Gate 或 claim state。
- 调研默认用于减少重复造轮子和避开经典错误，不得自动成为扩大 scope 的理由。

### TDD 研发

- 对 owned code、实验 harness、数据处理、策略逻辑和验证逻辑，默认采用严格 TDD。
- 实现前写清行为和完成判据；先写会失败的测试或最小可复现 fixture，并确认失败原因正确。
- 只写让当前失败测试通过的最小实现；通过后再做必要重构，并运行相关测试、格式检查和静态检查。
- 纯文档、外部环境预检或人工实验若不适合自动化测试，必须提前写明替代验证方式和可复核 artifact。
- instrumentation patch 与 behavior-changing admission patch 必须分开测试；观测能力不得悄悄改变 queue、batch、retry、读写或时序语义。

### 对抗式审查

- 主动尝试让实现或方案失败：异常输入、重复执行、并发、超时、取消、部分成功、晚到事件、重复 key、跨 worker race、上游漂移、环境不一致和依赖不可用。
- 优先检查 correctness、claim state、前缀闭包、证据可复核性、资源记账、异步生命周期、失败恢复和面试口径。
- 架构审查重点寻找隐藏耦合、重复权威、状态双写、过度抽象、不可观测路径和无法回放的决策。
- 每次审查都必须问：这个模块不做行不行？有没有更简单但仍正确的做法？失败后如何按 Gate/STOP 合法收口？

### 测试审查

- 测试必须证明合同规定的真实行为，不能复述当前实现。
- 严查样例特化、关键词匹配、固定行号、过宽 mock、无意义 snapshot、只覆盖 happy path 或为了通过测试而写的硬编码。
- 覆盖边界条件、失败路径、重复/乱序事件、partial batch、Put failure、shutdown 和 claim-state 变化。
- fixture 或 mock 必须说明它代表的真实系统合同，以及不能覆盖的风险。
- 对上游等价性、ALWAYS_ADMIT、ALWAYS_DROP 和异步资源配对，应优先使用可比较的行为 oracle，而不是只断言内部函数被调用。

## 当前唯一主线

唯一 behavior-changing mechanism 是：

    L2 DMA ack 完成
      → prefix-closure 检查
      → ADMIT_TO_L3 | DROP
      → upstream Mooncake Put 或直接返回

Prefix-DAG 是 workload；Mooncake 是 upstream shared-L3 substrate；conditional admission ledger 只用于给定 eligibility stream 的 action/payload 对账、敏感性分析与 candidate rejection，不能充当跨策略闭环因果证明。

## 实施纪律

- 所有源码事实绑定明确 commit；先读真实源码，再回答、设计或修改。
- 当前 SGLang source anchor 是 `b058dc910619c9d4bce9e9e24117104ffc491fa6`；Mooncake exact commit 尚待 G0 pin。
- behavior hook 与纯观测 instrumentation 分 commit、分测试、分 claim。
- 固定 L2 指算法、容量、配置、write-through 和 eviction 实现固定；不要求不同 treatment 的 L2 内容或 event sequence 相同。
- 不使用某一 arm 的 eligibility stream 作为另一 policy 的闭环反事实。
- G2b conditional ledger 只能拒绝候选；G3 双 worker 在线 A/B 是唯一策略裁决。
- 每个性能数字必须能追溯到 manifest、commit、raw log 和统计方法。
- 负结果、losing workload 和 STOP 与正结果同等重要。
- 不把 upstream SGLang/Mooncake 能力写成个人实现。

## Scope 默认拒绝

除非先修改 [PROJECT_PLAN.md](docs/project/PROJECT_PLAN.md) 并重新过 Gate，否则不得加入：

- L1/L2 或 L3 eviction
- router、affinity 或 load balancing
- SSD L4 或第二 cache backend
- RDMA/GDR/NIXL 数据面
- KV 量化、稀疏化或 kernel
- metadata HA、复制或故障恢复
- PD disaggregation、Kubernetes 或 GPUStack
- 通用 policy DSL 或动态 RPC policy service

## 任务清单

短期任务清单固定使用 [TASKS.md](TASKS.md)。

- 只有用户明确要求“加入任务清单”时，才能新增任务。
- 任务清单只记录近期可推进事项，不记录远期路线图。
- 不把 [PROJECT_PLAN.md](docs/project/PROJECT_PLAN.md) 的 G0-G4 自动展开成任务。
- Agent 可以更新已有任务的状态、执行证据、完成或废弃原因，但不能自行新增任务。
- 每个任务必须有完成判据；没有完成判据的事项继续讨论，不进入任务清单。
- 用户写成 `TASK.md` 时，默认理解为本仓库的 [TASKS.md](TASKS.md)，除非明确要求改名。

Codex 的会话内计划只用于当前执行，不替代仓库中的 TASKS.md，也不能绕过“用户明确新增”的规则。

## 面试集合

面试集合固定使用 [INTERVIEW_QA.md](docs/project/INTERVIEW_QA.md)。

- 任何可能在面试中被追问的设计、实现、实验或取舍，应同步为一个高压问题或更新既有回答。
- 每个回答必须区分 `ROADMAP`、`SOURCE_VERIFIED`、`IMPLEMENTED_UNVALIDATED` 和 `EXPERIMENTALLY_VALIDATED`。
- 没有代码、测试、双 worker trace 或实验 artifact 支撑的内容，不得写成完成时。
- 改变对外叙述、ownership、性能 claim、失败边界或停止条件的决策必须进入面试集合。
- 面试集合只派生和压缩证据，不得创造比 STATUS、implementation evidence 或 raw artifact 更高的 claim。

## 修改与验证

- 小步修改，避免提前抽象；保留与任务无关的用户改动。
- 修改 claim、Gate、STOP 或实验口径时，必须同步 [STATUS.md](STATUS.md)，必要时同步 [INTERVIEW_QA.md](docs/project/INTERVIEW_QA.md)。
- 声称完成前运行 `make check`，并报告实际命令和结果；涉及外部运行时的工作还必须执行对应 Gate 验证，`make check` 不能代替它。
- 不提交私有 source material；private 目录由 `.gitignore` 保护。
