# Project Status

Updated: 2026-08-05

## Current verdict

Conditional Select。

## Claim states

| Item | State |
|---|---|
| SGLang HiCache L2 → L3 source seam | SOURCE_VERIFIED against `b058dc910619c9d4bce9e9e24117104ffc491fa6`; G0 audit records exact hook/queue/ref evidence |
| Repository skeleton and migrated documentation | IMPLEMENTED_UNVALIDATED; local `make check` passed on 2026-08-05 |
| Mooncake `v0.3.12.post1` release candidate | SOURCE_VERIFIED: exact commit `6041a609a8c3af35e778f70db344f145c2914980` and official CPython 3.11 Linux x86_64 wheel digest are recorded; compatibility with the pinned SGLang adapter remains UNRESOLVED |
| Exact Mooncake runtime version/build compatibility | UNRESOLVED; G0-SOURCE BLOCKED pending target-Linux build identity and successful pinned adapter probe |
| New-Put payload-byte attribution | STOP under the current adapter/Mooncake terminal contract: race `OBJECT_ALREADY_EXISTS` is collapsed to success, so `put=0` cannot mean new Put |
| Worker A Put → fresh Worker B Get | ROADMAP |
| ALWAYS_ADMIT / ALWAYS_DROP behavior hook | ROADMAP |
| Async decision-to-adapter trace correlation | ROADMAP |
| Conditional admission ledger | ROADMAP |
| VALUE_DENSITY candidate | ROADMAP and gated behind G2a |
| Goodput or payload-efficiency improvement | ROADMAP; no X/Y exists |

## Next gate

G0：源码与运行时真相。

下一次对话首先按 `docs/implementation/G0_EXECUTION_PLAN.md` 完成：

1. 以 Mooncake `v0.3.12.post1` candidate 完成 API/build probe，并记录 full SHA 与 binary/build hash；
2. 打通 A Put → fresh B Get 的 stock external-store chain；
3. 在 payload metric 上先由用户裁决：停止 new-Put payload claim，或明确授权在 Mooncake duplicate-to-success 归约前增加独立 trace-only observation；
4. 仅在 R0/R1 runtime prerequisites 通过后，先实现并验证 trace-only correlation，再实现 ALWAYS_ADMIT / ALWAYS_DROP 最小 hook；
5. 不实现 VALUE_DENSITY，不启动大规模实验。

## Explicitly not done

- 没有部署 SGLang/Mooncake
- 没有 GPU 实验
- 没有 runtime hook
- 没有 trace instrumentation
- 没有 benchmark 数字
- 没有社区 issue/PR
- 没有已验证 Mooncake compatibility build、external store deployment 或 runtime artifact
