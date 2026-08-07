# G0 Runtime Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development` (recommended) or `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** turn the SOURCE_VERIFIED SGLang seam into a minimal, auditable two-worker runtime proof, or stop with retained failure artifacts.

**Architecture:** use two independently cold GPU SGLang workers and one external Mooncake Store. Keep L1/L2 write-through upstream; add one fail-open decision just before `write_storage`, then separately add opaque trace correlation from decision through adapter results. The external store is the only L3 memory contributor and uses TCP.

**Tech Stack:** SGLang `b058dc910619c9d4bce9e9e24117104ffc491fa6`; Mooncake release candidate `v0.3.12.post1` (`6041a60` release commit prefix); Python; CUDA GPU workers; Mooncake TCP Store; JSONL artifacts.

---

## Preconditions and hard admission checks

| Item | Required value / check | STOP if not true |
|---|---|---|
| SGLang | checkout resolves exactly to `b058dc910619c9d4bce9e9e24117104ffc491fa6` | Do not apply patches or collect data. |
| Mooncake | checkout tag is `v0.3.12.post1`; record full `git rev-parse HEAD`; installation reports `0.3.12.post1`; retain wheel/source-build SHA-256 | The tag does not resolve, version differs, or build API probe fails. |
| Mooncake build | First probe uses the published Linux x86_64 CPython 3.11 wheel `mooncake-transfer-engine==0.3.12.post1` with SHA-256 `8b73bf8a4f1de741a73f04f32f1e73549c60bfbf7ee73710141ef1f8ea324439`; there are no local CMake flags in this probe | The target cannot use this exact wheel. Do not silently substitute a source build or another wheel. |
| GPU layout | one compatible CUDA GPU visible on A and B; A and B are distinct processes; TP=PP=DP=DCP=1 | Do not use TP/PP/DP/DCP as a substitute for two workers. |
| Model | dense, non-hybrid model and tokenizer revision are immutable in the manifest; the same model/tokenizer hashes are visible on A and B | No floating model revision or differing tokenizer. |
| Cache | HiRadixCache is asserted from startup output; Unified Radix Tree disabled; one fixed page size and L1/L2 capacities | Any fallback cache implementation or a per-arm L1/L2 configuration change. |
| L3 | C is the only non-zero `global_segment_size`; A/B each use `0`; C's bounded segment is observable via the Mooncake health/segment endpoint | The workers contribute memory or C has zero/no segment. |
| Transport | `MOONCAKE_PROTOCOL=tcp`, blank device, no RDMA/GDR/NIXL flags | Do not broaden G0 to another data path. |
| New-Put payload attribution | The current adapter terminal cannot distinguish a race `OBJECT_ALREADY_EXISTS` from a newly completed Put. | STOP `BYTE_RECONCILE` / payload-efficiency claim unless the canonical contract is changed or the user explicitly authorizes a separate pre-collapse Mooncake trace-only observation. |

### Topology and canonical per-run configuration

```text
GPU Worker A (cold only at run start)  -- TCP -->  External Mooncake Store C
GPU Worker B (fresh / cold before probe) -- TCP -->  master + metadata + Store C
```

Use one master and one metadata service on C (they may be co-located) and one external store service with a non-zero, bounded segment. `A_HOST`, `B_HOST`, and `C_HOST` below are three resolved DNS/IP names recorded in the manifest; they are not runtime defaults.

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

On C, use a dedicated JSON config with `protocol: "tcp"`, `device_name: ""`, a non-zero integer `global_segment_size`, `local_buffer_size: 0`, and the addresses above. Start metadata, master, and the external store. Query the configured master segment endpoint and save the response before starting either worker. A and B use identical `--hicache-storage-backend-extra-config` except unique `local_hostname`; both set `global_segment_size: 0`, `protocol: "tcp"`, the same `tenant_id`/`extra_backend_tag`, and the same model name.

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

Pass: exact SGLang SHA, tag-resolved Mooncake full SHA beginning `6041a60`, version/build hash, and API surface recorded. Fail: any mismatch or error. Inconclusive: services cannot be reached. STOP: do not label a release compatible solely from tag/API shape; retain logs and the failure manifest.

## File and patch boundaries

| Patch | Owned files in external SGLang checkout | Tests | Commit boundary |
|---|---|---|---|
| Trace only | `python/sglang/srt/managers/cache_controller.py`; `python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py`; a new focused trace test | `test/registered/unit/mem_cache/test_l3_trace_correlation.py` | `trace: correlate storage operation batches without behavior change` |
| Behavior only | `python/sglang/srt/mem_cache/hiradix_cache.py`; a new narrow admission test | `test/registered/unit/mem_cache/test_l3_admission_seam.py` | `feat: add fail-open L3 admission seam` |
| Runtime driver/artifacts | this repository under `experiments/`, `src/agentic_kv/`, `tests/` | local deterministic tests and retained run bundles | separate commits after upstream patch tests pass |

