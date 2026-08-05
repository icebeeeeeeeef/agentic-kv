# 多轮 Agent Prefix Cache 项目：立项裁决与对抗式评审

> 日期：2026-08-04（Asia/Shanghai）  
> 目标：2027 届国内 AI Infra / LLM Serving / 推理引擎相关校招  
> 约束：单张 24GB 消费级 GPU，8–10 周业余时间  
> 状态：本报告评审的是 `roadmap`，不是已经实现或测得收益的项目

本裁决以用户给出的项目 SOP 为宪法层：它**不是学术 novelty 项目，也不是 PagedAttention/minivLLM 式特性复现**。成功标准是预算内回答一个有裁决权的坐标问题，并形成“自建仪器/源码级归因/机制级分析 + 可选的小改进”的真实工程闭环；prior art 是基线和边界坐标，不是需要回避的威胁。

## 0. 最终裁决

**我推荐这个选题，但不推荐按当前叙事和执行路径原样立项。**

准确 verdict 是：

> **`reshape → 先批准 Gate F/Gate S；证据通过后 select 完整实现`**

建议保留的核心是：

> 在一个真实推理框架、一个固定版本和同一请求 trace 下，研究多轮 Agent-like workload 的 exact-prefix 复用、容量压力与淘汰行为；如果观察到库存最强策略仍存在稳定、可归因的 future-reuse regret，只实现一个局部、在线可用的保留/淘汰决策，并用端到端 A/B、ablation、删除测试和失败区间闭环。

不建议保留的隐含前提是：

- “Agent workload 一定会让现有 LRU 失效”；
- “引用计数或会话活跃度自然就是有效改进”；
- “命中率提高会自然转化为 TTFT p99 提升”；
- “vLLM 与 SGLang 都做一遍会显著增加项目价值”；
- “淘汰没测出 gap，就改做 CPU offload”；
- “这个题天然比可信的 PagedAttention 实现高一个量级”。

### 条件性评分

| 评审对象 | 裁决 | 评分 | 评分含义 |
|---|---|---:|---|
| 当前宽叙事：双框架 characterization、尚未由数据选择的淘汰/offload、FP8、预期 PR | **reshape** | **60/100** | 岗位相关，但真实 gap、数据裁决权、硬件可行性和因果闭环均未过门 |
| 收窄后：单框架、单失配坐标、强基线、可选单策略 patch 与负结果 | **条件性 select** | **84/100 潜力** | 若完整做出，可成为 serving/cache-runtime 岗的强项目；这不是当前完成度或 offer 概率 |
| Gate S 没有发现稳定 gap | **停止策略实现，转仪器/机制裁决路径** | 不追求性能 headline | 输出库存策略边界、无 headroom 的负结果；不得为了“必须优化”发明控制器 |
| eviction、offload、FP8 同时写成主贡献 | **reject** | <55/100 | 三条独立成功条件，8–10 周内会牺牲 ownership、基线和复现 |

三份独立评审对当前方案给出 58–64 分，对收窄方案给出 79–88 分；84 是按 SOP 的“工程复杂度、裁决权、先验防否决”重新校准后的综合值，不是机械平均。数字分数不能覆盖硬门槛失败。项目仍是 `roadmap`；只有 commit、测试、raw data 和可复现实验完成后，相关 claim 才能升级为 `experimentally validated`。

## 1. 为什么仍然推荐这个切入点

### 1.1 它与目标岗位有真实重合，但重合范围比口号窄

此前岗位样本中，常规学生 JD 共 18 条：

- KV / Prefix Cache / offload 在 8/18 条职责中出现；
- 只有 1/18 把它写成所有候选人的明确硬性要求，另有 3/18 为加分项；
- 推理优化职责是 18/18，编程/数据结构硬要求 17/18，Linux/系统基础硬要求 12/18；
- CUDA/GPU/kernel 职责是 15/18，分布式/并行/通信职责是 13/18。

因此，市场证据支持的是：

> KV Cache 是 LLM Serving 中真实、活跃、能形成专长的一等资源子系统。

但不支持：

> KV Cache 是所有推理岗位唯一的“核心战场”，或者比编程、系统、GPU 和并行基础更普遍的筛选门槛。

这个项目对 **Serving runtime、cache lifecycle、scheduler-adjacent、MaaS serving backend** 的匹配度高；对 **CUDA kernel、编译器、国产芯片适配、RDMA/多机 P/D** 只能提供邻接认知，不能作为主证明。

### 1.2 公开技术动作证明问题是真的，不证明你的假设一定成立

2026 年的一手信号很强：

