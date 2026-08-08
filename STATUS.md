# Project Status

Updated: 2026-08-08

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
| Worker A Put → fresh Worker B Get | STOP on the current macOS/arm64 executor before any upstream process started; target-Linux CUDA rerun remains required, see `docs/implementation/G0_T5_LOCAL_PREFLIGHT_STOP.md` |
| ALWAYS_ADMIT / ALWAYS_DROP behavior hook | ROADMAP |
| Async decision-to-adapter trace correlation | ROADMAP |
| Runtime backbone | ROADMAP; its acceptance is trace-only non-interference + minimal fail-open hook + closure/lifecycle oracle, independent of VALUE_DENSITY |
| Conditional admission ledger | ROADMAP |
| VALUE_DENSITY candidate | ROADMAP and gated behind G2a |
| Goodput or payload-efficiency improvement | ROADMAP; no X/Y exists |

## Next gate

G0：源码与运行时真相。

当前本机的 T5 preflight 已 STOP；在目标 Linux CUDA 环境重新执行
`docs/implementation/G0_EXECUTION_PLAN.md` 前，不得开始 T6/T7。恢复时按以下顺序：

1. 以 Mooncake `v0.3.12.post1` candidate 完成 API/build probe，并记录 full SHA 与 binary/build hash；
2. 打通 A Put → fresh B Get 的 stock external-store chain；
3. 在 pinned Mooncake checkout 实现 D1 所授权的 pre-collapse trace-only observation，并先证明 trace-disabled/trace-enabled 不干扰；在此前不运行 `BYTE_RECONCILE` 或 payload-efficiency claim；
4. 仅在 R0/R1 runtime prerequisites 通过后，先实现并验证 SGLang trace-only correlation；它只生成 opaque observation ID，不计算或应用 admission action；
5. 仅在 trace-only 的 non-interference oracle 通过后，实现 ALWAYS_ADMIT / ALWAYS_DROP / POLICY_ERROR_FAIL_OPEN 最小 hook，并验证 closure/lifecycle；
6. 不实现 VALUE_DENSITY，不启动大规模实验。它只在 G2a 证明静态规则存在可行动 residual 后才可进入实现。

## Explicitly not done

- 没有部署 SGLang/Mooncake
- 没有 GPU 实验
- 没有 runtime hook
- 没有 trace instrumentation
- 没有 benchmark 数字
- 没有社区 issue/PR
- 没有已验证 Mooncake compatibility build、external store deployment 或 runtime artifact