Do not vendor either upstream checkout, add a submodule, modify a read path, alter L1/L2 eviction/configuration, or introduce a policy framework. The trace patch carries opaque IDs only; no trace value is used by admission, queue ordering, key construction, retry, or read behavior.

## Ordered implementation and acceptance tasks

### Task 1: establish stock external-store recovery

- [ ] Start C with an isolated bounded segment and save configuration, process logs, health response, and full committed source/build identities.
- [ ] Start stock pinned A and B with identical model/tokenizer/cache configuration and `global_segment_size=0`.
- [ ] Send a page-aligned shared prefix to A; wait for its upstream L3 write completion; stop/restart or otherwise prove B has empty local L1/L2; issue the same prefix to B.
- [ ] Preserve B's request log and Mooncake adapter/Get evidence; compare against a B-cold no-L3 control only as a correctness probe, not a performance claim.

Pass: A has successful Put evidence, B is locally cold before the request, B records successful remote Get/loaded storage pages, and fixed-decode output equals the no-L3 control. Fail: B cannot restore or outputs differ. Inconclusive: local coldness or remote Get cannot be proven. STOP: do not implement the hook; preserve all raw artifacts.

### Task 2: add trace-only correlation and prove it is inert

- [ ] Add `run_id`, `decision_id`, `operation_id`, `batch_ordinal`, and derived `attempt_id` as opaque correlation data. Generate `decision_id` at the seam only for an eligible segment.
- [ ] Store `operation_id` on `StorageOperation` correlation data after construction; derive `attempt_id = operation_id + batch_ordinal` in `_page_backup`; emit adapter records after `_batch_preprocess`, after exists filtering, and after Put/Get result reduction.
- [ ] Emit JSONL records with logical hashes, physical object keys, each physical `buffer_size`, exists/dedup decision, Put/Get result, and worker-local monotonic sequence. Do not log prompts or tokens.
- [ ] Run stock and trace-only builds against the same isolated microcase; compare output tokens, logical hash order, submitted operation order, successful page counts, and queue/ref terminal state.

Pass: deterministic joins exist from decision through operation/batch/physical result; trace-only equals stock on the stated invariants. Fail: a missing/duplicate join, changed key/order/result, or unbounded trace growth. Inconclusive: one side lacks an observable terminal. STOP: revert the trace patch rather than patching policy around uncertain telemetry.

### Task 3: add the minimal fail-open binary hook

- [ ] Write a failing unit test whose policy returns `DROP`; after `_finish_write_through_ack`, assert CPU/L2 event exists and `write_storage` was not called.
- [ ] Implement the policy call only after `top`, `key`, `hash_value`, `host_value`, and `prefix_keys` are ready and before `cache_controller.write_storage`.
- [ ] On a policy exception, emit a `POLICY_ERROR_FAIL_OPEN` trace record and execute the unchanged upstream write path.
- [ ] Write a failing `ALWAYS_ADMIT` equivalence test and an `ALWAYS_DROP` state test; run each before and after the minimal implementation.

Pass: fail-open invokes upstream write; DROP leaves L2 intact and creates no `StorageOperation`, backup queue entry, `ongoing_backup`, host protection, or Mooncake Put. Fail: any L2/control-path mutation or missing fail-open. Inconclusive: test cannot observe the async terminal. STOP: do not test a candidate policy.

### Task 4: enforce prefix closure at the decision boundary

- [ ] Represent an eligible decision group as root/known-resident anchor plus ordered logical pages; record `anchor_hash`, ordered hashes, and first drop offset.
- [ ] Unit-test ancestor ADMIT + descendant DROP, ancestor DROP + descendant forced DROP, and a split-chain reconstructed segment.
- [ ] Send a deliberate policy-produced hole to the runtime probe and verify B's lookup stops at the first missing page; then reject that action before it reaches production policy code.

Pass: no decision record contains an admitted descendant after the group's first DROP; normal full-prefix restore remains successful. Fail: an admitted unreachable suffix or a read-path change. Inconclusive: page order/anchor cannot be observed. STOP: do not add remote metadata or per-page RPCs to repair it.

### Task 5: execute the G0 matrix

Run every scenario in a fresh C instance or a truly capacity-isolated namespace; never treat `MooncakeStore.clear()` as sufficient evidence of an isolated experiment. Preserve a stock no-patch run for `ALWAYS_ADMIT` comparison.

