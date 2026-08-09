# Project Status

Updated: 2026-08-09

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
| Worker A Put → fresh Worker B Get / prefill survival | STOP on the current macOS/arm64 executor before any upstream process started; target-Linux CUDA rerun must separately prove `RESTORE_PATH_PASS` and `REMOTE_VALUE_SURVIVES`, see `docs/implementation/G0_T5_LOCAL_PREFLIGHT_STOP.md` |
| Stock pre-D1 performance sentinels | ROADMAP: after `REMOTE_VALUE_SURVIVES`, `WRITE_COST_SENTINEL` tests the whole stock L3 path-cost envelope and `CAPACITY_PRESSURE_SENTINEL` tests bounded-capacity sensitivity before D1 investment; neither is admission attribution |
| Double-null payload/resource exception | DECIDED but inactive: D12 defines a two-stage exception, but no owner-approved resource-objective record or runtime artifact exists |
| ALWAYS_ADMIT / ALWAYS_DROP behavior hook | ROADMAP |
| Async decision-to-adapter trace correlation | ROADMAP |
| Runtime backbone | ROADMAP; its acceptance is trace-only non-interference + minimal fail-open hook + closure/lifecycle oracle, independent of VALUE_DENSITY but conditional on surviving the pre-implementation investment ruling |
| Conditional admission ledger | ROADMAP and gated behind G2a; it is not required by G1, Runtime backbone or a G2a STOP closure |
| VALUE_DENSITY candidate | ROADMAP and gated behind G2a |
| Goodput or payload-efficiency improvement | ROADMAP; no X/Y exists |

## Next gate

G0：源码与运行时真相。

当前本机的 T5 preflight 已 STOP；在目标 Linux CUDA 环境重新执行
`docs/implementation/G0_EXECUTION_PLAN.md` 前，不得开始 T6/T7。恢复时按以下顺序：

1. 以 Mooncake `v0.3.12.post1` candidate 完成 API/build probe，并记录 full SHA 与 binary/build hash；
2. 打通 A Put → fresh B Get 的 stock external-store chain，并同时证明 `RESTORE_PATH_PASS` 与 `REMOTE_VALUE_SURVIVES`；后者要求 B-cold L3 arm 的 storage-cached tokens 大于 0，且相对同请求 B-cold no-L3 control 实际减少 uncached/prefill tokens，TTFT 只作诊断；
3. 仍使用 stock、无补丁系统运行 `WRITE_COST_SENTINEL` 与 `CAPACITY_PRESSURE_SENTINEL`：先只用 baseline/control 校准并 checksum 冻结 workload、L2_ONLY knee、roomy/small 构造、TTFT-SLO、物质性阈值、paired-run 区间方法和有限重复预算，再运行 treatment；至少一项必须留下区间下界越过阈值的稳定端到端信号才自动继续 D1；
4. 只有两项都在有效压力坐标下、以区间上界低于物质性阈值获得有效 `false`，才按 D12 在 owned patch 前 STOP；“未显著”不是 null。任一探针无法证明负载拐点、实际 segment size、公平对照，或预算耗尽后区间仍跨阈值，只能记为 `INCONCLUSIVE`；该 characterization 不满足 R/F；
5. 双 null 后只有新的 owner-approved resource-objective record 在 D1 结果未知时冻结真实 payload/resource 目标、预算、物质性判据和有界 observation-only 计划，才可例外解锁 D1；这不解锁 behavior hook；
6. 只有正常 sentinel-positive ruling 或 D12 第一次例外授权允许继续时，才在 pinned Mooncake checkout 实现 pre-collapse observation，并验证 trace-disabled/trace-enabled 不干扰；随后只实现完成 stock payload 归因所需的最小 SGLang opaque correlation；
7. sentinel-positive 分支可在 trace-only 通过后实现最小 hook；双-null 例外分支还必须先证明超过阈值、映射回资源目标的 new-Put/写后未读浪费，并取得第二次 owner ruling，才可实现 ALWAYS_ADMIT / ALWAYS_DROP / POLICY_ERROR_FAIL_OPEN；
8. 不实现 VALUE_DENSITY，不启动大规模实验。它只在 G2a 证明静态规则存在可行动 residual 后才可进入实现。

后续 G2a 还必须在“写成本 / 资源争用”与“容量竞争 / 查询时可用性”两条候选收益链中，至少闭合一条各 arm 自身的运行时中介证据与 paired Goodput@TTFT-SLO 结果。只有 bytes、NIC/CPU 计数器或 modeled occupancy 不能通过性能机会闸门；两条链都不成立时停止 Goodput/TTFT 策略方向，只有可复现 new-Put payload 节省时才允许降级到 payload-efficiency。

## Explicitly not done

- 没有部署 SGLang/Mooncake
- 没有 GPU 实验
- 没有 runtime hook
- 没有 trace instrumentation
- 没有 benchmark 数字
- 没有社区 issue/PR
- 没有已验证 Mooncake compatibility build、external store deployment 或 runtime artifact
