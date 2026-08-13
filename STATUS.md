# Project Status

Updated: 2026-08-13

## Current verdict

Conditional Select。

## Claim states

| Item | State |
|---|---|
| SGLang HiCache L2 → L3 source seam | SOURCE_VERIFIED against `b058dc910619c9d4bce9e9e24117104ffc491fa6`; G0 audit records exact hook/queue/ref evidence |
| Repository skeleton and migrated documentation | IMPLEMENTED_UNVALIDATED; local `make check` passed on 2026-08-05 |
| Mooncake `v0.3.12.post1` release candidate | EXPERIMENTALLY_VALIDATED for the first-C0 target only: exact commit `6041a609a8c3af35e778f70db344f145c2914980` and official CPython 3.11 Linux x86_64 wheel digest are recorded, and the pinned SGLang adapter completed the stock TCP/direct-I/O C0 path. This is not a general compatibility claim. |
| Exact Mooncake runtime version/build compatibility | RUNTIME_ARTIFACT: the target-Linux r6 artifact retains the resolved SGLang/Mooncake/model/build identities used by the passing C0. Fresh C1 must re-admit its own realized environment. |
| Upstream patch provenance scaffold | IMPLEMENTED_UNVALIDATED: repository manifest/test pin three ordered external series; all remain `PLANNED`, so no upstream patch or apply verification exists yet |
| New-Put payload-byte attribution | DECIDED but unimplemented: D1 authorizes a pre-collapse Mooncake trace-only observation patch. Until its focused test and trace-enabled non-interference artifact exist, new-Put attribution remains STOP. |
| Worker A Put → fresh Worker B Get / prefill survival | EXPERIMENTALLY_VALIDATED for first C0 r6: stock A published 512 prompt tokens; fresh B-L3 restored 448 storage-cached tokens with 64 uncached, while fresh B-no-L3 had 0 cached and 512 uncached. Prompt IDs, completion IDs and output hashes matched, so `RESTORE_PATH_PASS=PASS` and `REMOTE_VALUE_SURVIVES=PASS`. This does not satisfy fresh-C1 C0 or D14 S1. |
| D14 scope/baseline convergence | DECIDED: formal term is Shared-L3 Publication Admission; speculative scope, X*, S1–S3, online oracle stop bound and candidate freeze constrain subsequent work, but are not runtime evidence |
| C0 restore-qualification contract | DECIDED contract plus RUNTIME_ARTIFACT: owner-confirmed r6 classification is `execution_status=EXECUTED`, `gate_outcome=PASS`, `RESTORE_PATH_PASS=PASS`, `REMOTE_VALUE_SURVIVES=PASS`, `next_action=REVIEW_C1`. |
| C1 D14 preregistration contract | DECIDED: S1 endpoint, finite X* audit, S2/S3 witness and freeze rules are defined; all numeric/runtime fields remain UNRESOLVED |
| First-C0 execution materials | RUNTIME_ARTIFACT: r6 verified the fail-closed bundle at `data/c0-input-bundles/first-c0-20260812-r7`, manifest SHA-256 `207f866e2bbc83f96207d112a8d10730280fddd91422b59f02e7b858d9b7c477`, and one-shot runbook SHA-256 `577588c07b7cb7d5a593f5dd2b0d69a8d733a6c6cc898767374dc7a3b241b4ec`. Focused local counterexample tests and independent root/verifier/bundle checks pass. OCI, collector/classifier, dual GPUs, same-AZ and formal lifecycle controls were not required for C0 correctness. |
| First target C0 evidence | RUNTIME_ARTIFACT: r6 used an independent CPU/Store host with a 1 GiB TCP/CPU segment and sequential, independently cold A/B lifecycles on one L20 worker. The sealed archive is `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r6/c0-raw-evidence.tar`, SHA-256 `a155afe674d7a0fa76ad4e14a3b02a5cbeabf3ba22b437fd67ce79310b43f35c`; independent OSS readback matched. C and worker processes were stopped after capture. The r1–r5 deployment/admission evidence is also retained off-host under `c0/runs/first-c0-20260813-r{1..5}/preflight-blocker-evidence.tar`, with independently matching readback hashes recorded in the deployment retrospective. r4 (missing OpenSSL headers) and r5 (stock kernel D2H segfault) remain `BLOCKED_BEFORE_C0` with predicates `NOT_EVALUATED`; only r6, which used the stock `--hicache-io-backend direct` path, is the classified C0. |
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

