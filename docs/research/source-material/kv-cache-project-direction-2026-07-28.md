# KV Cache 求职项目方向复核

日期：2026-07-28
目标：单人、单卡、偏 runtime engineering，面向 LLM Serving / KV Cache 相关团队。

> **状态：历史方向选择输入，不是当前实施或简历口径。**
> 当前唯一权威设计是
> [KV Retrieval Lab 正式设计 v3](./kv-retrieval-lab-distributed-testbed-design-2026-07-28.md)：
> 默认交付 B0–B3 的 `Shared KV Retrieval Boundary & Admission Study`；只有
> `H*(Q,B_hat,L)` 动态可分性成立且 B4 在 held-out confirmatory 中战胜 B3，才使用
> `Contention-Aware Shared KV Retrieval Runtime`。主指标是
> `Goodput@TTFT+TPOT`，active decode ITL 是 guardrail。OffloadingConnector
> failure bridge 是独立 upstream contribution，不再作为本项目里程碑。
>
> 本文保留早期选方向证据；其中旧项目名、B0/B1 对照、Goodput@TTFT/ITL、
> failure+performance 双里程碑与实施顺序均已被 v3 取代。

## 一、裁决

不建议继续把 ToolGap-KV 扩展为“agent tool-wait KV 生命周期策略”，也不建议重做
Mooncake、LMCache 或 vLLM multi-tier 的缩小版。

目前最推荐的新主线是：

> **Recoverable, SLO-Aware KV Retrieval for vLLM**
> **面向 vLLM 分层/共享 KV Cache 的可恢复取回与成本边界控制**

它回答一个直接影响业务指标的问题：

> 当共享或外部 KV 已经命中时，系统应当取回 KV，还是直接重算 prefill？如果取回失败、
> 过期或被取消，能否准确定位受影响请求与 block，并安全回退到 recompute？

这个方向应拆成两个独立可交付里程碑：

1. **正确性里程碑：failure bridge。** 将异步 transfer job 的失败映射到请求和
   destination blocks，禁止失败 KV 变为可见，并进入已有的 invalidation/recompute
   路径。这更适合作为第一个 upstream contribution。
2. **性能主线：restore-vs-recompute admission。** 根据 prefix/KV 大小、层级、
   实测传输时间、排队和 prefill 成本决定取回还是重算，并以 TTFT、Goodput@SLO
   和 active decode tail latency 证明收益边界。

failure bridge 单独完成时，是一项不错的上游贡献和工程证据，但不应包装成一个已经有
性能收益的完整项目；admission controller 才提供完整的性能故事、trade-off 和量化空间。

## 二、为什么它匹配真实岗位

公开招聘信息显示，KV Cache 往往不是单独招聘名称，而是综合推理基础设施岗位中的一个
业务方向：

