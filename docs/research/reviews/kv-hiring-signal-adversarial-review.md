# KV cache storage/serving 校招项目对抗式裁决

> **历史评审归档（pre-D14 / NON-AUTHORITY）：**本文讨论的是早期 local retention/eviction、offload、FP8 与 vLLM 路线。它只保留反例、岗位信号和收窄理由；当前唯一机制、范围、Gate 与 STOP 以 [PROJECT_PLAN.md](../../project/PROJECT_PLAN.md)、D14 和 [STATUS.md](../../../STATUS.md) 为准，不得据此恢复旧实现方向。

> 视角：国内 AI Infra 推理团队中 KV cache storage/serving subgroup 的 TL / 技术面试官  
> 候选人：大三、2027 校招；8–10 周；1 张 GPU，可租 3–5 台普通机器  
> 证据截点：2026-08-05。上游事实基于当日官方文档/仓库；实施前仍需固定 commit。

## 1. 唯一裁决

**`RESHAPE P1 -> conditional SELECT`。** 不是选择原始“离线 admission/eviction simulator”，而是收窄为：

> **vLLM Agentic KV Retention Profiler & Calibrated Replay**：自建真实 vLLM block-lifecycle probe，把 agent/tool-pause workload 变成 byte-accurate trace；复用 libCacheSim 的库存策略作为 baseline，只自写一个使用线上可见 `session/range/TTL` 信息的 retention policy；最后通过最小 vLLM 在线 actuator、删除测试和 held-out workload 验证 replay 能否预测 TTFT/Goodput 边界。

核心问题只有一个：

> 在固定 KV 字节容量下，agent session 因 tool call 暂停而失去 refcount 后，session/range-aware bounded retention 相比 tuned LRU、固定 TTL 和 S3-FIFO，何时能减少 useful-prefix eviction 与 recompute，并改善 Goodput@SLO；何时因误保留、并发挤压和 policy overhead 反而更差？

P2、P3、P4 都不进入主线。P2 不是 P1 的“在线系统层”；真正需要的在线闭环只是 vLLM block-level retention actuator。P4 是 ownership 最强的挑战者，但当前没有已核实的 LMCache file/raw-block 结构性瓶颈，不能在 8–10 周预算内把“可能有问题”当成已经过门。

## 2. 为什么结论不是“P1 便宜，所以性价比高”

招聘项目的近似目标函数是：

```text
单位时间招聘信号
≈ 职责同构度 × owned hard part × 因果证据 × 可信度 / 周数
```

低成本只降低分母。原始 P1 若只做 `(timestamp, key, size) -> LRU/LFU hit rate`，也删掉了线上 block state、调度/排队、recompute 成本、TTFT 与生命周期不变量，分子下降得更快，所以原始 P1 **不合格**。

