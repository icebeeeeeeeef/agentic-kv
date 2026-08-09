# T5 local preflight STOP

**Captured:** 2026-08-08T09:32:32Z
**Scope:** this macOS executor only; not a statement about a future target Linux deployment.
**Gate outcome:** `STOP`
**Claim state:** `ROADMAP`

## Evidence

The retained local run bundle is
`experiments/runs/local-macos-arm64-preflight-20260808T093232Z/` (ignored by
Git because it is a raw run artifact). Its environment record establishes:

- macOS 15.7.4 on arm64, not target Linux x86_64;
- no `nvidia-smi` or `/dev/nvidia*` device;
- Python 3.8 only, with no Python 3.11;
- no Docker/Podman runtime;
- no local external checkout for either pinned SGLang or Mooncake revision.

No Mooncake wheel/API probe, Store C, SGLang worker, model, request, Put/Get,
trace, or performance measurement was started. Therefore this record cannot
upgrade or downgrade SGLang/Mooncake compatibility; it only proves that this
executor cannot run T5's required topology.

## Stop and resume rule

Do not install a macOS substitute, use a single process as two workers, use a
local non-CUDA fallback, or start T6/T7 from this state. T5 must be rerun from
its documented preconditions on a target Linux x86_64 CUDA environment with:

1. pinned SGLang `b058dc910619c9d4bce9e9e24117104ffc491fa6` and Mooncake
   `6041a609a8c3af35e778f70db344f145c2914980` checkouts;
2. the exact CPython 3.11 Linux wheel/API probe;
3. two distinct GPU SGLang workers A/B and a separately observable external
   Store C using TCP; and
4. retained configuration, process logs, health/segment response, cold-B
   evidence, A Put/B Get join, storage-loaded evidence, output equality, and an
   identical B-cold no-L3 control proving non-zero storage-cached tokens reduce
   uncached/prefill tokens; and
5. only after that mechanism result passes, stock/no-patch
   `WRITE_COST_SENTINEL` and `CAPACITY_PRESSURE_SENTINEL` runs with retained
   baseline-only service-curve knee selection, a checksummed treatment-blind
   preregistration, Store activity, actual roomy/small segment responses, paired
   endpoint intervals, and explicit true/false/INCONCLUSIVE signal fields. A
   true signal requires its interval lower bound above the frozen materiality
   threshold; a valid false requires the upper bound below it. At least one true
   signal is required to unlock T6 by default.

The command and acceptance details remain canonical in
[G0 execution plan](G0_EXECUTION_PLAN.md#ordered-implementation-and-acceptance-tasks).
