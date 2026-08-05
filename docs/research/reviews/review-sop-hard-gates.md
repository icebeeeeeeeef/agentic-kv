# SOP hard-gate evidence for P1-P4

Checked 2026-08-05. This note distinguishes an upstream problem from the exact proposed mechanism; an adjacent open issue is not enough to pass the gate.

## P1: libCacheSim KV-cache policy replay

- vLLM's open context-aware retention RFC says ordinary LRU loses agent-session blocks during tool pauses and proposes prioritized, TTL-aware retention. It is direct evidence that retention under agentic workloads remains an open design area, but it does not establish that a stock-policy tournament is the missing solution: <https://github.com/vllm-project/vllm/issues/37003>
- An earlier frequency/cost-aware eviction proposal was closed as not planned and had no assignee, milestone, branch, or PR. This is evidence of a suggestion, not upstream validation: <https://github.com/vllm-project/vllm/issues/23641>
- libCacheSim already supplies FIFO, LRU, Clock, ARC, CLOCK-PRO, Belady, S3-FIFO and trace/MRC tooling. Merely wiring these together leaves little owned algorithmic mechanism: <https://github.com/1a1a11a/libCacheSim>
- LMCache also requested/added multiple backend policies; its prior policy request says FIFO/LRU/LFU already existed and asked for S3FIFO/WA: <https://github.com/LMCache/LMCache/issues/1306>

Conclusion: the *phenomenon* gate has support; the original "compare stock policies by hit rate and write amplification" formulation does not match the unresolved mechanism. It needs a self-built vLLM trace probe, cost/SLO-aware oracle, and one owned retention decision.

## P2: local LRU/TTL plus remote Redis and consistent hashing

- LMCache already documents a remote Redis backend, Redis Sentinel, multi-worker key format, and vLLM connector setup: <https://docs.lmcache.ai/kv_cache/storage_backends/redis.html>
- LMCache documents a native RESP connector and L2 eviction; its storage architecture already spans local and remote tiers: <https://docs.lmcache.ai/kv_cache/storage_backends/resp.html>
- The 2025 Redis optimization RFC said functionality was already complete but heavy load degraded TTFT; it was later closed as not planned, while batching/async work was listed. It does not prove the proposed LRU/TTL/consistent-hash wrapper remains the current missing mechanism: <https://github.com/LMCache/LMCache/issues/1239>
- Dynamo already owns distributed multi-tier KV management and cache/load-aware routing: <https://github.com/ai-dynamo/dynamo/blob/main/docs/design-docs/architecture.md>

Conclusion: the original proposal is largely a parallel implementation/integration of existing capabilities. A current pinned upstream issue tied to a reproducible failure is missing.

## P3: backup request plus slow-node detection

- vLLM Production Stack's open 2026 roadmap lists request migration when a vLLM instance fails as P0: <https://github.com/vllm-project/production-stack/issues/855>
- The router already supports health checks, engine metrics and fault-aware endpoint exclusion: <https://github.com/vllm-project/production-stack/blob/main/src/vllm_router/README.md>
- Envoy already provides request hedging, retry budgets and outlier detection. A generic library therefore has a severe ownership/deletion problem: <https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/http/http_routing.html>, <https://www.envoyproxy.io/docs/envoy/latest/faq/load_balancing/transient_failures>

Conclusion: hard-failure migration is an official open problem, but that is not evidence that generic slow-node hedging is the missing solution. The project would need LLM-specific first-token hedging, loser cancellation, duplicate-compute accounting and KV-affinity semantics.

## P4: FIFO append-only TTL log engine

- LMCache's local-disk backend already creates one file per KV chunk, performs async puts and prefetch, enforces capacity, and supports LRU/LFU/FIFO/MRU: <https://docs.lmcache.ai/kv_cache/storage_backends/local_storage.html>
- Mooncake documents approximate-LRU memory eviction, leases and soft-pin TTL; its DFS file eviction is not provided. This is only an adjacent gap unless the proposal specifically replaces that persistence path: <https://github.com/kvcache-ai/Mooncake/blob/main/docs/source/design/mooncake-store.md>
- LMCache's open Q2 2026 roadmap asks for advanced L2 store/prefetch policies and production readiness, but does not identify append-only logging or file-per-chunk metadata as the bottleneck: <https://github.com/LMCache/LMCache/issues/2923>

Conclusion: ownership could be high, but there is no current official evidence that the exact append-only/FIFO/TTL mechanism solves an unresolved KV-cache storage bottleneck. A source-profiled file-per-chunk bottleneck and upstream acknowledgement are needed first.

## Scope combinations

P1 and P2 can fail independently: replay can complete without middleware, and middleware can function without replay. P3 adds another independent success criterion and a second fleet-level failure domain. The combined proposals therefore fail the one-question/feasibility gate under an 8-10 week part-time budget unless P2 is reduced to a thin online actuator for a single P1 decision and P3 is excluded.
