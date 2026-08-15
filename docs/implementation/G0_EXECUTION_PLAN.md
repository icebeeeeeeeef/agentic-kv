# G0 Runtime Closure Implementation Plan

**Goal:** turn the SOURCE_VERIFIED SGLang seam into a minimal, auditable two-worker-lifecycle runtime proof, or stop with retained failure artifacts.

**Architecture:** use two independently cold SGLang worker lifecycles and one external Mooncake Store. First C0 may run A and B sequentially on one physical GPU after A exits; this proves cross-process restore only. Keep L1/L2 write-through upstream. After C0 `PASS`, a fresh C1 cohort must redo C0, source/runtime-audit a finite X*, complete baseline-only freeze and establish `S1 RESTORE_VALUE_REGION`, then sticky-reuse `S2 PUBLICATION_COST_ENVELOPE` and `S3 CAPACITY_EXTERNALITY`. The old one-shot `WRITE_COST_SENTINEL` / `CAPACITY_PRESSURE_SENTINEL` procedure below is retained as superseded history and must not run. Only a surviving active contract (or D12's narrow payload exception) unlocks Mooncake D1 observation and SGLang opaque trace correlation; only after those are inert may one fail-open decision be added just before `write_storage`. The external store is the only L3 memory contributor and uses TCP.

**Tech Stack:** SGLang `b058dc910619c9d4bce9e9e24117104ffc491fa6`; Mooncake release candidate `v0.3.12.post1` (`6041a60` release commit prefix); Python; CUDA GPU workers; Mooncake TCP Store; JSONL artifacts.

**Historical local-executor note (2026-08-08):** the local macOS/arm64 preflight stopped before any
upstream process started; see [T5 local preflight STOP](G0_T5_LOCAL_PREFLIGHT_STOP.md). This
does not decide target-Linux compatibility, but it blocks T6/T7 on that executor. A future
Linux CUDA run must re-execute every precondition below rather than treating this record as a
partial deployment.

**First-C0 historical execution boundary:** the completed first C0 was governed by [D18's minimal execution contract](G0_PRE_RENTAL_EXECUTION_CONTRACT.md): materialize content-addressed inputs plus a one-shot runbook/raw-capture/off-host handoff, then verify target-host build/API/config/write-trigger/GPU/Store/private-TCP facts after rental and run Task 1. OCI/OSS are optional delivery mechanisms. Formal finalization, automatic classification and lifecycle controls were not first-C0 prerequisites. This cannot weaken either Task 1 predicate; fresh C1 requires its own reviewed runbook and admission.

**Evidence-driven deployment carry-forward:** first-C0 r1–r5 exposed a bounded set of real bootstrap/runtime blockers. The exact symptoms, minimal fixes and passing r6 environment are retained in the [first-C0 deployment retrospective](G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md). A future C1 runbook may reuse that dependency recipe and stock direct-I/O setting, but must have a new reviewed hash and fresh cohort; the historical r6 runbook and runtime state remain immutable evidence.

---

## Preconditions and hard admission checks

| Item | Required value / check | Required response if not true |
|---|---|---|
| SGLang | checkout resolves exactly to `b058dc910619c9d4bce9e9e24117104ffc491fa6` | `BLOCKED_BEFORE_C0`; do not apply patches or collect predicate data. |
| Mooncake | checkout tag is `v0.3.12.post1`; record full `git rev-parse HEAD`; installation reports `0.3.12.post1`; retain wheel/source-build SHA-256 | `BLOCKED_BEFORE_C0`; retain probe logs. |
| Mooncake build | First probe uses the published Linux x86_64 CPython 3.11 wheel `mooncake-transfer-engine==0.3.12.post1` with SHA-256 `8b73bf8a4f1de741a73f04f32f1e73549c60bfbf7ee73710141ef1f8ea324439`; there are no local CMake flags in this probe | `BLOCKED_BEFORE_C0`; do not silently substitute a source build or another wheel. |
| GPU layout | one compatible CUDA GPU; A and B are distinct, non-overlapping lifecycles with independent writable state; TP=PP=DP=DCP=1 | `BLOCKED_BEFORE_C0`; do not use TP/PP/DP/DCP as a substitute for two worker lifecycles. |
| Model | dense, non-hybrid model and tokenizer revision are immutable in the manifest; the same model/tokenizer hashes are visible on A and B | `BLOCKED_BEFORE_C0`; no floating model revision or differing tokenizer. |
| Cache | HiRadixCache is asserted from startup output; Unified Radix Tree disabled; one fixed page size and L1/L2 capacities | `BLOCKED_BEFORE_C0` for C0; do not accept fallback cache or per-arm L1/L2 changes. |
| L3 | C is the only non-zero `global_segment_size`; A/B each use `0`; exact C config/hash, post-`setup` success, live PID/TCP and stock master `/get_all_segments` raw response with target-confirmed schema jointly prove C admission | `BLOCKED_BEFORE_C0`; workers must not contribute memory and C must not be zero-segment. |
| Transport | `MOONCAKE_PROTOCOL=tcp`, blank device, no RDMA/GDR/NIXL flags | `BLOCKED_BEFORE_C0`; do not broaden G0 to another data path. |
| New-Put payload attribution | [D1](../project/DECISIONS.md#d1--保留-new-put-payload-指标并授权最小观察-patch) defines the only allowed pre-collapse Mooncake trace-only observation; its implementation is gated by the active S1–S3 ruling in [D14](../project/DECISIONS.md#d14--shared-l3-publication-admission-收敛与替代攻击) or D12's narrow payload exception. | Do not implement it after D14's valid opportunity STOP without D12's first-stage resource-objective record; never run `BYTE_RECONCILE` or make payload-efficiency claims until the patch and its trace-disabled/trace-enabled non-interference oracle pass. |

### Topology and canonical per-run configuration

```text
GPU Worker A (cold only at run start)  -- TCP -->  External Mooncake Store C
GPU Worker B (fresh / cold before probe) -- TCP -->  master + metadata + Store C
```

Use one master and one metadata service on C (they may be co-located) and one external store service with a non-zero, bounded segment. A/B are logical lifecycles and may share one recorded worker host/GPU sequentially for first C0; `A_HOST` may therefore equal `B_HOST`. `C_HOST` is the independently recorded Store endpoint. These names are not runtime defaults.

```bash
export SGLANG_SHA=b058dc910619c9d4bce9e9e24117104ffc491fa6
export MOONCAKE_TAG=v0.3.12.post1
export MOONCAKE_RELEASE_PREFIX=6041a60
export MOONCAKE_PROTOCOL=tcp
export MOONCAKE_MASTER=${C_HOST}:50051
export MOONCAKE_METADATA=http://${C_HOST}:8080/metadata
export MOONCAKE_GLOBAL_SEGMENT_SIZE=0
export SGLANG_ENABLE_UNIFIED_RADIX_TREE=0

git -C "$SGLANG_CHECKOUT" rev-parse HEAD
git -C "$MOONCAKE_CHECKOUT" checkout "$MOONCAKE_TAG"
git -C "$MOONCAKE_CHECKOUT" rev-parse HEAD
python3.11 -m pip download --only-binary=:all: --no-deps mooncake-transfer-engine==0.3.12.post1 -d "$MOONCAKE_WHEEL_DIR"
sha256sum "$MOONCAKE_WHEEL_DIR"/mooncake_transfer_engine-0.3.12.post1-cp311-cp311-manylinux_2_28_x86_64.whl
python3.11 -m pip install --no-deps "$MOONCAKE_WHEEL_DIR"/mooncake_transfer_engine-0.3.12.post1-cp311-cp311-manylinux_2_28_x86_64.whl
python3.11 -c 'import mooncake; import importlib.metadata as m; print(m.version("mooncake-transfer-engine"))'
```

The `sha256sum` output must equal the precondition value. The official SGLang adapter only documents the generic source build (`bash dependencies.sh && cmake .. && make -j`); it does not pin source-build switches for this SGLang commit. A source-build fallback is therefore a separate source-compatibility investigation, not an interchangeable G0 input.

On C, use a dedicated JSON config with `protocol: "tcp"`, `device_name: ""`, a non-zero integer `global_segment_size`, `local_buffer_size: 0`, and the addresses above. Start metadata, master, and the external store. Pinned SGLang uses the stock master `/get_all_segments` endpoint on metrics port 9003; retain the live raw response, then require owner-confirmed response fields to match C's private endpoint and exact configured nonzero segment before either request. When first C0 reuses one physical worker host, A and B use the same reviewed worker private endpoint in `local_hostname`; fresh PID/state/run identity proves lifecycle separation. Their Store/keyspace fields remain identical, including `global_segment_size: 0`, `protocol: "tcp"`, `tenant_id`/`extra_backend_tag`, model name, `master_metrics_port`, `check_server: true`, and prefetch threshold 256.

Pinned stock `MooncakeStore` writes one startup-only object whose key is `sglang_mooncake_store_warmup_key` + UUID. It is the sole exception to A's tested-key writer invariant because it bypasses `_tag_keys`, while model page keys are tagged by the shared `config_prefix`. Retain the pinned adapter hash/source proof and A/B-L3 warmup/config-prefix success logs; B must never write a tested config-prefix/model key.

The candidate is not compatible until this API smoke probe passes under the pinned checkouts:

```bash
python - <<'PY'
from mooncake.store import MooncakeDistributedStore
store = MooncakeDistributedStore()
for name in ("setup", "register_buffer", "batch_is_exist", "batch_put_from", "batch_get_into"):
    assert hasattr(store, name), name
print("MOONCAKE_API_SURFACE_OK")
PY
```

Pass: exact SGLang SHA, tag-resolved Mooncake full SHA beginning `6041a60`, version/build hash, and API surface recorded. Any mismatch, error or unreachable service before a request is `BLOCKED_BEFORE_C0`, not a C0 outcome. Do not label a release compatible solely from tag/API shape; retain logs and the attempt manifest.

## File and patch boundaries

Before any upstream change, use the repository-owned [patch provenance manifest](../../patches/manifest.json)
and its [materialization contract](../../patches/README.md). Its three entries are currently
`PLANNED`: they pin source and execution order only. The implementation task that creates a
real upstream change must export an ordered `git format-patch` series, record file hashes,
and prove fresh-worktree `git am` application before it can call the series `MATERIALIZED`.
This plan does not treat an empty declared directory as an applied patch.

| Patch | Owned location | Tests | Commit boundary |
|---|---|---|---|
| Mooncake observation only | pinned Mooncake checkout, at the `OBJECT_ALREADY_EXISTS -> success` reduction boundary; exact file/line pinned when implemented | focused cause-record and trace-disabled equivalence test | `trace: expose pre-collapse object Put terminal causes` |
| Trace only | `python/sglang/srt/managers/cache_controller.py`; `python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py`; a new focused trace test | `test/registered/unit/mem_cache/test_l3_trace_correlation.py` | `trace: correlate storage operation batches without behavior change` |
| Behavior only | `python/sglang/srt/mem_cache/hiradix_cache.py`; a new narrow admission test | `test/registered/unit/mem_cache/test_l3_admission_seam.py` | `feat: add fail-open L3 admission seam` |
| Runtime driver/artifacts | this repository under `experiments/`, `src/agentic_kv/`, `tests/` | local deterministic tests and retained run bundles | separate commits after upstream patch tests pass |

Do not vendor either upstream checkout, add a submodule, modify a read path, alter L1/L2 eviction/configuration, or introduce a policy framework. The trace patches carry opaque IDs and observation-only cause records; no trace value is used by admission, queue ordering, key construction, retry, or read behavior.

## Ordered implementation and acceptance tasks

### Task 1: establish stock external-store recovery and prefill survival

The exact C0 request construction, coldness certificate, evidence joins and classification table are
frozen in the [C0 Restore Qualification Contract](G0_C0_RESTORE_QUALIFICATION_CONTRACT.md). It
implements this Task 1 oracle and cannot relax it.

For the first target run, use only the one-shot C-host and worker commands from D18. Manual fail-fast execution is enough;
do not require an independent collector/classifier, C1 runner, general orchestrator or formal abort/finalizer machinery.

- [x] Complete the target admission probe: verify content hashes, build/API/config, actual page size, stock write policy/threshold, one GPU, C health/nonzero segment, worker zero-segment and private TCP. If any item fails, record `BLOCKED_BEFORE_C0` and do not evaluate either predicate.
- [x] Start fresh C/unique keyspace and save configuration, process logs, segment response and source/build identities; A is sole writer of tested config-prefix/model KV objects, with only the source-proved stock warmup-key exception retained and excluded.
- [x] Start stock pinned A with the frozen model/tokenizer/cache configuration and `global_segment_size=0`; run the minimal fixed request sequence that reaches the verified write condition and save terminal Put.
- [x] Save A exit, then start fresh B-L3 with the same runbook-bound realized configuration, empty request ledger, independent writable state, no persistent local cache and `global_segment_size=0`. A/B may sequentially use the same GPU.
- [x] Issue the identical page-aligned raw prompt/token sequence to B and close the A→C→B join using fresh C/keyspace, A sole-writer of tested config-prefix/model KV objects, the isolated stock warmup-key exception, A Put terminal and B Get/load evidence.
- [x] For the L3 arm, request the pinned runtime's cache-source breakdown and preserve B's `cached_tokens_details.storage`, total `cached_tokens`, `prompt_tokens`, and derived `uncached_prompt_tokens = prompt_tokens - cached_tokens` together with Mooncake adapter/Get evidence.
- [x] Run the identical deterministic-greedy request on a separately fresh B-cold no-L3 control. Preserve the same token-accounting fields, at least one completion token and output hash. This is a token-level mechanism control, not a TTFT/Goodput performance claim.
- [x] Before release, inventory/checksum the raw C0 bundle, copy it off-host and verify the copied checksum.

**First target C0 outcome (2026-08-13):** owner-confirmed r6 is `execution_status=EXECUTED`,
`gate_outcome=PASS`, `RESTORE_PATH_PASS=PASS`, `REMOTE_VALUE_SURVIVES=PASS`,
`next_action=REVIEW_C1`. A published 512 prompt tokens; fresh B-L3 reported 448 storage-cached
and 64 uncached tokens, while fresh B-no-L3 reported 0 cached and 512 uncached tokens. Prompt IDs,
completion IDs and output hashes matched. The sealed raw archive is
`oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r6/c0-raw-evidence.tar`,
SHA-256 `a155afe674d7a0fa76ad4e14a3b02a5cbeabf3ba22b437fd67ce79310b43f35c`,
with an independently matching OSS readback. Retained r4/r5 attempts are `BLOCKED_BEFORE_C0`,
not failed C0s; only r6 used the stock `--hicache-io-backend direct` path and reached the oracle.
This qualifies the restore mechanism only and cannot replace fresh-C1 C0 or D14 S1.

Record two outcomes rather than collapsing them into one:

- `RESTORE_PATH_PASS`: A has successful Put evidence, B is locally cold before the request, B records successful remote Get/loaded storage pages, and fixed-decode output equals the no-L3 control.
- `REMOTE_VALUE_SURVIVES`: `RESTORE_PATH_PASS` already holds, `cached_tokens_details.storage > 0`, and the L3 arm has fewer uncached/prefill tokens than the identical B-cold no-L3 control. TTFT may be retained as a diagnostic but is not a substitute for this token-level oracle and is not yet a performance claim.

No A terminal Put after the verified trigger sequence means `BLOCKED_BEFORE_C0`, not a restore failure. Once the request chain is executed: `PASS` only when both predicates hold. `FAIL` when B cannot restore, outputs differ, or a verified restore does not reduce uncached/prefill tokens; its next action is `STOP`, so do not implement D1/trace/hook and preserve all raw artifacts. `INCONCLUSIVE` when local coldness, remote Get, cache-source breakdown, output or comparable token counts cannot be proven; do not upgrade Task 1 or continue to Task 2. Never write two values into one `gate_outcome`.

`REMOTE_VALUE_SURVIVES` is necessary but is not the full D14 S1 ruling. Before any D1 work, the next target-Linux execution must create a treatment-blind S1 preregistration that defines the target workload/load/capacity coordinates, final endpoint, materiality/interval rule, B-cold recompute control and remote-Get materiality floor. If all covered, decisive target coordinates show `restore <= recompute`, or remote Get is approximately zero, record `STOP`; insufficient precision or missing comparability remains `INCONCLUSIVE`.

### Active Task 2: prepare and run D14 S2/S3 survival gates

The treatment-blind C1 freeze order, S1 endpoint, finite X* audit surface, sticky-reuse evidence
and S2/S3 interpretation are frozen in the [D14 Survival Preregistration Contract](G0_D14_SURVIVAL_PREREGISTRATION_CONTRACT.md).
It implements D14 and cannot alter its Gate/STOP.

Before any X* audit or calibration, create a fresh C1 cohort and rerun the full C0 oracle. C1 may reuse runbook/launcher code,
but never first-C0 Store/worker state, coldness or eligibility artifacts. A failed C1 C0 blocks the remaining C1 stages.

Do not copy the historical Task 2 manifest without revision. Before viewing treatment data:

- source-audit the pinned stock `write_through_selective` behavior, usable quota/eviction controls, adapter wiring and relevant metrics/prefetch semantics; record unresolved details as `SOURCE_TO_REVERIFY`, not `SOURCE_VERIFIED`;
- construct only the actually verified portion of X* = stock selective + sufficient L2 + usable stock controls; preserve configuration/effect evidence and do not pretend an unconfigured quota exists;
- freeze sticky-reuse operational criteria: it must pass stock selective's locally observed condition yet have low remote value over fixed H; record its estimated/observed publication mass. one-shot remains an X* negative control only;
- preregister S2 pressure witnesses, S3 bounded-capacity/shared-prefix witnesses, endpoint, `delta`, paired interval method, run isolation, repeat budget and stop rules. S1 is a hard veto; S2/S3 become valid false only when all witnesses hold and the interval upper bound is below `delta`.

S2/S3 cannot use offline replay to infer TTFT/Goodput. If both are valid false, record the D14 pre-implementation STOP. If either is `INCONCLUSIVE`, do not reinterpret it as a null; if either signals, it authorizes only trace-path investment, not a candidate. The online cheating oracle-vs-X* comparison comes later on the real runtime path and is stop-only.

### Historical Task 2: old D12 stock pre-D1 investment sentinels (superseded; do not execute)

Use only the stock pinned builds that passed Task 1. These are coarse system-level survival probes, not admission treatments, not a new Gate, and not substitutes for G2a/G3.

Before viewing either treatment arm, copy
[`g0-stock-sentinels-preregistration.example.json`](../../experiments/manifests/g0-stock-sentinels-preregistration.example.json)
into the ignored run bundle and complete `CALIBRATE_BASELINE → FREEZE_CONTRACT`:

- build the offered-load grid and choose the low-load sanity cell and knee from `L2_ONLY` baseline runs only; the mechanical knee rule is frozen before any L3-enabled result is inspected;
- derive the roomy/small Store values from one frozen KV-payload estimation method such that `reusable_set < small < reusable_set + one_shot_fill`, while roomy exceeds the full distinct set by a frozen safety margin; save the estimate inputs, and later verify each actual segment from a fresh Store response. This establishes the intended pressure coordinate, not observed occupancy or eviction;
- freeze TTFT-SLO, `Goodput@TTFT-SLO` as the sole primary endpoint, paired-run as the analysis unit, arm-order rule, one-sided interval method, engineering materiality threshold `delta`, minimum/maximum paired repeats, and the stopping rule. Minimum repeats are 3; the maximum must be a finite value chosen from the target-environment noise calibration and experiment budget before treatment. The interval method must be valid under any sequential stopping rule; otherwise run the frozen maximum and classify only once;
- checksum the completed preregistration before the first treatment result. A later change to workload, knee, capacity, threshold, interval method or repeat budget creates a new version and retains the old artifact; it never overwrites a null and retries silently.

For both sentinels, define positive relative degradation in the treatment arm. The control-arm Goodput denominator must be positive. A signal is `true` only when every pressure/fairness prerequisite and required mediator direction holds and the preregistered one-sided interval lower bound exceeds `delta`. It is a valid `false` only when those prerequisites hold and the interval upper bound is below `delta`. If the interval crosses `delta` when the frozen maximum repeat budget is exhausted, a denominator is non-positive, or a prerequisite is unproven, record `INCONCLUSIVE`. A non-significant p-value, near-zero point estimate, or the minimum three pairs alone never produces a valid null.

#### `WRITE_COST_SENTINEL`

- [ ] Use a page-aligned zero-reuse/one-shot workload so L3 Get value is absent and first-write waste is maximized; keep the external Store roomy enough that capacity pressure is not the intended mediator.
- [ ] Derive the target offered load from the stock baseline service curve before inspecting the treatment result; run one low-load sanity cell and one cell near the predeclared knee.
- [ ] Compare stock L3 enabled with stock L2_ONLY under identical model, request sequence, worker assignment, cache settings other than the necessary L3 enable/disable treatment, and fresh isolated run state. Use randomized paired order and at least 3 paired repeats.
- [ ] Retain client TTFT/Goodput and Store-side NIC RX/CPU counters. NIC/CPU only confirms that backend work was exercised; it is not new-Put attribution and cannot pass a performance chain alone.

Let `d_write = (Goodput_L2_ONLY - Goodput_L3) / Goodput_L2_ONLY`. `l3_path_cost_signal=true` only when the L3 arm has identifiable Store activity and the preregistered one-sided interval lower bound for `d_write` exceeds `delta` at the knee. Because L3 enable/disable changes Put together with lookup/miss, this is an upper-bound path-cost signal, not write-cost attribution; D1 and the later forced-action hook are still required to isolate chain A. More traffic without endpoint degradation is a valid null only when the interval upper bound is below `delta`. If the bound still crosses `delta`, or the knee, zero reuse, roomy capacity, Store activity, or fair arm difference cannot be established, record `INCONCLUSIVE`, not `false`.

#### `CAPACITY_PRESSURE_SENTINEL`

- [ ] Keep L3 enabled and use one fixed mixed workload: a reusable long-prefix stream plus a one-shot fill stream. The result is judged on the reusable requests.
- [ ] Compare two separately started, otherwise identical external Store C instances whose configured `global_segment_size` values are predeclared as roomy and small. Do not mutate capacity in place. Preserve each config and require the health/segment response to show the intended actual segment before accepting the arm.
- [ ] Keep model, requests, arrival times, worker assignment, A/B worker `global_segment_size=0`, transport, remote eviction implementation, warm-up, measurement, and drain fixed. Use randomized paired order and at least 3 paired repeats.
- [ ] Retain storage-cached tokens, successful remote Get/loaded-storage evidence, uncached/prefill tokens, TTFT and Goodput for the reusable stream.

Let `d_capacity = (Goodput_roomy - Goodput_small) / Goodput_roomy`. `capacity_pressure_signal=true` only when the small arm shows lower query-time storage availability/useful Get, higher uncached/prefill tokens, and the preregistered one-sided interval lower bound for `d_capacity` exceeds `delta`. This proves capacity sensitivity only; without SOURCE_VERIFIED telemetry it does not prove a specific occupancy, victim, eviction event, or admission benefit. A valid `false` requires the actual segment and intended fill-pressure coordinate to be proven and the interval upper bound to be below `delta`. If the bound still crosses `delta`, or actual segment, fill pressure, reuse source, or fair arm difference cannot be established, record `INCONCLUSIVE`, not `false`.

Record `gate_outcome` for execution quality separately from `l3_path_cost_signal` and `capacity_pressure_signal`. Continue automatically to Task 3 only when at least one signal is `true`. If both satisfy the preregistered exclusion rule and are valid `false`, record `gate_outcome=STOP` with `reason_code=PRE_IMPLEMENTATION_STOP`: stop the Goodput/TTFT mainline before D1, retain shared-L3 characterization, and do not call the result Runtime backbone or Flagship evidence closure. Runtime engineering depth alone is not a reason to continue. One `INCONCLUSIVE` result prevents the double-null STOP.

The only exception is a new owner-approved resource-objective record created before any D1 result is known. It must freeze how payload maps to a real bandwidth/Store CPU/capacity/cost or unit-resource-serving objective, the resource budget, materiality criteria for `new_physical_put_bytes` and `not-read-within-H`, and a bounded observation-only plan. That first ruling unlocks only the Mooncake D1 observation plus the minimum SGLang opaque correlation needed for stock payload attribution; it does not unlock Task 4. Task 4 requires a second owner ruling after the trace proves material new-Put and not-read waste that maps to the frozen objective. If either sentinel is `INCONCLUSIVE`, do not continue to Task 3 or reinterpret it as no opportunity.

### Task 3: add trace-only correlation and prove it is inert

- [ ] Add `run_id`, `observation_id`, `operation_id`, `batch_ordinal`, and derived `attempt_id` as opaque correlation data. Generate `observation_id` at the prospective seam only for an eligible segment; the later behavior patch may add a `decision_id` to the same record, but this task must not compute or apply an admission action.
- [ ] Store `operation_id` on `StorageOperation` correlation data after construction; derive `attempt_id = operation_id + batch_ordinal` in `_page_backup`; emit adapter records after `_batch_preprocess`, after exists filtering, and after Put/Get result reduction.
- [ ] Emit JSONL records with logical hashes, physical object keys, each physical `buffer_size`, exists/dedup decision, Put/Get result, and worker-local monotonic sequence. The SGLang adapter records `exists_skip`; the separately patched Mooncake boundary records pre-collapse `new_put` / `race_existing` / `put_failure` for actual Put attempts, joined by opaque ID. Do not log prompts or tokens.
- [ ] Run stock and trace-only builds against the same isolated microcase; compare output tokens, logical hash order, submitted operation order, successful page counts, and queue/ref terminal state.

Pass: deterministic joins exist from observation through operation/batch/physical result; trace-only equals stock on the stated invariants. Fail: a missing/duplicate join, changed key/order/result, or unbounded trace growth. Inconclusive: one side lacks an observable terminal. STOP: revert the trace patch rather than patching policy around uncertain telemetry.

### Task 4: add the minimal fail-open binary hook

Prerequisite: the active S1–S3 surviving branch has a passing Task 3, or the D12 payload exception has both a passing observation-only artifact and a second owner ruling. A first-stage payload/resource exception never authorizes this task by itself.

- [ ] Write a failing unit test whose policy returns `DROP`; after `_finish_write_through_ack`, assert CPU/L2 event exists and `write_storage` was not called.
- [ ] Implement the policy call only after `top`, `key`, `hash_value`, `host_value`, and `prefix_keys` are ready and before `cache_controller.write_storage`.
- [ ] On a policy exception, emit a `POLICY_ERROR_FAIL_OPEN` trace record and execute the unchanged upstream write path.
- [ ] Write a failing `ALWAYS_ADMIT` equivalence test and an `ALWAYS_DROP` state test; run each before and after the minimal implementation.

Pass: fail-open invokes upstream write; DROP leaves L2 intact and creates no `StorageOperation`, backup queue entry, `ongoing_backup`, host protection, or Mooncake Put. Fail: any L2/control-path mutation or missing fail-open. Inconclusive: test cannot observe the async terminal. STOP: do not test a candidate policy.

### Task 5: enforce all-or-none prefix closure at the decision boundary

- [ ] Represent an eligible decision group as root/known-resident anchor plus ordered logical pages; record `anchor_hash` and ordered hashes. The policy interface returns one action for the entire group.
- [ ] Unit-test fully admitted group, fully dropped group, descendant-only input rejected as an unprovable group, and a split-chain reconstructed complete group.
- [ ] Prove the G0 policy interface cannot express a partial group action; use a malformed partial-group fixture only to prove rejection before the runtime path.

Pass: every decision record contains exactly one action for its complete group; normal full-prefix restore remains successful. Fail: a partial group action, an admitted unreachable suffix, or a read-path change. Inconclusive: page order/anchor cannot be observed. STOP: do not add remote metadata or per-page RPCs to repair it.

### Task 6: execute the G0 matrix

Run every scenario in a fresh C instance or a truly capacity-isolated namespace; never treat `MooncakeStore.clear()` as sufficient evidence of an isolated experiment. Preserve a stock no-patch run for `ALWAYS_ADMIT` comparison.

| Scenario | Procedure | Pass | Fail | Inconclusive | STOP |
|---|---|---|---|---|---|
| `ALWAYS_ADMIT` | Hook always admits a fixed shared prefix; compare with stock pinned run. | Output, logical page/hash order, terminal Put/Get results, and terminal queue/ref state match stock within a predeclared functional equivalence check. | Any semantic/path divergence. | Missing stock or hook trace terminal. | Do not call hook upstream-equivalent. |
| `ALWAYS_DROP` | Hook always drops after L2 ack; issue same prefix on A then cold B. | L2 CPU event and request output remain correct; no operation/queue/protection/Put; `admitted_payload_bytes=0` and `submitted_payload_bytes=0`. | Any L3 mutation or L2/ref error. | L2 or backend terminal cannot be observed. | Do not infer zero Put from a missing aggregate metric. |
| `CROSS_WORKER_RESTORE` | A admits, B starts local-cold and requests exact prefix; compare token accounting with an identical separately fresh B-cold no-L3 control. | `RESTORE_PATH_PASS` and `REMOTE_VALUE_SURVIVES`: Put/Get/cold/output join; storage-cached tokens are non-zero; L3 uncached/prefill tokens are lower than control. | B recomputes without a successful remote Get, outputs differ, or restore reduces no uncached/prefill tokens. | Cannot prove B cold, correlate Get, obtain cache-source breakdown, or compare token counts. | Shared-L3 premise fails; a TTFT-only difference cannot rescue it. |
| `PREFIX_CLOSURE` | Exercise fully admitted/dropped complete groups and a malformed partial-group fixture. | The interface rejects partial action; normal full-prefix restore remains successful. | A policy-induced unreachable descendant is admitted. | Order/anchor unobservable. | No remote directory/control-plane expansion. |
| `BYTE_RECONCILE` | Run D1's pre-collapse observation patch with matched SGLang correlation. | Physical-object buffer aggregation joins to `new_put` / `race_existing` / `exists_skip` / `put_failure`; trace-enabled is behaviorally equivalent to trace-disabled. | Missing/non-injective terminal classification or trace behavior change. | One side lacks an observable terminal. | No new-Put payload-efficiency claim. |
| `DEDUP_RACE_FAILURE` | Repeat same keys, overlap two writers, and inject/observe a Put failure where Mooncake supports it. | Trace classifies exists-skip/race/new-Put/failure separately; every operation has terminal cleanup. | Dedup counted as new Put, missing terminal, or leak. | Failure injector unavailable. | Keep the no-failure result narrow; do not claim `G0-RUNTIME VALIDATED`. |
| fail-open | Policy deliberately raises once. | One `POLICY_ERROR_FAIL_OPEN`, then upstream Put result and normal cleanup. | Request fails or DROP occurs. | Exception path lacks terminal trace. | Do not enable the hook. |
| async cleanup | Delay backend work; repeat success, duplicate, fail-open, and shutdown/detach; include a real failure only when the upstream supports non-intrusive observation/injection. | `backup_queue=0`, `ack_backup_queue=0`, `ongoing_backup={}`, and host protections return to baseline. | Any residual entry/ref/protection or hang. | Only process exit hides the state, or failure cannot be observed/injected. | No `G0-RUNTIME VALIDATED` without real failure evidence. |
| opaque trace ID | Compare trace-disabled and trace-enabled `ALWAYS_ADMIT`; use syntactically different opaque IDs. | Keys, order, decisions, results, output, and cleanup are unchanged. | ID changes behavior or key-space. | Comparison lacks matched artifacts. | Do not collect causal traces. |

## Raw artifact and manifest contract

Each attempt writes an immutable directory under ignored `experiments/runs/<run_id>/`. Every attempt contains only the common
identity/execution subset plus artifacts required by the stage actually run; absence of a future-stage artifact is not a C0 failure.

Common to every attempt:

- `manifest.json`: run/stage identity, source/build/model/tokenizer/config hashes, realized hardware/environment/topology/endpoints and relevant patch identity;
- exact commands plus raw stdout/stderr and an artifact inventory/checksum list;
- `execution_status`; when blocked, the failed admission and raw evidence; when a Gate executed, its outcome/reason and links to the first failing event.

Stage-specific subsets:

- **C0:** C health/segment, A Put/exit, B cold/Get/load, raw responses, token accounting, deterministic output hashes, no-L3 control, A→C→B join and verified off-host-copy checksum;
- **C1/S1–S3:** its own fresh C0 artifact, X* source/runtime construction, preregistration checksum, baseline-only calibration, frozen workload/coordinates/endpoint/interval/repeat rules, paired order and required pressure/fairness witnesses;
- **trace/hook/G0 matrix:** only after its Gate unlocks it, observation/decision/operation/batch/adapter JSONL, output hashes and queue/ref/protection terminal snapshots required by that scenario.

The manifest must contain `claim_state` and `execution_status`; include `gate_outcome` only when the Gate actually executed. They are orthogonal. `claim_state` becomes `IMPLEMENTED_UNVALIDATED` only after the relevant patch exists and local tests pass. It remains `ROADMAP` for planning runs and becomes `EXPERIMENTALLY_VALIDATED` only for a retained, reproducible runtime artifact that satisfies the specific scenario—not for G3 performance. `BLOCKED_BEFORE_C0` evaluates no predicate; `gate_outcome=INCONCLUSIVE` never upgrades a complete G0 ruling.

## Completion gate

G0 may be reported as `G0-RUNTIME VALIDATED` only after every required scenario above has a retained passing artifact, exact resolved binaries/sources, and a fresh repository `make check` result. A single successful smoke test, a compatible-looking Python API, or a source audit alone does not meet this gate.
