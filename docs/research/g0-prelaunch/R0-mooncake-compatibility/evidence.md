# R0 evidence

- [Official release](https://github.com/kvcache-ai/Mooncake/releases/tag/v0.3.12.post1): tag, commit and release asset digest.
- [Full commit](https://github.com/kvcache-ai/Mooncake/commit/6041a609a8c3af35e778f70db344f145c2914980).
- [Distribution metadata](https://github.com/kvcache-ai/Mooncake/blob/6041a609a8c3af35e778f70db344f145c2914980/mooncake-wheel/pyproject.toml#L20-L29).
- [Linux-only wheel guard](https://github.com/kvcache-ai/Mooncake/blob/6041a609a8c3af35e778f70db344f145c2914980/mooncake-wheel/setup.py#L5-L12).
- [Pinned adapter import/call boundary](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py#L268-L292).

No runtime command is retained in this prelaunch evidence packet: it contains no target Linux/GPU installation or service artifact. The later first-C0 r6 evidence is separate.
