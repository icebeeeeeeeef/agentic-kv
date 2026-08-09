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

### T5 — 完成 G0 stock shared-L3 runtime 与 pre-D1 投资筛查，或以 artifact STOP（STOP 2026-08-08）

- Scope：在目标 Linux GPU 环境固定 SGLang/Mooncake build identity，建立 external Store C，分别证明 stock Worker A Put → fresh Worker B remote Get 的 `RESTORE_PATH_PASS` 与 token-level `REMOTE_VALUE_SURVIVES`；随后在不打 patch 的前提下运行 `WRITE_COST_SENTINEL` 与 `CAPACITY_PRESSURE_SENTINEL`，决定是否值得自动投入 D1。
- Depends on：T1、T4。
- Outcome：当前 macOS/arm64 executor 无 NVIDIA GPU、Python 3.11、container runtime 或 pinned upstream checkout；在未启动任何 upstream 进程前 STOP。此结果不评价目标 Linux compatibility，也不允许进入 hook。
- Resume：用户提供或切换到目标 Linux CUDA 环境后，重新执行完整 T5；除 Put/Get、B 冷态与输出一致外，还必须用相同请求的 B-cold no-L3 control 证明 storage-cached tokens 非零且 uncached/prefill tokens 实际减少。只有该结果通过后，才按 G0 execution plan 先用 baseline/control 完成并 checksum 冻结 stock-sentinel preregistration，再运行 paired arms；至少一个信号的区间下界越过物质性阈值才自动解锁 T6。只有两项区间上界都低于阈值才是触发 D12 的有效双 null；任一关键压力/公平性条件不可证或区间在冻结预算后仍跨阈值时为 `INCONCLUSIVE`。不得复用本次 STOP 作为任何 build、Store、A→B 恢复、prefill survival 或 sentinel 结论。
- Evidence：[tracked STOP record](docs/implementation/G0_T5_LOCAL_PREFLIGHT_STOP.md)、`experiments/runs/local-macos-arm64-preflight-20260808T093232Z/` immutable local bundle、STATUS 更新。

## Active

### T6 — 实现并验证 trace-only PathTruth correlation（BLOCKED by T5 STOP / pre-D1 ruling）

- Scope：在不计算或应用 admission action 的前提下，实现 `observation → operation → batch/attempt → physical adapter result` 的 opaque ID propagation，并比较 stock、trace-disabled、trace-enabled 的行为等价性；T7 才在同一 trace record 追加 decision。
- Depends on：T4、T5，且至少一个 stock pre-D1 sentinel 留下有效的稳定端到端信号；双 null 后只能由新的 owner-approved resource-objective record 依 D12 在 D1 结果未知时冻结真实资源目标、预算、物质性判据与有界 observation-only 计划，作为第一次例外授权。该授权只解锁 T6，不解锁 T7。
- Completion：trace 不改变 key、队列顺序、Put/Get result、输出或 terminal cleanup；每个 observed upstream operation 可确定性关联到一个终态分类，且无 prompt/token 明文落盘。
- Evidence：upstream focused tests、non-interference run bundle、JSONL schema 与 byte/reason-code contract。

### T7 — 实现最小 fail-open L3 admission seam 与运行时不变量

- Scope：在 L2 ack 后、`write_storage` 前实现 `ALWAYS_ADMIT`、`ALWAYS_DROP`、`POLICY_ERROR_FAIL_OPEN`；采用 T1 冻结的 prefix-closure group 规则，并验证 async cleanup。
- Depends on：T4、T5、T6；正常 sentinel-positive 分支在 T6 通过后继续。双-null payload 例外分支还必须由 T6 artifact 证明超过预注册阈值且映射回资源目标的 new-Put/写后未读浪费，并取得第二次 owner ruling。
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
