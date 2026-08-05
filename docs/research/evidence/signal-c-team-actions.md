# 信号源 C：目标团队公开技术动作与公司—团队业务重心

> 采集截止：2026-08-04（Asia/Shanghai）  
> 调查边界：推理引擎、LLM serving、KV/prefix cache、推理优化、异构计算；训练侧动作另列。  
> 证据纪律：只记录官方公司/团队页面、官方项目仓库、官方社区文章、论文原文。公开技术动作只能证明“该团队/项目公开投入了什么”，不能单独证明当前校招名额、团队人数、内部全量落地或具体办公地点。

## 1. 口径与证据等级

- **A级**：公司官方产品/技术文档，或明确写出公司/团队归属的官方项目仓库、论文；且动作和日期可核验。
- **B级**：官方社区/生态项目的一手材料，明确记录了公司参与或正式集成；可证明技术关系，不能直接等同于公司内部生产部署或行政归属。
- **C级**：仅为 roadmap、预览能力或归属不完整的线索。本表不据此下强结论。
- “业务方向结论”均为基于公开动作的**有限推断**；性能数字保留为发布方自报结果，不视为独立复现。

技术匹配度仅回答“固定项目叙事与公开技术方向有多重合”，不回答“是否正在招人”：

- **S**：直接覆盖多轮/agent workload、KV/prefix cache 行为测量、淘汰/offload 等主线变量。
- **A**：覆盖多个主线变量，但主要公开场景为分布式或大规模生产环境。
- **B**：有缓存或量化交集，但硬件栈/系统层次明显不同。
- **C**：只有机制词汇交集，运行环境与项目主线差异大。

## 2. 推理侧公开技术动作台账

