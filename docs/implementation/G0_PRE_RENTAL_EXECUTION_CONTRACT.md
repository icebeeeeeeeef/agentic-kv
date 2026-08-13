# G0 First-C0 Minimal Execution Contract

> Status: **OWNER-DECIDED EXECUTION PRIORITY / not runtime evidence** (2026-08-12).
> Authority: implements [D18](../project/DECISIONS.md#d18--首次-c0-的-correctness-only-入口与-evidence-driven-hardening). It is beneath the canonical Gate/STOP in [PROJECT_PLAN.md](../project/PROJECT_PLAN.md), the actual-state authority of [STATUS.md](../../STATUS.md), and the C0/C1 contracts. It does not authorize rental, cloud-resource creation, upstream execution, a patch, RDMA, or a benchmark.

## 1. Purpose and deletion test

The first target is one short-lived target-Linux C0 attempt, not a deployment or evidence platform. Its only runtime question is:

```text
stock A reaches terminal Put
  → fresh external C is the only nonzero L3
  → locally-cold fresh B restores the identical token prefix
  → fresh B-no-L3 executes the identical request
  → RESTORE_PATH_PASS ∧ REMOTE_VALUE_SURVIVES
```

A proposed prerequisite stays before C0 only if deleting it can cause a false predicate/outcome, contaminate isolation, or destroy the only reviewable evidence. If deletion merely makes a command fail explicitly and raw logs allow diagnosis and retry, defer it until that failure occurs.

The two workers are independent lifecycles, not necessarily two simultaneous physical GPUs. For first C0, A may exit after its Put terminal and fresh B may then use the same physical GPU. C remains an independent external Store process/host with the only nonzero bounded L3 segment. The Store data port uses a recorded private endpoint and is not exposed publicly; same-AZ and network-performance fairness are C1 concerns.

## 2. Must exist before rental

Only these two deliverables block rental:

1. **Content-addressed input bundle.** Pin and checksum the experimental payload inputs used by A/B/C: exact SGLang source, Mooncake provenance and official wheel, model/tokenizer inventory and request template. Transitive OS/CUDA/Python packages belong to the rental-day realized environment; their resolver/install stdout/stderr, install report, check and freeze must be retained, no download may be silent, and failure is `BLOCKED_BEFORE_C0`. A complete wheelhouse or OCI image is not a pre-rental Gate. Whichever delivery is selected, the target host must verify the same payload checksums before use.
2. **One-shot runbook and evidence handoff.** Provide the minimal commands and expected files for: target admission probe; C start; A fixed write-trigger sequence; A exit; fresh B-L3; fresh B-no-L3; raw stdout/stderr/API/config capture; bundle inventory/checksum; and off-host copy before release. Its separate owner-reviewed SHA-256 binds the owner-authorized inline TCP, worker-zero-segment, no-persistent-state and single-rank command template; each host must verify that external root before execution and retain the verified runbook before any command becomes runtime evidence. Manual, fail-fast commands are sufficient. There is no independent collector, automatic classifier, SSH orchestrator, scheduler, retry framework or C1 runner.

两份工件已在本地物化：fail-closed input bundle 位于被忽略的 `data/c0-input-bundles/first-c0-20260812-r7`，其 owner trust-root `bundle-manifest.json` SHA-256 为 `207f866e2bbc83f96207d112a8d10730280fddd91422b59f02e7b858d9b7c477`；手工 runbook 为 [`experiments/c0/FIRST_C0_RUNBOOK.md`](../../experiments/c0/FIRST_C0_RUNBOOK.md)，独立 owner trust-root SHA-256 为 `577588c07b7cb7d5a593f5dd2b0d69a8d733a6c6cc898767374dc7a3b241b4ec`。manifest root 通过已哈希 spec 绑定 Mooncake repository/tag/full commit 与官方 wheel hash；runbook root 不写回文件自身。本地已用 host SHA-256 先核对 bundle root，再独立核对 manifest-pinned verifier hash并执行 verifier；runbook 的错误外部 root/改字节反例也已通过。它们在物化时只构成 delivery evidence，后续 r6 才把该固定输入用于通过首次 C0。历史 roots 不得静默改写；fresh C1 必须为吸收真实 blocker 后的新 runbook 建立新的 owner-reviewed root。决议文本或没有对应 artifact 的静态检查不算物化。

## 3. Rental-day checks before the first request

These are target runtime facts and therefore cannot be required as already-passed pre-rental evidence:

1. Verify every loaded source/wheel/model/tokenizer object against the input-bundle checksum and the staged runbook against its separate runbook root. Save hashes of the generated C/worker configs plus server/runtime readback; record exact SGLang/Mooncake build/API identity and actual request/response fields.
2. Record actual cache implementation and page size; freeze the source-verified stock values `write_through`, write threshold `1`, one A request, prefetch threshold `256`, and require the aligned shared prefix length to be at least that prefetch threshold.
3. Verify one compatible GPU is visible with recorded UUID. A/B use separate PID/lifecycle and writable state, do not overlap, expose no persistent local cache, and set worker `global_segment_size=0`.
4. Start fresh C with a nonzero bounded segment; record health/config. Verify A/B can reach its recorded private endpoint and that the Store data port is not publicly exposed.

Any failed or missing check stops before the request chain:

```text
execution_status = BLOCKED_BEFORE_C0
RESTORE_PATH_PASS = NOT_EVALUATED
REMOTE_VALUE_SURVIVES = NOT_EVALUATED
```

This is not a C0 `FAIL`/`STOP`, S1 evidence, or a claim about shared-L3 value. Fix only the observed blocker, retain its raw output, and retry with a new attempt identity.

## 4. C0 execution and retained evidence

Follow [the C0 contract](G0_C0_RESTORE_QUALIFICATION_CONTRACT.md) exactly:

1. Create fresh C/unique keyspace; A is the only writer of tested config-prefix/model KV objects. The only permitted exception is the pinned stock client startup warmup object `sglang_mooncake_store_warmup_key` + UUID, whose namespace separation and A/B-L3 success logs must be retained; B may not write a tested key.
2. Run the smallest fixed A request sequence that satisfies the measured stock write condition and yields a terminal Put for the shared prefix. No terminal Put means `BLOCKED_BEFORE_C0`, not restore failure.
3. Save A terminal/exit; create fresh B-L3 with an empty request ledger and independent local state; run the identical raw prompt/token sequence.
4. Destroy B-L3; create fresh B-no-L3 and run the identical request/control.
5. Save raw identity/config/log/response, cold certificate, A→C→B join, Get/load, token accounting and deterministic output evidence. The owner applies the frozen table manually; a separate classifier is unnecessary.
6. Before releasing any instance, create the artifact inventory and checksum, copy the complete raw bundle off-host, and verify the copied checksum.

Docker/OCI, TTFT, a container restart, aggregate Store traffic, a human summary, or a direct L1/L2 metric alone cannot substitute for the token oracle, cold certificate, join, no-L3 control or deterministic output oracle.

## 5. After the first C0

- **PASS:** review only blockers actually encountered. Reuse the runbook/launcher code if useful, but C1 must use a fresh cohort, fresh Store/keyspace, fresh worker state, and its own C0 artifact before X*, calibration or S1.
- **BLOCKED / FAIL / INCONCLUSIVE:** retain raw evidence, identify the exact failed condition, and add only the smallest check/fix that prevents recurrence or misclassification. A C0 `FAIL` has next action `STOP` pending owner review; `STOP` is not written as a second gate outcome. Do not pre-build C1, D1, trace, hook, candidate, RDMA, or a general cloud experiment platform.

D16 controls—operator finalizer, deadline/quarantine, full abort lifecycle, RAM prefix-isolation, terminal markers and retention policy—remain optional hardening for a repeated/formal cohort when a real failure or C1 reproducibility requirement justifies them. They are neither implemented nor required for first C0.

## 6. Claim boundary

This contract's original pre-rental deliverables did not themselves establish runtime compatibility or C0 qualification. The later first-C0 r6 artifact did verify the scoped target-Linux build/API, Store/private-TCP, Put/Get, coldness, token-survival and off-host-copy chain; its observed deployment blockers and passing profile are recorded in the [first-C0 deployment retrospective](G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md). That result remains restore qualification/S1 input only, never S1, G0, performance, cross-GPU, multi-host, production or RDMA validation. Fresh C1 must re-admit its own environment and rerun C0 with new runtime state and evidence.
