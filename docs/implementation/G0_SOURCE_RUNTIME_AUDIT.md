# G0 Source and Runtime Audit

> Audit date: 2026-08-05; restore-value accounting addendum: 2026-08-09
> Historical source-phase verdict: **G0-SOURCE BLOCKED**
> Scope: fixed SGLang source seam and the minimum Mooncake runtime contract. This audit is not a runtime result. A later first-C0 r6 artifact did pass stock restore qualification in one TCP/direct-I/O/L20 topology; it does not alter this audit's source facts or complete G0. Current state: [STATUS.md](../../STATUS.md).

## Verdict and evidence boundary

The SGLang source seam is **SOURCE_VERIFIED** at
[`b058dc910619c9d4bce9e9e24117104ffc491fa6`](https://github.com/sgl-project/sglang/commit/b058dc910619c9d4bce9e9e24117104ffc491fa6).
At this audit's conclusion, the exact Mooncake release candidate was identifiable, but that SGLang commit neither declared a Mooncake package version nor locked a source revision, and no successful adapter/build probe had been retained. Therefore the source audit could not call any Mooncake version *compatible*. The later r6 artifact establishes only its recorded target-Linux stock combination, not a general compatibility claim; it does not invalidate the verified SGLang facts below.

| State | Item |
|---|---|
| SOURCE_VERIFIED | The narrow L2-ack-to-L3 seam, its queue/protection consequences, prefix first-miss behavior, and adapter object expansion described below. |
| SOURCE_VERIFIED | Stock SGLang propagates tokens actually loaded from L3 into per-request storage-cached accounting, can expose that source in response metadata, and defines uncached prompt tokens as prompt minus cached tokens. This is an available G0 oracle, not runtime proof that the target deployment survives. |
| SOURCE_VERIFIED | Mooncake release candidate `v0.3.12.post1`, release commit prefix `6041a60`, released 2026-07-25, and its CPython 3.11 x86_64 wheel SHA-256 `8b73bf8a4f1de741a73f04f32f1e73549c60bfbf7ee73710141ef1f8ea324439`. [Official release](https://github.com/kvcache-ai/Mooncake/releases/tag/v0.3.12.post1) |
| Inference | `v0.3.12.post1` is the best first candidate: it predates the pinned SGLang commit and exposes the APIs the adapter imports/calls. This is not an adapter compatibility proof. |
| SOURCE_VERIFIED | The release tag resolves to `6041a609a8c3af35e778f70db344f145c2914980`; the official CPython 3.11 Linux x86_64 wheel digest is recorded above. [Official commit](https://github.com/kvcache-ai/Mooncake/commit/6041a609a8c3af35e778f70db344f145c2914980) |
| EXPERIMENTALLY_VALIDATED, scoped | first-C0 r6 retained the target-Linux installed/build identities and successful stock SGLang `b058` + Mooncake candidate A→C→fresh-B probe. Fresh C1 must record and re-admit its own `git rev-parse HEAD`, package version, wheel/build hash and probe result. |

## Verified SGLang write path

1. `_inc_hit_count` increments a non-chunked write-through node and calls `write_backup` only once its threshold is reached; it has no L3 action itself. [hiradix_cache.py#L977-L986](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L977-L986)
2. `write_backup` rejects a non-root child whose parent is not L2-backed, asks the controller to DMA device indices to host, stores `node.host_value`, registers the write-through ack, and takes the write-through lock. [hiradix_cache.py#L840-L870](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L840-L870)
3. After the ack event is observed, `_finish_write_through_ack` clears the pending marker, emits the CPU-store event for every published node, then invokes `write_backup_storage`; only afterwards does it release the write-through lock. [hiradix_cache.py#L904-L915](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L904-L915) The caller synchronizes the ack event first. [hiradix_cache.py#L1023-L1058](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L1023-L1058)
4. `write_backup_storage` constructs the complete write inputs, calls `HiCacheController.write_storage`, then records `ongoing_backup[operation_id]` and calls `node.protect_host()`. [hiradix_cache.py#L916-L941](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L916-L941)
5. `HiCacheController.write_storage` is the first L3 state transition: it creates a `StorageOperation` and queues it. [cache_controller.py#L1090-L1104](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/cache_controller.py#L1090-L1104) The backup thread dequeues it, invokes `_page_backup`, then emits the completion ack. [cache_controller.py#L1186-L1225](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/cache_controller.py#L1186-L1225)

### Exact behavior-changing seam

The only acceptable behavior hook is inside `HiRadixCache.write_backup_storage`, **after** `top`, `key`, `hash_value`, `host_value`, and `prefix_keys` have been constructed (lines 919-935) and **before** `cache_controller.write_storage(...)` (line 937). A `DROP` returns from this function at that point.

That ordering is SOURCE_VERIFIED to preserve completed L2 write-through: the CPU event has already been recorded, while no `StorageOperation`, backup-queue entry, `ongoing_backup` entry, or host protection has yet been created. This establishes the required `ALWAYS_DROP` properties in source, but runtime tests must still prove them under asynchronous execution. A policy exception must be caught at this seam and turned into `ADMIT_TO_L3`; that fail-open behavior is a required patch property, not an upstream fact.

## Input construction and granularity

| Question | SOURCE_VERIFIED fact | Consequence |
|---|---|---|
| `keys` | The L3 logical page keys are `hash_value`; they come from the node or a parent-first concatenated split chain. [hiradix_cache.py#L916-L975](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L916-L975) | Record the logical hash list before the controller queue. |
| `host_indices` | The same host-index tensor is called `host_value` in `HiRadixCache`, then passed as `host_indices` into `StorageOperation`. [hiradix_cache.py#L920-L938](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L920-L938), [cache_controller.py#L168-L187](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/cache_controller.py#L168-L187) | The policy sees an L2-resident segment, not newly allocated L3 memory. |
| `prefix_keys` | Optional ancestor hashes come from `top.get_prefix_hash_values(top.parent)` only when `hicache_storage_pass_prefix_keys` is enabled. [hiradix_cache.py#L931-L935](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L931-L935) | The runtime manifest must state this flag; it cannot be assumed present. |
| Callback / completion unit | The decision unit is a TreeNode segment, or a continuous parent-first reconstructed split chain. The controller breaks it into `STORAGE_BATCH_SIZE` logical pages; the adapter can expand one logical MHA page to K/V objects (and further split-head objects). [cache_controller.py#L1186-L1210](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/cache_controller.py#L1186-L1210), [mooncake_store.py#L988-L1028](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py#L988-L1028) | It is neither a single page callback nor one Mooncake-object callback. Trace all three levels. |

### Legal online signals at the seam

SOURCE_VERIFIED availability is limited to the current node/chain data: `node.hit_count`, node and concatenated key length, page-aligned logical hashes, parent/ancestor relationship, L2 host indices, and optional prefix hash list. The precise physical `buffer_sizes` do not exist until the adapter's `_batch_preprocess`; use only a previously calibrated estimate online. Future demand, future Get result, later queue outcome, and later Mooncake availability are not legal policy inputs.

### Restore-value accounting

This accounting is an observation after restore, not a legal admission input:

- after prefetch completes, HiRadixCache records tokens actually loaded from storage as `min_completed_tokens - matched_length`; [hiradix_cache.py#L1644-L1704](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L1644-L1704)
- the scheduler moves that value to the request before the next scheduling round, and request accounting classifies the corresponding cached prefix as storage-sourced; [scheduler.py#L3164-L3175](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/scheduler.py#L3164-L3175), [schedule_batch.py#L2386-L2416](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/schedule_batch.py#L2386-L2416)
- the output path can expose the storage breakdown as `cached_tokens_details.storage`, while finished-request metrics define uncached prompt tokens as `prompt_tokens - cached_tokens`. [output_streamer.py#L70-L100](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/scheduler_components/output_streamer.py#L70-L100), [metrics_collector.py#L1693-L1700](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/observability/metrics_collector.py#L1693-L1700)

Therefore G0 can distinguish a functionally correct restore path from non-zero prefill substitution without a new observation patch. It still needs a real B-cold L3 run and an identical B-cold no-L3 control; source availability alone is not `REMOTE_VALUE_SURVIVES`, and TTFT alone cannot replace this token-level oracle.

## Prefix closure and first miss

Two distinct source facts matter:

- Write-through L2 itself skips a child until the parent is L2-backed, enforcing an L2 root-contiguous backup prefix. [hiradix_cache.py#L840-L847](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L840-L847)
- Remote lookup queries pages in order and breaks at the first batch that is not fully present. [cache_controller.py#L1023-L1045](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/cache_controller.py#L1023-L1045) The Mooncake adapter applies the backend/model key prefix and returns the number of continuous fully present logical pages, stopping on the first missing physical component. [mooncake_store.py#L1240-L1267](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py#L1240-L1267)

**Inference, to be tested:** the source proves first-miss lookup but does not provide an L3 admission policy or a proof that a new policy never creates a hole. Per the accepted [D9 decision](../project/DECISIONS.md#d9--g0-的-prefix-group-一律-all-or-none), G0 takes the smaller option: a root-anchored continuous group is all-or-none. It does not implement a first-DROP suffix rule.

## Async cleanup facts

On a backup acknowledgement, the scheduler removes the `ongoing_backup` entry and releases the node's host protection. [hiradix_cache.py#L660-L669](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L660-L669) Detach/shutdown has a separate force-release pass for left-over backup entries. [hiradix_cache.py#L516-L573](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L516-L573)

This supports a strict runtime oracle: `DROP` creates none of these states; each admitted completed/failed/shutdown operation eventually leaves no queue entry, `ongoing_backup` entry, or host protection. It does **not** prove that every backend partial/failure situation is represented separately: `_page_backup` currently breaks on a failed controller batch and the comment explicitly says partial success is not yet implemented. [cache_controller.py#L1194-L1202](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/cache_controller.py#L1194-L1202)

**Owned-boundary decision (not an upstream absence claim):** G0 adds its decision before `StorageOperation` exists, so a DROP owns no async state. It will test upstream success/dedup/fail-open/shutdown-detach cleanup, but it will not add request-cancellation, epoch, or a second stale-completion owner. A late ack, leak, or residual protection observed after detach is a G0 failure, not a reason to hide the issue behind a new state machine. See [D10](../project/DECISIONS.md#d10--failureasync-合同保持严格不伪造覆盖).

## Mooncake adapter and observation seam

`MooncakeStore.batch_set_v1` tags logical keys, expands logical pages into physical object keys/pointers/sizes, executes `batch_is_exist`, filters existing objects, then calls `batch_put_from`; its returned status is reduced to one bool per logical page. [mooncake_store.py#L1059-L1115](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py#L1059-L1115), [mooncake_store.py#L1277-L1316](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py#L1277-L1316)

### Race-observation limitation

**SOURCE_VERIFIED:** on Mooncake `6041a609a8c3af35e778f70db344f145c2914980`, a
`PutStart` `OBJECT_ALREADY_EXISTS` is converted to success, and the batch collector does
the same. [client_service.cpp#L1531-L1565](https://github.com/kvcache-ai/Mooncake/blob/6041a609a8c3af35e778f70db344f145c2914980/mooncake-store/src/client_service.cpp#L1531-L1565), [client_service.cpp#L2427-L2459](https://github.com/kvcache-ai/Mooncake/blob/6041a609a8c3af35e778f70db344f145c2914980/mooncake-store/src/client_service.cpp#L2427-L2459) The Python batch method returns `0` for a successful expected value. [real_client.cpp#L3756-L3783](https://github.com/kvcache-ai/Mooncake/blob/6041a609a8c3af35e778f70db344f145c2914980/mooncake-store/src/real_client.cpp#L3756-L3783)

Therefore `exists=missing → put_result=0` is not injective: it can denote this writer's
new Put or a competing writer's already-existing object. The adapter's per-object trace
can distinguish an **exists-skip** (precheck=1) and a negative failure, but cannot recover
that race cause after the Mooncake boundary. Under the current observation contract this is
`R2 state classification = FAIL` and `R2/R3 new-payload attribution = STOP`; do not call
the sum of `put_result=0` `buffer_sizes` `completed_new_put_bytes`. The project owner has
accepted [D1](../project/DECISIONS.md#d1--保留-new-put-payload-指标并授权最小观察-patch): an independent,
pre-collapse Mooncake trace-only observation boundary is defined, but not yet implemented or
validated. Until its non-interference proof exists, the STOP remains. This does not invalidate
restore or the Shared-L3 Publication Admission seam. D1 defines the observation boundary; [D12](../project/DECISIONS.md)
now separately gates only a narrow payload exception. The active pre-D1 survival ruling is [D14](../project/DECISIONS.md#d14--shared-l3-publication-admission-收敛与替代攻击), whose S1–S3 contract must not be inferred from this source audit.

The minimum **trace-only** propagation is:

```text
decision_id + run_id
  -> StorageOperation.operation_id
  -> operation_id + batch ordinal = attempt_id
  -> adapter logical keys + physical keys + buffer_sizes + exist/put result
```

`StorageOperation` currently has no trace fields, and the controller has no batch ID. Adding opaque fields (or a side correlation map keyed by `operation.id` plus per-operation batch ordinal) is an implementation requirement, not a source fact. The field must never participate in key construction, queue ordering, retry, dedup, Get, or admission. The instrumentation patch must precede and be independently tested from the behavior-hook patch.

## Minimum integration layout

**Selected:** external pinned SGLang and Mooncake checkouts, with each small ordered patch
series exported into this repository's [patch provenance directory](../../patches/README.md).
The repository does not vendor either upstream: it owns the manifest, `git format-patch`
artifacts once materialized, workload, collector, tests, and evidence. The currently declared
series are `PLANNED`; no patch may be described as existing or applicable until its entry carries
the exported files, hashes, focused-test result, and fresh-worktree apply verification.

| Choice | Decision | Reason |
|---|---|---|
| Vendor full SGLang/Mooncake | Rejected | Duplicates upstream and makes provenance/upgrades harder without improving the single hook. |
| Git submodules now | Rejected | A submodule records a revision but does not establish build/API compatibility; it adds repository coupling before the G0 probe. |
| One generic policy plugin framework | Rejected | The only current need is one fail-open binary seam and two forced actions. |
| Combined policy + trace patch | Rejected | It cannot distinguish behavior regression from observability regression. |
| External checkout + repository-held trace patch, then hook patch | Selected | Preserves upstream ownership and provides a reversible, reviewable proof surface. |

## Runtime configuration facts

The pinned SGLang README documents a source build, external master/metadata/store roles, `tcp` as a supported protocol, an external store's non-zero `global_segment_size`, and SGLang workers using `global_segment_size=0` when an external store exists. [README#L34-L78](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/README.md#L34-L78), [README#L116-L183](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/README.md#L116-L183), [README#L249-L253](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/README.md#L249-L253). The pinned registered test also configures `MOONCAKE_PROTOCOL=tcp`, blank device, metadata URL, and a global segment. [test_hicache_storage_mooncake_backend.py#L195-L211](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/test/registered/hicache/test_hicache_storage_mooncake_backend.py#L195-L211)

This source evidence supports the external non-zero segment configuration shape, but it does not prove that two arbitrary roomy/small values take effect in the unresolved target build or that capacity can be changed in place. D14 S3 `CAPACITY_EXTERNALITY` must therefore start a fresh Store for each value and retain that Store's runtime health/segment response; otherwise its capacity axis is `INCONCLUSIVE`.

This source audit contains no runtime deployment, hook, trace field, candidate policy, payload reconciliation or performance result. The separate first-C0 r6 artifact establishes only stock restore qualification; neither document may be upgraded to `G0-RUNTIME VALIDATED`.