- [SGLang Agent/Rollout KVCache Roadmap](https://github.com/sgl-project/sglang/issues/21846) 把 Agent/Rollout KV 管理、L2 tree、存储 prefetch 等列为显式方向；
- [SGLang Agent-Aware KV Cache RFC #24656](https://github.com/sgl-project/sglang/issues/24656) 提议把 workflow metadata 传播到 radix cache，并可选影响 eviction；该 RFC 于 2026-05-08 提出，当前为 closed/inactive；
- [vLLM Context-Aware KV-Cache Retention RFC #37003](https://github.com/vllm-project/vllm/issues/37003) 于 2026-03-13 提出按 token range 传递 retention priority/TTL，当前仍为 open，并声称已有工作实现和早期 ReAct benchmark；
- [vLLM × Mooncake 的公开 Agent trace 分析](https://vllm.ai/blog/2026-05-06-mooncake-store) 覆盖 610 条 Codex/SWE-bench Pro traces：中位 33 轮、context 中位从 12K 增到 80K、inter-turn delay 中位 5.2s / p99 81.4s、发布方报告 94.2% cache hit；公开数据集可作为校准或 held-out replay，而不是私有生产流量替代品；
- Tair KVCache/HiSim、FlexKV、Mooncake、AIBrix、FastDeploy、SGLang HiCache 等公开动作共同说明“workload—KV 生命周期—层级/淘汰—SLO”是企业真实工作。

这些证据让选题 **不空泛**；同时也说明宽泛的“agent-aware cache”并不新，且上游已经在抢占设计空间。个人项目的价值不能来自“我第一个想到”，只能来自：

1. 你在固定版本上发现了什么具体边界；
2. 你拥有哪一个局部决策和测试；
3. 哪组强基线、oracle、ablation 和失败区间证明结论；
4. 结论在哪些硬件、workload 和框架版本上不能外推。

### 1.3 它能命中面试里真正稳定的隐性要求

此前面经主样本 N=14 中：KV/prefix 出现在 6/14，框架机制/源码 8/14，系统诊断 10/14，手写代码 10/14，严格项目拷打 9/14，条件/边界问题 9/14。样本有作者和 CUDA 背景选择偏差，不能当真实面试概率；但它揭示了一个稳定模式：

> 面试官更在意“你如何定位、如何测、为什么归因给你的改动、什么时候失效”，而不是项目标题里有多少关键词。

这个题如果完整闭环，能同时展示 workload 建模、源码路径、性能测量、资源 trade-off、真实 patch、A/B、负结果和边界，因此比“部署过 vLLM”更容易形成 20–45 分钟的有效追问。

### 1.4 单卡约束仍可形成真实实验

本题不必假装生产集群。单卡可以通过固定模型后主动 sweep cache budget、并发会话数、reuse distance 和工作集/缓存比，制造可控压力。单卡不能证明跨实例 cache affinity、RDMA、远端存储、故障恢复和多节点 tail，但足以验证：

```text
请求前缀结构
  -> 本地 KV block 生命周期与 victim 决策
  -> 重算的 prefix tokens / prefill 时间
  -> TTFT / Goodput@SLO
```

这是一个完整而诚实的本地因果链。

### 1.5 按你的 SOP，三条硬标准的判定

| SOP 硬标准 | 当前原案 | 收窄后的通过方式 | 一票否决点 |
|---|---|---|---|
| 工程复杂度下限 | **条件通过**：generator 和真实框架足够形成起点，但“调用 API + 参数扫描 + 曲线”不够 | 自建 token/trace generator-replayer、cache-event probe、offline oracle；能沿源码解释 victim→recompute；若有 gap，再加一个小 adapter/patch | 只有部署、配置扫描、框架自带 metrics 和图表 |
| 可闭环性/数据裁决权 | **当前未通过**：原叙事主要期待某张卡上的 TTFT 百分比 | 主结论落在无量纲结构坐标和 break-even；消费卡负责主矩阵，A100/H100 只能做少量外部有效性复核 | 结论依赖 H100、RDMA、PCIe/CXL 带宽或大集群才能成立 |
| 先验否决风险 | **问题真实性通过，具体 gap 待证**：官方 roadmap/RFC 明确承认 agent retention/eviction 问题，但上游已有多种策略和 early implementation | 用官方 issue/RFC 防守“问题不存在”，用强 prior art 基线和单卡边界回答“墙在哪”；不声称无人注意或首次提出 | 找不到库存策略之外的 headroom，却仍声称通用策略失效 |

这里需要校正一个常见过度门槛：**engine patch 是强加分项，不是负结果分支的唯一 ownership 证明。** 如果你亲手完成了有裁决权的仪器、源码级归因、oracle 和边界测量，并证明库存方案已经覆盖可达区间，项目仍可合格。反过来，一个没有可靠因果证据的 200 行 policy patch，也不会因为“改了源码”自动变成强项目。

## 2. 为什么不能原样同意当前方案

### 2.1 “Agent 与普通 chat 完全不同”需要拆成可控变量

exact prefix cache 只认 token prefix。典型工具调用并不是把结果随意“插入历史中间”，而是把 tool result 追加在 assistant tool call 之后；下一轮复用此前的精确前缀。Agent 相对 chat 的独特压力主要是**数量上的**：

- 上下文更长且逐轮增长；
- 工具调用造成更长、更分散的 inter-turn gap；
- 多 session/worker 交错导致更大的 reuse distance；
- branch/fan-out 形成共享祖先和不同尾部；
- working set 更容易超过本地 KV 容量。

所以生成器至少需要三个 token/arrival budget 匹配的对照：

1. 单轮、共享 system prompt；
2. 线性多轮 chat；
3. branchy Agent-like session。

若三者不匹配总 token、prefix length、arrival rate 和 concurrency，就无法判断收益来自“Agent 结构”，还是仅仅来自更长上下文或更高负载。任意中间插入只适合作为“prefix invalidation 负对照”，不能当主 workload。

### 2.2 现有框架并不是一个朴素的统一 LRU 基线

这是当前计划最重要的技术反例。

SGLang 截至本次核验的源码快照已经提供 `lru`、`lfu`、`fifo`、`mru`、`filo`、`priority`、`slru` 策略；其中 LFU 使用 hit count，SLRU 把达到阈值的节点放入 protected segment，priority 先按显式 priority 再按 recency 淘汰：[策略工厂](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/utils.py)、[策略实现](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/evict_policy.py)。[RadixCache 实现](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/radix_cache.py) 又只从可淘汰叶节点开始，天然倾向保留共享祖先。

vLLM 的 automatic prefix cache 用 ref count 保护仍在使用的 block，并把请求尾部 block 先放回 free/eviction queue，从而让更深、覆盖 token 更多且通常更少复用的 suffix 更早被淘汰；核验快照也明确要求 reverse free：[vLLM KV cache manager](https://github.com/vllm-project/vllm/blob/cb8104839c141609d99f1254459ef3a4f1bd4263/vllm/v1/core/single_type_kv_cache_manager.py)。

因此：

- “结合引用计数”不是一个新策略；ref count 首先是生命周期安全机制，不是未来复用预测器；
- branch tree 不必然击穿 SGLang，因为共享祖先和叶级淘汰已经提供结构性保护；
- 在 SGLang 上只与 LRU 比较不公平，至少要先比较无额外 metadata 即可工作的 LFU/SLRU；`priority` 只有在请求到达时存在合法在线 metadata 和公开映射时才是有效基线，否则全 0 priority 会退化成 recency；
- 在 vLLM 上也必须先确认 tail-first ordering 和当前版本的 cache manager 行为。

你的研究问题必须从“LRU 会不会错”升级为：

> 在现有**最强相关库存策略**之后，是否仍存在由在线可见的 session/workflow 信号可以减少的 future-reuse regret？

### 2.3 上游重合既是市场证据，也是重复建设风险

SGLang #24656 和 vLLM #37003 已经覆盖 workflow metadata、TTL、priority、agent-aware eviction 等概念；[SGLang session radix cache PR #27058](https://github.com/sgl-project/sglang/pull/27058) 也已覆盖 session close 时的回收。它们的动机和早期数字不能替代你的本地验证，但足以否定两种包装：

- “主流框架没有意识到 Agent reuse”；
- “我提出了第一个 session-aware / TTL / priority 策略”。

合理定位是：

> source-verified 的上游问题空间 + 你对固定 commit、单卡结构坐标和强 prior-art baseline 的独立验证 + 若有 headroom 则一个边界清楚的小 patch，若无 headroom 则一个能否定增项的负结果。

| prior art | 已经解决/主张什么 | 本项目不重复什么 | 可差异化的裁决问题 |
|---|---|---|---|
| SGLang 内置 LFU/SLRU/priority + leaf eviction | 多种通用 victim ordering、共享祖先的树结构保护 | 不重新实现 LFU/SLRU/priority | 哪个 `ρ/D/S` 区间内，paused-but-live session 仍有 regret；最强库存策略谁赢 |
| SGLang #24656 | workflow metadata plumbing 和 agent-aware prototype 提案；当前 closed/inactive | 不声称首次提出 workflow hints | 固定版本上复现动机、测可达边界、检验简单 adapter 是否足够 |
| SGLang session radix cache | session close 后回收 | 不把“session lifecycle”泛化成个人创新 | session 尚存活但 tool-pause 时的 retention，而非 close reclaim |
| vLLM #37003 | token-range priority/TTL API；作者声称有工作实现和 early ReAct 结果，完整 benchmark 仍在进行 | 不重做整个 API，也不把 RFC 作者数字当本地结果 | 独立复现、消费卡单实例边界、matched controls、库存强基线和 losing conditions |
| vLLM × Mooncake | 长时多轮公开 trace 与分布式 KV pool/cross-instance 方案 | 不做 RDMA/多节点，不与其比生产吞吐 | 用公开分布校准单卡 trace；只裁决 local residency/eviction |
| [KVFlow](https://papers.neurips.cc/paper_files/paper/2025/hash/b7971d31a7d5eb0f1eed2f8f6f368195-Abstract-Conference.html) / [Continuum](https://arxiv.org/abs/2511.02230) 等论文 | workflow future knowledge、TTL/offload/score 等路线及特定实验 | 不宣称 idea novelty 或“打败论文” | 在本框架、本资源与不同结构坐标下做复现验证和边界扩展 |

这满足 SOP 的反脆弱性：如果社区在项目期间合入 agent-aware 功能，你的 generator、probe、oracle 和反例矩阵转而评测它；项目不因“官方也做了”而作废。

### 2.4 命中率不是业务结果，p99 也不适合自动成为唯一主指标

cache hit rate 可能被短而便宜的 block 拉高，却未显著减少 prefill；也可能通过保留 prefix 换来 scheduler CPU、吞吐或其他 session 的 tail 恶化。正确指标层次是：

- 主结果：`p95 TTFT` 或 `Goodput@SLO`；样本充足时再报告 p99；
- 机制指标：可复用机会、hit tokens、useful-prefix eviction、recomputed prefix tokens、prefill time、occupancy、reuse distance；
- 护栏：TPOT/ITL、aggregate throughput、GPU bytes、host CPU、策略每次决策开销、输出正确性/质量；
- 公平性：同一 immutable trace、arrival、tokenized prompt、seed、cache bytes、模型与框架 commit。

必须先证明 `eviction → recompute → TTFT/Goodput`，再声称端到端优化。

### 2.5 双框架深做会降低而不是提高证据密度

vLLM 与 SGLang 的 cache 表示、scheduler、block/radix topology、metric 和 backend 并不等价。把两边曲线放在一起很容易变成 apples-to-oranges；把两边都改又会把 8–10 周预算切半。

建议只在第 1–3 天做浅层 feasibility spike，然后冻结一个框架：

- 默认优先考察 **SGLang**：策略 seam 显式、库存基线丰富、RadixCache 与 Agent workload 语义直接，较适合单卡 characterization；
- 只有当你的具体消费卡/模型/FP8 backend 或 patch seam 在 vLLM 上明显更稳定时，才选 vLLM；
- 第二框架只能作为源代码语义参照或一个小规模外部效度检查，不做第二份实现。

这个建议不是断言 SGLang 一定有 gap；恰恰因为它的强基线更多，若仍测出 headroom，结论更可信。

Gate 后一个**可能合格但并未预先批准**的实现，是复用现有 cache-priority seam，做 paused-but-live session 的 soft priority/deadline adapter。它与 session close reclaim、request scheduling priority 必须分离；其 idea 已有 RFC/论文 prior art，所以个人价值来自小而清晰的 adapter、独立复现、结构坐标和失效边界，不来自“提出了新算法”。若固定版本不能在约 200–300 行以内隔离 cache priority，或这个信号被 SLRU/static priority 等价覆盖，就不实现。

### 2.6 offload 不是淘汰策略失败后的廉价备选

CPU offload 会引入 transfer latency/bandwidth、异步队列、prefetch 时机、host 容量、并发争用和恢复正确性。它是一条新的数据面因果链，不是换一个 victim score。

本项目中应当：

- 淘汰/保留策略与 offload **至多选一个主机制**；
- 若 Gate S 通过，默认把唯一自有机制限定为本地保留/淘汰决策；
- 若框架原生 offload 路径可用，它最多是一个现成 baseline 或主线完成后的补充观察；
- 若 Gate S 没有淘汰 gap，不得临时把项目改造成 offload 系统。

### 2.7 FP8 应成为容量交互实验，而不是第二个创新点

[vLLM 当前文档](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/) 列出了 FP8 KV cache、scale calibration 和 backend 支持；例如 `fp8_e4m3`/`fp8_e5m2` 在 CUDA 11.8+ 有对应支持。但具体消费卡、模型 head dimension、attention backend、框架 commit、质量和 kernel 性能仍需实机验证。

FP8 的因果链是：

```text
KV bytes/token 下降
  -> 若原本存在容量淘汰，驻留集合才可能改变
  -> 若新增驻留后来被复用，hit/recompute 才可能改变
  -> 扣除量化、scale、kernel 与质量代价
  -> 才可能改变 TTFT / Goodput
```

若 Gate S 产生 candidate，使用一个小型 2×2 交互实验：

| | stock policy | candidate policy |
|---|---:|---:|
| BF16/原生 KV dtype | 主基线 | 主策略 |
| FP8 KV | 容量敏感性 | 检查策略优势是否因压力下降而缩小/消失 |

若 Gate S 没有 candidate，则不存在这张 2×2；只在 stock policy 下做 BF16-vs-FP8 的等 bytes/等 token 容量边界，或者在 FP8 与主问题无关时跳过。

同时区分：

1. **同物理 HBM budget**：观察 FP8 的真实容量效应；
2. **同逻辑 cache-token capacity**：隔离 dtype/kernel/scale 开销。

若 capability gate 不通过，诚实记录“不支持/不稳定的硬件—框架边界”，不要伪造一个 FP8 性能结论。

### 2.8 PR 不是成功标准

社区是否接受 PR 受路线、maintainer 偏好、版本演进和已有 RFC 影响，不能作为 8–10 周项目的硬完成条件。必需交付是：

- pinned fork/commit；
- 正结果分支：owned diff 和回归测试；负结果分支：自建仪器、源码归因、oracle 与可审计的 kill decision；
- workload trace schema 与生成/回放器；
- raw logs、manifest、分析脚本和一键复现；
- 正结果或负结果报告；
- issue/PR/discussion 的状态如实区分为“准备、提交、review、merged”。

## 3. 批准后的唯一研究问题

### 3.1 可证伪问题

> 在固定 `[framework commit / model / GPU / KV dtype / cache bytes]` 与同一 immutable trace 下，当 exact-prefix working set 因 reuse distance、branching 和 concurrency 超过 GPU KV 容量时，库存最强相关策略是否存在可重复、端到端可见的 future-reuse regret？一个只使用在线可见信号、由本人拥有的局部 retention/eviction 决策，能否减少 recomputed prefix tokens，并改善 p95 TTFT 或 Goodput@SLO，同时不超过预先声明的 TPOT、throughput、CPU 和显存护栏？

这里：

- “future-reuse regret”由离线 oracle 计算，只用于证明 headroom；
- candidate 不得读取未来 trace；
- “Agent-specific”只有在 matched chat control 下仍成立才能使用；
- 若最强库存策略、简单静态 heuristic 或 FP8 容量本身已消除 headroom，则原假设被证伪。

### 3.2 最小因果链

```text
[prefix overlap graph / reuse distance / working-set-to-cache ratio / arrival]
  -> [库存 victim decision]
  -> [未来仍会复用的 block 被淘汰]
  -> [prefix recomputation / prefill cost]
  -> [candidate 改变 victim ordering]
  -> [p95 TTFT 或 Goodput@SLO]

guardrails:
  TPOT / ITL / throughput / GPU bytes / host CPU / policy overhead / output quality
```

任何不能挂在这条链上的功能都不进入主线。

### 3.3 让单卡数据拥有裁决权：主结论必须是结构坐标

消费卡上的绝对 TTFT、PCIe 带宽和 kernel 性能不能直接代表生产 H100 集群；但 replacement policy 的**访问结构边界**可以用归一化坐标表达：

- `ρ = unique reusable KV bytes / available GPU KV-cache bytes`：工作集压力；
- `D = last reuse 之后插入的不同 KV bytes / available KV-cache bytes`：容量归一化 reuse distance；
- `S = exact-reusable prefix tokens / input tokens`：精确前缀稳定度；
- `F = branch fan-out` 与 active session 数；
- `R = future-reused evicted bytes / all evicted bytes`，或其 recompute-cost 加权版本：库存策略 regret；
- `Δprefill_tokens`、p95 TTFT/Goodput 是把结构坐标翻译成目标岗位 SLO 的终点指标。

项目最有裁决权的数字不是“4090 上快了 17%”，而是类似：

> 当 `ρ` 从 `<1` 跨过某一区间、`D` 超过某阈值且 `S` 足够高时，库存策略开始产生可重复的 future-reuse regret；候选信号只在该区间有收益，并在低压力/低稳定度下因开销持平或输掉。

临时租一张 A100/H100 只用于检查**边界排序或趋势是否反转**，不能成为主结论成立的前提。若结论必须依赖 NVLink、RDMA、H100 特定 kernel 或大集群才出现，按 SOP 应直接排除。

### 3.4 Fermi 闸门

在安装和改代码前先估算墙是否落在单卡可测范围：

```text
KV bytes/token
  ≈ 2(K,V) × num_layers × num_kv_heads × head_dim × bytes_per_element

cache token capacity
  ≈ available KV-cache bytes / KV bytes/token

pressure ρ
  ≈ 去重后的、仍可能复用的 resident prefix tokens / cache token capacity
```

把模型、GQA/MQA 参数、权重占用和框架预留显存代入，估算需要多少 session × prefix length 才能让 `ρ` 穿过 1。可以主动收紧 KV budget 来制造压力，但必须固定并记录实际 cache bytes，不能只写一个模糊的 `gpu_memory_utilization`。

Fermi kill condition：若目标模型在 24GB 卡上连最小稳定服务都放不下，或者只有 100K+ context/几十张卡才能让结构边界出现，就换小模型/缩 cache budget；若这样仍无法在 4–8 个 session、可接受运行时间内跨过 `ρ≈1`，该策略子命题不立项。

## 4. 两层生存门

### 4.1 Gate F：前 3–5 天的可达性闸门

1. 固定 GPU 型号/Compute Capability、driver/CUDA、框架 commit、模型、dtype、attention backend、page/block size 和实际 KV bytes；
2. 完成上述 Fermi 估算，并用 4–8 个 session 做一次 `<1 / ≈1 / >1` 的压力 smoke；
3. 做 exact-prefix 真值表：完全相同、首部改 1 token、正常 append tool result、chat template/tool schema 改序；
4. 验证 cache event/metrics 能区分 prefix mismatch、eviction、queueing 和 recompute；
5. FP8 只做 10–30 分钟 capability smoke，失败不阻塞 BF16 主线；
6. 对 vLLM/SGLang 只做 seam 与可观测性比较，Day 4–5 冻结一个框架。

Gate F 不通过时，不进入八周工程；先修正模型/版本/观测口径。它不是“做了一半才发现卡跑不动”的容错机制。

### 4.2 Gate S：第 2–3 周的假设生存门

只有以下条件全部满足，才进入策略实现：

1. 固定一个框架 commit、一个模型、一个 attention backend、一张 GPU；
2. 实机验证原生 prefix cache；FP8 单独完成 capability check；
3. 形成 token/block ground truth：每个请求的可复用机会、实际命中、淘汰、重算、occupancy 和 TTFT 能对齐；
4. 用同一 trace 比较库存策略：SGLang 的无额外 metadata 基线通常至少含 LRU/LFU/SLRU；带 metadata 的 stock priority 只有在输入为请求到达时合法可见、映射规则预注册且不读未来时才纳入；future-aware priority 只能作 oracle；
5. 为 A1“stock + instrumentation”预注册 observer-effect 判据：主指标的置信区间落在非劣区间、关键事件完整、CPU/内存开销低于预设预算；不能用事后的“看起来足够小”；
6. 离线 oracle 在至少两个相邻压力 cell 上显示稳定 headroom，并且趋势能在一个未参与调参的 held-out trace/分布上复核；单条偶然 trace 不足以过门；
7. 观察差异明显大于 run-to-run variance，且排除了 warmup、tokenization、batch shape、arrival 和后台负载伪影；
8. 候选可以复现/移植 prior art，不要求概念新；但不能只是翻转已有开关，必须公开相对基线新增的在线信息预算，并预计在约两周内实现/测试。若复用 SGLang priority seam，要证明它只改变 cache victim ordering，不改变 request scheduling。

停止策略实现的条件：

- 只有人为极端 trace 才有 gap；
- 低成本库存策略或简单静态 heuristic 已经吃掉 headroom；
- gap 只存在于命中率，不能传到 recompute/TTFT/Goodput；
- candidate 必须泄漏未来信息才赢；
- patch 需要大范围重写 scheduler、cache data path 或 offload；
- FP8/框架/硬件路径不稳定，无法做公平 A/B。

停止不是失败。合格的负结果是：预注册假设、足够压力和统计能力、强基线、oracle、因果指标齐全，并且负结果改变了工程决策。此时自建仪器、源码级归因和边界坐标本身就是 owned delivery；不需要为了证明“我改过 engine”继续写一个没有价值的策略。仅仅“没跑通”不算研究结果。

## 5. 最小实验设计

### 5.1 请求 trace 先于请求执行

生成器先产出不可变 trace，再交给两个实验分支回放。每条至少保存：

- session/workflow id、turn/step id、parent id；
- arrival timestamp、tool gap、branch/fan-out；
- tokenized prefix 和新增 delta 的长度/哈希；
- online 可见 metadata；
- 未来复用只保存在 oracle 侧，不能暴露给 candidate；
- seed、模型 tokenizer 和 chat template 版本。

优先用公开 Agent trace 的统计分布校准 synthetic generator，并留一部分公开 trace 做 held-out replay。不要把 synthetic workload 写成“真实生产流量”。

### 5.2 最小 workload 族

| workload | 用途 | 应控制的混杂变量 |
|---|---|---|
| 单轮共享 system prompt | 非 Agent 高共享对照 | 总 token、arrival、cache budget |
| 线性多轮 chat | append-only 对照 | 轮数、prefix growth、inter-turn gap |
| branchy Agent-like | 主 workload | fan-out、session 数、同一 token budget |
| 低共享/低压力 | 必须输掉或持平的负对照 | cache working set < capacity |
| 高 reuse-distance/high churn | 压力场景 | arrival 与并发固定 |
| 中间插入导致 prefix invalidation | 机制诊断，不是主 workload | 明确标注非典型 tool path |

主轴只保留：`working-set/cache ratio`、`reuse distance/tool gap`、`branching`、`active sessions/arrival`。不要做全因子笛卡尔积；先用低/中/高小网格找边界，再只对关键 cell 做重复与 held-out confirmatory run。

正式主矩阵建议压成可执行的 72 runs：

```text
2 个 prefix stability（稳定 append-only / 首部突变负控）
× 2 个 pressure（ρ≈0.6–0.7 / ρ≈1.2–1.5）
× 2 个 reuse distance（短 / 长）
× 3 个线上策略（stock / 最强库存替代 / candidate）
× 3 个 seeds/repeats
= 72 runs
```

branch/fan-out 先固定一个主值，之后只在关键拐点补 2–3 个敏感性点。A0/A1 instrumentation check、offline oracle、signal-disabled 和 no-cache 只跑 anchor cells，不与全部 72 runs 笛卡尔相乘。这样既有反例，也不会让“实验严谨”演化成无限 scope。

### 5.3 最小 A/B 与 oracle

| 组 | 目的 |
|---|---|
| A0：unmodified stock | 真实库存基线 |
| A1：stock + instrumentation | 量化埋点开销与观察者效应 |
| A2：最强相关库存/静态 baseline | 防止只打最弱 LRU；按在线信息预算区分无 metadata、合法 metadata 和 future-aware oracle |
| A3：candidate | 唯一 owned policy |
| A4：candidate code path + signal disabled / revert | 删除测试，证明收益来自信号而非重构副作用 |
| A5：offline future-aware oracle | 估计理论 headroom，不参与线上公平比较 |
| A6：no-cache（可选） | 只用于校验 recompute/TTFT 机制链 |

### 5.4 结果判定

在 pilot 后、看正式结果前预先冻结：

- 主指标与 SLO；
- 重复次数和置信区间方法；
- guardrail 的非劣化 margin；
- 何谓“差异大于噪声”；
- 正结果、持平、负结果的判定；
- 哪些 workload 是适用区间，哪些是 losing condition。

不要先定“必须提升 20%”之类缺乏依据的目标。合理门槛是：作用在机制链上、可重复、明显大于测量方差、对端到端指标有意义，并完整报告代价。

## 6. 8–10 周执行版

| 时间 | 交付 | 决策点 |
|---|---|---|
| Day 1–5 | Fermi 估算、vLLM/SGLang 浅 spike、exact-prefix truth table、固定一个框架/commit、FP8 smoke | **Gate F**；Day 5 后不再双线深做 |
| Week 2 | immutable trace、匹配对照、源码调用链、A0/A1 埋点与 ground truth | 不能区分 mismatch/eviction/queue/recompute 就不做策略 |
| Week 3 | 库存强基线、结构坐标压力边界、offline oracle、held-out 预留 | **Gate S**：无稳定 headroom 就停止策略实现，转为负结果/边界报告 |
| Week 4–5 | 一个 candidate、单元/顺序测试、回退路径 | 删除 patch 后必须恢复库存行为 |
| Week 6 | ablation、signal-disabled、negative workload、策略开销 | 收益必须能归因给唯一信号 |
| Week 7 | 正式 A/B、重复、置信区间、held-out replay | 冻结结论，不继续调参追数字 |
| Week 8 | 有 candidate：做 policy×dtype 2×2；无 candidate：只做 stock BF16-vs-FP8 的容量边界，若无相关压力则跳过；能力门失败只记录边界 | 不把 FP8 写成自研 kernel/量化算法 |
| Week 9 | 失败区间、复现脚本、raw result audit | 允许结论是“不默认启用” |
| Week 10 | 技术报告、90 秒/10 分钟/45 分钟叙事、可选 issue/PR | merge 与否不改变项目是否完成 |

若只有 8 周，压缩 Week 8–10，不压缩 Gate F/Gate S、强基线、ablation 和复现。临时 A100/H100 验证、offload 补充和社区 PR 最先删除。

## 7. 个人 ownership 与面试防守

### 7.1 你必须能指着代码回答的四层边界

| 层 | 正确表述 |
|---|---|
| 上游已有 | prefix cache、block/radix 数据结构、库存策略、框架原生 FP8/offload |
| 你读取并验证 | 请求到 cache lookup/allocate/free/evict 的源码路径与版本行为 |
| 你拥有 | 必有：trace schema/runner、instrumentation、oracle、实验与分析；Gate S 通过时再加一个 victim/retention decision 与测试 |
| 你没有证明 | 生产流量、跨节点收益、RDMA、kernel ownership、普遍优于所有 workload、offer 因果 |

### 7.2 删除测试

- 正结果分支删除 candidate patch：行为和指标应回到 A1/A2；
- 正结果分支保留代码但关闭新信号：收益应消失或显著缩小；
- 删除 instrumentation：性能不应出现一个同方向的大变化；
- 删除 cache pressure：策略应持平或因开销小幅输掉；
- 换成 matched chat/低共享 trace：“Agent-specific”结论若仍不变，需要重新解释；
- 删除自写 generator、改用 held-out public replay：核心结论若完全消失，说明过拟合 synthetic workload。

### 7.3 最容易击穿你的问题

1. vLLM 已有 ref count，SGLang 已有 LFU/SLRU/priority，你的新信息到底是什么？
2. 为什么这不是“把未来 reuse 标签泄漏给 eviction policy”？
3. 共享祖先本来就受 radix leaf eviction 保护，你观察到的 regret 具体发生在哪一类节点？
4. 命中率提高了，为什么 TTFT/Goodput 没提高，或者 TPOT/吞吐变差？
5. 你怎么证明不是 generator 设计出来专门让你的策略获胜？
6. FP8 后容量压力下降，你的策略是否失去价值？
7. 为什么不开大缓存、用 SLRU/priority、做 routing，反而加这个策略？
8. 为什么不做 offload？单卡结论能否外推到 Mooncake/FlexKV？
9. 删除你的策略代码后，instrumentation/oracle 还能回答什么问题？反过来删除仪器后，你的策略收益还能被谁审计？
10. 你的策略在哪个 workload 明确输掉，为什么不应该默认合入？

若这些问题没有 raw trace、commit、图表和代码位置作答，这个项目撑不住 45 分钟。

## 8. 对原叙事逐条裁决

### 同意

- 用真实框架而不是 toy cache simulator 作为端到端被测系统；
- 参数化 workload + measurement-driven characterization；
- 在**同一框架、同一 trace、同一 cache bytes**下做 A/B；
- 只在观察到具体次优点后改一个小机制；
- 同时报告收益、开销、适用条件和 losing condition；
- 尝试用 issue/PR 接受社区审查，但不把 merge 当成功标准。

### 必须调整

- “SGLang 和 vLLM 分别跑”改为 1–3 天浅 spike 后单框架；
- “现有近似 LRU”改为逐版本核验的库存强基线集合；
- “工具返回插入”改为正常 append-only 主路径，中间插入仅作负对照；
- “命中率、TTFT、显存”扩展为机会—victim—recompute—端到端—护栏链；
- “引用计数/会话活跃度”改为 Gate S 后选择一个未被库存等价表达的在线信号；
- “CPU offload 或淘汰”改为至多一个主机制；有 headroom 时默认本地 retention/eviction，无 headroom 时不实现机制；
- FP8 改为主策略与容量压力的交互轴；
- “p99 改善 Y%”改为预注册主指标，样本不足时以 p95/Goodput@SLO 为主；
- 项目名在出结果前使用“行为、失配边界与策略评估”，不要预设一定能改进。

### 明确拒绝

- “KV cache 是整个 serving 的唯一核心战场”；
- “像 1990 年代 CPU cache”作为证据或面试主论据；
- “Agent cache 语义与 chat 完全不同”；
- “refcount 是我的新策略”；
- 只与 LRU 比较、回避 LFU/SLRU；或者给 priority 喂未来信息后把它伪装成公平在线基线；
- 为了正 headline 选择只对 candidate 有利的 synthetic trace；
- Gate S 失败后临时扩成 offload/分布式 KV store；
- 把框架原生 FP8 写成“实现了 FP8 量化/kernel”；
- 把单卡结果外推成跨节点、RDMA、MaaS 生产收益；
- “比复现 PagedAttention 完全不同量级”。

对 PagedAttention 更准确的比较是：

> 对 serving/cache-runtime 岗，真实框架里的测量仪器、源码归因、窄 patch（若有）和因果证据通常比 toy PagedAttention 更可迁移；对 engine/kernel 岗，一个包含 allocator、block table、COW/refcount、scheduler、正确性 oracle 和可信 kernel/benchmark 的 mini-engine 可能更深。价值由个人交付、证据和岗位子族决定，不由题目名称决定。

## 9. 按 SOP 构建叙事，而不是靠 novelty

### 经历

只使用你能提供一级证据的真实经历。若使用既有对象存储/缓存经历，准确说你负责或参与了什么数据路径、测量或故障定位；不要把团队工作、调研材料或社区实现写成自己的实践。

### 先验

一个可测试、但不假装正确的迁移先验可以是：

> 在容量受限系统中，只看最近访问而忽略对象生命周期/下一次使用结构，可能在 bursty、暂停—恢复型 workload 下做出代价不对称的 victim decision。

这只是来自存储系统经验的假设，不是结论。

### 问题

把先验投射成坐标问题，而不是“我要打败 LRU”：

> 对 exact-prefix Agent-like workload，`ρ/D/S` 在哪里让现有最强通用策略开始产生可见 regret？session signal 在什么区间增加信息，在什么区间只是噪声或重复已有 SLRU/priority？

### 实验与数字

你亲手造 generator/replayer、token truth、cache-event probe 和 oracle；最后给出拐点、break-even、收益区间、噪声、成本与负例。TTFT/Goodput 是目标岗位语言，结构坐标是单卡数据的裁决权来源。

### 先验裁决

这是最终叙事的高潮，必须同时回答“迁移成立”和“迁移断裂”：

- 可能成立：reuse distance、工作集压力、生命周期信号确实影响 victim quality；
- 可能断裂：KV 可重算，丢失主要伤害性能而非正确性；radix leaf eviction、refcount、tail-first ordering 已编码一部分结构；scheduler queue 和 decode 可能吞掉 cache 层收益；FP8 会移动容量边界；
- 最终结论：哪些存储直觉可以迁移，哪些必须改成 LLM Serving 的 SLO/成本模型。

这套叙事即使得到负结果也完整；它不要求学术 novelty，也不依赖“我比巨头更好”。

### 四类攻击的预案

| 攻击 | 回应核心 |
|---|---|
| “这不是推理方向” | 明确主攻 serving/cache-runtime；终点是 prefill、TTFT、Goodput，放弃用它证明 kernel/编译能力 |
| “早有人做了” | 展示官方 RFC/roadmap 和 prior-art 矩阵；说明自己测的是固定框架、消费卡、强基线下的边界坐标，不争 idea novelty |
| “为什么不做 offload/RDMA/kernel” | 这些重要，但数字依赖你够不着的硬件域，单卡数据无裁决权；本项目只做 local cache decision，并维护相关正典认知 |
| “是不是绕开正典” | 能画 prefix cache/block/radix 生命周期，解释 PagedAttention、continuous batching、prefill/decode、量化、GPU memory model；项目是尖峰，不替代底盘 |

## 10. 建议标题与简历声明

### 立项时标题

**多轮 Agent 工作负载下的 Prefix Cache 行为、失配边界与策略评估**

这个标题不预设库存策略一定失败。

### 若得到正结果

> 针对 `[framework@commit]` 在 `[具体 Agent-like workload]` 下的 `[具体库存失配]`，在 `[真实模块]` 中实现 `[唯一 owned policy]`；相对 `[stock + strongest built-in baseline]`，在 `[GPU/model/dtype/cache budget]` 下将 `[p95 TTFT/Goodput]` 改善 `[实测值]`，并报告 `[TPOT/throughput/CPU overhead]`、ablation、删除测试和 `[明确 losing condition]`。

### 若得到负结果

> 构建 prefix-block lifecycle trace/replay 与 future-aware offline oracle，在 `[framework@commit]` 上比较 `[库存强基线]` 与候选策略；确认在 `[覆盖范围]` 内库存策略无可利用 headroom/简单基线已覆盖，给出 break-even 和不建议默认启用的证据。

### FP8 的安全表述

> 评估框架原生 FP8 KV cache 在相同 HBM budget 与相同逻辑 token capacity 下对容量压力、命中、TTFT/TPOT 和质量的影响。

除非你真的写了 quantization/kernel 代码，否则不能写“实现 FP8 KV 量化”。

## 11. 最终推荐边界

### 我会推荐你立项，当且仅当

- 你的主投递仍是 LLM Serving / cache-runtime / inference backend；
- 接受一个框架、一个问题、一个策略；
- 接受 Week 3 因无 gap 而停止策略实现；
- 接受负结果也是合格交付，但“没跑通”不是结果；
- 把时间优先给源码路径、强基线、owned diff、raw evidence 和复现；
- 同时继续准备 C++/Python、数据结构、OS/Linux、GPU 性能模型等面试底座。

### 我会拒绝你按这个项目立项，如果

- 你坚持双框架深做；
- 你需要项目保证有性能提升或保证能合 PR；
- 你把淘汰、offload、FP8 都当独立主贡献；
- 你只打算写外部 workload runner、调框架开关和画曲线，没有低扰动 probe、token/cache ground truth、源码归因、oracle 或能改变策略选择的结构性裁决；
- 你的目标岗位实际是纯 kernel、编译器、异构芯片或 RDMA/多机数据面，却想用这个项目替代对应实现证据。

## 12. 最终结论（一句话）

> **推荐这个主题进入限时证伪阶段，但不是预先批准“现有策略一定有 gap”。在一个固定框架上，用自建仪器、强基线、`ρ/D` 结构坐标和离线 oracle 先裁决失配边界：有 headroom，就复现/实现一个局部、在线、可删除的策略并闭环；无 headroom，就以库存策略选择和负结果完成机制裁决，绝不靠 offload 或新控制器救题。**

这比原方案少了功能，却增加了科学性、个人 ownership、面试可防守性和按时完成概率。

## 13. 评审方法与局限

本裁决由三个独立角度交叉评审：市场/岗位适配、单卡技术可行性、面试/ownership 防守；随后又对最终草案做了一次独立反方审计。审计初判为 `REVISE`（P0=0、P1=5）；本文逐项修正 ownership 双路径、Fermi gate、`ρ/D` 边界、priority 信息预算和 FP8 分支后，独立复核结论为 **`PASS（P0=0，剩余 P1=0）`**。

局限包括：

- JD 样本量有限，渠道、公司和岗位子族分布不均；
- 面经 N=14 只来自 6 篇作者帖，且 CUDA 背景候选人造成明显选择偏差；
- GitHub main、RFC 和文档变化快，真正开工必须 pin commit 后重新核验；
- 公开 RFC 的动机、论文和发布方性能数字不是本地复现实证；
- 24GB GPU 的具体型号、Compute Capability、驱动、模型和 backend 尚未给出，FP8 可行性仍是 `unverified`；
- 没有公开数据能证明某个项目会因果性提高简历通过率或 offer 概率；
- 84/100 是收窄方案完成后的证据潜力，不是对尚未实现项目的能力认证。
