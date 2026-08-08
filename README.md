# agentic-kv

面向 AI Infra / KV Cache 团队的个人工程项目：

> 在 SGLang HiCache + Mooncake shared L3 上，固定 L1/L2 的算法、容量、配置与 write policy，只研究一个行为变化：完成 L1 → L2 备份后，当前 prefix-closed KV group 是否继续写入共享 L3。

## 当前状态

- 裁决：Conditional Select
- 阶段：仓库初始化完成，G0 尚未开始
- 已实现代码：仅仓库 smoke skeleton
- Mooncake source：`v0.3.12.post1` candidate（commit `6041a609a8c3af35e778f70db344f145c2914980`）已 SOURCE_VERIFIED；目标 Linux build/API 与 pinned SGLang adapter 的 runtime compatibility 仍未验证
- 未验证：跨 worker shared-L3 restore、D1 trace-only observation、SGLang trace correlation、L3 admission hook、候选策略及任何性能收益

不要把 ROADMAP、SOURCE_VERIFIED、IMPLEMENTED_UNVALIDATED 与 EXPERIMENTALLY_VALIDATED 混为一谈。

项目的工程完成不等于“VALUE_DENSITY 获胜”：先完成可独立审查的 runtime backbone（trace-only
non-interference、最小 fail-open hook、closure/lifecycle oracle），再形成可接受负结果的旗舰证据闭环；
VALUE_DENSITY 只有在 G2a 后才是可选候选。执行顺序固定为 stock restore → D1 observation →
SGLang trace-only → behavior hook，详见 [PROJECT_PLAN.md](docs/project/PROJECT_PLAN.md#32-三层完成定义)。

## 唯一权威入口

1. docs/project/PROJECT_EVALUATION_SOP.md：稳定的方法论；约束选题、能力信号、证据、主张与叙事
2. docs/project/PROJECT_PLAN.md：将 SOP 落实为本项目的问题、边界、Gate、STOP 与实验合同
3. STATUS.md：当前实际完成状态和下一步
4. docs/project/DECISIONS.md：已由 owner 确认、会约束实现或 claim 的 durable 决议
5. docs/README.md：文档权威层级与阅读顺序
6. AGENTS.md：在本仓库工作的行为约束
7. TASKS.md：仅记录用户明确授权的近期任务
8. docs/project/INTERVIEW_QA.md：由当前证据派生的面试防守集合

若项目选择、证据标准或叙事方法与 SOP 冲突，以 SOP 为准并修订项目计划；若 PROJECT_PLAN.md 描述计划、STATUS.md 描述实际进度，以 STATUS.md 的完成状态为准。研究评审材料不能反向覆盖上述文档。

## 明确不做

- 不修改 L1/L2 eviction、router 或 remote eviction
- 不实现 Mooncake backend、RDMA/GDR、量化、稀疏化或 metadata HA
- 不构造完整 L1/L2/L3 simulator
- 不把 conditional admission ledger 当成跨策略因果证据
- 不提前建设通用 policy framework、控制平台或第二套 cache backend

## 仓库布局

    docs/project/             稳定评审方法论与当前 canonical 项目契约
    docs/research/            市场、选题、证据和历史对抗评审
    docs/implementation/      通过 Gate 后产生的源码审计与实施文档
    patches/                  外部 upstream 的有序 format-patch provenance（当前仅 PLANNED）
    src/agentic_kv/           本项目 owned code
    tests/                    快速、确定性的本地测试
    experiments/              manifest 规范；运行结果不直接入 Git
    results/                  仅保留目录，原始输出默认忽略
    TASKS.md                  用户控制的短期任务清单

## 本地检查

    make check

当前检查只验证包可导入和仓库 smoke test。它不代表 G0 或任何实验 Gate 已通过。