| ID | 公司 / 团队 / 项目 | 类别 | 日期与公开动作 | 一手来源 | 能支持的业务方向结论 | 强度与边界 |
|---|---|---|---|---|---|---|
| C01 | 阿里云 Tair KVCache 团队 / HiSim | 云厂商 serving、分层 KV cache | 2026-05-22 发布 HiSim：对分布式多级 KV cache 做全生命周期仿真，显式覆盖 multi-turn / agent workload、路由、HBM/DRAM/DISK、prefetch、LRU/LFU/自定义淘汰和 TTFT/TPOT/吞吐量等 SLO，并用于配置 Pareto 搜索。 | [Alibaba Cloud 官方技术博客](https://www.alibabacloud.com/blog/603164) | 可以确认团队公开投入在“工作负载建模 + 测量/仿真驱动的 KV cache 策略评估 + 分层缓存”，与本项目方法论高度重合。 | **A / S**。博客明确写出 Tair KVCache team 及异构计算协作团队；仿真能力不等同于所有策略已在生产启用。 |
| C02 | 阿里云 Tair KVCache | 云厂商托管缓存服务 | 官方 OpenAPI 文档于 2026-06-26 更新，可查询 Tair KVCache inference operator、virtual cluster、cache service 等实例。 | [Alibaba Cloud OpenAPI 文档](https://www.alibabacloud.com/help/en/redis/developer-reference/api-r-kvstore-2015-01-01-describetairkvcacheinferinstances-redis) | 可以确认 KVCache 不只是研究文章，而存在云产品/托管实例的控制面对象；支持“云厂商 serving 存储服务”定位。 | **A / S**。API 存在不能推出使用规模、岗位数量或某项研究能力已经商用。 |
| C03 | AIBrix（最初由 ByteDance 开源；现为社区项目） | 云原生 LLM serving 控制面 | 2026-06-16 发布 v0.7 博文，GitHub release 于 2026-06-18 发布：三个月合入 242 个 PR，覆盖 vLLM/SGLang/TensorRT-LLM、多引擎运行、KV-cache-centric P/D data plane、可组合网关和 HA。 | [AIBrix v0.7 官方博文](https://aibrix.github.io/posts/2026-06-16-v0.7.0-release/)、[GitHub v0.7.0 release](https://github.com/vllm-project/aibrix/releases/tag/v0.7.0)、[项目来源说明](https://aibrix.github.io/posts/2025-02-20-vllm-control-plane/) | 可确认公开方向是多引擎、大规模 serving 控制面和 KV-aware 数据面；AIBrix 官方材料说明其最初由 ByteDance 开源。 | **A（项目）/ B（字节业务归因）/ A**。当前是社区项目，不能把全部当前功能、PR 或部署都归为字节内部成果。 |
| C04 | AIBrix / InfiniStore | 分层 offload、分布式 KV store | 2025-05-21 的 v0.3 发布包含 multi-tier KV offloading、prefix-cache-aware/fairness/load-aware routing、合成 workload 与 benchmark；文章明确称 InfiniStore 是 ByteDance 开发的高性能 RDMA KV cache server。 | [AIBrix v0.3 官方博文](https://aibrix.github.io/posts/2025-05-21-v0.3.0-release/)、[ASPLOS 社区活动及组织者单位](https://aibrix.github.io/community/) | 可确认字节相关公开技术动作覆盖缓存分层、路由、基准工作负载和 RDMA 远端 KV；与本项目的 offload、workload 和行为分析有直接概念重合。 | **A / S**。接近 15 个月；公开文章不能证明 InfiniStore 当前在具体内部产品中的覆盖率。 |
| C05 | 腾讯云 TACO / FlexKV | 分布式 KV store、多级缓存 | 官方仓库明确写明由腾讯云 TACO 团队与社区共同开发。2025-12 至 2026-06 连续公开 GDS SSD→GPU、Mooncake Transfer Engine、TensorRT-LLM、nvCOMP；2026-03 分别合入 NVIDIA Dynamo 和 vLLM 主线。系统拆分 StorageEngine、GlobalCacheEngine、TransferEngine，并公开频率感知 grace-period 淘汰等机制。 | [FlexKV 官方仓库](https://github.com/taco-project/FlexKV)、[vLLM PR #34328](https://github.com/vllm-project/vllm/pull/34328)、[Dynamo PR #5858](https://github.com/ai-dynamo/dynamo/pull/5858) | 可以确认团队持续投入 KV 的存储、全局共享、传输、淘汰和多框架接入，并获得两个上游项目的正式集成。 | **A / S**。合入上游证明接口/实现被接受，不等同于腾讯云内部部署规模或招聘状态。 |
| C06 | 月之暗面 / Kimi / Mooncake | MaaS/模型厂 serving、KVCache-centric 架构 | FAST ’25 论文将 Mooncake 明确描述为 Kimi 的 serving platform：利用 CPU/DRAM/SSD/NIC 资源池构成全局 KV cache，并结合 SLO-aware scheduler；论文报告当时已运行在数千节点并承载每日百亿级 token。 | [USENIX FAST ’25 论文原文](https://www.usenix.org/system/files/fast25-qin.pdf)、[Mooncake 官方仓库](https://github.com/kvcache-ai/Mooncake) | 可以确认 Kimi 的公开 serving 架构长期以 KV cache 解耦、分层资源池和全局调度为核心。 | **A / A**。会议时间为 2025-02-25 至 27，已接近 18 个月窗口；规模数据为论文作者自报快照，不代表 2026-08 当前规模。 |
| C07 | Mooncake Store × vLLM | agentic serving、跨实例 KV 共享 | 2026-05-06 vLLM 官方发布 agentic workload 集成实验：使用 610 条 Codex/SWE-bench Pro traces（中位 33 turns）评估跨实例 KV sharing；文章报告缓存命中率及 TTFT/吞吐改善，并扩展到 60 张 GB200。 | [vLLM 官方博客](https://vllm.ai/blog/2026-05-06-mooncake-store) | 可确认“真实多轮 agent trace + 分布式 KV 共享 + 命中率/TTFT/E2E 测量”已经成为主流 serving 项目的公开评测方法；对本项目的 workload 与指标设计是最直接的一手参照之一。 | **A（集成）/ B（月之暗面当前业务归因）/ S**。这是 vLLM 官方集成实验，不能写成 Moonshot 单方内部生产 benchmark；性能数字未独立复现。 |
| C08 | 百度 PaddlePaddle / FastDeploy | MaaS/全栈推理引擎、多硬件适配 | FastDeploy v2.5.0 于 2026-04-09 发布：包含 W4AFP8、P/D 解耦、动态 C8/RDMA、attention_store/file_store 等 KV stores、Go router 和 request trace/metrics；主仓库同时公开统一 KV transfer、global cache 与多类国产硬件支持。 | [FastDeploy v2.5.0 官方 release](https://github.com/PaddlePaddle/FastDeploy/releases/tag/v2.5.0)、[FastDeploy 官方仓库](https://github.com/PaddlePaddle/FastDeploy)、[百度官方业务页：PaddlePaddle 与 Qianfan](https://ir.baidu.com/baidu-general-business/)、[ERNIE 官方仓库](https://github.com/PaddlePaddle/ERNIE) | 可确认百度公开推理栈覆盖量化、P/D、KV 传输/存储、路由、可观测性及异构硬件，且百度官方将 PaddlePaddle、Qianfan 作为自有 AI 技术/云服务。 | **A（公开技术栈）/ B（FastDeploy 与 Qianfan 具体生产组织映射）/ A**。所选来源没有证明 v2.5 每项能力均由 Qianfan 线上采用。 |
| C09 | 华为昇腾 / MindIE LLM | 自研芯片适配、serving 引擎 | 2026-06-05 发布的 MindIE 1.0.RC3 LLM 开发指南列出 P/D 分离、并行解码、跨会话 Prefix Cache（RadixTree）和 KV Cache INT8 量化；同时写明 Atlas A2 等硬件及与多 LoRA 等能力的兼容边界。 | [华为昇腾官方 MindIE 1.0.RC3 LLM 开发指南 PDF](https://www.hiascend.com/doc_center/source/zh/mindie/10RC3/mindiellm/llmdev/MindIE%201.0.RC3%20LLM%E5%BC%80%E5%8F%91%E6%8C%87%E5%8D%97%2001.pdf) | 可确认昇腾推理栈在做硬件绑定的 prefix reuse、KV 量化和分离式 serving，且工程文档重视功能组合的适用边界。 | **A / B**。这里是 **INT8 KV cache，不是 FP8**；文档不能提供公开 workload/生产规模。 |
| C10 | 阿里巴巴 MNN | 端侧推理 | MNN 3.5.0 于 2026-04-07 发布：覆盖 Vulkan/MUSA/QNN/RISC-V 等后端，新增/更新 TurboQuant TQ3/TQ4 KV cache 量化、多轮 text-level prompt cache、采样流水线和 MNNChat。 | [MNN v3.5.0 官方 release](https://github.com/alibaba/MNN/releases/tag/3.5.0)、[MNN 官方仓库](https://github.com/alibaba/MNN) | 可确认阿里在端侧运行时中也公开投入多轮缓存复用、KV 压缩和跨硬件推理。 | **A / C**。机制词汇重合，但端侧内存、算力、runtime 与 vLLM/SGLang 云端环境差异大，不应包装成同类系统经验。 |
| C11 | DeepSeek 在线推理系统 | 模型/API 厂 serving | 2025 Open Source Week 的在线推理概览公开 P/D 分离、EP32 prefill、EP144 decode、负载均衡与 KV 使用均衡；统计窗口 2025-02-27 12:00 至 02-28 12:00，报告 608B 输入 token 中 342B 命中磁盘 KV cache。 | [DeepSeek 官方 open-infra-index：V3/R1 inference overview](https://github.com/deepseek-ai/open-infra-index/blob/main/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md) | 可以确认 DeepSeek 的公开线上推理架构把磁盘 KV reuse、P/D 与大规模并行负载均衡作为核心组成。 | **A / A**。日期栏采用统计窗口结束日 2025-02-28；页面未单列发布日期。数据为单日一方快照，且接近 18 个月窗口。 |
| C12 | DeepSeek / FlashMLA | CUDA kernel、FP8 KV cache | 官方仓库 2025-09-29 的更新公开 V3.2-Exp sparse attention kernels；覆盖 prefill/decode，并给出 FP8 KV cache 的混合布局和 kernel 接口。 | [FlashMLA 官方仓库](https://github.com/deepseek-ai/FlashMLA) | 可以确认 FP8 KV cache 是真实推理内核方向，不只是 JD 关键词；其收益和约束与模型 attention 布局、数据格式、GPU kernel 强绑定。 | **A / B**。只能支持本项目做“容量/命中率/质量/时延的实验轴”；不能把调用现成能力包装成 CUDA kernel 开发。 |
| C13 | 美团 / LongCat | 模型厂 serving、国产卡适配 | 2026-07-12 官方技术文章公开 LongCat-2.0 及国产卡推理代码：包括 attention absorb/indexer/MLA prolog、KVP KV split、高速逐层 KV 传输、P/D 分离、异步 EPLB、约束解码、多步/MTP 和 BF16/FP8/INT8。 | [美团技术团队官方文章](https://tech.meituan.com/2026/07/12/LongCat-2.0-Open-source.html) | 可确认美团公开投入模型—推理引擎—国产硬件协同，以及 agentic coding 模型的长上下文 serving。 | **A / B**。其 1.6T 模型、专家并行和国产卡协同与单卡项目规模差异极大；只能做方向重合证据。 |
| C14 | NVIDIA / Dynamo | 国际厂商、分布式推理平台 | 2026-03-16 官方发布 Dynamo 1.0 production-ready：覆盖 agentic priority routing/cache pinning、多模态 E/P/D、KV Block Manager、对象存储接入和弹性恢复。 | [NVIDIA 官方 Dynamo 1.0 博客](https://developer.nvidia.com/blog/nvidia-dynamo-1-production-ready/)、[NVIDIA KV cache bottleneck 博客，2025-09-18](https://developer.nvidia.com/blog/?p=106133) | 可确认国际主流 serving 平台同样把 agentic cache affinity、KV 生命周期和外部存储作为控制面/数据面核心问题。 | **A / A**。这是国际参照，不表示中国区当前有对应校招名额；名额必须由信号源 A 验证。 |
| C15 | SGLang / HiCache（生态校验，不归属于单一公司） | 开源 serving 引擎、分层缓存 | 2025-09-10 官方文章发布 HiCache：GPU/CPU/外部存储多级缓存、prefetch/write policy、Mooncake/3FS/NIXL backend 和多轮 workload benchmark；致谢中明确列出 Alibaba Cloud TairKVCache integration team 等参与者。 | [LMSYS/SGLang 官方博客](https://www.lmsys.org/blog/2025-09-10-sglang-hicache/) | 可确认本项目关注的“多轮 workload—缓存层级—策略—命中/SLO”问题已经进入主流开源引擎；也能交叉验证多个公司项目与 SGLang 的生态关系。 | **A（生态技术）/ S**。不能从致谢名单反推个人当前雇主、团队编制或公司内部部署。 |

## 3. 公司—团队业务重心地图（仅由信号源 C 推断）

| 公司 / 公开团队或项目 | 业务重心分类 | 被公开动作直接支持的重心 | 固定项目叙事的技术匹配 | 归因边界 |
|---|---|---|---|---|
| 阿里云 / Tair KVCache | **云厂商 serving / 托管 KV 服务** | 多层 KV cache、仿真/容量规划、路由、淘汰、prefetch、SLO、云上实例控制面 | **S**：workload 生成、行为测量、淘汰/offload 与其公开问题结构几乎同构 | 技术动作和产品对象可确认；当前校招/实习、团队规模、实际客户规模不可由 C 推出 |
| 字节跳动相关公开动作 / AIBrix、InfiniStore | **云原生 serving 控制面 + 分布式 KV 数据面** | 多引擎、P/D、KV-aware routing、多级 offload、RDMA KV server、benchmark | **S**：主线变量高度重合，尤其是多引擎 workload、cache-aware routing、offload | AIBrix 已是社区项目；只能把“最初开源”和文章明确写明的 InfiniStore 归因给字节 |
| 腾讯云 TACO / FlexKV | **云厂商 serving 存储层** | 全局 KV cache、SSD/GDS/RDMA 传输、淘汰、压缩、多框架适配、上游集成 | **S**：淘汰、分层 offload、A/B 指标很贴近；agent workload 公开证据相对少 | 公开仓库证明持续工程动作，不证明内部产品采用率或招聘开放 |
| 月之暗面 / Kimi / Mooncake | **MaaS / 模型厂 serving** | KVCache-centric 分离式架构、全局缓存池、SLO scheduler、agent trace 下跨实例共享 | **S**：多轮 agent prefix reuse 是直接重合点 | FAST 论文可归因于 Kimi；2026 vLLM 联合实验是生态集成，不能全部写成 Moonshot 内部 benchmark |
| 百度 / PaddlePaddle、FastDeploy、Qianfan | **MaaS + 全栈引擎 + 异构硬件** | P/D、KV transfer/store/global cache、FP8 等量化、路由/trace、国产硬件 | **A**：cache/FP8/源码阅读均可对齐，公开栈比本项目范围更宽 | 百度官方能证明产品/项目同属其 AI 栈，但所选材料未证明 FastDeploy v2.5 各功能在线上 Qianfan 的具体采用 |
| 华为昇腾 / MindIE | **自研芯片适配 + serving** | Prefix Cache、KV INT8、P/D、并行解码及硬件/功能兼容边界 | **B**：缓存机制重合，硬件和量化格式差异显著 | 只能说 MindIE/Ascend 栈支持这些功能；不能说本项目的 FP8 结果可直接迁移 |
| DeepSeek / online inference、FlashMLA | **模型/API 厂 serving + 自研 kernel** | 磁盘 KV reuse、P/D/EP 平衡、FP8 KV attention kernel | **A**：缓存 reuse 与 FP8 实验轴有交集；kernel/EP 深度远超单卡项目 | 在线数据是 2025 单日快照；FlashMLA 证明 kernel 方向，不证明普通框架实验等价于 kernel 研发 |
| 美团 / LongCat | **模型厂 serving + 国产卡协同** | agentic coding 模型、KVP/KV 传输、P/D/EPLB、量化、国产卡推理 | **B**：长上下文/KV/量化重合，但系统规模和模型架构差异大 | 公开文章能证明代码/方向；不能推出对应团队当前校招开放 |
| 阿里巴巴 / MNN | **端侧** | 多轮 prompt cache、KV 低比特量化、多后端/移动端 runtime | **C**：只有 cache/量化机制重合，项目运行环境不同 | 不应把端侧动作与阿里云 Tair 混为一个团队或同一类岗位 |
| NVIDIA / Dynamo | **国际厂商分布式推理平台** | agentic cache affinity、KV 生命周期、外部存储、P/D/E、多引擎生态 | **A**：适合作为国际技术基线；项目可对齐问题定义而非规模 | 是否有国内可投岗位、地点和届别必须回到 JD；技术博客不能代替招聘证据 |

### 对公司投递优先级的使用方法

信号源 C 只能给出**技术叙事优先级**，不能直接生成最终投递优先级。与固定项目最能形成“问题—方法—指标”闭环的公开团队集群是：

1. 云厂商 KV/serving 存储层：Tair KVCache、TACO/FlexKV、字节相关的 AIBrix/InfiniStore；
2. 以 agentic / KVCache-centric serving 为核心的模型厂：Mooncake/Kimi；
3. 全栈引擎与 MaaS：FastDeploy/PaddlePaddle；
4. 自研芯片、国产卡和端侧团队的重合主要在机制层，面试叙事必须保留硬件环境差异。

最终排序必须与信号源 A 做交集：只有“当前校招/实习 JD 可投”才能提升投递优先级；社招 JD 和本表技术动作只作为业务方向证据。

## 4. 固定项目组成与信号 C 的对应关系

| 固定项目组成 | 公开动作中的直接参照 | 可据此采用的诚实包装边界 |
|---|---|---|
| 参数化 multi-turn agent workload 生成器 | Tair HiSim；vLLM × Mooncake 的 610 条 Codex/SWE-bench Pro traces；SGLang HiCache multi-turn benchmark | 强调 turn 数、共享前缀、inter-turn delay、会话并发和路由对 cache reuse/SLO 的影响；不要把合成 workload 写成生产流量 |
| 测量驱动的行为分析 | Tair 的 TTFT/TPOT/throughput 与配置 Pareto 搜索；AIBrix benchmark；FastDeploy trace/metrics | 用可复现实验矩阵解释“何时命中、何时失效、代价转移到哪里”；性能结论只限定在单卡/所测版本 |
| 小范围淘汰策略改进 | Tair LRU/LFU/custom policy；FlexKV frequency-aware grace period | 可把策略差异与 workload 条件绑定；不声称发明企业级全局缓存算法 |
| 分层 offload | AIBrix multi-tier KV offloading；FlexKV SSD/GDS/RDMA；HiCache GPU/CPU/external storage；Mooncake 全局池 | 单卡可验证的是本地层级/传输代价与适用边界；不能用 CPU/SSD 实验冒充 RDMA 跨机结果 |
| KV cache FP8 量化实验 | DeepSeek FlashMLA FP8 KV；FastDeploy W4AFP8/FP8 栈；LongCat BF16/FP8/INT8 | 强调容量、命中率、质量、TTFT/吞吐的联合变化；明确区分“调用框架能力”和“自己实现 FP8 CUDA kernel” |
| vLLM/SGLang 源码阅读 | AIBrix 多引擎、FlexKV 上游 vLLM 合入、Mooncake Store × vLLM、SGLang HiCache | 最有价值的源码证据是画清 request→router→block manager/cache connector→transfer/store 的真实路径，并定位自己的最小改动点 |

### 由公开动作得到的关键边界发现

公开市场技术动作并未否定本项目内核，反而共同验证了其问题结构；但企业公开成果大多落在**跨实例、RDMA、远端存储、多 GPU/多节点**。在单张 24GB GPU 上，可信叙事应是：复现和解释多轮 workload 下的缓存行为，做局部策略/本地 offload/FP8 的受控 A/B，并明确哪些结论不能外推到分布式系统。这是证据边界，不是建议更改项目方向。

## 5. 训练侧动作（单独标注，不作为推理岗位能力标尺）

| ID | 公司 / 项目 | 日期与动作 | 一手来源 | 结论与边界 |
|---|---|---|---|---|
| T01 | 阿里巴巴 Taotian Future Living Lab + Alibaba AI Engine / ROLL | 官方仓库明确双方联合开发；2025–2026 更新覆盖异步 agentic RL、vLLM/SGLang rollout backend、FP8 rollout、多角色 Ray 架构，并于 2026-06-16 列出 ROLL Art / OSDI ’26 动作。 | [ROLL 官方仓库](https://github.com/alibaba/ROLL) | **训练 infra**：证明训练/rollout 系统会复用 serving engine 与量化能力；不能把 RL orchestration 要求当作本项目或推理岗硬门槛。 |
| T02 | SGLang × Mooncake TransferEngine | 2026-04-29 发布 RDMA P2P 权重更新，文章报告 Kimi-K2 1T 参数权重同步由 53 秒降至 7.2 秒。 | [LMSYS/SGLang 官方博客](https://www.lmsys.org/blog/2026-04-29-p2p-update/) | **训练—推理耦合**：面向 RL 的权重同步，不是 KV cache reuse；可作为相邻业务方向证据，不能混入 KV 项目成果。性能数字为发布方自报。 |

## 6. 样本与证据缺口

### 样本概况

- 推理侧动作记录：**15 条**；训练/训练—推理耦合动作：**2 条**。
- 公司覆盖：**8 个国内公司集团**（阿里、字节、腾讯、月之暗面、百度、华为、DeepSeek、美团），另含 **NVIDIA** 国际参照和 **SGLang/LMSYS** 生态校验。
- 团队/项目集群：Tair KVCache、AIBrix/InfiniStore、TACO/FlexKV、Kimi/Mooncake、FastDeploy/PaddlePaddle、MindIE、MNN、DeepSeek online inference/FlashMLA、LongCat、Dynamo；另列 ROLL 与 SGLang×Mooncake 训练侧动作。
- 近 12 个月（2025-08-04 后）占推理记录的大多数；AIBrix v0.3、Mooncake FAST ’25、DeepSeek 2025-02 快照作为 12–18 个月内的架构基线，已单独标明日期和时效边界。

### 证据缺口与不可推出项

1. **公开开源动作不等于招聘开放。** 是否有 2026 秋招/2027 届或日常实习、工作地点和 HC，必须由信号源 A 的当前 JD 证明。
2. **社区归因风险。** AIBrix 当前是社区项目；SGLang、vLLM 的集成和致谢不能自动归为某一家公司的内部成果，也不能凭个人 PR 资料猜测雇主。
3. **组织映射不完整。** Mooncake 的平台归属在论文中明确，但行政团队名未公开；所选证据也没有完整证明 FastDeploy 每项能力与 Qianfan 生产运行时的组织/部署映射。
4. **内部生产规模缺失。** FlexKV、AIBrix/InfiniStore、MindIE 等材料能证明功能和工程方向，但缺少一致口径的内部采用率、流量和 SLO 数据。
5. **公司覆盖偏差。** 未找到并纳入同等强度、近 12–18 个月、可明确归因的一手材料的公司（例如快手、小红书、京东及部分芯片/云团队）不能据此判定“没有相关团队”；只是本轮证据缺口。
6. **发布偏差。** 样本天然偏向愿意开源、发论文或写技术博客的团队；低公开度团队会被系统性低估。
7. **性能数字不可横比。** 论文/博客的硬件、模型、workload、版本和规模不同，不能把 3.8×、46×、40 GiB/s 等宣传数字直接横向排名，也不能作为个人项目预期值。
8. **FP8 不是单一变量。** FlashMLA、FastDeploy、LongCat 所称 FP8 与 MindIE 的 INT8、MNN 的 TQ3/TQ4 在数据格式、attention 布局、kernel 和硬件上不同；只能证明量化是业务动作，不能合并成同一实验结论。

## 7. 可供总报告直接引用的结论

1. 2025-08 至 2026-08 的一手公开动作显示，国内推理团队的 KV 工作已经从“单实例 prefix cache”扩展到 workload-aware routing、跨实例共享、多级存储、P/D 数据面、缓存传输和量化；但这些动作分别属于不同系统层，不能仅凭关键词视为同一种经验。
2. 对固定个人项目而言，最强业务重合不是“实现一个企业级 KV store”，而是用多轮 agent workload 和可解释指标回答 cache reuse 何时成立、何时失效，以及淘汰/offload/量化如何改变容量—命中—质量—时延的权衡。
3. 阿里云 Tair、腾讯云 TACO/FlexKV、字节相关 AIBrix/InfiniStore、Kimi/Mooncake 的公开问题结构与项目主线最接近；百度 FastDeploy 是全栈引擎/异构硬件方向的强次级匹配。该判断只用于项目叙事匹配，投递可行性仍取决于当前校招/实习 JD。
4. 华为 MindIE、DeepSeek FlashMLA、美团 LongCat 和阿里 MNN 能支持量化、缓存和硬件适配的重要性，但不能据此要求单卡、8–10 周项目扩展到 CUDA kernel、专家并行、国产芯片适配或端侧 runtime。

