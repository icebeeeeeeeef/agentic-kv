# Project Status

Updated: 2026-08-05

## Current verdict

Conditional Select。

## Claim states

| Item | State |
|---|---|
| SGLang HiCache L2 → L3 source seam | SOURCE_VERIFIED against the pinned planning source |
| Repository skeleton and migrated documentation | IMPLEMENTED_UNVALIDATED until local checks pass |
| Exact Mooncake runtime version | ROADMAP |
| Worker A Put → fresh Worker B Get | ROADMAP |
| ALWAYS_ADMIT / ALWAYS_DROP behavior hook | ROADMAP |
| Async decision-to-adapter trace correlation | ROADMAP |
| Conditional admission ledger | ROADMAP |
| VALUE_DENSITY candidate | ROADMAP and gated behind G2a |
| Goodput or payload-efficiency improvement | ROADMAP; no X/Y exists |

## Next gate

G0：源码与运行时真相。

下一次对话首先完成：

1. 重新核对 pinned SGLang source seam；
2. pin Mooncake exact commit/build；
3. 决定 upstream checkout/patch 的最小集成方式；
4. 把 G0 拆成可执行、可测试的最小任务；
5. 不实现 VALUE_DENSITY，不启动大规模实验。

## Explicitly not done

- 没有部署 SGLang/Mooncake
- 没有 GPU 实验
- 没有 runtime hook
- 没有 trace instrumentation
- 没有 benchmark 数字
- 没有社区 issue/PR