- [百度 2027 校招岗位](https://talent.baidu.com/jobs/detail/GRADUATE/127e69e3-6b3b-440e-83d6-080076768c13)
  同时要求 vLLM/SGLang 推理调度、动态 batching、KV 复用，以及基于 Mooncake 的
  分布式 KV Cache 池化和高速传输，并提到容错、恢复和可观测性。
- [NVIDIA AI Infra 实习岗位](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Solution-Architecture-Intern--AI-Infra---2026_JR2019909)
  在同一 JD 中同时列出 vLLM/SGLang、CUDA，以及 CPU/SSD/远端存储上的多级 KV
  offloading/reuse。
- [阿里巴巴 A-Star](https://campus-talent.alibaba.com/campus/alistar)
  列出大模型推理 KV Cache 系统、存储架构和分布式 KV Cache 网络优化。
- [字节跳动 2027 校招岗位](https://joinbytedance.com/search/7633538176269306117)
  将 KV Cache 系统、调度和分离式执行放在推理基础设施方向内。

这些 JD 的共同信号不是“会部署 Mooncake”，而是：

```text
引擎集成 + 池化/复用 + 传输路径 + 调度决策 + 容错/观测 + 可量化效率
```

推荐主线覆盖其中大部分能力，同时不要求自研 CUDA kernel、RDMA 或多机集群。

## 三、上游核验

### 3.1 多级存储和共享池已经是成熟数据面

- [vLLM KV offloading 文档](https://docs.vllm.ai/en/latest/features/kv_offloading_usage/)
  已支持 CPU primary tier，以及文件系统、对象存储、P2P 等 secondary tiers；
  还支持跨进程共享、自定义 spec 和按请求限制 offload token。
- [vLLM multi-tier RFC](https://github.com/vllm-project/vllm/issues/38260)、
  [FlexKV](https://github.com/taco-project/FlexKV)、
  [Mooncake](https://github.com/kvcache-ai/Mooncake) 和
  [LMCache](https://docs.lmcache.ai/) 已覆盖大量 tier、adapter、promotion、
  eviction、远端传输和共享复用能力。

因此，自研一个新的文件/对象存储 KV backend 很难形成足够清晰的候选人 ownership。
这些系统更适合做项目的数据面依赖和强基线。

### 3.2 最新 vLLM OffloadingConnector 仍有明确的失败桥接缺口

在核验时的 vLLM commit
[`e3c2fc3`](https://github.com/vllm-project/vllm/blob/e3c2fc3b3ca3f41466126cd2aa0b228eb8465844/vllm/distributed/kv_transfer/kv_connector/v1/offloading/worker.py)
中，`OffloadingWorker` 仍然：

- 对同步 `submit_store` / `submit_load` 的返回结果直接 `assert success`；
- 对异步 completion 明确注释当前不支持 job failure，并断言
  `transfer_result.success`。

与此同时，vLLM scheduler 已有
[`invalid_block_ids` 和 recompute 的失败恢复测试](https://github.com/vllm-project/vllm/blob/e3c2fc3b3ca3f41466126cd2aa0b228eb8465844/tests/v1/kv_connector/unit/test_kv_load_failure_recovery.py)，
示例 connector 也展示了
[invalid-block recovery](https://github.com/vllm-project/vllm/blob/e3c2fc3b3ca3f41466126cd2aa0b228eb8465844/examples/disaggregated/kv_load_failure_recovery_offline/load_recovery_example_connector.py)。

所以当前可验证的缺口不是“vLLM 完全不会恢复”，而是：

```text
OffloadingWorker transfer failure
  -> job/request/destination-block attribution
  -> invalid_block_ids
  -> scheduler 已有的 recompute 或显式失败
```

ToolGap-KV 的 D029 判断仍基本成立；但这项 patch 的合理定位是第一个 upstream
contribution，而不是整个求职项目的全部内容。

### 3.3 自适应 KV 策略正在成为活跃方向

[SGLang 2026 高优先级路线图](https://github.com/sgl-project/sglang/issues/21846)
列出了 agentic KV scheduling、session-aware RadixTree、PREFETCH/DEMOTE/PIN hints、
直接 L3 共享池、存储 prefetch 接口、CPU-only simulator 和 cache correctness
canary。这说明问题真实且与业务相关，也说明宽泛的“智能 KV policy”很容易与上游路线
重叠。

个人项目需要选择窄而可证伪的机制：**取回与重算的成本边界，以及失败后的正确性契约。**

## 四、最小项目设计

### 4.1 只拥有一层小而明确的机制

复用 vLLM/Mooncake/FS/CPU tier 的物理数据面，只增加：

```text
external hit
  -> observe(prefix tokens, KV bytes, tier, queue/transfer state)
  -> estimate T_restore and T_recompute
  -> RESTORE | RECOMPUTE
  -> completion success | failure/stale/cancel
  -> visible KV | invalidate + recompute
  -> DecisionTrace + metrics
```

不新增 block manager、不写新的存储引擎、不接管 refcount、不做通用 policy DSL。

### 4.2 Gate F0：动手前必须先证明 seam

固定一个 vLLM commit，在单卡上证明：

1. stock CPU/FS tier 可以稳定运行；
2. 可以强制得到 always-restore 和 recompute-only 两条公平基线；
3. job、request、destination blocks 可以被准确关联；
4. lookup wait、transfer bytes/time 和 fallback reason 可观测；
5. 可以确定性注入 submit failure、async completion failure、cancel/stale completion；
6. 普通请求和受影响请求可在同一测试中区分。

如果这些条件无法在窄 patch 内满足，就停止 adaptive policy：保留 failure
contribution 和共享池评测报告，不扩大 fork。

### 4.3 Admission controller

第一版不需要机器学习或复杂预测：

```text
T_restore =
  observed_lookup_wait
  + estimated_queue_wait
  + KV_bytes / effective_tier_bandwidth
  + fixed_transfer_overhead

T_recompute =
  calibrated_prefill_cost(prefix_tokens, current_load)

restore only if:
  T_restore + safety_margin < T_recompute
```

离线校准可以来自同一模型、同一硬件上的 prefix length × concurrency 曲线。在线只做
常数时间判断。若观测不足或估计过期，默认回退到静态策略或 recompute，而不是增加复杂
控制器。

### 4.4 Failure bridge

需要覆盖：

- 同步 load/store submit 失败；
- 异步 load completion 失败；
- 多 chunk/worker 的 partial failure；
- request cancel 后晚到的 stale completion；
- store 失败不得影响当前请求的正确输出；
- load 失败的 destination blocks 不得被声明有效；
- 失败后 job/fence/block bookkeeping 完整清理；
- 无关请求的输出和调度状态不变。

### 4.5 工程交付：窄范围 KV connector 验收/诊断入口

补充文章强调了源码验收、跨后端集成、CLI 验证和自动排障。这里确实有工程价值，但不应
扩成统一推理网关。项目只需要一个轻量的 `kvdiag`（工作名）：

```text
kvdiag probe   # 版本、connector、tier、共享目录/服务端和关键配置检查
kvdiag smoke   # store -> retrieve -> output equivalence -> cross-process reuse
kvdiag fault   # submit/completion/cancel/stale 的确定性故障矩阵
kvdiag bench   # 固定 manifest，运行 restore/recompute/admission 基线并导出 JSON
```

它的价值是把候选人的 claim 变成可复核证据，而不是创造新的网关控制面。内部直接复用
项目测试和 benchmark runner，不新增 plugin system、通用 Runtime API 或后端注册中心。

## 五、基线、负载和指标

### 基线

1. vLLM stock：hit 后总是 restore；
2. recompute-only：禁止外部 load；
3. static threshold：按 prefix tokens 或 tier 固定阈值；
4. proposed：基于实测成本和排队状态的 admission；
5. failure contract 关闭/开启的 removal test。

### 负载

- 长文档问答或长 system prompt，多请求共享 prefix；
- agent 多轮会话；
- 短且唯一的 prompt，作为负区间；
- 低复用率，使 store 成本无法摊销；
- 人工放慢 FS/CPU tier 或增加 transfer contention；
- 高取消率和 stale completion；
- 同时存在 active decode，验证 prefill/transfer 对 ITL 的干扰。

### 主指标

- p50/p95/p99 TTFT；
- Goodput@TTFT/ITL SLO；
- active decode 的 p95/p99 ITL 或 TPOT。

### 解释指标与正确性护栏

- external hit、实际 restore、fallback 的比例；
- lookup wait、queue wait、transfer bytes/time；
- recompute tokens；
- store/read bandwidth 和队列深度；
- recovery success、output equivalence；
- leaked jobs/fences/blocks；
- fast path 无故障请求的开销。

报告必须展示失败区间：

- 长、热 prefix + 快 CPU tier：restore 应胜出；
- 小 prefix + 慢 tier/排队：recompute 应胜出；
- 低复用：store 可能是净损失；
- 高并发 active decode：吞吐改善不能以 p99 ITL 恶化为代价。

## 六、用户给出的六篇实战文章如何使用

微信公众号页面当前无法可靠抓取正文，以下只根据标题决定其用途，不采用标题中的性能
数字或未读到的实现细节。

| 文章方向 | 建议 |
|---|---|
| 单机 A100 × Mooncake 共享 KV 取回链路 | **复现。** 用于打通数据面、理解分层路径和建立 baseline，不作为核心贡献。 |
| 共享 KV Cache 池收益测量 | **重点吸收实验方法。** 对照其 workload、冷热条件、指标和负区间，再用官方 benchmark 校验。 |
| 跨实例 KV 复用 | **复现 correctness 与 TTFT。** 单卡可用小模型、顺序启动或受控双进程做功能验证，不需要伪装成多 GPU P/D。 |
| 两张 A100 跑 P/D | **阅读，后置验证。** 主线完成后可短租双卡做一次集成证据；不是单卡项目的前置条件。 |
| 8×A100 稠密模型是否 P/D | **学习 trade-off。** 用来解释 P/D 不是必然收益，不作为实现任务。 |
| 8×910B4 的 MTP/并行调优 | **排除出主线。** 更偏投机解码、模型执行、NPU 和多卡并行，不能增强当前 KV runtime ownership。 |

官方可复用的评测工具包括：

- [LMCache benchmark CLI](https://docs.lmcache.ai/cli/bench.html)；
- [LMCache benchmarking guide](https://docs.lmcache.ai/getting_started/benchmarking.html)；
- [LMCache observability metrics](https://docs.lmcache.ai/production/observability/metrics.html)；
- [LMCache deterministic fault injection](https://docs.lmcache.ai/mp/l2_storage/fault_inject.html)；
- [Mooncake storage trace benchmark](https://kvcache-ai.github.io/Mooncake/performance/mooncake/storage-benchmark.html)；
- [Mooncake + vLLM 性能资料](https://kvcache-ai.github.io/Mooncake/performance/vllm/vllm-v1-mooncake-store.html)。

### 6.1 后续六篇补充文章的作用

新增的微信公众号页面仍无法在当前环境可靠读取正文；精确标题搜索也没有找到可验证的
全文镜像。因此下表只评估标题指向的问题，不继承文章结论。

| 补充文章方向 | 对项目的实际作用 | 不应演变成 |
|---|---|---|
| KV Cache 优化方法汇总 | 建立时间、空间、结构三类知识地图，帮助解释为何当前选择 placement/retrieval runtime，而非压缩、稀疏 attention 或模型架构。 | 把量化、压缩、逐出、P/D、投机解码全部塞进同一个项目。 |
| vLLM + LMCache 多级卸载源码验收 | 学习固定版本、沿调用链核验实际能力、保留配置与 raw trace；可作为 `kvdiag smoke` 的参考。 | 仅完成安装和配置后声称“实现多级 KV”。 |
| LMCache & HiCache 多后端外部 KV 复用验收 | 借鉴同一 oracle、同一 workload 下的 connector conformance 方法；项目后期可选择第二个 connector 做可移植性验证。 | 首版同时适配多个 backend，稀释核心机制。 |
| 编排网关 Runtime API 抽象 | 学习如何把 engine capability 和请求选项表达清楚；只抽取本项目需要的 `RetrievalDecision`、`FailureOutcome` 和 trace schema。 | 自研统一 Runtime API、插件平台或框架拼接层。 |
| CLI 验证与自动排障 | 纳入最终证据包：probe、smoke、fault、bench 四个固定命令。 | 做一个只有日志聚合、没有 runtime 机制和量化结果的“运维平台”。 |

当前 [LMCache Quickstart](https://docs.lmcache.ai/getting_started/quickstart.html) 已将
独立 MP 服务作为推荐模式，并明确支持多个 vLLM 实例共享缓存；
[MP 架构文档](https://docs.lmcache.ai/mp/index.html) 还列出了进程隔离、多级存储、
独立扩缩和内置可观测性。最新 release 中继续增加跨版本 connector snapshot、L1/L2
健康指标、adapter 级吞吐、共享缓存和多后端能力
（[LMCache Releases](https://github.com/LMCache/LMCache/releases)）。

这进一步说明：

1. “把 LMCache 跑起来”越来越像标准集成工作，不能独立支撑项目含金量；
2. 版本兼容、conformance、故障归因和性能边界是真实工程问题；
3. 这些验收能力应围绕候选人拥有的 failure/admission 机制服务，而不是取代它。

## 七、六周最小交付

### 第 1 周：基线和 manifest

- 固定 vLLM commit、模型、GPU、容器/依赖；
- 跑通 CPU tier 和单节点 FS/Mooncake；
- 保存 always-restore 与 recompute-only 原始结果。

### 第 2 周：失败审计

- 做 deterministic fake worker/connector；
- 复现 submit、completion、cancel/stale 等失败；
- 输出 job/request/block trace。

### 第 3 周：failure bridge

- 接入 invalidation/recompute；
- 完成 output equivalence、普通请求隔离、cleanup 和 removal tests；
- patch 足够窄时提交 upstream PR。

### 第 4 周：admission v1

- 校准 prefill 和 restore 成本；
- 实现静态阈值及 cost-aware controller；
- 记录 DecisionTrace。

### 第 5 周：矩阵实验

- prefix length、reuse、concurrency、tier speed、cancel rate；
- 同时运行 active decode；
- 每组重复运行并保留原始数据。

### 第 6 周：收口

- ablation、负区间和失败实验；
- 将现有 runner 收口为 `probe/smoke/fault/bench` 四个窄命令；
- 一键复现脚本、架构图、结果表；
- README 明确区分 upstream、candidate-owned code 和 roadmap。

为了控制风险，首版只支持一个模型、一个 GPU、CPU + FS 两层和一个简单控制器。
Mooncake 作为额外集成验证，不应阻塞核心实验。

## 八、候选方向排序

| 方向 | 裁决 | 条件性评分 | 主要原因 |
|---|---:|---:|---|
| 可恢复、SLO-aware KV retrieval | select after F0 | 82/100 | 业务贴合、候选人 ownership 清晰、单卡可量化、有正确性与性能完整故事 |
| KV failure bridge 单项贡献 | do first, not whole project | 72/100 | 上游缺口具体、工程可信，但性能和系统 trade-off 展示不足 |
| KV correctness canary / corruption detector | strong backup | 75/100 | 单卡可做、可靠性价值高，但性能 headline 较弱 |
| 多 connector conformance + 自动诊断 | supporting deliverable | 70/100 | 工程可信度高，但单独做容易退化为测试/集成平台 |
| 单卡 Mooncake 共享池复现与调优 | baseline / reshape | 62/100 | 学习价值高、能出数据，但大部分能力来自上游配置 |
| progressive onloading / HOL blocking | defer | 68/100 | 问题有价值，但 scheduler 改动面和失败风险较大 |
| 自研多级 KV store / LMCache clone | reject | <55/100 | 上游强、范围大、个人 ownership 难讲清 |
| 单卡 P/D、完整 KV-aware router、MTP 多卡调优 | reject now | <50/100 | 资源和实验条件无法支撑可信结论 |

评分是项目选择前的条件性评价，不代表当前已经完成或验证。

## 九、简历表述模板

证据产出后可改写为：

> 针对共享/分层 KV 命中在慢层取回排队时反而拖高 TTFT 的问题，在 pinned vLLM
> OffloadingConnector 中实现 request/job/block 归因、失败回退与基于实测成本的
> restore/recompute admission；在单张 A10、`[模型]`、CPU/FS tier 下，相比 stock
> always-restore 将 p95 TTFT 降低 `[X%]`、Goodput@SLO 提升 `[Y%]`，同时将 active
> decode p99 ITL 回归控制在 `[Z%]`；通过 `[N]` 类确定性故障注入验证无错误 KV
> 可见性、无 job/block 泄漏及无关请求隔离。

在实测完成前，所有数字必须保留为占位符，不使用“实现了性能提升”等完成时表述。

## 十、最终建议

保留 ToolGap-KV 作为历史实验和问题发现过程，但将项目主叙事从 “agent tool wait
policy” 改成 “shared/tiered KV retrieval runtime”。先用三周完成可独立提交的
failure bridge，再以三周完成 restore-vs-recompute 的最小成本控制器和实验矩阵。

这不是追求一个从未有人做过的题目；它追求的是：

```text
真实上游系统
+ 一个候选人拥有的窄机制
+ 正确性与故障证据
+ 明确的性能基线和失败区间
+ 可复现的工程交付
```

这组信号比“部署过共享池”或“做了一个新的 KV 存储后端”更接近 KV Cache 相关团队
在校招面试中真正能验证的工程能力。
