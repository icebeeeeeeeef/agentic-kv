# R4 evidence

- [First-miss storage query](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/cache_controller.py#L1023-L1045).
- [Adapter physical first-miss lookup](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py#L1240-L1267).
- [Storage-loaded token accounting](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L1632-L1656).
- [Scheduler propagates loaded storage tokens before the next request round](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/scheduler.py#L3164-L3175).
- [Request cache-source accounting records storage-cached tokens](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/schedule_batch.py#L2386-L2416).
- [Output cache breakdown exposes the storage source](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/scheduler_components/output_streamer.py#L70-L100).
- [Finished-request metrics define uncached prompt tokens as prompt minus cached](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/observability/metrics_collector.py#L1693-L1700).
- [Required fixed runtime contract](../../implementation/G0_EXECUTION_PLAN.md#preconditions-and-hard-admission-checks).

This prelaunch evidence packet contains no model hash, launch log, cold-state proof, Put/Get join, output artifact, cache-source response, or no-L3 token control. The later first-C0 r6 artifact is separate and does not make this prelaunch packet runtime evidence.
