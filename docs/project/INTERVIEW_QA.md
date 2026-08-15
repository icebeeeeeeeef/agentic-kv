# Interview Defense Collection

本文件是 `agentic-kv` 的面试防守集合。它只压缩已存在的项目决策和证据，不是新的项目权威，也不允许升级 claim state。

## Claim-state vocabulary

- `ROADMAP`：只有计划或设计，尚未实现。
- `SOURCE_VERIFIED`：在明确固定版本的一手源码中核对过的事实。
- `IMPLEMENTED_UNVALIDATED`：代码存在，但要求的运行时或实验 Gate 尚未通过。
- `EXPERIMENTALLY_VALIDATED`：在明确 manifest、commit、raw log 和统计方法下可复现。

`gate_outcome`（`PASS` / `FAIL` / `INCONCLUSIVE` / `STOP`）与上述 claim state 正交；一次 scenario 的
PASS 只能支持它实际覆盖的主张，不能自动升级完整 G0 或性能 claim。

回答时必须明确主语：哪些是 upstream SGLang/Mooncake 提供，哪些是本项目集成、实现、测量或验证。没有 artifact 支撑的内容不得使用完成时。

## Current defense boundary

当前可确认的个人产出包括仓库组织、规划材料、G0 源码审计，以及 first-C0 r6 的 stock restore qualification。固定 SGLang source 上的接缝仍是 `SOURCE_VERIFIED`；pinned SGLang adapter + Mooncake `v0.3.12.post1` 已在 r6 的 TCP/direct-I/O/L20 拓扑完成 A→external C→fresh B 的 `RESTORE_PATH_PASS` 与 `REMOTE_VALUE_SURVIVES`，因而这一**单一**组合是 `EXPERIMENTALLY_VALIDATED`。L3 admission hook、instrumentation、workload generator、conditional ledger、在线策略、fresh-C1 C0、S1–S3 与任何性能收益仍未完成。r6 不支持 cross-GPU、multi-host、生产或通用 compatibility claim，也不构成完整 G0。

权威细节见：

- [PROJECT_PLAN.md](PROJECT_PLAN.md)
- [STATUS.md](../../STATUS.md)
- [implementation evidence](../implementation/)
- [durable decisions](DECISIONS.md)

## Required current questions

### Q: 为什么还需要 Shared-L3 Publication Admission，而不是 stock selective + L2 + Mooncake eviction？

**Decision state：** `DECIDED`（D14）
**Claim state：** `ROADMAP`；其中 stock quota/adaptor wiring、exact selective semantics 和 PR/production细节为 `RESEARCH_REVIEW / SOURCE_TO_REVERIFY`。

**短回答：** 本项目不预设 L3-only gate 必然有价值。最强简单替代是 X*：stock `write_through_selective`、足够 L2 和所有实际可用的 stock quota/eviction controls。它虽然改变 L2 treatment，不能混成 L3-only 因果基线，却必须作为替代攻击被正面比较。独立 gate 的唯一待测 residual 是 sticky-reuse：本地复用足以通过 stock selective、却很少被远端读取的 speculative publication；one-shot/unique-heavy 预期应由 X* 在 seam 前过滤，不能支撑本项目。

**证据边界：** 当前只在 fixed SGLang source 中验证了 L2 ack 后、`StorageOperation` 前的 seam；还没有本项目 runtime trace 证明 sticky-reuse mass、X* 可构造或 quota 已可用。外部讨论中的 PR、阈值、eviction 或 production 说法未被独立复核，不是 `SOURCE_VERIFIED`。

**反例与 trade-off：** 若 X* 构造后已经相当或更好，或者仅在独立 `ORACLE_EVAL` split 读取 future label 的 online cheating oracle 也无法物质性击败它，按 D14 STOP。这个 oracle 即使获胜也只说明存在未排除机会，不能证明 Agent hint、`VALUE_DENSITY` 或任意候选有效，更不能污染 TARGET_HELD_OUT。

**不能声称：** “stock selective 必然不够”“Mooncake eviction 必然较差”或“sticky-reuse 已在真实 agent workload 中证明”。

### Q: speculative publication 与 intent-coupled publication 如何区分？

**Decision state：** `DECIDED`（D14）
**Claim state：** `ROADMAP`

**短回答：** 当前 hook 只裁量 L2 已可用、但尚无已证实远端需求的 speculative/opportunistic publication。当前 mainline 中经本项目 source-verified 的 intent-coupled set 为空。若未来出现明确交付/复用 intent，它必须 direct-admit 或先通过新计划定义可测试的 priority 语义；不能悄悄走 speculative `DROP`。