阿里云 Tair KVCache 团队的官方 HiSim 证明“trace + 仿真 + 配置裁决”是实际团队工作，但它公开的门槛不是“写一个 cache simulator”：它建模完整请求生命周期、调度、KV load/evict 和多级存储，并自报相对真实硬件误差 `<5%`。[Tair HiSim 官方博客](https://www.alibabacloud.com/blog/603164) 其低成本价值来自已校准的高保真模型，不来自逃避真实系统。

P1* 被选中，是因为它同时具备：

1. **官方问题证据**：vLLM 2026-03 的开放 RFC 明确指出 agent/tool-pause 下 LRU 看不到 session/reuse 结构，并提出 token-range priority + duration/TTL actuator；状态仍是开放 RFC，且作者声明已有 working implementation、系统 benchmark 仍在进行。[vLLM Context-Aware Retention RFC #37003](https://github.com/vllm-project/vllm/issues/37003)
2. **预算内裁决权**：1 张 GPU 可通过固定 3B–7B 模型并限制 KV blocks 制造真实压力；不依赖多 GPU、RDMA 或分布式存储。
3. **可拥有的工程难点**：vLLM block event probe、trace schema、replay-to-online calibration、一个 policy consumer、正确性/开销测试和失败边界，而不是重写算法库。
4. **明确停止条件**：若 useful-eviction opportunity mass 太小、replay 无法预测在线 ordering，或 strongest static baseline 已吃掉大部分 oracle headroom，就能在两周内停止。

换言之，低成本只被用于便宜地证明“值不值得继续”；它不是招聘价值本身。

## 3. 官方/一手证据如何防一句话否决

### 3.1 P1 的问题是真问题，但“自己写 simulator”不是贡献

vLLM RFC #37003 的官方 issue 明确描述：agent session 在 tool call 期间 block 无引用，竞争负载下会被 LRU 淘汰；提议让 orchestrator 通过 token range、priority、duration 与 scope 表达 retention intent。它还明确区分 request scheduling priority 与 block eviction priority，并把具体策略留给 API consumer。

这可以防“agent pause 与 LRU 失配是你臆想的”这一句，但也抬高了 baseline：候选人不能声称首次发现或首次实现 retention priority。

同时，[libCacheSim 官方仓库](https://github.com/1a1a11a/libCacheSim) 已有 FIFO、LRU、Clock、ARC、Belady、GDSF、WTinyLFU、S3-FIFO、Sieve，多种 admission/prefetch 算法，并直接支持 trace analysis、multi-layer cache 和 consistent-hash cluster。候选人重写这些，只会降低 ownership 可信度。P1* 应复用它们，自有代码必须落在 KV-specific probe、cost/lifecycle model、online policy 与 calibration。

### 3.2 P2 的大部分能力已经存在

LMCache 当前官方架构已经覆盖 GPU、CPU、local disk 与 remote backend；已有 token/chunk 索引、GPU/CPU 搬移、默认 LRU、异步 offload/prefetch，并直接列出 Redis、Mooncake 等 remote connector。[LMCache Architecture](https://docs.lmcache.ai/developer_guide/architecture.html)

LMCache 还已有原生 C++ Redis/Valkey RESP backend，包含多线程 I/O、batch tiling、eventfd completion 和 MP/non-MP 接入。[LMCache RESP Backend](https://docs.lmcache.ai/kv_cache/storage_backends/resp.html) 官方把 Redis connector 当新增 native backend 的参考实现。[Adding Native Backends](https://docs.lmcache.ai/developer_guide/extending_lmcache/native_connectors.html)

旧 Redis 优化 RFC 确曾记录 heavy-load TTFT degradation，但已经 `closed as not planned`；而现有 native RESP 又覆盖了当时提出的多线程/批处理方向。[LMCache RFC #1239](https://github.com/LMCache/LMCache/issues/1239) 所以“local LRU+TTL+Redis+consistent hash”不能自动升级为 KV storage ownership。

### 3.3 P3 既偏职责层，也超出硬件条件

NVIDIA Dynamo 官方文档把 load-only routing 与 KV-overlap routing 分开；KV-aware routing依据 worker cache events 与 active load。其本地两个 worker 示例明确需要 2 张 GPU。[Dynamo KV-aware Routing](https://docs.nvidia.com/dynamo/dev/cli/model-deployment/kv-aware-routing) [Dynamo Router](https://docs.nvidia.com/dynamo/components/router)

只有 1 张 GPU 时，用 `sleep` 或 mock worker 制造慢节点，可以验证 hedging 状态机，却无法同时验证重复 prefill、GPU 排队、KV locality 破坏和 Goodput 损失。它更像 gateway/serving reliability 项目，不是 KV storage 主项目。

### 3.4 P4 有强 ownership，但当前缺问题证据

LMCache 当前 L2 已有 `fs`、`fs_native`、`raw_block`、`nixl_store(_dynamic)`、S3、Mooncake 等 adapter；已有 async StoreController/PrefetchController、O_DIRECT、固定槽 raw device、persist/recover 和 eviction 配置。[LMCache L2 Storage](https://docs.lmcache.ai/mp/l2_storage.html)

Mooncake 与 FlexKV 的官方架构还表明，真实 KV store 需要处理 immutable object/block identity、index、allocation、async transfer、lease/pin/incomplete write、eviction safety、metrics 等，而非只有 append log。[Mooncake Store Design](https://github.com/kvcache-ai/Mooncake/blob/main/docs/source/design/mooncake-store.md) [FlexKV 官方仓库](https://github.com/taco-project/FlexKV)

因此 P4 不能凭“FIFO+TTL 与 KV 很搭”开工。它需要先在现有 `fs_native/raw_block` 上复现 file-per-object metadata、fixed-slot fragmentation、GC/recovery 或 read-tail 的结构性瓶颈，并获得 upstream issue/maintainer 讨论或可复现实机证据。当前这道门未过。

## 4. 候选逐项裁决

总分采用固定 100 分 rubric：角色价值 15、ownership 15、机制深度 20、证据严谨 25、工程完整 10、trade-off 10、表达 5。分数是假设“按原描述完整交付”的潜力上限；hard gate 失败会覆盖总分。

| 候选 | 简历筛选信号 | 技术面深挖空间 | 与 KV storage/serving 同构度 | 最容易被一句话否决 | 规划分 / hard gate | 裁决 |
|---|---|---|---|---|---:|---|
| P1 原案：离线 admission/eviction simulator | 关键词直接；但“simulator”会触发真实性复核 | 校准、counterfactual、oracle、queueing 可深挖；只有 hit rate 时很浅 | 对容量规划/策略中高，对在线 data path 低 | “结论只在你自己的模型里成立；和真实 vLLM 的误差是多少？” | **69**；online ownership、calibration 失败 | `reshape` |
| P2 local LRU+TTL+Redis+consistent hash | 第一眼词多，源码复核后快速降级 | 可聊 sharding/hot key/TTL，但多为通用 cache | 中低；没有 token/block/lifecycle 语义 | “LMCache 已有原生 Redis 与多级缓存，你拥有的 KV-specific 难点是什么？” | **59**；真实 gap、ownership 失败 | `reject` |
| P3 Backup Request+慢节点 | 能命中 SLA/重试/负载均衡 | hedging threshold、cancel、duplicate cost 可聊 | 对 gateway 中等，对 KV storage 低 | “单 GPU 的 sleep 慢节点实验证明的是网关重试，不是 KV cache。” | **52**；target、feasibility 失败 | `reject` |
| P4 FIFO TTL log engine | storage 代码 ownership 强 | append/index/reclaim/crash/I/O 可深挖 | 独立 toy 中等；做成真实 L2 才高 | “LMCache 已有 fs/raw-block/NIXL；你的 log 解决了哪个已复现瓶颈？” | **74**；real problem 失败 | `defer`，不是首选 |
| P1+P2（原描述） | 表面像闭环，实则故事过宽 | 双层 eviction、hash skew、离线偏差可聊 | 只有同一 block decision seam 才高；当前中低 | “simulator 的 action 改变了哪个 vLLM block，并让哪个请求跳过 prefill？” | **64**；单一因果链失败 | `reject as specified` |
| P1+P2+P3 | 关键词最多，筛选叙事最混乱 | 每块都能聊一点，无法追到底 | 被 P3 稀释，三个成功条件独立 | “这是三个项目；删除哪一个 patch 能解释主结果？” | **56**；scope、falsifiability、feasibility 失败 | `reject` |
| **P1\***：probe + calibrated replay + one online retention policy | 固定 vLLM、KV lifecycle、agent workload、benchmark/patch，信号集中 | block path、模型误差、policy、SLO、负例可连续追问 | **高**：落在 KV lifecycle/control plane 与 engine seam | “是否只是拿 libCacheSim 跑自造 trace？”——由自建 probe、在线校准、删除测试回答 | **86 projected**；两周 survival gate 后 select | **唯一首选** |

## 5. 为什么“离线算法插入在线中间件 = 完整闭环”是错的

闭环不是架构图上多一个箭头。至少要同时满足：

1. **同一观测单位**：离线 trace 与线上 actuator 都以同一 token/block identity 和真实 bytes 表达，而不是 request key 对 Redis key 的近似映射。
2. **同一决策时点**：线上策略只用当时可见信息；不能偷用 trace 的 future reuse、下一次到达或未来 session 长度。
3. **真实 actuator**：决策确实改变 vLLM block eviction/retention；“写进 Redis”本身不保证 engine 跳过 prefill。
4. **生命周期正确**：不能破坏 refcount、in-flight、scope downgrade/clear、TTL expiry 与 block reuse；异常必须回到原生 LRU/安全 miss。
5. **同一结果指标**：不能以 hit rate 代替 TTFT/Goodput；必须守住 queue dwell、GPU 利用率、recompute、policy CPU/heap overhead。
6. **因果验证**：强 baseline、同 trace A/B、删除 patch、信号 ablation、负 workload、replay-to-online calibration 都要成立。

P1+P2 当前描述至少有四个断点：

- request/key 级 simulator 与 vLLM token/block residency 不同构；
- local LRU、Redis TTL 与 engine 自身 eviction 会形成双重、互相不可见的策略；
- consistent hash 解决对象归属，不解决 partial-prefix reuse 与 restore 比 recompute 是否划算；
- remote hit 可能被序列化、网络、H2D 和排队抵消，hit-rate 上升仍可能让 p99 TTFT/Goodput 变差。

P1* 的在线闭环不需要 P2：使用 vLLM RFC 所描述的 block-level priority/duration seam或等价最小 patch，直接把 replay 的同一 decision 映射到真实 block eviction，然后校准预测误差即可。

## 6. P1* 最小可信实现

### 6.1 owned artifacts

候选人必须拥有：

- vLLM 固定 commit 上的 source probe：block hash/id、真实 bytes、token range、session/scope、allocate/free/hit/evict、request arrival/queue/TTFT、recompute tokens/time；
- byte-accurate KV trace schema 和 deterministic replay；
- replay calibration：forced baseline/forced policy 与在线结果逐 cell 对齐；
- 一个仅使用线上可见 session/range/TTL 信息的 retention policy；
- vLLM 最小 actuator/consumer、回退路径、单元/集成测试；
- benchmark matrix、raw logs、plots、negative cases、删除测试。

候选人不拥有：libCacheSim 的 LRU/ARC/S3-FIFO/Belady，vLLM 的 block manager 基线，GPU attention/prefill 实现。不得把依赖能力写成个人实现。

### 6.2 causal chain

```text
agent tool pause / multi-session interleave
  -> useful prefix blocks become unreferenced
  -> stock LRU cannot see session/range intent
  -> useful block eviction + later full-prefix recompute
  -> session/range-aware bounded retention
  -> fewer saved-prefill-ms lost
  -> p95 TTFT / Goodput@SLO changes
```

### 6.3 baseline ladder

1. vLLM stock LRU；
2. fixed TTL / uniform priority（不利用 range/session structure）；
3. S3-FIFO 与 ARC（offline baseline，固定真实 bytes）；
4. strongest static threshold selected only on train trace；
5. Belady/next-use + cost oracle（upper bound，绝不能在线使用）；
6. candidate policy；
7. candidate policy 删除/信号 ablation。

若 pinned vLLM 已合入 RFC 的工作实现，把它放进 baseline；不能假装上游没有。

### 6.4 metrics

- 主指标：Goodput@SLO 或 p95 TTFT，预注册一个 headline；
- KV：prefix hit tokens、useful eviction count、recompute tokens、saved-prefill-ms、KV byte occupancy；
- tail：p95/p99 TTFT、queue dwell、session completion latency；
- guardrail：TPOT/ITL、throughput、GPU utilization、policy CPU/heap ops、metadata bytes；
- calibration：replay 对在线 hit/recompute/TTFT 的误差、各 policy ordering 一致率；
- fairness：固定 model/dtype/KV bytes/trace/arrival/warmup/seed/repetitions/commit/GPU。

不要使用“写放大”描述 GPU KV eviction，除非确实接入了 offload/write path；原始 P1 没有写路径。

## 7. 两周 survival gate 与数字化停止条件

阈值是建议预注册值，不是当前结果。

### Day 1–3：Fermi / opportunity gate

- 固定一个 vLLM commit、一个 3B–7B full-attention 模型、一张 GPU；通过 `gpu_memory_utilization`/KV block 上限制造可控压力；
- 至少一个公开 agent/tool-use trace + 一组 adversarial synthetic workload；
- 在现实压力范围内，stock LRU 必须真实淘汰后续会复用的 block；
- useful-eviction opportunity 对总 prefill/recompute 的质量必须足以影响 headline。若低于实验噪声或仅在极端单点出现，STOP。

### Day 4–7：observability / calibration gate

- 能从同一 request/block 对齐 allocate、free、evict、hit、recompute 和 TTFT；
- forced LRU 的 replay 与在线结果，在 hit/recompute 口径上的误差建议不超过 10%，TTFT 预测误差建议不超过 15%，或至少在 80% 以上 matrix cells 保持 policy ordering；
- 若两轮排障后仍无法区分 engine scheduling/queueing 与 cache policy 影响，STOP。

### Day 8–10：headroom gate

- train trace 上选参，held-out trace 才作结论；
- candidate 相对 strongest static baseline 的 held-out 改善需大于 `max(5%, 2× run-to-run noise)`，并在至少两个相邻压力 cell 同方向；
- candidate 应吃到可观 oracle headroom，而不是只赢人为弱 LRU；
- 若 tuned fixed TTL/S3-FIFO 已覆盖绝大多数可获收益、收益仅在违反 SLO 后出现、或 policy overhead 抵消收益，STOP。

## 8. 预期输掉的 workload

必须主动展示：

- 低并发/容量充足，无 useful eviction；
- session pause 明显长于 TTL，保留只制造污染；
- session 元数据错误或 session 已结束，stale priority 挤压活跃请求；
- one-shot prefix/低复用，S3-FIFO 或 LRU 更简单且不差；
- 高 churn、多 tenant 竞争，过度 soft-pin 导致其他 session p99 变差；
- shared prefix 与 unique tail 的 range signal 不准；
- policy heap/metadata 开销在短上下文、高 QPS 下抵消收益。

## 9. JD 责任动词：哪些能诚实命中

当前 JD 样本的职责簇包括：推理引擎设计研发、性能评估与调优、瓶颈定位和优化验证、Cache 池化/传输、CPU/SSD/远端 KV offload/reuse、主存预取、异步推理/资源调度、KV 资源治理和成本 ROI。P1* 强命中的是 **性能建模/评估、瓶颈定位、框架源码修改、KV 生命周期/淘汰、SLO 验证**；对 RDMA、SSD backend、分布式池只算相邻，不得宣称命中。

| 方案 | 可用责任动词 | 不得越级的动词 |
|---|---|---|
| P1 原案 | `构建` trace/replay；`评估/比较` 策略；有误差验证后才可 `预测` | `上线`、`实现 KV 存储系统`、`降低线上成本` |
| **P1\*** | `埋点/定位` KV eviction；`构建/校准` replay；`实现` bounded retention policy；`验证` TTFT/Goodput 边界；`分析` 失效条件 | 未做就不能写 `分布式 KV pool`、`Redis/SSD/RDMA 数据面`、`生产级`、`大规模` |
| P2 | 真写 connector 才可 `实现/集成/压测` Redis backend；只部署现成 LMCache 应写 `复现/配置` | `研发多级 KV cache`、`设计 KV 生命周期` |
| P3 | `实现` hedged request/故障注入；`识别/隔离` 慢节点；`评估` tail/cost | `优化 KV cache`、`实现分布式 KV 容错`、`提升生产可用性` |
| P4 | 有真实 connector 才可 `设计/实现` L2 backend、`定位/优化` I/O、`实现` reclaim/recovery | 未做就不能写 `分布式`、`RDMA/GDS`、`多副本/HA`、`生产级` |
| P1+P2 / +P3 | 只能分别使用已证实的动词 | 组合不会自动获得 `端到端闭环`、`全链路优化`、`平台化` |

## 10. 技术面必须能守住的问题

1. vLLM 哪个 block 生命周期事件证明 LRU 淘汰了“以后会复用”的 block？给出事件时间线。
2. 哪些字段在线可见，哪些只允许 oracle 使用？如何防 future leakage？
3. 为什么不用固定 TTL、S3-FIFO、ARC；strongest static baseline 怎么调？
4. replay 为什么能预测在线结果；TTFT 误差来自 queueing、prefill batching 还是 policy？
5. retention priority 与 request scheduling priority 有何区别？
6. session 结束、取消、TTL expiry、scope downgrade 时如何清理；错误 metadata 如何回退？
7. 删除候选人 policy 后，哪些 held-out cells 退化；只删 simulator 是否影响线上结果？
8. 哪些代码属于候选人，哪些来自 vLLM RFC/libCacheSim？
9. 哪些 workload 让 policy 输，为什么？

## 11. P4 为什么不选，以及它如何翻案

P4 的最强反对意见成立：**它比 P1* 更像真正的 storage engineering，删除候选人代码后整个 backend 消失，ownership 最强。**

但“代码量和所有权”不能代替真实问题。P4 翻案必须在 7–10 天内同时满足：

- 在 pinned LMCache `fs_native/raw_block` 路径复现可归因的 inode/metadata、fixed-slot space、read-tail、GC/recovery 瓶颈；
- 获得 current upstream issue/RFC/maintainer 确认，或至少形成第三方可复现 profile，而不是只用 synthetic microbenchmark；
- 等容量、等 durability 语义比较现有 backend，测 write/read/space amplification、p95 load、GC stall、recovery 与 end-to-end TTFT；
- 范围只做单节点 LMCache L2 adapter，不扩成 distributed store。

当前没有这些证据，因此它是 challenger，不是 8–10 周的首选。

## 12. Claim-state 与简历句式

- 立项时：全部为 `roadmap`；vLLM/LMCache/libCacheSim 事实为 `source-verified`。
- probe、policy 与测试跑通：相应 artifact 可标 `shipped`（仅本项目环境）。
- 固定环境、重复试验、baseline/ablation/负 workload 与 replay-online calibration 完成后，性能结论才是 `experimentally validated`。
- 单 GPU 结果不能写成 multi-node、distributed、production 或 RDMA 结论。

只有实测后才允许填写：

> 针对 `[agent/tool-pause workload]` 下 vLLM LRU 无法感知 session/range reuse 导致的 `[实测 useful eviction]`，在固定 `[vLLM commit、GPU、模型、KV 字节容量]` 上构建 block-lifecycle probe 与 calibrated replay，并实现 `[线上可见信号]` 驱动的 bounded retention policy；相对 tuned `[LRU/fixed TTL/S3-FIFO]`，在 held-out trace 下将 `[Goodput@SLO 或 p95 TTFT]` 改善 `[数值和波动]`，replay-online 误差为 `[数值]`，并报告其在 `[失败 workload]` 下的回退。

若没有实测值，这不是可放进简历的完成态 bullet。
