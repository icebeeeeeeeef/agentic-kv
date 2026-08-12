# Project Status

Updated: 2026-08-12

## Current verdict

Conditional Select。

## Claim states

| Item | State |
|---|---|
| SGLang HiCache L2 → L3 source seam | SOURCE_VERIFIED against `b058dc910619c9d4bce9e9e24117104ffc491fa6`; G0 audit records exact hook/queue/ref evidence |
| Repository skeleton and migrated documentation | IMPLEMENTED_UNVALIDATED; local `make check` passed on 2026-08-05 |
| Mooncake `v0.3.12.post1` release candidate | SOURCE_VERIFIED: exact commit `6041a609a8c3af35e778f70db344f145c2914980` and official CPython 3.11 Linux x86_64 wheel digest are recorded; compatibility with the pinned SGLang adapter remains UNRESOLVED |
| Exact Mooncake runtime version/build compatibility | UNRESOLVED; G0-SOURCE BLOCKED pending target-Linux build identity and successful pinned adapter probe |
| Upstream patch provenance scaffold | IMPLEMENTED_UNVALIDATED: repository manifest/test pin three ordered external series; all remain `PLANNED`, so no upstream patch or apply verification exists yet |
| New-Put payload-byte attribution | DECIDED but unimplemented: D1 authorizes a pre-collapse Mooncake trace-only observation patch. Until its focused test and trace-enabled non-interference artifact exist, new-Put attribution remains STOP. |
| Worker A Put → fresh Worker B Get / prefill survival | Local execution-path STOP on the current macOS/arm64 executor before any upstream process started; C0 predicates are `NOT_EVALUATED`. Target-Linux CUDA must separately prove `RESTORE_PATH_PASS` and `REMOTE_VALUE_SURVIVES`, see `docs/implementation/G0_T5_LOCAL_PREFLIGHT_STOP.md` |
| D14 scope/baseline convergence | DECIDED: formal term is Shared-L3 Publication Admission; speculative scope, X*, S1–S3, online oracle stop bound and candidate freeze constrain subsequent work, but are not runtime evidence |
| C0 restore-qualification contract | DECIDED: request/coldness/token-oracle and classification contract is frozen; no target-Linux runtime artifact exists |
| C1 D14 preregistration contract | DECIDED: S1 endpoint, finite X* audit, S2/S3 witness and freeze rules are defined; all numeric/runtime fields remain UNRESOLVED |
| First-C0 execution priority | OWNER_DECIDED by D18: keep only content-addressed pinned inputs, a one-shot C0 runbook/raw capture/off-host checksum handoff, and rental-day target-host admission. OCI/OSS are optional delivery mechanisms; automated collector/classifier, dual physical GPUs, same-AZ and formal lifecycle controls are not C0 correctness gates. No input bundle, runbook or target runtime artifact exists yet. |
| S1–S3 survival contract | ROADMAP: old D12 one-shot sentinel definitions are superseded; S1 restore-value is a hard veto, S2/S3 require sticky-reuse pressure witnesses and interval exclusion before D1 investment |
| X* / online cheating oracle | ROADMAP; stock quota/adaptor wiring, exact selective semantics, target workload cohort and runtime comparison are unverified; external review claims remain `SOURCE_TO_REVERIFY` |
| Double-null payload/resource exception | DECIDED but inactive: D12 defines a two-stage exception, but no owner-approved resource-objective record or runtime artifact exists |
| ALWAYS_ADMIT / ALWAYS_DROP behavior hook | ROADMAP |
| Async decision-to-adapter trace correlation | ROADMAP |
| Runtime backbone | ROADMAP; its acceptance is trace-only non-interference + minimal fail-open hook + closure/lifecycle oracle, independent of VALUE_DENSITY but conditional on surviving the pre-implementation investment ruling |
| Conditional admission ledger | ROADMAP and gated behind G2a plus a non-stopping O1-vs-X* result; it is not required by G1, Runtime backbone or an opportunity STOP closure |
| Agent hint / VALUE_DENSITY candidate | ROADMAP and currently frozen; no candidate may be designed or implemented without post-residual owner decision |
| Goodput or payload-efficiency improvement | ROADMAP; no X/Y exists |