**反例与 trade-off：** 预先设计 intent RPC、priority scheduler 或通用 policy service只会给空集增加控制面；现阶段不做。这个边界不代表已经集成或实现了 SGLang Agentic KV，后者只是潜在 complement/workload producer。

**不能声称：** “项目已经支持 Agentic KV intent”或“intent path 已经被测试”。

### Q: 这会不会只是一个 `decide()` 函数加参数扫描？

**Claim state：** `SOURCE_VERIFIED + ROADMAP`；first-C0 r6 仅建立 stock restore prerequisite

**短回答：** 通过 pre-D1 存活筛查并进入工程实现后，不把候选策略获胜作为工程完成前提。最低交付是独立的
trace-only correlation、pre-collapse payload observation、L2 ack 后的 fail-open seam、prefix closure 与 async terminal oracle；它们都在真实
SGLang→Mooncake 生命周期上，并要求 focused test、patch provenance 和 run artifact。当前这些 owned
patch 尚未实现，因此不能说已经拥有 runtime 工程成果。

**证据：** [runtime backbone contract](PROJECT_PLAN.md#32-三层完成定义)、
[minimum ownership/deletion oracle](PROJECT_PLAN.md#34-工程最低交付与反向删除测试)。

**反例与 trade-off：** 如果项目已经通过投资筛查，但删除 benchmark 后只剩阈值函数，R 层即失败；解决办法
不是增加 policy framework，而是完成已有生命周期与观测合同。若 S1 STOP，或 S2/S3 在有效坐标下均为 null，
则按 D14 在 owned patch 前 STOP，不能为了凑 R 层继续施工。

**不能声称：** “已经实现了分层 KV cache / Mooncake transfer”或“策略已带来收益”。

### Q: 为什么 trace-only 必须先于 admission hook？

**Claim state：** `SOURCE_VERIFIED + ROADMAP`

**短回答：** source 只证明 seam 的位置，不能证明异步 operation、batch、physical object terminal 的运行时
关联。先加 behavior hook 会混淆观测回归与机制回归；所以先在不计算/应用 action 的条件下，用 opaque
`observation_id` 证明 trace-disabled/trace-enabled 行为等价，之后才允许写 `ALWAYS_*` hook。

**证据：** [active execution order](PROJECT_PLAN.md#212-唯一正确的下一动作顺序)、
[trace-only acceptance](../implementation/G0_EXECUTION_PLAN.md#task-3-add-trace-only-correlation-and-prove-it-is-inert)。

**反例与 trade-off：** trace 改变 key、队列、Put/Get result、输出或 cleanup 时，必须 STOP/revert trace
patch；不能用 policy 绕过不可信 telemetry。

**不能声称：** 目前没有 trace-disabled/enabled artifact，不能说关联链已经正确或无开销。

### Q: 为什么成功的 remote Get 还不足以让 G0 通过？

**Claim state：** `SOURCE_VERIFIED + EXPERIMENTALLY_VALIDATED（仅 first-C0 r6）+ ROADMAP`

**短回答：** 成功 Put/Get 和输出一致只形成 `RESTORE_PATH_PASS`，证明 shared-L3 链路功能正确；项目还要求
`REMOTE_VALUE_SURVIVES`：fresh B 的 `cached_tokens_details.storage` 非零，且相对相同请求的 B-cold no-L3
control，实际 uncached/prefill tokens 更少。否则只是“搬了数据”，没有证明替代计算，不值得继续投入 admission
hook。TTFT 在 G0 只作诊断，不能替代 token-level oracle，也不能形成性能 claim。

**证据：** [cross-worker premise](PROJECT_PLAN.md#112-为什么必须双-worker)、
[stock restore acceptance](../implementation/G0_EXECUTION_PLAN.md#task-1-establish-stock-external-store-recovery-and-prefill-survival)、
[pinned token-accounting evidence](../research/g0-prelaunch/R4-runtime-attribution/evidence.md)。

**反例与 trade-off：** restore 可能确实减少 prefill，但 TCP Get 使 TTFT 暂时不降；这仍允许继续验证机制，
但必须在后续 G2a/G3 诚实检验净系统价值。反之，一次 TTFT 偶然降低但 prefill 未减少，不能救活项目。

**不能声称：** r6 只证明指定 stock TCP/direct-I/O/L20 拓扑的 restore 和 token-level prefill substitution；不能说 fresh C1、S1、完整 G0、TTFT/Goodput、跨 GPU/multi-host 或生产已经通过。

### Q: L3 admission 为什么可能改善 Goodput？减少写入字节还不够吗？

**Claim state：** `ROADMAP`

**短回答：** 不够。在本项目的单一 action 下，性能收益只允许沿两条候选链解释：一是 DROP 低价值写入后，
真实新 Put 与 backup queue/CPU/内存/NIC/Store 争用下降，最终改善 Goodput@TTFT-SLO；二是有限 L3 中的低价值
竞争下降，使高价值 KV 在查询时更可用、useful Get 增加、computed prefill/recompute 减少，最终改善
Goodput。G2a 只要求至少一条成立，但每条都必须同时具有各 arm 自身的运行时中介证据和 paired 端到端结果。

**证据边界：** 链 A 必须闭合 decision → `new_physical_put_bytes` → queue/resource pressure →
Goodput/TTFT；NIC/CPU 只是诊断。链 B 必须闭合 decision → query-time availability/useful Get → computed
prefill/recompute → Goodput/TTFT；modeled occupancy 不能充当在线事实。当前两条链都没有实验数据。

**反例与 trade-off：** 写成本被完全隐藏、容量宽松，或固定 remote eviction 已经有效保护高价值对象时，
ADMIT_ALL 应最好或持平。反过来，“eviction 更晚决策”不自动证明它的信息更强，因此这是一项 losing condition，
不是选择性准入必然冗余的先验结论。

**不能声称：** 只有 new-Put payload 下降时只能声称 payload efficiency；不能声称缓解资源争用、改善容量
可用性或提升 Goodput，也不能在缺少 SOURCE_VERIFIED telemetry 时声称观察到具体 occupancy、victim 或 eviction
reason。

### Q: 为什么不先把 D1 trace 和 hook 做完，再看有没有性能机会？

**Claim state：** `SOURCE_VERIFIED + ROADMAP`

**短回答：** D1 和 hook 是 admission-specific 投资，不应先于问题存在性。先让 S1 验证 restore-vs-recompute 的可裁决价值区域；再让 S2 在会通过 stock selective 的 sticky-reuse publication 流量上验证 publication-cost envelope，让 S3 在 shared-prefix + sticky background 的 bounded L3 中验证 capacity externality。one-shot/unique-heavy 只能是 X* 预期过滤的负控制，不能让任一 gate 通过。只有 active survival contract 留下稳定端到端信号，才自动继续 D1。

执行前先做 treatment-blind preregistration：knee 只由 L2_ONLY service curve 选择，roomy/small 按冻结的 KV payload
估算关系构造，并冻结 TTFT-SLO、物质性阈值、paired-run 区间方法和有限重复预算。`true` 要求区间下界越过阈值；有效
`false` 要求区间上界低于阈值。三次重复或 p-value 不显著都不是 null oracle。

**证据：** [active S1–S3 contract](PROJECT_PLAN.md#s1s3当前-survival-contract)、
[active survival procedure](../implementation/G0_EXECUTION_PLAN.md#active-task-2-prepare-and-run-d14-s2s3-survival-gates)。

**反例与 trade-off：** S2/S3 都不是 admission proof，缺少 telemetry 时也看不到具体 eviction。S1 在可裁决 region 内 restore 不优于 recompute、remote Get≈0，或 S2/S3 都以区间排除规则成为有效 false 时，均在 owned patch 前 STOP，且不满足 R/F；关键压力/公平条件不可证，或冻结预算后区间仍跨物质性阈值，只能记为 `INCONCLUSIVE`。不能把 runtime 工程量或“更深负结果”本身当作问题价值。

**不能声称：** first-C0 r6 只证明 restore 机制，不能说写争用或容量压力已经存在；D1 未完成前也不能把
NIC 流量或 submitted bytes 称为 `new_physical_put_bytes` 或 payload-efficiency。

### Q: S2/S3 都是有效 null，或 S1 不存在 restore-value region，为什么不继续把 runtime backbone 做完？

**Decision state：** `DECIDED`（D12 + D14）

**Claim state：** `ROADMAP`；其 restore 前提仅 first-C0 r6 为 `EXPERIMENTALLY_VALIDATED`

**短回答：** Runtime backbone 是“若要称为 runtime flagship 的最低工程线”，不是无条件施工承诺。S2/S3 在预注册 pressure coordinate 下都以效应区间上界低于物质性阈值成为有效 null，说明当前 sticky-reuse publication 的两条机会链都没有留下可行动投资信号；S1 若无 restore-value region 更早 STOP。此时继续
写 D1/hook 只为补工程量，会失去真实目标函数。项目按 D12/D14 在 owned patch 前 STOP，保留 characterization 和
方向筛查负结果，但不称为 R/F。

**证据：** [D14 active STOP](DECISIONS.md#d14--shared-l3-publication-admission-收敛与替代攻击)、
[completion boundary](PROJECT_PLAN.md#32-三层完成定义)。

**反例与 trade-off：** 如果在 D1 结果未知时已经存在真实带宽/Store CPU/容量/成本或单位资源服务目标，owner
可以先冻结资源预算与 new-Put/not-read 物质性判据，只授权 observation-only D1。只有 trace 证明物质性浪费后，
才二次评审最小静态 hook；第一次例外不解锁 behavior，也不解锁 `VALUE_DENSITY`。

**不能声称：** 双 null 是普适的“admission 无价值”，也不能把 pre-implementation STOP 包装成已完成的
runtime flagship。没有区间排除能力的“不显著”结果不能叫双 null；没有新的 resource-objective record 时，当前例外并未被触发。

### Q: 为什么不在 G1 就把 conditional ledger 做完，用它判断有没有策略机会？

**Decision state：** `DECIDED`（D13）

**Claim state：** `ROADMAP`

**短回答：** G1 要证明的是“真实运行发生了什么能否被可信记录”，所以保留 workload replayability、在线
trace/correlation、non-interference、payload reconciliation 和 workload split。conditional ledger 固定一条
source-run eligibility stream 后离线回放其他 policy；真实 policy 会改变后续 L3 hit、L2 fill、recompute 和新的
eligibility，因此 ledger 不能替 G2a 或 O1-vs-X* 证明在线机会。只有 G2a 和 online oracle 都未停止方向，才
值得在 G2b 实现 ledger，拒绝动作差异太小或依赖错误模型的候选；`VALUE_DENSITY` 不再是默认交付。

**证据：** [D13](DECISIONS.md#d13--conditional-ledger-仅在-g2a-通过后实现)、
[activation gate](PROJECT_PLAN.md#90-activation-gate)、[G2b contract](PROJECT_PLAN.md#g2bconditional-replay-rejection-filter)。

**反例与 trade-off：** ledger 可以比在线候选实验便宜，但提前实现会把尚未证明存在的问题变成 simulator 工程，
并诱导把条件式结果误写成因果结论。后移不删除 generator 或 trace 校验；它只删除 G1 中的多策略 replay、modeled
resident state 和 future-aware upper bound。

**不能声称：** 当前 ledger 尚未实现；即使将来 G2b 通过，也只能说候选“未被条件式拒绝”，不能说它已经在线
优于 STATIC_FREQ* 或改善 TTFT/Goodput。

### Q: 你如何证明“减少写入”不是 dedup 或 two-writer race？

**Claim state：** `SOURCE_VERIFIED + ROADMAP`

**短回答：** adapter 的 `put_result=0` 会把真正新 Put 与 `OBJECT_ALREADY_EXISTS` race 合并为 success，
不能作为新物理写入。D1 因此只允许在 Mooncake 归约前使用严格 trace-only observation；实际施工还必须通过
pre-D1 ruling。只有它的 non-interference artifact 通过后，`new_physical_put_bytes` 才能用作 payload 分子。

**证据：** [D1](DECISIONS.md#d1--保留-new-put-payload-指标并授权最小观察-patch)、
[race limitation](../implementation/G0_SOURCE_RUNTIME_AUDIT.md#race-observation-limitation)。

**反例与 trade-off：** 观测不到原始原因码或观测改变行为时，payload 分支 STOP，不用模糊的
`completed_put_bytes` 替代。

**不能声称：** 目前尚无 observation patch/test，不能给出 new-Put 字节或 payload-efficiency 数字。

### Q: 为什么 prefix group 必须 all-or-none，而不做更细的按页规则？

**Claim state：** `SOURCE_VERIFIED + ROADMAP`

**短回答：** remote lookup 在第一个缺失 page 停止。若 ancestor DROP 而 descendant ADMIT，后者不可达。
G0 选择 root/known-resident anchor 加有序 logical pages 的完整 group 一次性 ADMIT 或 DROP；这用最少状态
满足可达性，不引入 remote metadata、read-path repair 或逐页策略。

**证据：** [D9](DECISIONS.md#d9--g0-的-prefix-group-一律-all-or-none)、
[prefix closure contract](PROJECT_PLAN.md#54-前缀闭包不变量)。

**反例与 trade-off：** callback 不能证明完整可达 group 时必须整体 DROP，可能牺牲更细粒度收益；不能以
“整个 suffix 一起写”猜测闭包。

**不能声称：** 规则尚无 runtime artifact，不能说任何真实 workload 已验证 closure。

### Q: 取消、failure 或 late completion 怎么处理？

**Claim state：** `SOURCE_VERIFIED + ROADMAP`

**短回答：** DROP 在 `StorageOperation` 之前返回，不新增 async owner；admitted path 继续使用 upstream
ack/detach cleanup。项目必须验证 success、dedup、race、fail-open、shutdown/detach 的终态；真实 failure
injector 不可得时只能是 `INCONCLUSIVE`，不能靠 mock 或进程退出声称 G0 validated。

**证据：** [D10](DECISIONS.md#d10--failureasync-合同保持严格不伪造覆盖)、
[async source facts](../implementation/G0_SOURCE_RUNTIME_AUDIT.md#async-cleanup-facts)。

**反例与 trade-off：** 若 detach 后观察到 residual protection、late ack 或 leak，这是 G0 FAIL/STOP，
不是新增 cancellation registry/epoch state machine 的理由。

**不能声称：** 当前未运行 G0 matrix，不能声称这些终态已经全部通过。

### Q: 为什么首次 C0 不把 Docker/OCI、OSS 和自动归档当 correctness Gate？

**Decision state：** `DECIDED`（D18；D16 只保留为后续 formal-cohort hardening）

**Claim state：** `ROADMAP`

**短回答：** C0 correctness 只依赖输入身份不漂移、A/C/B 与 no-L3 control 的隔离和 join、token/output oracle，
以及原始证据离开短命实例。内容寻址 source/wheel/model/tokenizer/config bundle、目标 host 使用前的 checksum 和一次
人工 raw-bundle/checksum/off-host copy 已经满足这三点。Docker/OCI 与 OSS 只是交付选择；自动 collector/classifier、
finalizer、deadline/quarantine 和完整 abort lifecycle 不增加首次 C0 的判别力，反而会在看到真实 blocker 前扩大平台面。

target Linux/CUDA、build/API、实际 write threshold、GPU、Store segment 和 private TCP 只能租机后验证。它们失败时
记录 `BLOCKED_BEFORE_C0`、两个 predicate `NOT_EVALUATED`，不能把“环境没跑起来”伪装成 shared-L3 `FAIL/STOP`。
一旦真实 C0 `PASS`，C1 仍须 fresh cohort 重做 C0；代码可以复用，环境状态和资格 artifact 不能复用。

**证据：** [D18](DECISIONS.md#d18--首次-c0-的-correctness-only-入口与-evidence-driven-hardening)、
[pre-rental execution contract](../implementation/G0_PRE_RENTAL_EXECUTION_CONTRACT.md)。

**反例与 trade-off：** 如果首次运行真实暴露跨境下载不稳定、人工归档易漏或重复执行造成误判，就按该具体 failure
增加最小 staging、capture 或 finalization；不能因为“未来也许重复很多次”提前建设 registry/orchestration platform。
另一方面，checksum、A Put terminal、B cold certificate、A→C→B join、fresh no-L3 control 和 deterministic output
oracle 不能删，因为删掉会产生假结论或不可复核证据。

**不能声称：** first-C0 的 input bundle/runbook、target-host probe 与 r6 runtime artifact 已存在，但这不表示自动部署、自动归档、fresh C1、cross-GPU/multi-host 或生产适用性已通过。

## Question template

新增问题时使用以下最小结构：

### Q: 追问问题

**Claim state：** `ROADMAP | SOURCE_VERIFIED | IMPLEMENTED_UNVALIDATED | EXPERIMENTALLY_VALIDATED`

**Gate outcome（如存在 run artifact）：** `PASS | FAIL | INCONCLUSIVE | STOP`；没有 artifact 时明确写“无”。

**短回答：** 先给结论，明确 ownership 和边界。

**证据：** 固定 commit、测试、run manifest、raw log 或统计产物的路径。

**反例与 trade-off：** 什么时候失效，最强简单基线是什么，失败时如何按 Gate/STOP 收口。

**不能声称：** 当前证据尚不支持的扩大表述。
