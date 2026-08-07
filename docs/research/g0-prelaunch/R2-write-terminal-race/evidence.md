# R2 evidence

- [Adapter exists filter and reduction](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py#L999-L1115).
- [Mooncake result contracts](https://github.com/kvcache-ai/Mooncake/blob/6041a609a8c3af35e778f70db344f145c2914980/mooncake-store/include/real_client.h#L153-L244).
- [Duplicate-to-success mapping](https://github.com/kvcache-ai/Mooncake/blob/6041a609a8c3af35e778f70db344f145c2914980/mooncake-store/src/client_service.cpp#L1531-L1565) and [batch reduction](https://github.com/kvcache-ai/Mooncake/blob/6041a609a8c3af35e778f70db344f145c2914980/mooncake-store/src/client_service.cpp#L2427-L2459).
- [Controller partial batch limitation](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/cache_controller.py#L1194-L1202).
- [Ack cleanup](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py#L660-L669).

No sequential dedup, overlap, failure or drain artifact exists; this does not weaken the source-level classification failure above.
