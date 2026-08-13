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
允许实施仍受 [D14](#d14--shared-l3-publication-admission-收敛与替代攻击) 的 active S1–S3 investment ruling 约束，
或受下文 D12 的窄 payload 例外约束。

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

## D12 — 有效 null 纪律与窄 payload 例外（旧 sentinel 已由 D14 替代）

**日期：** 2026-08-09
**状态：** DECIDED；sentinel、D1 与 hook 均未运行时验证。D12 保留“有效 null 不得靠施工补救”和两级 payload 例外的纪律；其旧的 `WRITE_COST_SENTINEL` / `CAPACITY_PRESSURE_SENTINEL` 定义已由 [D14](#d14--shared-l3-publication-admission-收敛与替代攻击) 收敛为 S1–S3，不能再按旧 workload 直接执行。

### 采用

当前 active workload 和 Gate 完全由 D14 的 S1–S3 定义：S1 是 hard veto；S2/S3 双有效 false 才停止性能方向。D12 不再定义独立 workload、signal 或“至少一个 signal 即自动进入 D1”的路径；旧 sentinel 和其 manifest 仅为历史 provenance，不能执行或解锁 trace/hook。

“有效 `false`”不是“没有统计显著差异”：对 D14 的 S2/S3，必须在查看 treatment 前冻结 workload、压力/公平 witness、`Goodput@TTFT-SLO`、工程物质性阈值、paired-run 区间方法与有限重复预算；所有前提成立后，预注册单侧效应区间的上界低于物质性阈值，才有排除能力。区间仍跨阈值、预算耗尽仍看不清，或任一前提不可证，均为 `INCONCLUSIVE`。最少 3 对重复只是执行下限，不是 null oracle。

窄例外只适用于 S1 已通过、且性能方向仅因 S2/S3 双有效 false 停止之后：owner 必须在查看 D1 结果**之前**另行确认一个真实、独立的 payload/resource 目标，并冻结：payload 如何映射到
带宽、Store CPU/容量、成本或单位资源服务能力，目标资源预算，`new_physical_put_bytes` 与
`not-read-within-H` 的物质性判据，以及有界的 observation-only 证据计划。该决议只解锁 Mooncake D1
pre-collapse observation 和完成 stock payload 归因所必需的最小 SGLang opaque correlation；不解锁 behavior hook。

只有 observation-only artifact 证明 stock 路径存在超过预注册阈值、且能映射回上述资源目标的 new-Put 与写后未读浪费，
owner 才可再次评审是否解锁最小静态 hook。即使 hook 获准，payload A2 终局仍须由在线 treatment 证明
`new_physical_put_bytes` 下降、Goodput 满足预注册 non-inferiority，且收益不是 dedup、race、顺序或清池造成；
`VALUE_DENSITY` 仍不因此解锁。

### 拒绝

- 仅以“补足工程复杂度”“patch 已经设计好”或“做更深负结果”为理由继续 D1/hook。
- 运行旧 `WRITE_COST_SENTINEL` / `CAPACITY_PRESSURE_SENTINEL`，或把历史 manifest 的任一结果作为 active Gate、D1 或 hook 的解锁条件。
- 把 D14 的有效 null 包装成已完成的 runtime flagship、R 层或 F 层。
- 一次 owner payload 例外同时授权 observation 和 behavior；两者之间必须保留第二次证据裁决。
- 在看到 null 后移动 workload、knee、容量压力或物质性阈值，直到出现正信号。
- 用 p-value 不显著、近零点估计或最低重复数替代有效-null 的区间排除条件。

### 翻案条件与 Gate 影响

任一 D14 通道的关键压力、公平性或实际运行条件不可证，或效应区间在冻结预算耗尽后仍跨越物质性阈值时，结果是
`INCONCLUSIVE`，不适用有效-null STOP。若合同本身必须改变，必须新建 D14 preregistration 版本并保留旧 artifact，
不能覆盖旧结果。D14 的 S1/S2/S3 结果决定正常路径；任何历史 sentinel 的信号均不产生自动解锁。S2/S3 双有效 false 后若没有新的 owner-approved resource-objective record，D1、trace 和 hook 保持 blocked，项目按 pre-implementation 分支收口或重新选题。

### 依据

[PROJECT_EVALUATION_SOP.md](PROJECT_EVALUATION_SOP.md) 要求真实目标函数和岗位边际价值，且明确不能靠增加功能补救失败闸门；
历史 D12 使用两个 stock sentinel 体现该原则。其 active workload/Gate 合同已由 [D14](#d14--shared-l3-publication-admission-收敛与替代攻击) 的 S1–S3 替换。

## D13 — conditional ledger 仅在 G2a 通过后实现

**日期：** 2026-08-09
**状态：** DECIDED；ledger 与候选策略均未实现、未运行时验证。

### 采用

G1 只验收真实在线实验必需的 workload replayability、trace/correlation、non-interference、payload
reconciliation、online-feature 合法性和 workload split。conditional admission ledger、policy replay、modeled
resident set 与 future-aware upper bound 不属于 G1、Runtime backbone 或 G2a STOP 分支的默认交付物。

只有 G2a 用各 arm 自己的在线 lifecycle trace 证明 shared L3 价值、可行动浪费、至少一条候选收益因果链和
STATIC_FREQ* residual，且 D14 的 online oracle-vs-X* 未停止方向后，才允许实现最小 conditional ledger。它不再默认
实现 `VALUE_DENSITY`；任何 candidate 必须由新的 owner decision 根据 residual 重新定义。ledger 只用于对给定
source-run eligibility stream 做 action/payload 对账、敏感性分析和 candidate rejection；G3 在线 A/B 保留唯一跨策略因果裁决权。

### 拒绝

- 在 G1、G2a 或 D14 的 oracle/X* 替代攻击前建设 policy simulator、modeled resident state 或 future-aware upper bound。
- 因为 ledger 是规划交付物，就在 G2a STOP 后补实现它。
- 用某一 source arm 的 eligibility stream 证明另一策略真实运行时的 hit、recompute、TTFT 或 Goodput。
- 因 ledger 后移而删除 G1 的确定性 workload generator、在线 trace 关联、payload 对账或 non-interference oracle。

### 翻案条件与 Gate 影响

若未来出现一个不依赖 policy replay、但 G1 无法完成真实 trace/payload 对账的最小离线校验器，只能把该校验器
作为 instrumentation test 加回 G1；它不得携带多策略 resident-state 演化或候选排名。G2a 未通过时，项目以
shared L3 无价值、ADMIT_ALL 无浪费或静态规则足够收口，conditional ledger 保持 ROADMAP 且不影响该 Gate 的
诚实结论。G2a 与 D14 oracle 上界均未停止方向后，G2b 才接管 ledger correctness、source-run 标识、modeled-state 边界和候选拒绝标准；它不授权默认 candidate。

### 依据

[PROJECT_PLAN.md](PROJECT_PLAN.md#9-replay-的职责与边界) 明确 conditional replay 不能产生跨策略因果结果；
[PROJECT_PLAN.md](PROJECT_PLAN.md#g2a机会生存闸门) 要求机会由各 arm 自己的在线 lifecycle evidence 证明。

## D14 — Shared-L3 Publication Admission 收敛与替代攻击

**日期：** 2026-08-10
**状态：** DECIDED；这是项目范围、基线和 Gate 的决议，不是 runtime 或 upstream 实验结论。

### 采用

项目正式术语收敛为 **Shared-L3 Publication Admission**。它只控制
**speculative / opportunistic publication**：L2 已完成备份、但系统尚未拥有已证实远端需求的
KV group 是否值得尝试发布到 shared L3。

唯一 owned seam 不变：

```text
L2 backup completion / ack
  -> prefix-closure check
  -> ADMIT_TO_L3 | DROP
  -> (only ADMIT) StorageOperation -> upstream Mooncake Put
```

`DROP` 在 `StorageOperation` 创建前返回，因此不拥有新的异步状态；它不应创建 queue、
`ongoing_backup`、host protection 或 Put。该性质仍须按 D10 由真实测试证明。

本项目与 SGLang Agentic KV 的关系是 **complement**，不是替代或重复实现：Agentic KV 若将来产生
明确的跨 worker 复用/交付意图，可成为 workload 或 intent producer；HiCache 与 Mooncake 始终是
L2/L3 生命周期和 shared-pool substrate。本项目当前 mainline 没有一个可 source-verified 的
intent-coupled publication producer。因此 intent-coupled set 现在为空；若未来出现，必须 bypass
speculative `DROP`（direct admit），或先修改 canonical plan 定义可验证的 priority 语义，绝不能静默
当成 speculative 数据丢弃。

项目的主张不再是“Agent hint 有用”，而是：若 source reverify 证明当前 upstream 将 L2 admission 与 L3 publication
绑定，能否在传输前独立控制 shared-L3 publication 的构成并留下物质 residual。绑定的具体 stock semantics 目前是
`RESEARCH_REVIEW / SOURCE_TO_REVERIFY`，不是本决议新制造的 `SOURCE_VERIFIED` 事实。Agent hint、`VALUE_DENSITY`、
stale-publication、page-level admission、router 和 eviction 都不是当前候选；只有后续在线 residual
明确指向它们，且重新通过 Gate/Scope review，才能重开。

### 最强替代基线与 null hypothesis

`ADMIT_ALL` 继续是同一 L2 write-through treatment 下的因果基线，却不再是项目价值的最强 null。
外部替代前沿定义为：

```text
X* = stock write_through_selective
   + sufficient L2 capacity
   + every source/runtime-verified usable stock quota and eviction control
```

X* 与 L3-only hook 不共享同一 L2 treatment，故不能混入 L3-only causal attribution ladder；但它是
“为什么不直接采用更简单 upstream 组合？”的强替代攻击。任何策略方向最终必须证明相对**可实际构造的** X*
存在预注册的物质差异，或停止。quota 是否可由 pinned SGLang adapter 配置并生效仍是 OPEN；在此之前
不得把假设中的 quota 写成已运行的 X* component。

在线 cheating oracle publication policy 可作为**stop-only opportunity upper bound**：它只可使用预先冻结、独立于
`TARGET_HELD_OUT` 的 `ORACLE_EVAL` workload split 的 future demand label 决定 publication，必须在真实双-worker runtime、fresh isolated Store、
各 arm 自己演化的 lifecycle 中运行，并直接与 X* 比较。它不是 deployable candidate，不能为 online feature
背书，也不能用 conditional ledger/offline replay 的 TTFT 或 Goodput 推断替代。若这个在线 oracle 都不能在
预注册物质性和区间规则下击败 X*，则停止 publication-admission 策略方向；若它能赢，只说明机会未被上界排除，
不授权任何具体 candidate。

### 承重 workload 与 survival contract

`unique-heavy` / pure one-shot 流量不再是 admission 主线的承重 waste：stock selective 可能在 seam 前把它
过滤。它只可作为负控制或 path-cost characterization，不能被用来证明独立 L3-only gate 的必要性。

主假设改为 **sticky-reuse background**：对象在本地复用达到 stock selective 阈值、因此会被 upstream
放行，却几乎没有 remote Get / remote reuse value；同时存在真正可跨 worker 复用的 shared prefix。这个比例、
实际阈值和 pinned implementation 的具体行为仍未在本项目独立核验。

active survival sequence 为：

1. `S1 RESTORE_VALUE_REGION`：先证明 shared-L3 restore 不仅路径可达、确实替代 prefill，还在预注册的
   target coordinate 中存在 restore 优于 recompute 的净价值区域。若在已覆盖、可裁决的目标 region 内
   `restore <= recompute`，或 remote Get 近似为零，则 STOP；不以更多 policy 工程补救。不能建立区间排除时为
   `INCONCLUSIVE`。
2. `S2 PUBLICATION_COST_ENVELOPE`：在 sticky-reuse publication 流量上，证明传输/Store/queue 等发布成本
   有可观测的压力 witness 与端到端可传导空间；one-shot 结果不能替代它。
3. `S3 CAPACITY_EXTERNALITY`：在 bounded L3、shared-prefix 与 sticky-reuse background 的公平坐标中，证明
   publication 构成能改变 query-time availability、useful Get 与 recompute 的机会空间；不把缺少 telemetry
   的 unavailable 直接归因为某个 eviction victim。

S1 是硬前置一票否决。S2/S3 继续使用 treatment-blind preregistration、压力/fairness witness、有限重复
预算和单侧区间排除：下界越过物质性阈值才是 signal，上界低于阈值才是有效 false；其余均为
`INCONCLUSIVE`。两个机会通道均获得有效 false 时停止主线。即使任一通道有 signal，若 trace 显示
sticky-reuse eligible/admitted publication bytes 低于预注册物质性质量，或目标部署的 remote Get 近似为零，
也停止而不是设计更聪明的 policy。

### 证据边界与 OPEN

本决议吸收了外部研究讨论的设计结论，但不把其中的 upstream 动态、生产比例、PR benchmark 或性能数字升级为
`SOURCE_VERIFIED` 或 `EXPERIMENTALLY_VALIDATED`。在固定 source 或独立 runtime artifact 复核前，应使用
`RESEARCH_REVIEW / SOURCE_TO_REVERIFY`（研究来源状态，**不是 claim state**）标注。

至少保留以下 OPEN：

- X* 中 quota 与 eviction controls 的 pinned-SGLang adapter 可配置性、实际生效路径和公平配置；
- 目标 workload 的 sticky-reuse 比例、eligible/admitted publication bytes 与真实 remote Get 频率；
- pinned commits 的 hit-count/selective semantics、metrics 和 prefetch threshold；
- PR #33862、PR #30796 及其后续 upstream 变动对当前 pins、容量/拒绝/benchmark 解释的影响；
- S1–S3 的 exact workload coordinate、materiality threshold 与 oracle/X* preregistration（包含独立 `ORACLE_EVAL` / `TARGET_HELD_OUT` split），均须在运行前冻结。

### 拒绝

- 把 stock selective 能过滤的 one-shot 流量当作 L3-only gate 的价值证据；
- 用一条 arm 的 offline replay 或 conditional ledger 推断另一策略的 TTFT、Goodput、remote Get 或 recompute；
- 因 oracle 能赢就提前实现 Agent hint、`VALUE_DENSITY`、page-level admission、router 或 eviction；
- 将 intent-coupled 数据静默 `DROP`，或为尚不存在的 intent 创建动态 policy service/通用框架；
- 把本文的 `DECIDED` 或 `RESEARCH_REVIEW` 状态写成已运行、已兼容或已实验验证。

### 翻案条件与 Gate 影响

若 source/runtime 复核表明 stock selective 已可在不伤害必要本地复用的条件下表达独立 L3 publication，或
Mooncake/adapter 已提供同等的 value-aware pre-transmission control，则重新进行替代攻击，不默认保留 owned
seam。相反，只有 S1–S3、online oracle-vs-X* 和各 arm 的 online lifecycle evidence 留下可行动 residual，
才可用新的 owner decision 重开一个最小 candidate。D12 的反 scope-creep 与有效-null纪律继续适用，但其旧
sentinel workload/命名由本决议替换。

## D15 — C0/C1 实验合同物化

**日期：** 2026-08-11
**状态：** DECIDED；合同已收口，未运行时验证。D18 后续修订了首次 C0 的固定 8K/32-token、direct local metric
和双物理 GPU realization；双 predicate、no-L3 control 与 token/output oracle 保持有效。

### 采用

将 D14 的首次 target-Linux TCP cohort 分成两个不可互相升级的 implementation contracts：

- [C0 Restore Qualification Contract](../implementation/G0_C0_RESTORE_QUALIFICATION_CONTRACT.md)
  冻结 request identity/page alignment、A Put→C→B join、B local-cold certificate、fresh B-cold
  no-L3 control、32-token output oracle 与 token-level predicate；
- [D14 Survival Preregistration Contract](../implementation/G0_D14_SURVIVAL_PREREGISTRATION_CONTRACT.md)
  冻结 C1 的 finite X* audit surface、S1 `Goodput@TTFT-SLO` endpoint、B-cold recompute control、
  remote-restore-mass floor、sticky-reuse logical-mass witness、S2/S3 causal pairs、fresh-store
  isolation、interval/null discipline 和 manifest freeze points。

C0 PASS 只表示 `RESTORE_PATH_PASS` 与 `REMOTE_VALUE_SURVIVES` 已被 runtime artifact 证明；它只是 S1 的
必要输入。C1 必须在自己的 fresh cohort 重做 C0 preflight。S1 以 `Goodput@TTFT-SLO` 为 primary endpoint，
`resumed_ttft` 仅为诊断，不能以 TTFT-only 或 token accounting 单独宣告 S1 存活。

X* 的“最强”限定为冻结 audit surface 内实际 source/runtime-verified、可配置、已生效且公平的 stock control；
未验证 quota/eviction 永远排除并写明原因。若实际 X* 在预注册规则下消除 sticky publication mass/pressure 且
endpoint 非劣，按 D14 的 `FRONTIER_ELIMINATES_OPPORTUNITY` 方向 STOP；无法证明 X* 构造或效果时为
`INCONCLUSIVE`，不是 STOP。

### 拒绝

- 把 C0 的一次 token reduction、TTFT 变化或 C 上无关对象写成 S1 或性能结论；
- 把 C0 runtime artifact 移植给 C1，或在 C1 看过 target-treatment 后补填 SLO、delta、mass floor、capacity、
  interval、repeat budget 或 X* components；
- 用 NIC/CPU bytes 代替 sticky-reuse logical publication-mass witness，或把该 witness 写成
  `new_physical_put_bytes`；
- 将 X* 混入 fixed-L2 causal attribution ladder，或因未确认 control “可能存在”而将其计入 X*。

### Gate 影响

D15 不改变 D14、D12 或 PROJECT_PLAN 的 Gate/STOP，也不授权租机、build、upstream execution、D1 trace、
behavior hook、candidate、`VALUE_DENSITY`、RDMA 或 benchmark。它仅使 T9/T10 的讨论合同可审查；所有 source/runtime
字段、数值、实际 effect、S1–S3 outcome 和 claim state 保持原状。

## D16 — 短生命周期 cohort 的租机前执行与证据合同

**日期：** 2026-08-11
**状态：** DECIDED；合同已收口，未实施、未租机、无 runtime artifact。D18 将本决议的完整 lifecycle 限定为
repeated/formal cohort 的按需 hardening；它不再定义首次 C0 的 correctness entrance。

> **FORMAL_COHORT ONLY：** 下述 OSS、三角色 RAM、双 GPU、finalizer、deadline/quarantine、terminal marker、
> retention 与 OCI bootstrap 是 D16 当时冻结的完整 formal-cohort 方案，不是 D18 后的首次 C0 要求。未来也只能按
> 已观察到的 blocker 或 C1 reproducibility 需求逐项启用，不能整体自动恢复为 Gate。

### 采用

若 repeated/formal 大陆 target Linux CUDA TCP cohort 启用本方案，其运行输入不依赖大陆 ECS 在租机日访问 GitHub、Hugging Face 或其他
跨境公网源。Git 保持 canonical source；operator 在租机前本地取得并校验固定 SGLang source、Mooncake wheel、
BF16 model/tokenizer snapshot、static role template 与 bootstrap revision，再将带完整 `release-manifest.json` /
`SHA256SUMS` 的 immutable `releases/<release_sha256>/` stage 到同 region OSS。A/B/C 只读该 prefix 与各自的
immutable role launch input，运行时不得替换 source、revision、wheel、模型或 config。

三台实例各自使用 least-privilege RAM role，只写其 `A/`、`B/` 或 `C/` artifact prefix；operator finalizer
独占 run-root outcome、checksum、terminal marker 和 release 权限。A/B/C 都不得自行写 `UPLOAD_COMPLETE`。A/B
须以三次 GPU UUID/PID snapshot 证明分别绑定不同物理 GPU；C 无 public IP，Store data plane 只走同 VPC/AZ
private endpoint，实际端口由最终 C config 得到而非猜测。

每次 formal cohort 有预声明的 hard deadline。正常 release 只发生在完整 artifact hash 已验证、outcome 和
`UPLOAD_COMPLETE` 已最终写入之后。中断、deadline 或意外实例丢失一律使受影响 predicate/pair
`INCONCLUSIVE`，不可跨 reconstructed cohort 补 arm；已校验 partial archive 可用 `RUN_ABORTED` +
`UPLOAD_ABORTED` 封口并释放。若没有可验证 archive，则停止工作负载并 quarantine，等待 operator 修复，不能为
控费静默销毁证据。任何 upstream process 启动后发现 preflight/config failure，均不得原地修复后称 fresh cohort。

完整和 abort evidence 均保留至“写入满 12 个月”与 owner 记录 project closeout 两者中较晚时点，之后 OSS
lifecycle 才可删除。这是 D16 的历史完整方案；当前
[first-C0 minimal contract](../implementation/G0_PRE_RENTAL_EXECUTION_CONTRACT.md) 不实现它。未来若逐项启用，
必须在对应 fresh formal-cohort manifest/contract 中重新冻结具体 release bundle、role bootstrap、artifact 与
refusal conditions。

静态运行用户态采用 Docker/OCI，而非每个 cohort 在机器上临时拼装。operator 在租机前构建并核验
`linux/amd64` worker（A/B 共用）与 Store（C）OCI archive；二者连同 archive SHA-256、OCI image digest、原始
SGLang/Mooncake/model/tokenizer identity 和静态 role template 都进入同一个 OSS release prefix。A、B 是同一
worker digest 的两个独立容器、独立 writable state，并且必须仍以 host/container GPU UUID evidence 证明物理隔离；
容器重启、无 shared volume 或 image digest 均不能单独证明 B local coldness。租机后才产生的 private endpoints、
run ID、最终 ports 等以 hash-recorded、role-scoped readonly launch input 注入，不能烤入 image。OSS 继续是证据
archive；该 formal 方案不引入 ACR，也不创建 custom ECS image。

### 拒绝

- 将大陆 ECS 对 GitHub/Hugging Face 的一次临时可达性、或 GitHub global status，当作 formal cohort 的输入
  availability 保证；
- 让 A/B/C 共用 archive-root 写权限、让任一 role 自行宣布 complete，或在 checksum 不匹配时释放；
- 只凭 GPU logical index、进程重启或 Store 名称声称 A/B 物理隔离、B coldness 或 fresh C；
- 给 C 公网 IP、把 Store data port 向 `0.0.0.0/0` 开放、猜测 Store port，或把 controlled bootstrap egress
  混同于 public Store data plane；
- 在 upstream 启动或请求后原地修改输入并把修复后的状态作为同一 fresh C0/C1；
- 用 mutable OCI tag、ACR availability、container restart 或无共享 volume 代替 release identity、host GPU/runtime
  preflight、B coldness certificate 或 C0 token-level oracle；
- 将 Docker/OCI 解释成已经验证的 Linux/CUDA compatibility，或以它取代 OSS evidence archive、operator finalizer
  和 terminal-marker 纪律。
- 用 `UPLOAD_ABORTED` 作为 PASS、S1、性能或 G0 completion 的证据，或把 partial cohort 与新 cohort 配对。

### Gate 影响

D16 只记录一个可后置选择的 formal-cohort execution contract。它不产生 `READY_TO_RENT`，不改变 PROJECT_PLAN、D12、D14、
T9/T10 或 G0 execution plan 的 Gate/STOP，不证明 OCI build/load、host Docker/GPU runtime、OSS/RAM/security
configuration、input staging、bootstrap、Mooncake compatibility、external Store、A Put/B Get、token reduction、S1–S3
或性能。T12 已完成该独立审查；D18 的当前 ruling 明确不以本方案的完整 harness 或 launch manifest 作为首次 C0
租机 blocker。

## D17 — C0-first 最小前置与 preflight 后置收敛

**日期：** 2026-08-11
**状态：** HISTORICAL DECIDED；已被 D18 取代其首次 C0 前置范围。不是 runtime evidence，也不产生租机授权。

### 采用

首次目标 Linux CUDA 工作的目的只是尽快、可裁决地运行 C0：固定 release 下，stock A Put → external C
→ locally-cold B 是否同时满足 `RESTORE_PATH_PASS` 与 `REMOTE_VALUE_SURVIVES`。因此先做已知、便宜且直接影响
C0 可解释性的前置，不把尚未遇到的中断、回收或权限失败预先建设成一套控制平台。

首次 C0 的最小入口仅包括：

1. 构建并静态核验真实 `linux/amd64` worker（A/B 共用）和 Store（C）OCI archive；记录 platform、archive
   SHA-256、image digest 和 pinned source/wheel/model/tokenizer identity。静态核验不是 Linux/CUDA runtime proof。
2. 将 immutable release stage 到同 region OSS，完成 re-list、readback 和 hash 比对；Git 仍是 canonical，动态
   endpoint、port、GPU UUID、run ID 和 writable state 仍不烤入 image。
3. 提供一个薄的 `stock_restore_preflight` execution path：C host 启动 Store 并保存 health/segment evidence；双 GPU
   worker host 按 A Put → fresh B-L3 → fresh B-no-L3 control 的固定顺序运行。它保存 C0 所需原始 artifact，并由
   C0 contract 的 classifier 产生 outcome；它不是 SSH orchestrator、scheduler 或 C1 runner。
4. 租机日、首个 upstream request 前只检查：verified archive 可被 Docker load、A/B container 分别看到不同物理
   GPU UUID、A/B `global_segment_size=0`、C 的 nonzero segment/health 以及 A/B→C private TCP。C 无 public IP 和
   same VPC/AZ 的 TCP topology 继续保持。

C0 的 request identity、B cold certificate、A→C→B join、fixed-decode output oracle、token-level oracle 及
`PASS`/`FAIL`/`INCONCLUSIVE`/`STOP` 分类一字不弱化。C0 `PASS` 后，才从这次真实运行遇到的 blocker 提炼最小
preflight；C1 必须在自己的 fresh cohort 重跑该 preflight 和 C0 oracle，不能复用 C0 artifact。

### 后置，而非取消

D16/T11 中的 operator finalizer、三角色 RAM prefix-isolation verification、run-root terminal marker、automatic
deadline/quarantine、完整 abort lifecycle、12-month retention 和 C1 formal-cohort archive discipline 保留为后续
hardening。它们不得作为首次 C0 的前置，也不得在 C0 失败前凭假设扩展实现；C0 `PASS` 后只按实际发现的问题
增量引入。

### 拒绝

- 以“先跑起来”为由跳过 release identity、OSS readback/hash、host GPU isolation、private Store topology 或 C0
  token oracle；这些是已知的 C0 裁决前提。
- 将本地 OCI inspect、Docker load 或一次 API shape 当作 target Linux/CUDA compatibility 或 C0 PASS。
- 把首次 C0 的 artifact 当作 C1 fresh-cohort preflight，或在 C0 尚未通过时实现 S1–S3 runner、D1、trace、hook、
  `VALUE_DENSITY`、RDMA 或通用 deployment platform。

### 历史 Gate 影响（已由 D18 取代首次 C0 blocker）

以下只记录 D17 在 2026-08-11 的裁决，不是当前 `NOT_READY_TO_RENT` blocker；当前入口以 D18、STATUS 和 T12 为准。

本决议只改变首次 C0 的执行优先级与 T12 `READY_TO_RENT` 的前置范围。它不改变 SOP、PROJECT_PLAN、D14/D15
的 Gate/STOP，也不升级任何 claim state。当前 OCI build/stage、OSS readback 和 thin runner/collector/classifier
均未实现，因此当前仍是 `NOT_READY_TO_RENT`。这些租机前项目真实通过并经 owner review 后才可授权租机；第 4 项
host GPU/Store/private-TCP 是租机后、第一条 request 前的 admission check，不是可在租机前假装已通过的条件。

## D18 — 首次 C0 的 correctness-only 入口与 evidence-driven hardening

**日期：** 2026-08-12
**状态：** DECIDED；取代 D17 对首次 C0 前置范围的裁决，并修订 D15 中固定 8K/32-token、direct-local-metric
与双物理 GPU 等具体 C0 realization；D15 冻结的双 predicate、no-L3 control 和 token/output oracle 不变。它不是
runtime evidence，不产生租机授权，也不改变 SOP、PROJECT_PLAN 的 Gate/STOP 或 D14 的生存条件。

### 原则

首次实验前只保留三类条件：缺失会导致错误 `PASS`/`FAIL`/`STOP`，会污染 treatment/coldness，或会让一次成功
运行的原始证据随短命实例不可恢复。若缺失只会让命令显式失败，且原始日志足以诊断并重试，则不把它建设成
首次 C0 前置；在真实 blocker 出现后再做针对性 hardening。

### 采用

1. 租机前只物化内容寻址的固定输入：pinned source/wheel/model/tokenizer/config identity、对应 checksum，以及一份
   单次 runbook。runbook 只覆盖 C 启动、A 的固定触发序列、fresh B-L3、fresh B-no-L3、原始输出捕获、bundle、
   checksum 和离机复制。OCI/OSS 可以作为交付方式，但不是 C0 correctness Gate；首次 C0 不要求独立 collector、
   自动 classifier、SSH orchestrator、scheduler 或 C1 runner。
2. 租机后、首个 upstream request 前在目标 host 核验实际输入 hash、build/API/config echo、实际 cache page size、
   stock write policy/threshold、worker `global_segment_size=0`、C 的 nonzero bounded segment/health，以及 A/B 到 C 的
   private TCP。Store data port 不得公网暴露；同 AZ、网络吞吐、NIC/CPU baseline 属于 C1/性能公平性，不是 C0
   correctness admission。
3. A/B 必须是相互独立、无共享可写状态的 worker lifecycle。首次 C0 允许在同一物理 GPU 上顺序运行：A 取得
   Put terminal 后退出，再创建全新 B 进程；这只能证明 cross-worker/process restore，不能外推成 cross-GPU、
   multi-host 或并发结论。C1 仍须在自己的 fresh cohort 重做 C0 并冻结其正式拓扑。
4. C0 使用相同 raw prompt/token identity；shared prefix 只需满足实际 page alignment，并达到已核验的 stock
   write/prefetch 条件，产生非零 Put/Get。decode 使用确定性 greedy，至少比较一个 completion token，并保存 token
   IDs（若 API 可得）或固定 UTF-8 output hash；不把固定 `N >= 8192` 或恰好 32 个 completion tokens 当作 oracle。
5. 最小 cold/join 证据是：fresh C 与唯一 keyspace、A 是 tested `config_prefix`/model KV objects 的唯一 writer；
   唯一允许例外是 pinned stock client startup `sglang_mooncake_store_warmup_key` + UUID，须用 source 和 A/B-L3
   success/config-prefix 日志证明它不经过 `_tag_keys` 且与 tested key 分离，不得允许 B 写 tested key。另需 A 的 Put terminal、A 结束后创建的 fresh B、
   B 的空 request ledger 与独立 writable state、B 禁用本地 persistent cache、B 对相同 token hash 的 remote
   Get/load，以及 fresh B-no-L3 control。stock 若直接暴露 L1/L2 empty 或 C-side request/key identity 则保存，但它们
   不是首次 C0 的循环前提，也不为此提前实现 trace patch。
6. target probe 后按实际 write threshold 运行最小固定 A 请求序列。若没有 A Put terminal，或 build/API/config、
   GPU、C health、private TCP 等入口检查失败，则记录 `execution_status=BLOCKED_BEFORE_C0`、两个 predicate
   `NOT_EVALUATED`；不得把它升级为 shared-L3 `FAIL` 或项目 `STOP`。只有真实 C0 请求链已经执行后，才按冻结的
   token/output oracle裁决 `RESTORE_PATH_PASS` 与 `REMOTE_VALUE_SURVIVES`。
7. 在释放实例前人工生成 raw bundle、checksum 并复制到 off-host 持久位置。首次运行不要求 operator finalizer、
   automatic deadline/quarantine、完整 abort lifecycle、terminal marker、三角色 RAM prefix-isolation 或 retention
   平台。

### 后置，而非取消

首次 C0 `PASS` 后，复盘真实 blocker，并只增加能消除该 blocker 的 preflight/hardening。C1 runner、D1 trace、
behavior hook、candidate、RDMA，以及 D16 的 formal-cohort lifecycle 控制，仍受各自 Gate 约束。C1 可以复用已验证的
runbook/launcher 代码，但必须使用 fresh cohort、fresh Store、fresh worker state 和自己的 C0 artifact，不能复用首次
C0 的环境状态或资格证明。

### 拒绝

- 把 OCI、OSS 完整 readback、独立 collector/classifier、双物理 GPU、同 AZ、网络 benchmark、固定 8K prefix 或
  恰好 32 token decode 当作首次 C0 correctness Gate；
- 在 A 没有满足 stock write condition 时把“无 Put”写成 restore premise `FAIL`；
- 把 host admission failure 写成 C0 outcome，或用 Docker、TTFT、容器重启、Store 流量、人工摘要替代 token-level
  oracle、B cold certificate、A→C→B join、fresh B-no-L3 control 和固定 output oracle；
- 在看到真实 blocker 之前建设云端实验平台或 formal-cohort lifecycle。

### Gate 与当前状态影响

执行顺序收敛为：首次 C0 → fresh C1 重做 C0 → finite X* source/runtime audit → baseline-only calibration/freeze
→ S1 → sticky-reuse S2/S3。D18 不改变 C0 必须同时满足 `RESTORE_PATH_PASS` 与 `REMOTE_VALUE_SURVIVES`，也不
削弱 S1 hard veto 或 D14 STOP。

当前仍是 `NOT_READY_TO_RENT`，但精确 blocker 仅是内容寻址输入 bundle 与单次 C0 runbook/raw-capture/off-host
handoff 尚未物化并经 owner review。目标 Linux/CUDA、build/API、write threshold、GPU、C segment 与 private TCP
均是只能在租机后验证的 runtime admission facts，不得伪装成租机前 blocker 或已通过证据。
