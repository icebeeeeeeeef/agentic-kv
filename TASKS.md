# Short-term Tasks

本文件只记录用户明确授权加入的近期任务，不承载项目路线图。项目 Gate 与阶段依赖以 [PROJECT_PLAN.md](docs/project/PROJECT_PLAN.md) 为准，实际完成状态以 [STATUS.md](STATUS.md) 为准。

## Completed

### T1 — 冻结 payload、failure 与异步边界合同（COMPLETED 2026-08-08）

- Scope：裁决 D1 的 new-Put payload 观测口径；明确 D10 的 failure 覆盖策略；审核 cancellation / stale completion 在该 L2→L3 写路径中是 required 还是 `NOT_APPLICABLE`。
- Depends on：无。
- Completion：在 `docs/project/DECISIONS.md` 记录采用项、拒绝项、翻案条件和 claim/Gate 影响；`PROJECT_PLAN.md`、`STATUS.md` 与 G0 文档不再对 payload 或 failure 的可验证性作互相矛盾的表述。
- Evidence：[D1 / D9 / D10 决议](docs/project/DECISIONS.md)、[pinned source audit](docs/implementation/G0_SOURCE_RUNTIME_AUDIT.md)、canonical/G0 plan 同步 diff；`make check` 通过。

### T2 — 收口 canonical 工程完成定义与 Gate 顺序（COMPLETED 2026-08-08）

