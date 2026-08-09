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
但阻塞以 payload efficiency 为目标的 G0 通过声明。D1 只固定“若进入 payload 归因时允许怎样观测”；实际何时
允许实施仍受 [D12](#d12--两个-stock-sentinel-有效-null-时在实现前-stop-payload-例外分两级授权) 的 pre-D1
投资裁决约束。

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

## D12 — 两个 stock sentinel 有效 null 时在实现前 STOP，payload 例外分两级授权

**日期：** 2026-08-09
**状态：** DECIDED；sentinel、D1 与 hook 均未运行时验证。

### 采用

若 `WRITE_COST_SENTINEL` 与 `CAPACITY_PRESSURE_SENTINEL` 都在各自预注册压力坐标、公平对照和重复要求下得到有效
`false`，则 Goodput/TTFT admission 主线在 D1 前 `STOP`。该结果只形成 shared-L3 characterization 与
pre-implementation 方向筛查负结果，不满足 Runtime backbone（R）或 Flagship evidence closure（F）；不得为了
展示 runtime 工程量自动实现 D1、trace correlation 或 behavior hook。

“有效 `false`”不是“没有统计显著差异”：必须在查看 treatment 前用 baseline-only calibration 冻结 workload、
knee、capacity coordinate、`Goodput@TTFT-SLO`、工程物质性阈值、paired-run 区间方法与有限重复预算；所有压力/
公平前提成立后，预注册单侧效应区间的上界低于物质性阈值，才有排除能力。区间仍跨阈值、预算耗尽仍看不清，或任一
前提不可证，均为 `INCONCLUSIVE`，不能触发本决议。最少 3 对重复只是执行下限，不是 null oracle。

唯一例外是 owner 在查看 D1 结果**之前**另行确认一个真实、独立的 payload/resource 目标，并冻结：payload 如何映射到
带宽、Store CPU/容量、成本或单位资源服务能力，目标资源预算，`new_physical_put_bytes` 与
`not-read-within-H` 的物质性判据，以及有界的 observation-only 证据计划。该决议只解锁 Mooncake D1
pre-collapse observation 和完成 stock payload 归因所必需的最小 SGLang opaque correlation；不解锁 behavior hook。

只有 observation-only artifact 证明 stock 路径存在超过预注册阈值、且能映射回上述资源目标的 new-Put 与写后未读浪费，
owner 才可再次评审是否解锁最小静态 hook。即使 hook 获准，payload A2 终局仍须由在线 treatment 证明
`new_physical_put_bytes` 下降、Goodput 满足预注册 non-inferiority，且收益不是 dedup、race、顺序或清池造成；
`VALUE_DENSITY` 仍不因此解锁。

### 拒绝

- 仅以“补足工程复杂度”“patch 已经设计好”或“做更深负结果”为理由继续 D1/hook。
- 把两个 sentinel 的有效 null 包装成已完成的 runtime flagship、R 层或 F 层。
- 一次 owner payload 例外同时授权 observation 和 behavior；两者之间必须保留第二次证据裁决。
- 在看到 null 后移动 workload、knee、容量压力或物质性阈值，直到出现正信号。
- 用 p-value 不显著、近零点估计或最低重复数替代有效-null 的区间排除条件。

### 翻案条件与 Gate 影响

任一 sentinel 的关键压力、公平性或实际运行条件不可证，或效应区间在冻结预算耗尽后仍跨越物质性阈值时，结果是
`INCONCLUSIVE`，不适用本决议的有效-null STOP。若合同本身必须改变，必须新建 preregistration 版本并保留旧 artifact，
不能覆盖旧结果；若至少一个 sentinel 有稳定端到端信号，则按 canonical 顺序自动进入 D1，不需要 payload 例外。
双 null 后若没有新的 owner-approved resource-objective record，T6 保持 blocked、T7 不启动，项目按终局 C 的
pre-implementation 分支收口或重新选题。

### 依据

[PROJECT_EVALUATION_SOP.md](PROJECT_EVALUATION_SOP.md) 要求真实目标函数和岗位边际价值，且明确不能靠增加功能补救失败闸门；
[PROJECT_PLAN.md](PROJECT_PLAN.md#d1-投资前的-stock-survival-sentinels) 中的两个 stock sentinel 用于在 admission-specific
instrumentation 前判断两条性能收益链是否值得投资。

## D13 — conditional ledger 仅在 G2a 通过后实现

**日期：** 2026-08-09
**状态：** DECIDED；ledger 与候选策略均未实现、未运行时验证。

### 采用

G1 只验收真实在线实验必需的 workload replayability、trace/correlation、non-interference、payload
reconciliation、online-feature 合法性和 workload split。conditional admission ledger、policy replay、modeled
resident set 与 future-aware upper bound 不属于 G1、Runtime backbone 或 G2a STOP 分支的默认交付物。

只有 G2a 用各 arm 自己的在线 lifecycle trace 证明 shared L3 价值、可行动浪费、至少一条候选收益因果链和
STATIC_FREQ* residual 后，才允许实现最小 conditional ledger，并在其中实现 ROADMAP 状态的 VALUE_DENSITY。
ledger 只用于对给定 source-run eligibility stream 做 action/payload 对账、敏感性分析和 candidate rejection；
G3 在线 A/B 保留唯一跨策略因果裁决权。

### 拒绝

- 在 G1 或 G2a 前建设 policy simulator、modeled resident state 或 future-aware upper bound。
- 因为 ledger 是规划交付物，就在 G2a STOP 后补实现它。
- 用某一 source arm 的 eligibility stream 证明另一策略真实运行时的 hit、recompute、TTFT 或 Goodput。
- 因 ledger 后移而删除 G1 的确定性 workload generator、在线 trace 关联、payload 对账或 non-interference oracle。

### 翻案条件与 Gate 影响

若未来出现一个不依赖 policy replay、但 G1 无法完成真实 trace/payload 对账的最小离线校验器，只能把该校验器
作为 instrumentation test 加回 G1；它不得携带多策略 resident-state 演化或候选排名。G2a 未通过时，项目以
shared L3 无价值、ADMIT_ALL 无浪费或静态规则足够收口，conditional ledger 保持 ROADMAP 且不影响该 Gate 的
诚实结论。G2a 通过后，G2b 才接管 ledger correctness、source-run 标识、modeled-state 边界和候选拒绝标准。

### 依据

[PROJECT_PLAN.md](PROJECT_PLAN.md#9-replay-的职责与边界) 明确 conditional replay 不能产生跨策略因果结果；
[PROJECT_PLAN.md](PROJECT_PLAN.md#g2a机会生存闸门) 要求机会由各 arm 自己的在线 lifecycle evidence 证明。