首次 C0 已完成并封存。它只解除“stock external-L3 restore 是否真实存在”的资格疑问；不得复用其 C/worker 状态进入 C1，也不得据此开始 D1、behavior hook 或性能主张。下一步按以下顺序：

1. 按 [first-C0 deployment retrospective](docs/implementation/G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md) 把首次运行实际暴露的前置写入下一版 C1 runbook/admission：stable CPython 3.11.13 与 headers、`libssl-dev`、可发现的 venv/ninja 路径、`SGLANG_BUILD_RUST_EXTS=none`，以及 passing L20/driver 580.126.09/PyTorch 2.11.0+cu130 组合使用 stock `--hicache-io-backend direct`；不预建 OCI、通用 runner、自动 classifier/finalizer 或完整依赖平台；
2. 创建 fresh C1 cohort，以新 keyspace、独立 C/worker state 和新 evidence destination 完整重做 C0。r6 的 runner/命令可以复用，r6 的 Store、coldness、ledger 和 predicate artifact 不可复用；
3. C1 C0 再次 `PASS` 后，执行 finite source/runtime audit X* 的 actual selective semantics、quota/adapter wiring、metrics/prefetch threshold 与相关 PR impact；未复核内容保持 `SOURCE_TO_REVERIFY` 或从 X* construction 移除；
4. treatment-blind 完成 baseline-only calibration/freeze 后先做 S1 `RESTORE_VALUE_REGION`，再以 sticky-reuse workload 运行 S2 `PUBLICATION_COST_ENVELOPE` 与 S3 `CAPACITY_EXTERNALITY`。S1 无价值 region/remote Get≈0 时 STOP；S2/S3 双 valid-false 只有区间上界排除阈值才 STOP；
5. 只有 S1–S3 surviving ruling 或 D12 的窄例外允许继续时，才实现 Mooncake pre-collapse observation 与最小 SGLang opaque correlation；trace-only 非干扰通过后才允许 fail-open behavior hook；
6. 不实现 Agent hint、`VALUE_DENSITY`、stale/page-level admission、router 或 eviction；只有残余证据与新的 owner decision 才可重开一个最小 candidate。

当前不是 C0 evidence blocker；当前 C1 入口 blocker 是第 1 项尚未物化并复核。它只包含已由 r4/r5 证明会阻断运行的修正，不把未发生的错误假设提前平台化。

后续 G2a 还必须在“写成本 / 资源争用”与“容量竞争 / 查询时可用性”两条候选收益链中，至少闭合一条各 arm 自身的运行时中介证据与 paired Goodput@TTFT-SLO 结果。只有 bytes、NIC/CPU 计数器或 modeled occupancy 不能通过性能机会闸门；两条链都不成立时停止 Goodput/TTFT 策略方向，只有可复现 new-Put payload 节省时才允许降级到 payload-efficiency。

## Explicitly not done

- 没有 fresh C1 cohort 的 C0 重跑
- 没有 S1 restore-value、S2 publication-cost 或 S3 capacity-externality 结果
- 没有 runtime hook
- 没有 trace instrumentation
- 没有 TTFT/Goodput 性能结论；首次 C0 token 计数只证明 restore 机制
- 没有社区 issue/PR
- 没有超出首次 r6 TCP/direct-I/O/L20 拓扑的通用 Mooncake/SGLang compatibility claim
