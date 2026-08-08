# Durable Decisions

本文件记录已由项目 owner 确认、会约束后续实现或 claim 的决议。它不替代
[PROJECT_PLAN.md](PROJECT_PLAN.md) 的 Gate/STOP，也不把决议升级为实现或运行时证据；实际状态仍以
[STATUS.md](../../STATUS.md) 为准。

## D1 — 保留 new-Put payload 指标，并授权最小观察 patch

**日期：** 2026-08-08
**状态：** DECIDED；未实现、未运行时验证。

### 采用

保留 `new_physical_put_bytes` 作为将来 payload/capacity-efficiency 结论的唯一“新物理写入”分子。
允许在 pinned Mooncake `6041a609a8c3af35e778f70db344f145c2914980` 的
`OBJECT_ALREADY_EXISTS -> success` 归约**之前**增加独立、trace-only 的 observation patch。

该 patch 只可为每个实际 Put attempt 的 physical object 追加：opaque `attempt_id`、不可逆
object-key hash、buffer size、原始终态原因（`new_put`、`race_existing` 或 `put_failure`）和本地单调
序号。`exists_skip` 仍由 SGLang adapter 的 precheck trace 记录，二者以 opaque ID join。它不得改变
Put/Get 返回值、object key、锁、队列顺序、重试、传输、网络协议或 Store 状态；trace-disabled 与
trace-enabled 必须有独立的非干扰性 oracle。

### 拒绝

- 用 `precheck-miss + put_result=0` 推断本 writer 产生新物理 Put；该映射在固定 Mooncake commit 中非单射。
- 用 `completed_put_bytes` 这种未说明 race 归属的名称作为“减少写入”的分子。
- 因为新增观测而改变 Mooncake 或 SGLang 的行为路径，或扩展为新的 backend/数据面。

### 翻案条件与 Gate 影响

若无法在归约前取得原因码，或 trace-enabled 改变任何行为 oracle，停止该 payload 分支并修改
canonical metric contract；不得用模糊 success 字节替代。patch 与其 non-interference 证据完成前，
`BYTE_RECONCILE` 和一切 new-Put payload claim 仍为 STOP。它不阻塞 stock restore source/runtime probe，
但阻塞以 payload efficiency 为目标的 G0 通过声明。

### 一手依据

Mooncake 在固定 commit 将 `OBJECT_ALREADY_EXISTS` 归约为成功；现有 Python terminal `0` 因而不能区分
race-existing 与新 Put。详见 [G0 source audit](../implementation/G0_SOURCE_RUNTIME_AUDIT.md#race-observation-limitation)。

## D9 — G0 的 prefix group 一律 all-or-none

**日期：** 2026-08-08
**状态：** DECIDED；未实现、未运行时验证。

### 采用

G0 的 decision unit 是“root 或可证明已驻留 anchor + 有序 logical pages”的完整连续 group；一个 decision
要么使整个 group `ADMIT_TO_L3`，要么使整个 group `DROP`。如果当前 callback 不能给出完整、可证明可达的
group，则整体 DROP。

### 拒绝

- 首个 DROP 后再强制 suffix DROP 的逐页策略；它对 G0 没有额外可验证价值，却引入更多状态与测试面。
- 远端目录、metadata RPC 或 read-path repair 来修补 policy-induced hole。

### 翻案条件与 Gate 影响

只有出现按页选择能带来必要证据、且能独立证明闭包与生命周期的后续项目，才重新讨论逐页规则。当前
`PREFIX_CLOSURE` 必须证明任何 admitted group 都不存在 policy-induced unreachable suffix。

### 一手依据

固定 SGLang remote lookup 在首个缺失 page 停止；源码只证明该 first-miss 行为，并未提供 L3 admission
policy。详见 [G0 source audit](../implementation/G0_SOURCE_RUNTIME_AUDIT.md#prefix-closure-and-first-miss)。

## D10 — failure/async 合同保持严格，不伪造覆盖

**日期：** 2026-08-08
**状态：** DECIDED；未实现、未运行时验证。

### 采用

G0 必须保留正常成功、sequential dedup、two-writer overlap、policy exception fail-open 与
shutdown/detach 的 terminal artifact。每条 admitted path drain 后，`backup_queue`、`ack_backup_queue`、
`ongoing_backup` 与 host protection 都必须回到基线；`DROP` 则不得创建这些 L3 状态。

若没有官方且非侵入式的 Put-failure injector，failure coverage 只能记录为 `INCONCLUSIVE`。不得用 mock
backend、聚合成功字节、或进程退出作为 runtime failure lifecycle 的替代证据；在这种情况下不得声称
`G0-RUNTIME VALIDATED`。

本项目不会为该 seam 新增 request-cancellation 协议、epoch 或自建 stale-completion state machine。原因是
decision 在 `StorageOperation` 创建之前发生：DROP 没有异步 owned state，而 admitted operation 的完成、
ack 与 detach 清理仍由 upstream lifecycle 拥有。`shutdown/detach` cleanup 是 required runtime case；若它
暴露 late ack、残留保护或泄漏，即为 G0 FAIL/STOP，不得以新状态机掩盖。这里的 `NOT_APPLICABLE` 仅指
**新增** request-cancellation/epoch 机制，不免除现有 async cleanup 的验证。

### 拒绝

- 将 failure injector 不可得写成 PASS。
- 将 upstream partial-batch 未实现的行为包装为已覆盖的 partial-success 语义。
- 因单一 admission hook 引入全局 cancellation registry、epoch fencing 或另一个 async owner。

### 翻案条件与 Gate 影响

若固定上游源码或实际运行显示该写路径已有可传递的 request cancellation/epoch contract，或 trace context
本身会在 detach 后产生生命周期所有权，则先暂停实现并重新审计；不得静默扩大 scope。否则，完整 G0
结论严格取决于真实 failure evidence，且 D1 patch 完成后 race/dedup 还须按 pre-collapse 原因码对账。

### 一手依据

固定 SGLang 在 backup ack 时释放 `ongoing_backup`/host protection，并在 detach/shutdown 有强制释放路径；
同时 controller 对失败 batch 会中断，且明确未实现 partial success。详见
[G0 source audit](../implementation/G0_SOURCE_RUNTIME_AUDIT.md#async-cleanup-facts)。