## Next gate

G0：源码与运行时真相。

当前本机的 T5 preflight 已 STOP；在目标 Linux CUDA 环境重新执行
`docs/implementation/G0_EXECUTION_PLAN.md` 前，不得开始 T6/T7。恢复时按以下顺序：

1. 租机前物化 D18 的内容寻址 input bundle，以及单次 C0 runbook、raw capture、checksum/off-host handoff；经 owner review 后才租机。OCI/OSS 可用于交付，但不是 correctness Gate；不得预建 collector/classifier、finalizer、自动 abort/lifecycle、C1 runner 或 policy infrastructure；
2. 租机后、首个 request 前，以 Mooncake `v0.3.12.post1` candidate 核验输入 hash、API/build identity、config echo、page size、stock write policy/threshold、C health/nonzero segment、worker `global_segment_size=0` 与 private TCP。入口失败记 `BLOCKED_BEFORE_C0`，两个 predicate `NOT_EVALUATED`；
3. 用满足实际 write condition 的最小固定 A 请求序列取得 Put terminal；A 退出后创建 fresh B-L3 和 fresh B-no-L3 control，按 token/output、coldness、A→C→B join 与 token-level reduction 同时裁决 `RESTORE_PATH_PASS` 和 `REMOTE_VALUE_SURVIVES`；
4. 首次 C0 `PASS` 后创建 fresh C1 cohort 并重做 C0；随后 finite source/runtime audit X* 的 actual selective semantics、quota/adapter wiring、metrics/prefetch threshold 与相关 PR impact，未复核内容保持 `SOURCE_TO_REVERIFY` 或从 X* construction 移除；
5. C1 baseline-only calibration/freeze 后先完成 S1 `RESTORE_VALUE_REGION`，再以 sticky-reuse workload 运行 S2 `PUBLICATION_COST_ENVELOPE` 与 S3 `CAPACITY_EXTERNALITY`。S1 无价值 region/remote Get≈0 时 STOP；S2/S3 双 valid-false 只有区间上界排除阈值才 STOP；
6. 双有效 false 后只有 D12 的 owner-approved resource-objective record 才可例外解锁 D1 observation；第一次例外不解锁 behavior hook；
7. 只有 S1–S3 surviving ruling 或 D12 例外允许继续时，才实现 Mooncake pre-collapse observation 与最小 SGLang opaque correlation，并验证 trace-disabled/trace-enabled non-interference；
8. trace-only 通过后才实现 ALWAYS_ADMIT / ALWAYS_DROP / POLICY_ERROR_FAIL_OPEN、prefix closure 与 async cleanup oracle；再按 G2a/O1 的 stop-only 顺序决定是否允许任何 candidate；
9. 不实现 Agent hint、`VALUE_DENSITY`、stale/page-level admission、router 或 eviction；只有残余证据与新的 owner decision 才可重开一个最小 candidate。

当前 `NOT_READY_TO_RENT` 的精确 blocker 是第 1 项尚未物化并经 owner review。第 2 项全部是只能在租机后验证的
host/runtime 事实，不是租机前 blocker，也没有被任何 `DECIDED` 文档证明为已通过。

后续 G2a 还必须在“写成本 / 资源争用”与“容量竞争 / 查询时可用性”两条候选收益链中，至少闭合一条各 arm 自身的运行时中介证据与 paired Goodput@TTFT-SLO 结果。只有 bytes、NIC/CPU 计数器或 modeled occupancy 不能通过性能机会闸门；两条链都不成立时停止 Goodput/TTFT 策略方向，只有可复现 new-Put payload 节省时才允许降级到 payload-efficiency。

## Explicitly not done

- 没有部署 SGLang/Mooncake
- 没有 GPU 实验
- 没有 runtime hook
- 没有 trace instrumentation
- 没有 benchmark 数字
- 没有社区 issue/PR
- 没有已验证 Mooncake compatibility build、external store deployment 或 runtime artifact
