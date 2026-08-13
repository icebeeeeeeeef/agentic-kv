# agentic-kv

面向 AI Infra / KV Cache 团队的个人工程项目：

> 在 SGLang HiCache + Mooncake shared L3 上，固定 L1/L2 的算法、容量、配置与 write policy，只研究一个行为变化：完成 L1 → L2 备份后，当前 prefix-closed、speculative KV group 是否继续**发布**到共享 L3。

项目正式术语为 **Shared-L3 Publication Admission**。它只处理 speculative/opportunistic publication：`L2 ack → prefix closure → ADMIT_TO_L3 | DROP → (only ADMIT) StorageOperation / Mooncake Put`。`DROP` 位于 `StorageOperation` 前，因而不拥有异步 L3 state。HiCache/Mooncake 是 upstream substrate；SGLang Agentic KV 若未来提供明确 intent，只是 complement/workload producer，当前 mainline 的 intent-coupled set 为空，未来不得静默 DROP。

## 当前状态

- 裁决：Conditional Select
- 阶段：首次 C0 restore qualification 已通过并封存；fresh C1 尚未开始
- 已实现代码：仓库 smoke skeleton，以及首次 C0 的内容寻址输入和一次性执行/证据工件；尚无 runtime hook
- Mooncake source：`v0.3.12.post1` candidate（commit `6041a609a8c3af35e778f70db344f145c2914980`）已 SOURCE_VERIFIED；固定 r6 TCP/direct-I/O/L20 拓扑已 EXPERIMENTALLY_VALIDATED，不构成通用 compatibility claim
- 已验证：first-C0 stock A → external C → fresh B 的 `RESTORE_PATH_PASS` 与 `REMOTE_VALUE_SURVIVES`；部署 blocker 复盘见 [`G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md`](docs/implementation/G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md)
- 未验证：fresh-C1 C0、S1–S3、D1 trace-only observation、SGLang trace correlation、L3 admission hook、候选策略及任何性能收益

不要把 ROADMAP、SOURCE_VERIFIED、IMPLEMENTED_UNVALIDATED 与 EXPERIMENTALLY_VALIDATED 混为一谈。

首次目标环境执行服从 D18 的 correctness-only 入口：租机前只物化内容寻址输入和一次性 C0 runbook/raw-evidence
handoff；租机后才核验 build/API/write threshold/GPU/Store/private TCP，并立即运行 stock A → external C → fresh B
及 no-L3 control。OCI/OSS、自动 classifier/finalizer、双物理 GPU与同 AZ 都不是首次 C0 correctness Gate；入口失败
只记 `BLOCKED_BEFORE_C0`，不得伪造 shared-L3 `FAIL/STOP`。C0 `PASS` 后 C1 仍须 fresh cohort 重做 C0。

当前先执行 D14 的替代攻击：`S1 RESTORE_VALUE_REGION` 是一票否决；随后在 sticky-reuse（**待对 pin 复核**的 stock selective 放行条件成立、却低 remote reuse value）上运行 `S2 PUBLICATION_COST_ENVELOPE` 与 `S3 CAPACITY_EXTERNALITY`。one-shot/unique-heavy 只作为 stock frontier X* 预期能过滤的负控制，不能承重独立 L3-only gate 的价值。X* = stock `write_through_selective` + sufficient L2 + 经 source/runtime 证明可用的 stock quota/eviction controls；它虽不是相同 L2 treatment 的因果基线，却是必须正面击败的简单替代。离线 replay 不得推断 TTFT/Goodput；只有真实 online cheating oracle 也无法物质性击败 X* 时，才以 STOP 收口。

当前 brainstorm 冻结：不提前设计 Agent hints、`VALUE_DENSITY`、stale-publication、page-level admission、router 或 eviction。只有后续在线 residual 与新的 owner decision 才可重开。外部讨论中尚未对本仓库 pins 独立核验的 upstream 动态统一记为 `RESEARCH_REVIEW / SOURCE_TO_REVERIFY`，不是新的 claim state，不能升级为 `SOURCE_VERIFIED` 或 `EXPERIMENTALLY_VALIDATED`。

Conditional admission ledger 不属于 G1 或 runtime backbone：只有 G2a 用各 arm 自身的在线 trace 证明可行动
residual，且 online oracle-vs-X* 未停止方向后，才在 G2b 实现它并用于候选拒绝；它不默认实现 `VALUE_DENSITY`，G3 在线 A/B 保留最终因果裁决权。

## 唯一权威入口

1. docs/project/PROJECT_EVALUATION_SOP.md：稳定的方法论；约束选题、能力信号、证据、主张与叙事
2. docs/project/PROJECT_PLAN.md：将 SOP 落实为本项目的问题、边界、Gate、STOP 与实验合同
3. STATUS.md：当前实际完成状态和下一步
4. TASKS.md：仅记录用户明确授权的近期任务；不能改写上位 Gate/STOP
5. docs/implementation/：固定源码事实、实验合同与 runtime artifacts；低层合同不能改写上位 Gate/STOP
6. docs/project/DECISIONS.md：owner 已决约束；`DECIDED` 不是 runtime evidence
7. docs/README.md：文档地图与 claim-state 词典
8. AGENTS.md：在本仓库工作的行为约束
9. docs/project/INTERVIEW_QA.md：由当前证据派生的面试防守集合

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
