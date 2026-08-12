# 上游重叠与可行性审查（截至 2026-08-05）

> **HISTORICAL / NON-AUTHORITY（pre-D14）。** 本文保留 2026-08-05 的早期 source scan 和候选讨论，不能定义当前 Gate、workload、candidate 或 claim。当前唯一 canonical contract 是 [D14](../../project/DECISIONS.md#d14--shared-l3-publication-admission-收敛与替代攻击) 及 [PROJECT_PLAN.md](../../project/PROJECT_PLAN.md)。
>
> 文中从 mutable `main`、外部 issue/PR、benchmark 或讨论得到的阈值、绑定语义和性能说法一律只是 `RESEARCH_REVIEW / SOURCE_TO_REVERIFY`，不是 `SOURCE_VERIFIED` 或实验结论。

## 结论

- 四个原始题目均不宜原样作为 8–10 周旗舰项目：P1 的评价口径不成立，P2/P4 与成熟上游高度重复，P3 的尾延迟机制是老问题且不够贴 KV storage。
- 如果目标岗位明确是 KV storage 组，唯一值得继续做 Gate-0 的方向是：在 **SGLang HiCache 现有数据路径中解耦 L2 与 L3 写入准入**，实现一个可删除、可反证的 L3 admission 机制；不是另造存储引擎，也不是泛泛实现 selective write。
- 若只追求 8–10 周内更容易测出因果，vLLM agent-aware retention 更简单；但它已有进行中的 RFC/working implementation，而且更像调度/缓存策略，项目所有权和 KV storage 岗位信号都弱于 HiCache L3 admission。

## 源码级缺口：SGLang HiCache L2/L3 admission 耦合

当前 `HiRadixCache` 对 `write_through` 使用阈值 1，对 `write_through_selective` 使用阈值 2；命中数达到阈值才调用 `write_backup`，即准入到 host/L2。DMA ack 完成后，只要启用了 storage，就直接调用 `write_backup_storage`，没有独立的 L3 决策。因此，L3 继承 L2 的同一准入结果，尽管 L2 与 L3 的容量、写队列、写成本、读回成本和跨实例复用价值不同。

- 源码：[`write_through_threshold` 与 `_inc_hit_count`](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/hiradix_cache.py)
- 源码：[`_finish_write_through_ack` 无条件触发 `write_backup_storage`](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/hiradix_cache.py)
- 官方文档已经把 `write_through_selective` 定义为命中计数阈值策略，所以不能把“selective write”本身声称为新贡献：[HiCache 设计文档](https://sgl-project.github.io/advanced_features/hicache_design.html)
- 官方高优先级 roadmap 明确指出 agentic workload 下 storage/transfer bottleneck，并列出 direct L3、agent-aware scheduling、storage prefetch、storage group visibility/eviction 等工作：[SGLang #21846](https://github.com/sgl-project/sglang/issues/21846)

这是当时的“源码级候选缺口”假设，仍不足以证明“官方确认缺口”。当前必须按 D14 对 pinned source/runtime 复核，而不能用本文或当时的 issue/maintainer response 代替。

## 历史建议的最小机制（已冻结，不授权实现）

下列内容只记录早期候选如何形成；它不是批准的 `L3AdmissionPolicy`，也不授权 second-hit sketch、动态成本估计或任何 policy 实现。D14 已冻结 Agent hint、`VALUE_DENSITY`、page-level admission、router 与 eviction，直到在线 residual 和新的 owner decision 出现。

早期文字曾设想：L2 backup 完成后，基于**连续前缀组**的第二次复用证据和实测成本决定是否 enqueue L3 write：

`admit iff predicted_saved_prefill_time > measured_L3_write_cost + predicted_L3_read_cost`

实现最多包含：小型 ghost/second-hit sketch、动态的 L3 写/读成本估计、组级准入与可观测 reason code。不得同时造新 L3 后端、路由器或通用策略框架。

硬验收不是 hit rate，而是固定 workload 下的 TTFT/Goodput@SLO、L3 bytes written、写队列等待、读回命中后节省的 prefill tokens，以及 recompute-vs-load 的反例边界。

## 最强反例

单 GPU、本地 SSD/L3 的实验里，L2 可能已经装下热点且 L3 写队列无压力，独立 admission 几乎不触发；对短前缀，L3 read 还可能比 recompute 慢，使“命中率更高”反而恶化 TTFT。如果无法构造并复现这些 losing conditions，该项目的收益主张不成立。另一个项目风险是上游 roadmap 正在活跃推进，未获 maintainer 对问题边界的认可就可能做成重复实现。

## 四题裁决简表

| 题目 | 上游/事实判断 | 最大工程失败点 | 裁决 |
|---|---|---|---|
| P1 libCacheSim/CacheLib replay | libCacheSim 支持 FIFO/LRU/ARC/S3-FIFO/SIEVE 等，但没有 `CLOCK-FIFO`；S3-FIFO 本身已有 ghost queue，`FIFO+Ghost` 不是独立第六算法。CacheLib 的公开 `kvcache` 是通用 KV 服务 trace，不是 LLM KV。 | 普通对象 hit rate 没有连续 prefix、refcount/pin、transfer/recompute cost、scheduler feedback，无法推导 TTFT/Goodput。 | 仅作 1–2 周筛选实验；必须换 Mooncake agent/tool trace 或真实 block-event probe，并用 longest-contiguous-prefix oracle。 |
| P2 vLLM + Redis | LMCache 已有 vLLM connector、Redis/Valkey RESP L2、async store/prefetch、序列化、容量与 eviction；Redis Cluster 已有 slot/hash-tag/MOVED/ASK。 | 真问题是 GPU→CPU→serde→TCP 的生命周期、背压、取消、布局兼容与故障，而不是 consistent hashing。 | 停止；原样是较弱的 LMCache 重做。 |
| P3 backup request + slow node | Tail hedging 是 2013 年以前的成熟思想；vLLM Router 已有 health/retry/circuit breaker，production-stack 也有 request migration/failover。 | streaming 首 token 后不能安全切换；副本采样可能分叉；取消滞后造成重复 prefill、GPU 负载和 cache pollution；“慢节点”与长请求/冷 miss/批处理难区分。 | 只可保留首 token 前、spare-capacity gated hedge 的窄实验；不适合作为 KV storage 旗舰。 |
| P4 FIFO TTL append log | Mooncake 已有 offset allocator 单文件、bucket 顺序大块写、FIFO 驱逐、CRC、checkpoint/tombstone recovery、reader extent pinning；LMCache Raw Block 与 CacheLib Navy 也覆盖相邻机制。 | TTL/delete 会制造垃圾；不 compact 会填满，compact 会引入写放大、尾延迟、crash consistency 与 reader/GC 竞争。 | 不另造引擎。若上游确认，可做 Mooncake OffsetAllocator 的可恢复 LRU；TTL 暂无官方优先级证据。 |

## 主要一手来源

- [libCacheSim](https://github.com/1a1a11a/libCacheSim)、[S3-FIFO](https://s3fifo.com/)、[CacheLib eviction](https://cachelib.org/docs/Cache_Library_User_Guides/eviction_policy/)
- [Mooncake FAST25 traces](https://github.com/kvcache-ai/Mooncake/tree/main/FAST25-release)、[KVCache.ai prefix simulator](https://github.com/kvcache-ai/kvcache-blog/tree/main/packages/kvcache-simulator)
- [LMCache Redis backend](https://docs.lmcache.ai/kv_cache/storage_backends/redis.html)、[LMCache MP RESP](https://docs.lmcache.ai/mp/l2_storage/resp.html)、[LMCache MP L2](https://docs.lmcache.ai/mp/l2_storage.html)
- [vLLM agent-aware retention RFC #37003](https://github.com/vllm-project/vllm/issues/37003)、[vLLM Router](https://github.com/vllm-project/router)、[Tail at Scale](https://research.google/pubs/the-tail-at-scale/)
- [Mooncake OffsetAllocator source](https://github.com/kvcache-ai/Mooncake/blob/a6b4db4cfa371a3fc7f189a19977c102e14c4dfc/mooncake-store/src/storage_backend.cpp#L4766-L5064)、[CacheLib Navy BlockCache](https://cachelib.org/docs/Cache_Library_Architecture_Guide/navy_overview/#block-cache)、[LMCache Raw Block](https://docs.lmcache.ai/mp/l2_storage/raw_block.html)