- Scope：在 `PROJECT_PLAN.md` 明确 runtime backbone、flagship evidence 与 optional policy-positive 三层完成定义；写入工程最低交付线、判断 A→B→C 顺序和反向删除测试；统一 trace-only 先于 behavior hook 的执行顺序；拆分 claim state 与 Gate outcome。
- Depends on：T1。
- Completion：README、STATUS、PROJECT_PLAN 与 G0 execution plan 对唯一机制、上游/owned 边界、Mooncake source/runtime 状态、payload metric 和 G0 顺序完全一致；删除 VALUE_DENSITY 后仍存在明确的 runtime engineering acceptance。
- Evidence：[三层完成与删除测试](docs/project/PROJECT_PLAN.md#32-三层完成定义)、[claim/Gate 正交字段](docs/project/PROJECT_PLAN.md#141-claim-state-与-gate-outcome-是正交字段)、[G0 trace-first plan](docs/implementation/G0_EXECUTION_PLAN.md)、入口文档交叉审查；`make check` 通过。

### T3 — 建立 durable decision routing，并更新派生口径（COMPLETED 2026-08-08）

- Scope：发布 `docs/project/DECISIONS.md` 作为已决约束入口；将 D1/D9/D10 从 `G0_DISCUSSION_LIST.md` 移为链接；更新 docs/research map、INTERVIEW_QA 和旧 selection/market 文档的 current/historical 标识。
- Depends on：T1、T2。
- Completion：一个新 agent 仅阅读 README、STATUS、PROJECT_PLAN、DECISIONS 即可获得当前机制、未决项、claim state 和停止条件；旧 eviction/FP8 选题材料不会被误读为当前主线。
- Evidence：[durable decision record](docs/project/DECISIONS.md)、[discussion routing](docs/implementation/G0_DISCUSSION_LIST.md)、[documentation map](docs/README.md)、[high-pressure interview Q&A](docs/project/INTERVIEW_QA.md)；`make check` 通过。

### T4 — 将 upstream patch provenance 变为仓库可审查 artifact（COMPLETED 2026-08-08）

- Scope：定义并落地有序 patch-series 目录、upstream SHA、执行顺序、校验命令和 patch manifest；保留外部 checkout，但不 vendor upstream。
- Depends on：T1、T2。
- Completion：仓库已固定三类 series 的 upstream SHA、执行顺序、目录、导出/应用/回滚命令，并有本地测试防止把 `PLANNED` 条目误称为 patch。实际实现任务必须在同一 contract 下物化相应 `git format-patch`、hash 与 fresh-worktree apply verification；在此之前不得声称 patch 已存在或可复现。
- Evidence：[patch manifest](patches/manifest.json)、[materialization contract](patches/README.md)、[local provenance test](tests/test_patch_provenance.py)；`make check` 通过。

## Closed / STOP

### T5 — 完成 G0 stock shared-L3 runtime 与 pre-D1 投资筛查，或以 artifact STOP（STOP 2026-08-08；旧 sentinel 合同已由 D14 取代）

- Historical scope：本任务最初将 stock A→B restore 后的两个 one-shot sentinel 作为 pre-D1 投资筛查；该 workload/Gate 合同已被 D14 的 `S1 RESTORE_VALUE_REGION`、sticky-reuse `S2 PUBLICATION_COST_ENVELOPE` 与 `S3 CAPACITY_EXTERNALITY` 取代，旧 sentinel 不得执行。
- Depends on：T1、T4。
- Outcome：当前 macOS/arm64 executor 无 NVIDIA GPU、Python 3.11、container runtime 或 pinned upstream checkout；在未启动任何 upstream 进程前形成 local execution-path STOP，C0 predicates=`NOT_EVALUATED`。此结果不评价目标 Linux compatibility，也不允许进入 hook。
- Resume：当前入口以 D18 和 `PROJECT_PLAN` 为准。目标 Linux CUDA 环境先运行首次 C0：build/API/write-trigger admission 后，A Put → fresh B-L3 → fresh B-no-L3 必须同时证明 `RESTORE_PATH_PASS` 与 `REMOTE_VALUE_SURVIVES`。只有首次 C0 `PASS`，才创建 fresh C1 cohort 并重做 C0；随后 finite source/runtime-audit X*、baseline-only freeze、S1 与 sticky-reuse S2/S3。只有 S1 存活、目标 remote Get 非近零、sticky-reuse publication mass 达到冻结阈值且 S2/S3 至少一个留下有效 signal，才自动解锁 T6；S1 STOP、remote Get≈0、mass 过小或 S2/S3 双 valid-false 均在 owned patch 前收口。D12 仅保留窄 payload/resource 例外。不得复用本次 macOS STOP、首次 C0 状态或 artifact 作为 target build、C1 eligibility、prefill survival 或 D14 Gate 证据。
- Evidence：[tracked STOP record](docs/implementation/G0_T5_LOCAL_PREFLIGHT_STOP.md)、`experiments/runs/local-macos-arm64-preflight-20260808T093232Z/` immutable local bundle、STATUS 更新。

## Completed contract closures

### T9 — 收口 C0 Restore Qualification 实验合同（COMPLETED 2026-08-11）

- Scope：只讨论并冻结首次目标 Linux TCP cohort 的 C0 功能性请求：同一共享 prefix 的构造与 page-alignment 证据、A Put、B 本地冷态、fresh B-cold no-L3 control、固定 decode/output oracle、token accounting 与单值 outcome/STOP-next-action 分类。不得租机、启动上游、改源码、添加 trace/policy 或以 TTFT 替代 token-level oracle；具体 realization 以后续 D18 修订为准。
- Depends on：T5 的 macOS STOP 记录、[G0 环境部署合同](docs/implementation/G0_DEPLOYMENT_ENVIRONMENT_DISCUSSION.md)；不依赖任何尚未取得的 Linux runtime result。
- Completion：形成一个与 [G0 execution plan Task 1](docs/implementation/G0_EXECUTION_PLAN.md) 一致的 C0 输入/控制/观测/判定合同，并显式列出哪些值必须在 target runtime probe 后冻结。合同必须保持 `RESTORE_PATH_PASS` 与 `REMOTE_VALUE_SURVIVES` 为两个独立门；C0 PASS 只能称 restore qualification，不能称 T5 或 G0 完成。
- Evidence：[C0 Restore Qualification Contract](docs/implementation/G0_C0_RESTORE_QUALIFICATION_CONTRACT.md)、canonical Task 1 oracle、C0 cohort contract 和 future realized manifest schema。该合同是 owner 决策，不是 Linux runtime artifact。

### T10 — 收口 C1 的 D14 survival preregistration 合同（COMPLETED 2026-08-11）

- Scope：只讨论 C1 在通过并重做 C0 preflight 后的 baseline-only calibration、X* 的实际构造、S1 `RESTORE_VALUE_REGION`、sticky-reuse S2/S3 的 workload/pressure witness、容量坐标、paired-arm 公平性、负载/knee、统计区间、重复预算、workload split、冻结/checksum 与有效 null 规则。不得观察 treatment 后回填阈值，不得把网络/Store NIC 诊断当作 payload attribution，也不得将 future label 用于 `TARGET_HELD_OUT`。
- Depends on：T9 的 C0 合同；实际 C1 execution 必须在自己的 fresh cohort 重做 C0 preflight 并保留自身 `RESTORE_PATH_PASS` + `REMOTE_VALUE_SURVIVES` artifact。
- Completion：`experiments/manifests/d14-survival-preregistration.example.json` 的每个当前 `null` 字段都有明确来源、冻结时点与不能在 treatment 后修改的理由；S1 的 hard-veto、S2/S3 的 `true`、有效 `false` 与 `INCONCLUSIVE` 可按 [G0 execution plan Active Task 2](docs/implementation/G0_EXECUTION_PLAN.md#active-task-2-prepare-and-run-d14-s2s3-survival-gates) 独立判定；X* 未验证 component 明确排除而非假设存在。只有 S1 存活、remote Get 非近零、sticky-reuse mass 达到冻结阈值且 S2/S3 至少一项为 signal 才可能解锁 T6；双 valid-false、remote Get≈0 或 mass 过小触发 D14 的 pre-implementation STOP。
- Evidence：[D14 Survival Preregistration Contract](docs/implementation/G0_D14_SURVIVAL_PREREGISTRATION_CONTRACT.md)、[manifest schema](experiments/manifests/d14-survival-preregistration.example.json)、workload/config hash contract、baseline-only artifact checklist、X* source/runtime construction record 和 canonical D14 links。合同只冻结规则与来源，所有 runtime field 保持未决。

### T11 — 收口短生命周期 cohort 的租机前执行与证据合同（COMPLETED 2026-08-11；FIRST-C0 SCOPE REVISED 2026-08-12）

- Scope：冻结首次 C0 的输入、目标 host admission、A/C/B 与 no-L3 control 顺序及证据 handoff 边界。D18 取代 D17 对首次前置范围的裁决：内容寻址输入与单次 runbook 是租机前工作；host runtime 事实留到租机后；OCI/OSS、双物理 GPU、same-AZ、自动 collector/classifier 与 D16 lifecycle controls 均不是首次 C0 correctness Gate。
- Depends on：[G0 环境部署合同](docs/implementation/G0_DEPLOYMENT_ENVIRONMENT_DISCUSSION.md)；T9/T10 的输入与 artifact 要求。
- Completion：D18 已将首次入口收敛为内容寻址 input bundle、单次 C/worker runbook、raw capture/checksum/off-host handoff，以及租机日的最小 target-host probe；A/B 可在同一 GPU 上使用独立 lifecycle 顺序运行。没有实现、cloud/runtime artifact 或租机授权被本合同隐含产生。
- Evidence：[C0-first execution contract](docs/implementation/G0_PRE_RENTAL_EXECUTION_CONTRACT.md)、[deployment contract](docs/implementation/G0_DEPLOYMENT_ENVIRONMENT_DISCUSSION.md)、T9/T10 artifact contracts、[D16–D18](docs/project/DECISIONS.md)。合同是 owner 决策，不是 cloud/runtime artifact 或租机授权。

### T12 — 作出“允许开始租机”的 G0 pre-rental ruling（COMPLETED 2026-08-12；C0-first `NOT_READY_TO_RENT`）

- Scope：对 T9–T11 做 authority-first 交叉审查，并按 D18 的删除测试区分 correctness prerequisite、租机日 runtime fact 与 C0 后 hardening；确认没有把 source fact、owner decision、runtime artifact 与 inference 混写，也不把 C0、C1 或 TCP 结论外推到 RDMA/生产。
- Depends on：T9、T10、T11。
- Outcome：原 full-lifecycle harness、OCI/OSS 强制交付、双物理 GPU、same-AZ、独立 collector/classifier 均不再是首次 C0 blocker。当前 `NOT_READY_TO_RENT` 的精确 blocker 仅是内容寻址 input bundle 与单次 C0 runbook/raw-capture/checksum/off-host handoff 尚未物化并经 owner review。build/API/config、write threshold、GPU、C segment 和 private TCP 故意留在租机后、第一条 request 前；不能把它们伪造成租机前已通过。结论不升级任何 runtime claim。
- Evidence：[D18](docs/project/DECISIONS.md)、[C0-first execution contract](docs/implementation/G0_PRE_RENTAL_EXECUTION_CONTRACT.md)、[C0 contract](docs/implementation/G0_C0_RESTORE_QUALIFICATION_CONTRACT.md)；authority-first adversarial review。

## Active

### T6 — 实现并验证 trace-only PathTruth correlation（BLOCKED by T5 STOP / pre-D1 ruling）

- Scope：在不计算或应用 admission action 的前提下，实现 `observation → operation → batch/attempt → physical adapter result` 的 opaque ID propagation，并比较 stock、trace-disabled、trace-enabled 的行为等价性；T7 才在同一 trace record 追加 decision。
- Depends on：T4、T5，且 D14 的 S1 存活、S2/S3 至少一个留下有效 signal；双 valid-false 后只能由新的 owner-approved resource-objective record 依 D12 在 D1 结果未知时冻结真实资源目标、预算、物质性判据与有界 observation-only 计划，作为第一次例外授权。该授权只解锁 T6，不解锁 T7。
- Completion：trace 不改变 key、队列顺序、Put/Get result、输出或 terminal cleanup；每个 observed upstream operation 可确定性关联到一个终态分类，且无 prompt/token 明文落盘。
- Evidence：upstream focused tests、non-interference run bundle、JSONL schema 与 byte/reason-code contract。

### T7 — 实现最小 fail-open L3 admission seam 与运行时不变量

- Scope：在 L2 ack 后、`write_storage` 前实现 `ALWAYS_ADMIT`、`ALWAYS_DROP`、`POLICY_ERROR_FAIL_OPEN`；采用 T1 冻结的 prefix-closure group 规则，并验证 async cleanup。
- Depends on：T4、T5、T6；正常 D14-surviving 分支在 T6 通过后继续。双-null payload 例外分支还必须由 T6 artifact 证明超过预注册阈值且映射回资源目标的 new-Put/写后未读浪费，并取得第二次 owner ruling。
- Completion：ALWAYS_ADMIT 与 stock path 功能等价；ALWAYS_DROP 保留 L2 且不创建 L3 operation/queue/protection/Put；fail-open 回落 upstream；closure、duplicate/race、delay、shutdown/detach 和 T1 适用的异常场景都有诚实的 PASS/FAIL/INCONCLUSIVE 结论。
- Evidence：upstream focused tests、G0 matrix run bundles、queue/ref/protection terminal snapshots 和 STATUS/INTERVIEW_QA 更新。

### T8 — 对 runtime backbone 做独立收口审查

- Scope：复查 T1–T7 的 claim state、文档一致性、patch provenance、删除测试和复现实验路径；确认能否进入 G1/G2a，而不是默认开始 candidate policy。
- Depends on：T1–T7。
- Completion：输出 `PASS`、`STOP` 或 `INCONCLUSIVE` 的 G0 ruling；只有所有 required runtime artifacts 与 `make check` 都通过时才允许写 `G0-RUNTIME VALIDATED`。
- Evidence：G0 outcome record、manifest/checksum、最终 diff 审查和新鲜 `make check` 输出。

## Rules

- 新任务必须由用户明确要求加入。
- 每项任务必须包含 scope、完成判据和证据位置。
- Agent 可以更新已有任务的状态和证据，但不能自行把 G0-G4 或研究建议展开为新任务。
- 完成、废弃或阻塞时保留结论和证据链接，不用口头状态覆盖文件状态。
