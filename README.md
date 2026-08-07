# agentic-kv

面向 AI Infra / KV Cache 团队的个人工程项目：

> 在 SGLang HiCache + Mooncake shared L3 上，固定 L1/L2 的算法、容量、配置与 write policy，只研究一个行为变化：完成 L1 → L2 备份后，当前 prefix-closed KV group 是否继续写入共享 L3。

## 当前状态

- 裁决：Conditional Select
- 阶段：仓库初始化完成，G0 尚未开始
- 已实现代码：仅仓库 smoke skeleton
- 未验证：跨 worker shared-L3 restore、L3 admission hook、payload instrumentation、候选策略及任何性能收益

不要把 ROADMAP、SOURCE_VERIFIED、IMPLEMENTED_UNVALIDATED 与 EXPERIMENTALLY_VALIDATED 混为一谈。

## 唯一权威入口

1. docs/project/PROJECT_PLAN.md：项目问题、边界、Gate、STOP、实验与叙事合同
2. STATUS.md：当前实际完成状态和下一步
3. docs/README.md：研究材料的权威层级与阅读顺序
4. AGENTS.md：在本仓库工作的行为约束
5. TASKS.md：仅记录用户明确授权的近期任务
6. docs/project/INTERVIEW_QA.md：由当前证据派生的面试防守集合

若研究评审材料与 PROJECT_PLAN.md 冲突，以 PROJECT_PLAN.md 为准；若 PROJECT_PLAN.md 描述计划、STATUS.md 描述实际进度，以 STATUS.md 的完成状态为准。

## 明确不做

- 不修改 L1/L2 eviction、router 或 remote eviction
- 不实现 Mooncake backend、RDMA/GDR、量化、稀疏化或 metadata HA
- 不构造完整 L1/L2/L3 simulator
- 不把 conditional admission ledger 当成跨策略因果证据
- 不提前建设通用 policy framework、控制平台或第二套 cache backend

## 仓库布局

    docs/project/             唯一 canonical 项目规划
    docs/research/            市场、选题、证据和历史对抗评审
    docs/implementation/      通过 Gate 后产生的源码审计与实施文档
    src/agentic_kv/           本项目 owned code
    tests/                    快速、确定性的本地测试
    experiments/              manifest 规范；运行结果不直接入 Git
    results/                  仅保留目录，原始输出默认忽略
    TASKS.md                  用户控制的短期任务清单

## 本地检查

    make check

当前检查只验证包可导入和仓库 smoke test。它不代表 G0 或任何实验 Gate 已通过。