| Scenario | Procedure | Pass | Fail | Inconclusive | STOP |
|---|---|---|---|---|---|
| `ALWAYS_ADMIT` | Hook always admits a fixed shared prefix; compare with stock pinned run. | Output, logical page/hash order, completed Put/Get results, and terminal queue/ref state match stock within a predeclared functional equivalence check. | Any semantic/path divergence. | Missing stock or hook trace terminal. | Do not call hook upstream-equivalent. |
| `ALWAYS_DROP` | Hook always drops after L2 ack; issue same prefix on A then cold B. | L2 CPU event and request output remain correct; no operation/queue/protection/Put; `completed_put_bytes=0`. | Any L3 mutation or L2/ref error. | L2 or backend terminal cannot be observed. | Do not infer zero Put from a missing aggregate metric. |
| `CROSS_WORKER_RESTORE` | A admits, B starts local-cold and requests exact prefix. | A completed Put, B completed Get, B storage-loaded pages, and output equality all join by IDs. | B recomputes without a successful remote Get. | Cannot prove B cold or correlate Get. | Shared-L3 premise fails. |
| `PREFIX_CLOSURE` | Exercise ancestor/suffix decisions and an intentionally invalid attempted hole. | First missing page stops lookup; implementation rejects hole-forming action; no admitted suffix after drop. | A policy-induced unreachable descendant is admitted. | Order/anchor unobservable. | No remote directory/control-plane expansion. |
| `BYTE_RECONCILE` | **Blocked at source audit.** Current adapter terminal maps a race-existing object and a new Put to the same `0` result. | Not runnable under the current observation boundary. | State classification is source-proven non-injective. | Not applicable; more runs of the same API add no information. | No new-Put payload-efficiency claim; obtain a user decision before changing the observation boundary or metric contract. |
| `DEDUP_RACE_FAILURE` | Repeat same keys, overlap two writers, and inject/observe a Put failure where Mooncake supports it. | Trace classifies exists-skip/race/Put success/failure separately; every operation has terminal cleanup. | Dedup counted as successful new Put, missing terminal, or leak. | Failure injector unavailable. | Keep the no-failure result narrow; do not claim failure coverage. |
| fail-open | Policy deliberately raises once. | One `POLICY_ERROR_FAIL_OPEN`, then upstream Put result and normal cleanup. | Request fails or DROP occurs. | Exception path lacks terminal trace. | Do not enable the hook. |
| async cleanup | Delay backend work; repeat success, failure, duplicate, shutdown/detach. | `backup_queue=0`, `ack_backup_queue=0`, `ongoing_backup={}`, and host protections return to baseline. | Any residual entry/ref/protection or hang. | Only process exit hides the state. | No runtime policy experiments. |
| opaque trace ID | Compare trace-disabled and trace-enabled `ALWAYS_ADMIT`; use syntactically different opaque IDs. | Keys, order, decisions, results, output, and cleanup are unchanged. | ID changes behavior or key-space. | Comparison lacks matched artifacts. | Do not collect causal traces. |

## Raw artifact and manifest contract

Each attempt writes an immutable directory under ignored `experiments/runs/<run_id>/` containing:

- `manifest.json`; source SHAs, resolved Mooncake tag/SHA/version/wheel-or-build SHA-256, model/tokenizer revisions/hashes, hardware/driver, environment, topology, endpoint configs, cache values, policy and patch commits;
- A/B/C stdout/stderr, exact launch commands, health/segment endpoint responses before/after, and worker-local monotonic event logs;
- decision, operation, batch/attempt, adapter-object, Get, output-hash, queue/ref/protection snapshot JSONL files;
- workload input hash, request-to-worker assignment, warm-up/measurement/drain bounds, cleanup method, repeat/order, and a cryptographic checksum list;
- a one-page outcome record with `PASS`, `FAIL`, `INCONCLUSIVE`, or `STOP`, reason, and links to the first failing event.

The manifest must explicitly contain `claim_state: IMPLEMENTED_UNVALIDATED` only after the hook exists and local tests pass. It remains `ROADMAP` for planning runs and becomes `EXPERIMENTALLY_VALIDATED` only for a retained, reproducible runtime artifact that satisfies the specific scenario—not for G3 performance.

## Completion gate

G0 may be reported as `G0-RUNTIME VALIDATED` only after every required scenario above has a retained passing artifact, exact resolved binaries/sources, and a fresh repository `make check` result. A single successful smoke test, a compatible-looking Python API, or a source audit alone does not meet this gate.
