# 2026 AI Infra 推理方向校招岗位匹配度调查

> 采集截点：2026-08-04（Asia/Shanghai）
>
> **路由状态（2026-08-08）：**本文件是岗位市场证据，不是当前工程计划。其早期“vLLM/SGLang 二选一、
> local eviction/offload、FP8 轴”的项目建议已经被 [PROJECT_PLAN.md](../project/PROJECT_PLAN.md) 的
> 单一 shared-L3 write-admission scope 取代；不得据此恢复这些被排除项或升级实现/性能 claim。
>
> 固定项目内核：在 vLLM 或 SGLang 中选定一个框架，研究多轮 Agent prefix/KV cache 复用行为，做小范围策略改进、A/B 对照与 FP8 KV cache 实验轴；单张 24GB GPU，8–10 周。

## 结论先行

1. **在本次目的性样本中，没有发现项目与 serving/cache-runtime 子方向的重大错配；该结论不能外推到全部推理引擎岗位。** 它对“LLM serving / KV cache / 推理存储与调度”是高相关项目，对“CUDA 算子 / 编译器 / 自研芯片适配”则不是。当前岗位名称经常把这两类工作都写成“推理引擎/推理优化”，因此主要风险是**岗位 title 错配**，而不是项目方向错配。
2. **团队公开动作更强地证明了这个业务问题真实存在，但不直接证明它能提高简历通过率。** 阿里云 Tair KVCache HiSim 已公开把多轮/Agent workload、真实 trace、cache-aware routing、KV 加载/淘汰、分层配置和 TTFT/TPOT/吞吐评估放到同一套工作流里；AIBrix、FlexKV、Mooncake 也持续推进分布式 KV、分层 offload、路由与异构 serving。这要求项目靠真实框架版本、可复现实验、明确 owned patch、强基线和失败区间成立，而不是依赖“题目新颖”。
3. **JD 负责筛关键词，面试负责拆穿关键词。** vLLM/SGLang、KV cache、量化、CUDA、分布式等在扩展 JD 样本中反复出现；P/D、投机解码、RDMA 则主要集中在部分专项岗位和业务动作，不能称普遍高频。在这组面经里重复出现更多的是项目逐层追问、精确指标、瓶颈定位、基础机制、手写代码，以及“为什么这样做、何时失效、换一个约束会怎样”。所以包装重点不应是堆术语，而应是“问题—基线—测量—改动—收益—代价—失效条件”的闭环。
4. **FP8 KV cache 是合理的附带轴，但收益是条件性的。** 它天然命中“低精度/量化/KV 容量”词，但不能在实验前写成“FP8 提升命中率”：容量扩大只有在 KV 压力导致淘汰、且具体 GPU/框架后端支持该路径时，才可能转化为更高命中或更低延迟。[vLLM 2026-04-22 的官方验证](https://github.com/vllm-project/vllm-project.github.io/blob/main/_posts/2026-04-22-fp8-kvcache.md) 也只覆盖 Hopper/Blackwell 路径，并明确记录长上下文精度、hybrid/sliding-window layer 与 `head_dim=256` 的 prefill 回归边界；消费级 24GB GPU 不能据此假定支持或等收益。硬件兼容、精度和 prefill/decode 回归都必须作为 gate。
5. **8–10 周内最有价值的增量不是扩大系统边界，而是提高证据密度。** 主线应是测量闭环加**至多一个**主要策略改动；FP8 是用户固定的附带轴，但先做 capability gate；offload 只有在复用成熟路径且主线提前闭环时才进入，不默认与淘汰策略叠加。自研 CUDA 算子、MLIR、RDMA、多机 P/D 或自建分布式 KV store 应明确不做。

综合判定：**固定内核继续成立；投递与叙事应定位为 serving/cache runtime 的测量与策略项目，而不是宣称覆盖整个推理引擎栈。**

## 1. 研究口径与样本

- **采集截点：**2026-08-04；“近 6 个月”定义为 2026-02-04 之后发布或刷新。
- **信号源严格分开：**A 为岗位 JD（筛选层），B 为第一人称或可辨认具体轮次的面经（验证层），C 为团队官方博客、仓库、演讲、论文（业务方向层）。C 不反推开放岗位，社招 JD 不反推学生能力门槛。
- **岗位边界：**只纳入推理引擎、推理优化、LLM serving、异构计算、明确涉及推理侧的 AI Infra；训练/推理混合岗单列。纯算法、RAG、Agent 应用、业务后端不纳入。
- **JD 去重：**同公司、同团队、同文本仅保留一条，城市镜像不重复计数。特殊博士项目/人才计划单列，不进入常规校招基线。
- **关键词计数：**`D` 是职责/业务方向，`H` 是所有候选人明确必备，`H*` 是“满足 A/B/C 任一项”中的可选硬路径，`B` 是加分项；不能把职责自动升级成门槛。每份 JD 在**同一分类**内对一个主题最多计一次，但 H/H*/B 是非互斥标签：例如 Python 是 H、C++ 是 B 时，归一化的“编程语言”行会同时贡献 H 与 B。因此三项之和可能大于 N，不能当并集岗位数。社招编码只描述文本位置，不是对用户的能力标尺。
- **面经计数：**以一个可辨认的“同一候选人 × 同一公司 × 同一岗位申请”记录为单位；它可能包含一轮或多轮，不保证是该申请的全部流程。某主题在该申请记录中出现至少一次即记 1，不按问题数量计数。主频率样本只使用可辨认公司/方向/轮次与具体问题的正文；旧于 2025 年或来源转述的内容只作趋势，不进入主频率。
- **解释边界：**这是一组目的性样本，不是全量招聘数据库。百分比只表示本样本覆盖率，不等于市场份额或真实面试概率。
- **对用户两份 2026-07-28 文档的使用：**只作为候选索引与历史判断输入；本报告重新打开可访问的原始 JD/技术页面并记录 2026-08-04 状态，没有把旧文中的“当时存在”直接写成“当前开放”。旧项目方向文档与本轮固定内核冲突的部分不继承。

## 2. 信号源 A：岗位 JD

### 2.1 去重后的岗位账本

| 样本层 | N | 状态与用途 |
|---|---:|---|
| 常规校招 | 7 | 百度 5、小米 1、小红书 1；当前开放 6，近 6 个月截止 1 |
| 常规实习 | 11 | NVIDIA 3、字节 1、快手 2、卓识 1、阿里芯片框架 1、PDD 1、MiniMax 1、SmartX 1；当前开放 4、有明确日期的近期截止 4、日期未验证但页面已结束 2、状态冲突 1 |
| 特殊人才计划 | 6 | 快Star 3、阿里星 3；证明专项方向，不并入普通校招门槛 |
| 国内社招业务方向 | 4 | 百度 2、华为 1、美团 1；只用于业务方向，不拿年限/资深要求评价学生 |
| **总计** | **28** | 20 条有近 6 个月明确日期；1 条开始日期较旧、在采集日前 4 天截止；7 条精确发布日期未验证 |

常规学生岗合计 N=18。这个扩展集合回答“当前可见页面与近一轮窗口写过什么”，其中 MiniMax、SmartX 的起止日期未验证，**不能支持近 6 个月判断**；判断“此刻能不能投”时只能看状态为当前开放的 10 条。校招仍明显受百度文本支配（7 条中 5 条），因此所有频率都写成“本样本 x/N”，不外推为国内市场份额。

训练/训推混合岗位单独标注如下：百度 J101228 是训练 infra（含 rollout serving），PDD I9 是训练为主但明确包含在线推理，百度 J100730/J101236/J100724 与小红书 C7 是训推混合。它们进入“推理职责明确”的扩展矩阵，但不用于声称样本都是纯 serving。若只移除最明确的训练 infra J101228，常规学生岗为 N=17；关键方向仍为推理优化 D=17/17、KV D=7/17、CUDA/GPU D=15/17，主结论不变。

NVIDIA I1/I2 的 title 是 Solution Architecture，本报告仍把它们纳入扩展实习矩阵，是因为原文职责直接包含 vLLM/SGLang 社区开发、推理瓶颈优化、kernel 与 KV offload/reuse；这是一种**按职责纳入的技术相邻岗**，不等于核心引擎研发 title。若严格排除两条 SA，常规学生岗 N=16：编程 H=15/16、系统基础 H=10/16、推理优化 D=16/16、KV D=7/16、CUDA/GPU D=14/16，主排序仍不变。

完整逐条台账见附录 A；下面先列当前窗口与项目关系最强或最能说明岗位分层的记录：

| 公司/团队 | 岗位 | 类型/状态 | 日期 | 原始链接 | 技术词与边界 |
|---|---|---|---|---|---|
| 百度/基座研发 | AI Infra 推理工程师 J101235 | 校招/当前开放 | 2026-07-21 | [官方 JD](https://talent.baidu.com/jobs/detail/GRADUATE/7753cdb4-70b0-462b-a634-ee53818c7c9a) | 批调度、分离部署、cache 池化/传输；同时硬看 CUDA/CUTLASS/CuTe/Triton，属于 engine/kernel 重岗 |
| 百度/团队未披露 | AI Infra 工程师 J100730 | 校招/当前开放 | 2026-07-21 | [官方 JD](https://talent.baidu.com/jobs/detail/GRADUATE/59d9bb54-46e5-4d3c-aa26-e59b1dea387a) | 推理引擎、INT8/FP16、KV、显存；C++/Python、分布式、量化/推理/内存基础 |
| 百度/基座研发 | AI Infra 强化学习工程师 J101228 | 校招/当前开放；训练 infra 单列 | 2026-07-21 | [官方 JD](https://talent.baidu.com/jobs/detail/GRADUATE/127e69e3-6b3b-440e-83d6-080076768c13) | rollout 调度、dynamic batching、KV reuse、Mooncake、K8s/Ray；不是纯 serving 岗 |
| 百度/团队未披露 | AI 异构计算工程师 J101236 | 校招/当前开放 | 2026-07-21 | [官方 JD](https://talent.baidu.com/jobs/detail/GRADUATE/f0c02346-05c2-4742-aa52-2a8d50cf0792) | P/D、KV、投机解码、量化、TTFT；CUDA/算子/vLLM/SGLang 明确硬要求 |
| 小红书/中台 AI Infra | 训练/压缩/推理 Infra 研发 17015 | 校招/当前开放；发布日期未验证 | 采集 2026-08-04 | [官方 JD](https://job.xiaohongshu.com/campus/position/17015?referer_code=C09UF8OCSZ4M) | RedServing/DirectLLM、调度、监控、量化、异构、通信/CUDA；训推混合且要求面宽 |
| 小米/MiMo | 大模型推理框架开发 | 校招/近期截止 | 2026-03-12—06-19 | [牛客 JD](https://www.nowcoder.com/jobs/detail/440140) | vLLM/SGLang、性能监控与 CUDA kernel；说明框架岗常与算子并列 |
| NVIDIA/Solution Architecture | AI Infra Intern JR2019909 | 实习/当前开放，技术相邻岗 | 约 2026-06-16；官方日期非静态字段 | [官方 JD](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Solution-Architecture-Intern--AI-Infra---2026_JR2019909)、[日期镜像](https://www.iagora.com/work/en/offer/internship-work-from-home-construction/6197696) | SGLang/vLLM、GEMM/attention、FlexKV 多级 offload/reuse、分布式性能；项目高度相关但岗位面宽 |
| 字节/基础设施计算 | AI Infra 后端开发实习生-计算 | 实习/当前开放；精确发布日期未验证 | 采集 2026-08-04 | [牛客可读 JD](https://www.nowcoder.com/jobs/detail/431803) | 广义 IaaS AI Infra；框架、GPU、高性能网络是加分，不应与 Seed/KV 团队合并归因 |
| PDD/云弧计划 | AI Infra 研发实习 | 实习/当前开放；硕博 | 2026-07-20—12-31 | [牛客 JD](https://www.nowcoder.com/jobs/detail/454371) | 训推混合、调度、通信、量化、在线推理；因学历要求不列用户当前 P0 |
| 快手/Model Serving | Model Serving 留用实习 | 实习/近期截止 | 2026-03-25—07-02 | [牛客 JD](https://www.nowcoder.com/jobs/detail/442015) | 分布式 KV 传输/池、prefix hit、预取、显存复用、资源调度；项目叙事直接匹配 |
| 快手/快Star | 基础大模型推理引擎 452683 | 特殊校招/当前开放 | 2026-07-07—12-31 | [牛客 JD](https://www.nowcoder.com/jobs/detail/452683) | engine、异构、量化/蒸馏、并行；vLLM/SGLang/TRT-LLM 与 CUDA/Triton 是加分而非统一硬门槛 |
| 阿里/阿里星 | KV Cache 全栈演进 446421 | 特殊实习/状态冲突；博士 | 2026-04-24；页面状态矛盾 | [牛客 JD](https://www.nowcoder.com/jobs/detail/446421) | 多级池、预取、调度、量化/压缩、ROI；证明业务方向，不作为本科能力标尺 |
| 百度/ACG MaaS | 大模型推理工程师 J101025 | 社招/业务证据 | 2026-07-21 | [官方 JD](https://talent.baidu.com/jobs/detail/SOCIAL/336e82e0-307f-49f1-ae1f-4831fb9d570e) | batching、KV、热加载、扩缩容、隔离、熔断、SLA、压测与成本；只用于方向证据 |
| 华为/OTT2 系统部 | requisition 28183（标题未验证） | 社招/业务证据 | 采集 2026-08-04；发布日期未验证 | [官方 JD](https://career.huawei.com/reccampportal/portal5/social-recruitment-detail.html?dataSource=1&jobId=28183) | 国产算力、量化/KV 压缩、投机、P/D、MoE、推理服务；硬件栈不同 |

### 2.2 关键词频率矩阵

#### A. 任职要求：`H/H*/B`

`H`=所有候选人明确必备，`H*`=跨主题的可选硬路径，`B`=仅加分。单元格为 `H/H*/B`；三列是非互斥标签，不能相加后除以 N。社招列只描述文本，不用来评价用户。

| 归一化关键词 | 常规校招 N=7 | 常规实习 N=11 | 快Star N=3 | 阿里星 N=3 | 国内社招 N=4 |
|---|---:|---:|---:|---:|---:|
| 编程语言/数据结构 | 7/0/0 | 10/0/2 | 3/0/0 | 2/0/0 | 4/0/0 |
| Linux/OS/系统基础 | 3/0/0 | 9/0/0 | 2/0/0 | 2/0/0 | 4/0/0 |
| vLLM/SGLang/TRT-LLM 等引擎 | 2/1/3 | 2/2/4 | 1/1/1 | 1/0/1 | 4/0/0 |
| PyTorch/TensorFlow 等 DL 框架 | 4/1/1 | 2/2/2 | 0/1/0 | 2/0/0 | 3/0/0 |
| Transformer/LLM 推理原理 | 2/0/0 | 3/0/0 | 0/0/0 | 2/0/0 | 3/0/0 |
| 推理优化实战 | 4/0/1 | 3/0/1 | 1/0/0 | 2/0/1 | 3/0/1 |
| Profiling/benchmark/性能建模 | 2/0/0 | 0/0/1 | 1/0/0 | 0/0/0 | 3/0/0 |
| KV/Prefix Cache/offload | 1/0/1 | 0/0/2 | 0/0/0 | 0/0/1 | 2/0/1 |
| 量化/模型压缩 | 2/0/1 | 0/0/1 | 0/0/1 | 1/0/0 | 3/0/1 |
| 调度/batching/serving | 1/1/1 | 1/0/0 | 0/0/0 | 0/0/0 | 1/0/2 |
| 分布式/并行/通信 | 4/2/0 | 2/0/5 | 1/0/0 | 3/0/0 | 3/0/1 |
| CUDA/GPU/kernel | 4/0/3 | 1/0/5 | 0/0/3 | 1/0/1 | 2/0/1 |
| Docker/K8s/Ray/云原生 | 0/0/1 | 2/0/1 | 0/0/0 | 0/0/1 | 2/0/0 |
| 异构硬件 | 1/0/0 | 0/0/3 | 0/0/0 | 0/0/0 | 1/0/2 |
| 投机解码 | 0/0/1 | 0/0/0 | 0/0/0 | 0/0/0 | 1/0/0 |
| 编译器/MLIR/TVM/图优化 | 0/1/1 | 0/0/0 | 0/0/2 | 0/0/1 | 0/0/0 |
| RDMA/NVLink/GPU Direct | 1/0/0 | 0/0/1 | 0/0/0 | 0/0/2 | 0/0/1 |
| SLA/可靠性/可观测性 | 0/0/0 | 0/0/1 | 0/0/0 | 0/0/0 | 1/0/1 |
| 开源贡献 | 0/1/3 | 0/0/1 | 0/0/1 | 0/0/2 | 0/0/0 |
| 顶会论文 | 0/1/2 | 0/0/2 | 0/0/2 | 0/0/2 | 0/0/0 |

#### B. 工作职责/业务方向：`D`

| 归一化关键词 | 常规校招 N=7 | 常规实习 N=11 | 快Star N=3 | 阿里星 N=3 | 国内社招 N=4 |
|---|---:|---:|---:|---:|---:|
| 推理引擎/框架 | 7 | 10 | 2 | 3 | 4 |
| 推理优化 | 7 | 11 | 3 | 3 | 4 |
| Profiling/benchmark | 2 | 8 | 0 | 2 | 4 |
| KV/Prefix Cache/offload | 4 | 4 | 0 | 3 | 3 |
| 量化/压缩 | 3 | 3 | 2 | 2 | 4 |
| 调度/batching/serving | 4 | 5 | 1 | 1 | 3 |
| 分布式/并行/通信 | 6 | 7 | 2 | 3 | 3 |
| CUDA/GPU/kernel | 6 | 9 | 3 | 2 | 4 |
| Docker/K8s/云原生 | 2 | 5 | 0 | 0 | 2 |
| 异构硬件 | 4 | 5 | 2 | 1 | 3 |
| 投机解码 | 1 | 2 | 0 | 1 | 1 |
| 编译/图优化 | 2 | 2 | 2 | 0 | 0 |
| RDMA/高性能网络 | 1 | 1 | 0 | 1 | 1 |
| SLA/可靠性/可观测性 | 4 | 5 | 0 | 2 | 3 |
| 开源框架研发 | 0 | 1 | 0 | 2 | 0 |

#### C. 只基于信号 A 可下的结论

1. 常规学生岗 N=18 中，KV/Prefix/offload 是 8/18 条的工作内容，但只有 1/18 把它列为所有人必备的 H，另有 3/18 为 B。它更像真实业务方向和差异化项目证据，而非统一筛选门槛。
2. 最稳定的明确筛选底座仍是编程与系统基础：编程/数据结构 H=17/18，Linux/系统 H=12/18。推理引擎是 H=4、H*=3、B=7；把 H* 混进 H 会夸大“人人都必须深懂某个框架”的程度。
3. 推理优化是 D=18/18；分布式/并行/通信是 D=13/18、H=6、H*=2、B=5。职责重复出现不等于每个岗位以同样深度筛选。
4. CUDA 是明显的岗位分层器：D=15/18、H=5、B=8。纯引擎/异构/算子岗更容易写成 H，serving/backend 岗更常放在 B 或职责背景。
5. 量化 D=6、H=2、B=2；投机解码 D=3、H=0、B=1；可靠性/可观测 D=9、H=0、B=1。Profiling 是 D=10，但 H=2、B=1：测量常被工作默认承接，却不一定单独写成筛选词。
6. 阿里星 3 条中 2 条明确博士，快Star 3 条覆盖 kernel、compiler 与基础引擎；两类特殊计划能证明公司投入，不能代替普通校招画像。

## 3. 信号源 B：真实面经

### 3.1 面经账本

主样本是 14 个“同一候选人 × 同一公司 × 同一岗位申请”的可辨认申请流程/轮次记录，其中近 6 个月 6 个；它们不一定覆盖该申请的所有轮次。记录只来自 6 篇作者帖，且 2025 年有 7 个流程来自同一候选人；因此下面是**记录到的流程出现率**，不是 14 个独立候选人的市场概率。

| ID | 公司/岗位方向 | 类型 | 面试/发布日期 | 真实来源 | 可核对的实际问题摘要 |
|---|---|---|---|---|---|
| B01 | 百度 Summer Camp，大模型平台策略推理优化 J98029 | 实习 | 面试 2026-04-02；文 04-08 | [知乎第一人称汇总](https://zhuanlan.zhihu.com/p/2023015325172507141) | 项目创新/PR、PagedAttention、CUDA Graph、TP attention、chunked prefill、all-reduce、FlashAttention、prefill/decode、投机解码，Triton 手写 attention |
| B02 | 快手，大模型推理优化留用实习 | 实习 | 面试 2026-04-02；文 04-08 | [同一第一人称汇总](https://zhuanlan.zhihu.com/p/2023015325172507141) | softmax、bank conflict、FA v1/v2、column parallel、变长序列、speculative sampling、算法题 |
| B03 | 吉利研究院座舱，异构推理 | 实习 | 面试 2026-04-02；文 04-08 | [同一第一人称汇总](https://zhuanlan.zhihu.com/p/2023015325172507141) | JAX/PyTorch 精度对齐、TPU HBM/SRAM、部署、fusion、变长限制、TPU/GPU、时间—精度权衡 |
| B04 | 百度文心一言，AI Infra | 实习 | 发布 2026-05-02；平台只显月日 | [牛客正文](https://www.nowcoder.com/feed/main/detail/ebc23c1010144143a69654b465272226?urlSource=home-api) | KV/continuous batching、vLLM、TP、P/D 与 KV 传输、KV 容量、memory-bound、prefix/block manager、chunked prefill、GPU 层次、C++/算法题 |
| B05 | 快手，AI Infra 一面 | 实习 | 发布 2026-03-04；年份由页面上下文锚定 | [牛客正文](https://www.nowcoder.com/feed/main/detail/b77d789783d04541ab39972a59832bb2) | 模型显存估算、量化/FA 实测、TensorRT、vLLM/PagedAttention、FLOPs、PyTorch GPU 管理、训练/推理差异、算法题 |
| B06 | 华为海思图灵，AI Infra/算子 | 实习 | 文 2026-07-09 | [牛客第一人称](https://www.nowcoder.com/discuss/899808901892239360?sourceSSR=dynamic) | int/指针/sizeof、栈堆、简历项目、链表；这一轮没有可确认的推理/CUDA 深问 |
| B07 | 美团，大模型推理引擎研发 | 实习 | 面试 2025-03-20/25；文 04-17 | [2025 春招第一人称汇总](https://www.nowcoder.com/discuss/736868736837173248?sourceSSR=post) | 实习深挖、Attention/FA、CUDA memory、算子如何测/保精度/判 compute-bound、C++、MHA；反问得知团队实际偏分布式预训练 |
| B08 | 蚂蚁，AI 金融智能大模型系统 | 实习 | 面试 2025-03-14/17；文 04-17 | [同一 2025 汇总](https://www.nowcoder.com/discuss/736868736837173248?sourceSSR=post) | 两轮深挖推理优化项目、A/B 如何设计、优化点如何定位、量化/SFT/DPO、平台端到端瓶颈 |
| B09 | 蚂蚁基础平台，离线推理引擎 | 实习 | 面试 2025-04-09/14；文 04-17 | [同一 2025 汇总](https://www.nowcoder.com/discuss/736868736837173248?sourceSSR=post) | DeepSeek FP8 vs Qwen BF16、TRT-LLM vs vLLM、continuous batching、prefix cache、GPU memory manager、量化/算子、PagedAttention |
| B10 | 阿里国际，AI Business 大模型平台 | 实习 | 面试 2025-04-11/16；文 04-17 | [同一 2025 汇总](https://www.nowcoder.com/discuss/736868736837173248?sourceSSR=post) | coalescing/bank conflict、CPU/GPU cache、非对称量化、Tensor Core、BF16、推理瓶颈、NVLink、CUDA Softmax、C++ |
| B11 | 快手容器云，AI Infra | 实习 | 面试 2025-02-24/28；文 04-17 | [同一 2025 汇总](https://www.nowcoder.com/discuss/736868736837173248?sourceSSR=post) | 流量调度、分布式训练、GPU 架构、prefix KV/compression、Raft、精确优化数值、量化逻辑、冲突指标、硬件特化是否值得 |
| B12 | 淘天基础平台，深度学习引擎 | 实习 | 面试 2025-03-28；文 04-17 | [同一 2025 汇总](https://www.nowcoder.com/discuss/736868736837173248?sourceSSR=post) | 约 40 分钟持续深挖算子项目与 C++/CUDA 实现；团队工作偏端侧算子加速 |
| B13 | 百度，大模型推理研发 | 实习 | 面试 2025-03-27/31；文 04-17 | [同一 2025 汇总](https://www.nowcoder.com/discuss/736868736837173248?sourceSSR=post) | DeepSeek、Attention、CUDA 手写 all-reduce、矩阵乘、算法题；工作涉及昆仑芯框架 |
| B14 | 百度，大模型推理研发暑期实习 | 实习 | 发布 2025-05-12 | [牛客独立第一人称](https://www.nowcoder.com/feed/main/detail/15b60a5204564b12baee4ff3d2a6487a) | 项目方法、更高压缩率、GPU 并行、TP/通信、降低 KV、MLA、量化、Linux 数据传输、FA/局部性、三道代码题 |

边界提醒：B06 表明“AI Infra/算子”岗位某一轮可能只问 C/C++；B07 表明 title 写“推理引擎”，实际团队也可能偏预训练。面试反问是核验团队真实工作的必要动作。

### 3.2 面试主题频率

| 主题 | 扩展样本 N=14 | 近 6 个月 N=6 | 命中流程 ID | 只允许下的结论 |
|---|---:|---:|---|---|
| KV / prefix cache | 6（43%） | 3（50%） | B01、B04、B05、B09、B11、B14 | 明确高价值，但不是“每场必问” |
| 调度/batching/变长请求 | 5（36%） | 3（50%） | B01、B02、B04、B09、B11 | 常与 KV、TTFT/吞吐一起验证；B02 的证据是变长序列处理，故使用宽主题名 |
| 量化 | 6（43%） | 1（17%） | B05、B08、B09、B10、B11、B14 | 2025 样本更集中，近 6 月不足以称高频 |
| 投机解码/采样 | 2（14%） | 2（33%） | B01、B02 | 本样本只观察到两条；B02 是 speculative sampling，仍不足以称普遍高频 |
| 算子/GPU 性能模型 | 13（93%） | 5（83%） | B01–B05、B07–B14 | 本样本最稳定，但受到同一 CUDA 背景候选人多投的显著影响；不能推出项目必须改为算子 |
| 分布式/并行/通信 | 7（50%） | 3（50%） | B01、B02、B04、B10、B11、B13、B14 | B03 只有异构/设备问题，不再计入；问机制不等于必须做多机实现 |
| 系统架构/性能诊断 | 10（71%） | 4（67%） | B01、B03、B04、B05、B07、B08、B09、B10、B11、B14 | 瓶颈、P/D、内存、部署与 A/B 比背名词更稳定 |
| 手写代码 | 10（71%） | 5（83%） | B01、B02、B04、B05、B06、B07、B10、B11、B13、B14 | 算法、C++、CUDA/Triton 或核心伪码并存 |
| 框架机制/源码 | 8（57%） | 4（67%） | B01、B03、B04、B05、B07、B09、B10、B11 | “会调用 API”通常不够 |
| 严格项目拷打 | 9（64%） | 3（50%） | B01、B03、B05、B07、B08、B09、B11、B12、B14 | 正文可确认的下界；不是录用概率 |
| 严格条件/边界问题 | 9（64%） | 4（67%） | B01、B02、B03、B05、B07、B09、B10、B11、B14 | 本样本稳定重复出现的验证方式 |

B07 的岗位 title 是“推理引擎”，但候选人反问得到的实际业务偏分布式预训练，因此把它作为 title 错配边界行。若从纯推理验证频率中移除 B07，N=13：算子/GPU 12/13、系统诊断 9/13、手写代码 9/13、框架机制 7/13、项目拷打与边界问题各 8/13；核心排序不反转。

### 3.3 “项目拷打”与边界性问题

严格口径下，“只让你介绍项目”不算拷打，“解释 X”不自动算边界问题。9/14 个流程出现了至少一种可审计追问，常见链条是：

> 你做了什么 → 为什么这是瓶颈 → 基线是什么 → 怎么测 → 数字是否可信 → 代码/数据路径在哪里 → 换 workload、dtype、硬件、并行方式后是否还成立 → 失败时怎么办。

| 典型模式 | 面经实例 | 固定项目必须准备的证据 |
|---|---|---|
| ownership/源码路径 | B01：修过什么 bug/PR，再追 PagedAttention/TP/手写核心算子 | 上游已有、你只调用、你的埋点、你的策略 diff 四者分开 |
| 实测效果审计 | B05/B11：量化/FA 实测多少、TRT-LLM 精确收益 | 环境、基线、原始结果、重复与波动，禁止“大幅提升” |
| A/B 与瓶颈归因 | B07/B08：怎么测、怎么保正确、怎么判瓶颈、A/B 怎么设计 | 同 workload/warmup/资源限制，先证明瓶颈再证明改动命中 |
| 系统设计迁移 | B09：GPU memory manager、FP8/BF16、batch/切分维度 | 能画资源/数据路径；不要求把认知题并入项目实现 |
| 改变约束找失效点 | B03/B14：换设备、变长、更高压缩率、多卡后是否成立 | 至少一个明确输掉或无法外推的条件式结论 |
| 多目标冲突 | B11：指标冲突如何调度，硬件特化是否值得 | 同时报告命中、TTFT、TPOT、吞吐/波动、精度与成本，不只挑胜出的指标 |

固定项目的每个结果应写成条件句：

> 在 `[框架 commit / GPU / 模型 / dtype / workload / 并发 / 容量压力]` 下，相对 `[库存基线]`，`[改动]` 改善 `[指标]`；当 `[低共享、无容量压力、长 idle、传输过重、后端不支持]` 时收益消失或回退。

## 4. 筛选层—验证层落差

由于 A 与 B 的公司、年份和岗位构成并不相同，下面只能称为**本样本观察到的落差**；“B 中少见/未见”不能解释为行业面试不会问。

| 观察 | JD（筛选层） | 面经（验证层） | 对准备的含义 |
|---|---|---|---|
| 编程/系统基础没有落差 | 常规学生岗最稳定的明确要求 | 10/14 有手写代码，B06 甚至主要问 C/C++ | 项目不能替代算法题、C++/Python、OS/内存/并发基础 |
| 框架名 → 数据路径 | vLLM/SGLang/TRT-LLM 常出现在职责、硬性或加分 | 8/14 问 PagedAttention、block manager、continuous/chunked、TP、P/D、memory manager | 简历不要写“熟悉框架”；要能画选定框架的真实调用链和自己的改动点 |
| CUDA 同时是筛选分层器和验证层高频 | engine/kernel/异构岗常写 H/H*；serving/backend 更常写 B 或背景 | 13/14 出现 GPU/算子，但样本被 CUDA 背景候选人放大 | 不改变项目主线；必须达到性能模型/profiler 认知层，kernel 岗则承认 ownership 不匹配 |
| KV 是业务高频，面试中等频率 | 常规学生岗中经常是职责，但较少作为统一硬门槛 | 6/14 明确问 KV/prefix/PagedAttention/压缩 | 这是项目的差异化业务证据，不是凭一个名词过筛；命中定义与资源模型必须说清 |
| 量化从关键词变成条件题 | JD 常写量化/低精度，但不总是硬性 | 6/14；问题是 FP8/BF16、非对称量化、压缩率、精确收益 | FP8 轴必须同时测支持性、容量、命中、质量、TTFT/TPOT，而不是只报 dtype |
| P/D、投机解码、RDMA、多级远端 offload 在 B 中证据薄 | 当前 JD/团队动作可见，尤其专项岗和社招业务方向 | P/D 零散；投机解码/采样 2/14；严格样本未观察到 RDMA 实现追问 | 只能说本面经样本未充分覆盖；列入认知层或团队定向准备，不能声称“面试少问” |
| JD 几乎不写“证据审计” | 很少要求候选人预先写基线、失败条件、ownership | 严格项目拷打与边界问题各 9/14 | **隐性高价值目标**：原始 trace、基线、公平 A/B、精确数值、失败区间和 owned diff |
| Profiling/benchmark 文本频率可能不高，但验证层常问 | 普通学生 JD 中常藏在“性能优化”，专项/业务职责更显式 | 系统诊断 10/14，反复问如何定位/测量/判 bound | workload 与测量闭环是项目价值核心，不是附属脚本 |
| 可靠性/HA/K8s/Ray 的面试证据较少 | serving/backend 或 RL rollout JD 会写 | 本样本主要聚焦技术面，实际追问不足 | 对平台岗做认知层准备；不要为了命中词把单机实验改造成生产平台 |

隐性目标按性价比排序：`项目证据审计 > 手写代码与系统基础 > 选定框架数据路径 > GPU 性能模型 > 团队定向机制（P/D、投机解码、RDMA 等）`。

## 5. 信号源 C：团队公开技术动作

公开技术动作只能回答“团队真实在做什么”，不能回答“现在是否有 HC”。下面优先列与固定项目直接相关的一手证据；性能数字均视为发布方自报，不做横向排名。

| 公司/团队或项目 | 日期 | 一手动作 | 对业务方向的可靠结论 | 与项目重合度及边界 |
|---|---|---|---|---|
| 阿里云 Tair KVCache / HiSim | 2026-05-22 | [官方博客：HiSim](https://www.alibabacloud.com/blog/603164) 明确覆盖 multi-turn/Agent workload、HBM/DRAM/Disk、多种淘汰、prefetch、路由与 TTFT/TPOT/吞吐评估；[OpenAPI](https://www.alibabacloud.com/help/en/redis/developer-reference/api-r-kvstore-2015-01-01-describetairkvcacheinferinstances-redis) 2026-06-26 更新并暴露 KVCache 服务对象 | 云厂商确有托管 KV 服务和 workload/测量驱动的配置与策略工作 | **重合极高**。应交代真实框架执行、单卡约束、owned patch、强基线和 negative cases，而不是宣称“首创模拟” |
| AIBrix / InfiniStore（最初由字节开源，现为社区项目） | 2026-06-16/18；相关 offload 动作 2025-05-21 | [AIBrix v0.7](https://aibrix.github.io/posts/2026-06-16-v0.7.0-release/) 覆盖多引擎、KV-centric P/D 数据面与 HA；[v0.3](https://aibrix.github.io/posts/2025-05-21-v0.3.0-release/) 覆盖 multi-tier offload、prefix-aware routing、workload/benchmark，并明确 InfiniStore 为 ByteDance 开发的 RDMA KV server | 云原生 serving 控制面、cache-aware routing 和分布式 KV 数据面是真实方向 | **重合高**。当前 AIBrix 功能不能全部归为字节内部成果；单卡实验不能外推到 RDMA 与多节点 |
| 腾讯云 TACO / FlexKV | 2025-12—2026-06，2026-03 合入 vLLM/Dynamo | [官方仓库](https://github.com/taco-project/FlexKV) 与 [vLLM PR #34328](https://github.com/vllm-project/vllm/pull/34328) 展示全局 KV、CPU/SSD/GDS、传输、淘汰和多框架集成 | 腾讯云公开持续投入 serving 存储层和分层 KV，且获得上游正式集成 | **重合极高**。offload/淘汰直接重合；合入上游不等于内部部署规模或当前招聘 |
| 月之暗面 Kimi / Mooncake | FAST ’25；生态实验 2026-05-06 | [FAST ’25 论文](https://www.usenix.org/system/files/fast25-qin.pdf) 明确 Mooncake 是 Kimi 的 KVCache-centric serving platform；[vLLM × Mooncake](https://vllm.ai/blog/2026-05-06-mooncake-store) 使用 610 条 Codex/SWE-bench Pro traces 测跨实例共享 | FAST ’25 证明 Kimi 真实使用全局 KV 与 SLO 调度；另一个独立主体 vLLM 的 2026 生态集成证明 agentic traces 已用于 cache-sharing 评估 | **重合极高**。不能把 2026 的 trace benchmark 写成 Moonshot 内部实验 |
| 百度 PaddlePaddle / FastDeploy | 2026-04-09 | [FastDeploy v2.5.0](https://github.com/PaddlePaddle/FastDeploy/releases/tag/v2.5.0) 含 W4AFP8、P/D、动态 C8/RDMA、KV stores、Go router、request trace/metrics；[仓库](https://github.com/PaddlePaddle/FastDeploy) 继续公开全局 cache 与异构硬件 | 百度公开栈覆盖 MaaS、全栈引擎、量化、KV 传输/存储、路由、可观测与国产硬件 | **重合高**。cache/FP8/源码阅读可对齐；所选证据不能证明每项能力在千帆线上采用 |
| 华为昇腾 / MindIE | 2026-06-05 | [MindIE 1.0.RC3 开发指南](https://www.hiascend.com/doc_center/source/zh/mindie/10RC3/mindiellm/llmdev/MindIE%201.0.RC3%20LLM%E5%BC%80%E5%8F%91%E6%8C%87%E5%8D%97%2001.pdf) 列出 P/D、并行解码、跨会话 Prefix Cache、KV INT8 及硬件兼容边界 | 自研芯片适配与 serving engine 是核心 | **重合中**。缓存机制相通，但这是 Ascend/INT8，不应外推本项目的 GPU/FP8 结果 |
| DeepSeek online inference / FlashMLA | 2025-02；FlashMLA 2025-09 更新 | [在线推理概览](https://github.com/deepseek-ai/open-infra-index/blob/main/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md) 披露 P/D、EP 与磁盘 KV reuse；[FlashMLA](https://github.com/deepseek-ai/FlashMLA) 公开 FP8 KV attention kernel | 模型/API 厂把磁盘 KV reuse、并行负载均衡和低精度 kernel 作为真实优化点 | **重合中高**。能验证 FP8/KV 的业务真实性，不能把调用现成功能写成 CUDA kernel 经验 |
| 美团 / LongCat | 2026-07-12 | [官方文章](https://tech.meituan.com/2026/07/12/LongCat-2.0-Open-source.html) 公开 KVP/KV 传输、P/D、EPLB、量化和国产卡推理 | 模型厂 serving 与国产卡协同是公开方向 | **重合中**。长上下文/KV/量化有交集，但模型规模、EP 与硬件环境远超单卡项目 |
| NVIDIA / Dynamo（国际参照） | 2026-03-16 | [Dynamo 1.0](https://developer.nvidia.com/blog/nvidia-dynamo-1-production-ready/) 覆盖 agentic priority routing/cache pinning、KV Block Manager、对象存储与恢复 | 国际主流 serving 平台同样把 agentic cache affinity 与 KV 生命周期当核心问题 | **重合高**。只能作为技术参照；中国区招聘须由 A 类 JD 另证 |
| SGLang / HiCache（生态校验） | 2025-09-10 | [官方博客](https://www.lmsys.org/blog/2025-09-10-sglang-hicache/) 公开 GPU/CPU/外部存储多级缓存、prefetch/write policy 与 multi-turn benchmark | “多轮 workload—缓存层级—策略—命中/SLO”已进入主流 serving 引擎 | **重合极高**。是生态方向，不归属于单一公司，也不能据致谢反推招聘 |

**最硬的市场校准：**企业公开成果多发生在跨实例、RDMA、远端存储、多 GPU/多节点，而个人项目的可信边界是单机真实执行、局部策略、本地 offload/FP8 的受控 A/B。把边界说清不会削弱项目；把单卡结果外推成分布式结论才会。

## 6. 固定项目内核的匹配度映射

### 6.1 已天然覆盖

| 项目组成 | 命中的市场信号 | 应交付的证据 | 简历可用措辞边界 |
|---|---|---|---|
| 参数化多轮 Agent workload + 行为分析 | benchmark、profiling、Agentic workload、性能诊断、可观测性 | workload 参数表、固定 seed、trace schema、重复次数、原始结果 | 写“构建并回放参数化 workload，刻画共享前缀、轮间间隔、并发对 KV 驻留和 TTFT/TPOT 的影响”；不要写“还原真实线上流量”，除非确有真实 trace |
| prefix/KV cache 复用测量 | KV/prefix cache、内存管理、cache-aware scheduling | 命中定义、block/token 口径、occupancy、eviction、restore/recompute 成本 | 写清是 prefix hit、block hit 还是请求命中；不要只写一个无法解释的“命中率提升” |
| 一项小范围淘汰策略改进 | eviction、cache policy、调度、资源效率 | 库存基线、owned diff、A/B、重复试验与波动范围、输掉的 workload | 写“相对框架原生策略在 X 条件下改善 Y，同时在 Z 条件下回退”；不要包装成通用最优策略 |
| 选定的 vLLM **或** SGLang 源码阅读与埋点 | 框架 internals、二次开发、源码理解 | 固定 commit、模块/调用链、埋点位置、为何该位置能测到所需事件 | 只写实际选定框架；除非真做了双框架实验，否则不要用斜杠暗示两者都深入 |

建议的主简历句式（数值只允许在实验完成后填入；`[选定框架]` 只能填实际做过的一个框架）：

> 针对多轮 Agent 中共享前缀与轮间间隔造成的 KV 驻留/淘汰失配，在固定的 `[选定框架 commit]` 上构建参数化 workload 与 trace runner，记录 prefix/block hit、KV occupancy、TTFT/TPOT/p95；实现 `[策略/小改动]`，相对 `[原生基线]` 在 `[GPU、模型、负载]` 下使 `[指标]` 改善 `[实测值]`，并报告其在 `[失效条件]` 下的回退。

### 6.2 低成本可靠拢

这些项是**候选实验轴，不要求全部累加**；8–10 周约束下，主线只承诺“测量闭环 + 至多一个主要策略改动”。下列时间均为基于范围的**规划估计**，不是来源事实；框架熟悉度、connector 和硬件支持会显著改变成本。

| 增量 | 命中词 | 额外成本 | 偏离主线 | 进入条件与停止条件 |
|---|---|---:|---|---|
| 实验清单、版本锁定、原始 trace/CSV、重复试验 | benchmark、observability、reproducibility、testing | 2–3 天 | 无 | 必做；若连一次实验的配置与结果都无法重放，先停止策略扩展 |
| 增加 adversarial/negative workload | 项目深挖、边界问题、稳定性 | 2–3 天 | 无 | 必做；至少覆盖低共享、高 churn、长 idle、突发并发、容量不过载五类反例 |
| 接入框架已有 CPU/offload 或现成 connector 作基线 | offload、分层 KV、memory management | 规划估计 5–8 天，前提现成路径可在目标框架工作 | 低 | 仅在主线提前闭环后进入；只比较“恢复 vs 重算”与传输/排队成本。若需自建远端 KV 服务、改网络协议，或两天仍无法跑通最小样例，则停止该轴 |
| FP8 KV cache 轴 | FP8/低精度、量化、容量、性能 | 规划估计 4–7 天，前提是后端路径可用；含正确性、精度、性能与一次有限排障 | 低 | 先做 capability gate；需同时报告容量、真实命中、TTFT/TPOT 与精度。若实际 24GB GPU/框架组合不可运行，这是影响固定输入的**重大发现，需用户决策**；不能静默改成纯文档分析，也不能模拟收益 |
| 为一个测量点或策略做最小源码 patch | 框架二次开发、C++/Python、ownership | 3–7 天 | 低—中 | patch 必须服务主问题且可被测试；若演变为通用插件系统，砍掉抽象层 |

### 6.3 认知层覆盖

这些主题面试价值高，但不值得为了“简历命中”塞进项目实现：

| 主题 | 面试要达到的深度 | 项目中的最小连接点 |
|---|---|---|
| PagedAttention、block manager、refcount、prefix tree | 能从请求到 block 分配/复用/释放画出数据路径，解释碎片与写时复制 | 解释你的命中和 occupancy 埋点为何正确 |
| continuous batching、chunked prefill、调度 | 能解释 TTFT/TPOT/吞吐之间的冲突，以及调度如何扰动缓存行为 | workload 的并发、到达率和 prefill/decode 组成 |
| MHA/MQA/GQA/MLA 与 KV 容量模型 | 能按层数、head、head dim、dtype、序列长度估算 KV 大小 | 预测容量压力并与实测核对 |
| 量化/FP8 | scale 粒度、校准、误差、硬件支持、存储与计算 dtype 区别 | 解释为什么容量翻倍不必然变成命中或延迟收益 |
| FlashAttention 与 CUDA 性能模型 | memory-bound/compute-bound、带宽、访存合并、shared memory、kernel launch；能读 profiler | 解释为何本项目不改 attention kernel，以及 cache 传输/重算的成本边界 |
| TP/PP/EP、NCCL、RDMA/GPUDirect | 理解通信量、拓扑和远端 KV 传输路径，不要求实现 | 能评估单卡结论不能外推到多机的原因 |
| speculative decoding | 接受率、draft/target 成本、batch/cache 交互、何时失效 | 作为外部机制理解，不并入实验变量 |
| serving 可靠性 | backpressure、超时、重试、熔断、负载均衡、SLO/goodput | 知道离线 benchmark 与生产 serving 的证据边界 |
| C++/Python、OS、数据结构与手写代码 | 能完成常见算法题，掌握内存、并发、缓存、进程/线程基础 | 框架调用链和实验工具的工程质量 |

### 6.4 明确放弃

下列成本同样是规划级范围估计，用于说明为何在单卡、8–10 周内不应进入项目，不是外部来源统计。

| 明确不做 | 预计成本/资源 | 放弃理由 | 面试中的诚实回应 |
|---|---:|---|---|
| 自研 CUDA/Triton/CUTLASS 算子 | 2–4+ 周，并需独立正确性/性能基线 | 与“缓存行为与策略”主变量正交；会挤掉可复现闭环 | “我能解释 GPU 性能模型并读 profiler，但这次把 owned change 固定在 cache runtime；没有把调用现成 kernel 包装成算子开发经验。” |
| MLIR/LLVM/TVM/AI 编译器 | 4–8+ 周 | 完整的另一条岗位族，无法在当前周期形成可信深度 | “这是编译器/图优化方向，我没有项目证据，因此不把它列为已掌握。” |
| RDMA/NCCL/GPUDirect 或多机 KV 传输实现 | 3–6+ 周，且缺少公平硬件环境 | 单卡无法验证端到端网络、拓扑和多租户行为；模拟结果不能充当生产证据 | “我做了机制与成本模型学习，但单卡环境不足以公平验证 RDMA，所以没有把模拟写成工程结论。” |
| 完整 P/D 分离、多机调度或生产 MaaS | 4–8+ 周并需多 GPU/集群 | 系统边界失控，且会同时引入调度、网络、容错、部署变量 | “我明确只研究单机 cache runtime；多机 P/D 是外部效度限制。” |
| 自建 LMCache/Mooncake 类分布式 KV store | 6–10+ 周 | 重复成熟系统且无法证明可靠性；不是低成本 offload 实验 | “offload 只复用现成路径做对照，没有宣称重做分布式 KV 存储。” |
| 训练/RL infra、模型微调 | 3–8+ 周 | 与固定推理缓存问题正交，混淆项目身份 | “我只学习它们如何改变请求形态，不把训练能力写进这个项目。” |
| 端侧部署/自研芯片适配 | 4–8+ 周且缺少设备 | 不同硬件、runtime 和约束体系 | “该项目结论限定在已报告的 GPU/软件栈，不外推到端侧或 NPU。” |

## 7. 公司—团队地图与投递优先级

把“现在能投”与“技术最重合”拆开，否则会把博士专项或尚未证实 HC 的团队错误排到本科生投递 P0。

### 7.1 当前可投/近期窗口榜（只由信号 A 判定）

| 实际优先级 | 公司与已核验入口 | 2026-08-04 状态 | 资格与岗位分流 | 项目匹配判断 |
|---|---|---|---|---|
| **P0 当前投** | 百度 2027 校招：[AI Infra 工程师 J100730](https://talent.baidu.com/jobs/detail/GRADUATE/59d9bb54-46e5-4d3c-aa26-e59b1dea387a) | 2026-07-21 发布，当前页面存在 | 训推混合但门槛比纯 kernel 岗更宽，仍需 C++/Python、框架、分布式和量化/内存基础 | cache/measurement、框架源码和性能实验直接可用 |
| **P1 选择性投** | 百度：[AI Infra 推理 J101235](https://talent.baidu.com/jobs/detail/GRADUATE/7753cdb4-70b0-462b-a634-ee53818c7c9a)、[AI 异构 J101236](https://talent.baidu.com/jobs/detail/GRADUATE/f0c02346-05c2-4742-aa52-2a8d50cf0792) | 2026-07-21 发布，当前页面存在 | 两条都明确重 CUDA/算子/异构，J101235 还列 CUTLASS/CuTe/Triton/TileLang | 项目是系统侧证据，不能代替 kernel ownership；按面试准备度选择性投 |
| **相邻岗单列** | 百度 [RL AI Infra J101228](https://talent.baidu.com/jobs/detail/GRADUATE/127e69e3-6b3b-440e-83d6-080076768c13)、自动驾驶 [J100724](https://talent.baidu.com/jobs/detail/GRADUATE/15a59bf3-83f9-4c35-8d5e-bce6c50c59cc) | 2026-07-21 发布，当前页面存在 | 前者是训练 infra/rollout，后者硕士及以上且 kernel/compiler 偏重 | 解释为何没有列入 P0；仍可作为业务与知识准备参照 |
| **P1 当前投** | 字节基础设施计算团队：[AI Infra 后端开发实习生-计算](https://www.nowcoder.com/jobs/detail/431803) | 页面可申请；精确发布日期未验证 | 这是 IaaS/计算团队的广义 AI Infra，不是 Seed/AIBrix/InfiniStore 的已证实入口 | 后端、系统基础和框架实验可用；不能把公开社区成果写成所投团队工作 |
| **P2 技术相邻投** | NVIDIA 中国 Solution Architecture：[AI Infra Intern JR2019909](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Solution-Architecture-Intern--AI-Infra---2026_JR2019909)、[AI in Industry JR2014186](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Solution-Architecture-Intern--AI-in-Industry---2026_JR2014186) | 官方页面存在；前一条日期由[第三方镜像](https://www.iagora.com/work/en/offer/internship-work-from-home-construction/6197696)补足为 2026-06-16，另一条只显示 `30+ Days Ago` | 接受在读学生，但 title 是 Solution Architecture；因职责含开源开发、kernel、KV offload 才保留为技术相邻岗 | 多级 KV/workload 有交集；岗位本身不是核心引擎研发的等价物 |
| **P1 当前投** | 小红书中台 AI Infra：[训练/压缩/推理 Infra 研发 17015](https://job.xiaohongshu.com/campus/position/17015?referer_code=C09UF8OCSZ4M) | 官方页当前显示投递入口；精确发布日期未验证 | 本科及以上，但任职面很宽，通信、CUDA、量化/压缩、框架源码均写在资格中 | RedServing/DirectLLM 与 cache/runtime 相关；项目不能覆盖其 kernel/通信面，需按实际面试团队分流 |
| **P1 专项投** | 快手快Star：[基础大模型推理引擎 452683](https://www.nowcoder.com/jobs/detail/452683)、[高性能算子 452689](https://www.nowcoder.com/jobs/detail/452689)、[训推优化 452715](https://www.nowcoder.com/jobs/detail/452715) | 2026-07-07—12-31，当前开放 | 属 Special Offer；452683 未见具体学历硬限制且最贴近 runtime，452715 明确硕士及以上、对本科资格不符；452689 偏 kernel | 以 452683 为主；其余不能因为同一专场就统一列作本科 P1 |
| **不列本科当前可投** | PDD [AI Infra 实习 454371](https://www.nowcoder.com/jobs/detail/454371) | 2026-07-20—12-31，当前开放 | JD 明确 2027 届硕士/博士；对当前本科背景是资格不匹配 | 可证明广义训推 infra 方向，但不应抬高本科门槛或列为用户 P0 |
| **状态/资格待核验** | 阿里星 KV/推理课题 | 牛客同时出现 2027 截止日与“已结束”，状态矛盾 | 部分课题明确博士；属于特殊人才计划 | 只进入技术重合/监控榜，不列普通本科当前可投 |

有明确近期截止日期、值得滚动监控的同类岗位：小米 MiMo 推理框架（2026-03-12—06-19）、快手 Model Serving/推理优化留用实习（2026-03-25—07-02）、卓识基金推理实习（2026-06-08—07-31）。MiniMax 2027 与 SmartX 页面已结束但起止日期未验证，只能作为方向补充，不能声称属于近 6 个月窗口。

### 7.2 技术重合/监控榜（由信号 C 判定，不代表 HC）

| 技术监控级别 | 团队/项目 | 公开业务重心 | 项目重合 | 招聘证据缺口 |
|---|---|---|---|---|
| **T0** | 阿里云 Tair KVCache / HiSim | **云厂商 serving/KV 服务**：托管 KV、多轮 workload、测量、分层缓存、淘汰、offload、路由 | **最高** | 当前具体入口以博士/专项为主且状态有冲突；不是本科生“当前投递 P0” |
| **T0** | 腾讯云 TACO / FlexKV | **云厂商 serving 存储层**：分布式 KV store、多级缓存、传输、淘汰、vLLM/Dynamo 上游集成 | **最高** | 本轮未核验到当前普通校招/实习 JD |
| **T0** | 月之暗面 Kimi / Mooncake | **MaaS/模型厂 serving**：KVCache-centric 架构、全局 cache、SLO；agent traces 只作为 vLLM 生态集成参照 | **最高** | 本轮未核验到当前国内校招/实习精确 JD；不把生态 benchmark 归为 Kimi 内部动作 |
| **T0/T1** | 字节相关 AIBrix/InfiniStore | **云原生 serving 控制面/数据面**：KV-aware routing、P/D、远端 KV | **高** | AIBrix 已是社区项目；InfiniStore 仅按文章明确归因；不能与 Seed 或通用 IaaS 实习合并成一个可投团队 |
| **T1** | 百度 FastDeploy/PaddlePaddle | **MaaS + 全栈引擎 + 异构**：KV、P/D、量化、路由、国产硬件 | **高** | 当前校招证据强，但 FastDeploy 与千帆具体生产组织映射未完全证实 |
| **T2** | 华为 MindIE、DeepSeek FlashMLA、美团 LongCat | **自研芯片/国产卡或模型—硬件协同**：P/D/EP、低精度 kernel | **机制相通、实现层不同** | 公开动作强，但当前普通校招入口未全部证实；项目不能替代硬件/kernel 经验 |
| **T3** | 阿里 MNN 等端侧 runtime | **端侧**：多轮 prompt cache、低比特 KV、多硬件 backend | **低** | 机制词相通，但功耗、内存、runtime 和设备约束与云端 vLLM/SGLang 不同，不作为本项目主投类型 |

快手推理引擎、MiniMax、小米 MiMo、小红书 RedServing 的方向在本轮有 **JD（信号 A）** 支持，但没有找到同等强度、近 12–18 个月且可明确归因的公开技术动作，因此不混入这张 C 类榜；不能从“C 缺口”推出这些团队没有相关业务。

按团队类型看，项目叙事的自然排序是：

1. **云厂商 serving / KV 存储层**：Tair KVCache、TACO/FlexKV、字节相关 KV 数据面；
2. **KVCache-centric 模型厂 serving**：Kimi/Mooncake；
3. **MaaS / 全栈推理引擎中的 cache/runtime 子组**：百度 FastDeploy/PaddlePaddle；字节只按 AIBrix/InfiniStore 已核验归因讨论，不写成未证实的 `Seed serving`；
4. **泛推理引擎、异构和算子组**：可投，但项目只覆盖系统侧，需要认知层防守；
5. **端侧、AI 编译器、纯 kernel、自研芯片深度适配**：不是该项目的主匹配岗位。

## 8. 简历包装和证据口径

### 8.1 项目标题

优先使用能让筛选者立即看到边界的标题，例如：

> **多轮 Agent 工作负载下的 `[选定框架]` Prefix/KV Cache 行为分析与策略实验**

不建议使用“企业级 KV Cache 系统”“分布式推理引擎”“高性能 CUDA 推理框架”等超出证据的标题。

### 8.2 四条不可省略的证据

1. **环境真相：**GPU 型号、显存、模型、框架与 commit、后端、dtype、并发模型。
2. **基线真相：**原生策略/功能是什么，是否使用同一 workload、warmup、采样窗口和资源限制。
3. **ownership 真相：**哪部分是 workload/runner，哪部分是测量埋点，哪部分是你的策略 diff，哪部分调用上游现成功能。
4. **失败真相：**至少一个策略输掉、FP8 无收益或 offload 不划算的区域，以及为什么。

### 8.3 面试时的 90 秒叙事骨架

> 多轮 Agent 请求不是稳定连续地复用前缀，复用受共享前缀长度、轮间间隔、并发和缓存压力共同影响。我先固定选定框架的版本，用参数化 workload 和 trace 把 prefix/block hit、occupancy、eviction、TTFT/TPOT 对齐到同一时间线；确认原生策略在哪类负载下次优后，只做一个局部策略改动并与库存实现 A/B。FP8 是固定的受控实验轴，比较容量、真实命中、时延和精度；只有主线提前闭环且现成路径可用，才增加 offload 的“恢复与重算”对照。我不会把单卡结果外推成 RDMA/多机结论，也会展示策略失效的 workload。

这段叙事的价值不在于覆盖所有热词，而在于面试官可以继续追问每个名词的定义、数据来源和边界。

## 9. 本调查的局限性

1. **样本量小且不是随机抽样。** 当前 JD 和面经来自可公开访问、能读到正文的页面；频率用于识别重复信号，不是招聘市场总体比例。
2. **渠道偏差。** 牛客对大厂、技术岗和主动分享者过度代表；BOSS/脉脉登录态、反爬和岗位下线会让一部分文本不可复核；公司官网岗位名和团队名也经常过粗。
3. **公司集中度偏差。** 百度当前官网可核验岗位较多，若直接按 JD 条数计数会放大百度文本习惯；报告做了文本去重并在解释中避免把单公司高频当成全市场结论。
4. **面经时间窗口落后于 JD。** 近 6 个月、明确属于目标岗位且包含完整问题的第一人称面经稀缺；部分高质量样本来自 2025 年，只能说明验证机制的延续性。2026 年转载、匿名聚合或 AI 辅助文章不进入主频率。
5. **岗位命名噪声。** “推理引擎/推理优化/AI Infra”可能分别指 cache/serving、CUDA kernel、编译器、自研芯片或通用平台；公司级匹配不能替代逐条 JD 分流。
6. **公开动作存在发布偏差。** 愿意开源、发论文和写博客的团队会被高估；没有近期开源证据不能推出团队没有相关业务。
7. **公开动作不能证明招聘。** 仓库、论文与产品文档能证明业务方向，不能证明当前 HC、地点、届别、团队规模或内部采用率。
8. **性能数字不可横比。** 企业博客、论文和仓库使用不同模型、硬件、workload 和版本；本报告只采用其问题结构，不把自报倍数当个人项目目标。
9. **硬件可行性未替用户实验。** FP8 KV cache 在具体 24GB 消费卡、框架版本和模型上的支持与性能必须在开工前做 capability gate；报告不把文档支持推断成用户环境已支持。
10. **职位会继续变化。** 采集截点之后岗位可能新增、下线或修改。所有“当前”判断均限定到 2026-08-04。

## 附录 A：完整 JD 来源

状态含义：`开放`=页面当前有有效入口，`近期截止`=本招聘窗口已结束但进入近一轮趋势统计，`未验证`=日期/状态缺失或页面自相矛盾。团队名未公开时不猜测。

| ID | 公司/团队 | 岗位与类型 | 日期/状态 | 原始来源 | 关键技术词 |
|---|---|---|---|---|---|
| A-C1 | 百度/基座研发 | AI Infra 强化学习工程师 J101228；校招，训练 infra 含 rollout | 发布 2026-07-21；开放 | [官方](https://talent.baidu.com/jobs/detail/GRADUATE/127e69e3-6b3b-440e-83d6-080076768c13) | vLLM/SGLang、dynamic batching、KV reuse、Mooncake、Ray/K8s、容错/观测 |
| A-C2 | 百度/未披露 | AI Infra 工程师 J100730；校招，训推混合 | 发布 2026-07-21；开放 | [官方](https://talent.baidu.com/jobs/detail/GRADUATE/59d9bb54-46e5-4d3c-aa26-e59b1dea387a) | 推理引擎、INT8/FP16、KV、GPU/NPU、显存、分布式、C++/Python |
| A-C3 | 百度/未披露 | AI 异构计算工程师 J101236；校招 | 发布 2026-07-21；开放 | [官方](https://talent.baidu.com/jobs/detail/GRADUATE/f0c02346-05c2-4742-aa52-2a8d50cf0792) | P/D、KV、spec decode、量化、TTFT、CUDA/算子、vLLM/SGLang |
| A-C4 | 百度/基座研发 | AI Infra 推理工程师 J101235；校招 | 发布 2026-07-21；开放 | [官方](https://talent.baidu.com/jobs/detail/GRADUATE/7753cdb4-70b0-462b-a634-ee53818c7c9a) | batch 调度、分离部署、cache 池/传输、CUDA/CUTLASS/CuTe/Triton、Agent cache |
| A-C5 | 百度/自动驾驶 | 大规模 AI 系统优化与异构计算 J100724；校招，训推混合 | 发布 2026-07-21；开放 | [官方](https://talent.baidu.com/jobs/detail/GRADUATE/15a59bf3-83f9-4c35-8d5e-bce6c50c59cc) | CUDA、kernel fusion、NCCL、Triton/vLLM、TVM/TensorRT；硕士及以上 |
| A-C6 | 小米/MiMo | 大模型推理框架开发；2026 届校招 | 2026-03-12—06-19；近期截止 | [牛客](https://www.nowcoder.com/jobs/detail/440140) | vLLM/SGLang、监控/profiling、C++/Python、Transformer、CUDA kernel |
| A-C7 | 小红书/中台 AI Infra | 训练/压缩/推理 Infra 研发 17015；校招 | 采集 2026-08-04；开放；发布日期未验证 | [官方](https://job.xiaohongshu.com/campus/position/17015?referer_code=C09UF8OCSZ4M) | RedServing/DirectLLM、调度、监控、量化、NCCL/RDMA、CUDA、异构 |
| A-I1 | NVIDIA/Solution Architecture | AI Infra Intern JR2019909；技术相邻岗 | 约 2026-06-16；开放；日期由第三方镜像补足，非官方静态字段 | [官方 JD](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Solution-Architecture-Intern--AI-Infra---2026_JR2019909)、[日期镜像](https://www.iagora.com/work/en/offer/internship-work-from-home-construction/6197696) | vLLM/SGLang、GEMM/attention、FlexKV 多级 offload/reuse、分布式性能 |
| A-I2 | NVIDIA/Solution Architecture | AI in Industry Intern JR2014186；技术相邻岗 | 采集 2026-08-04；开放；官方仅显 30+ days | [官方](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Solution-Architecture-Intern--AI-in-Industry---2026_JR2014186) | 瓶颈定位、TRT/vLLM/SGLang/Dynamo、KV 性能建模、分离式推理 |
| A-I3 | NVIDIA/未披露 | LLM 推理优化实习（可转正） | 2025-09-17—2026-07-31；近期截止，旧于 6 月 | [牛客](https://www.nowcoder.com/jobs/detail/418691) | TRT-LLM、算子/分布式、KV 量化、稀疏、投机、Streaming-LLM、compiler |
| A-I4 | 字节/基础设施计算 | AI Infra 后端开发实习生-计算；2027 转正实习 | 采集 2026-08-04；开放；发布日期未验证 | [牛客正文](https://www.nowcoder.com/jobs/detail/431803)、[官方入口](https://jobs.bytedance.com/campus/m/position/7599649121267927349/detail) | IaaS AI Infra、异构调度、云原生、训推性能；框架/GPU/高速网为加分 |
| A-I5 | 快手/Model Serving | Model Serving 开发，杭州留用实习 | 2026-03-25—07-02；近期截止 | [牛客](https://www.nowcoder.com/jobs/detail/442015) | GPU 池化/显存复用、分布式 KV 传输/池、prefix hit、预取、资源调度 |
| A-I6 | 快手/多模态推理优化 | 大模型推理优化，北京留用实习 | 2026-03-25—07-02；近期截止 | [牛客](https://www.nowcoder.com/jobs/detail/441925) | 高性能算子、量化、分布式并行、投机；CUDA/vLLM/SGLang 为加分 |
| A-I7 | 卓识基金/大模型团队 | 大模型推理与应用工程师；2027 校招实习 | 2026-06-08—07-31；近期截止 | [牛客](https://www.nowcoder.com/jobs/detail/450144) | vLLM/SGLang 集群、网关、监控/HA、GPU 基线、并行、K8s；KV 为加分 |
| A-I8 | 阿里/芯片框架 | 芯片框架开发；2027 实习 | 2026-03-18；页面写 2027-03-18 截止但又显示已结束；未验证 | [牛客](https://www.nowcoder.com/jobs/detail/439560) | vLLM/SGLang/vLLM-Omni、benchmark、PyTorch、AI 芯片、CUDA 加分 |
| A-I9 | PDD/云弧计划 | AI Infra 研发实习；训推混合 | 2026-07-20—12-31；开放 | [牛客](https://www.nowcoder.com/jobs/detail/454371) | 分布式训推、调度/通信、显存、MoE、量化、在线推理、HA；硕博 |
| A-I10 | MiniMax/未披露 | 大模型推理研发实习，2027 届 | 采集 2026-08-04；页面已结束；起止日期未验证，不能判断是否属于近 6 月 | [牛客](https://www.nowcoder.com/jobs/detail/429159) | 推理框架、C/C++、高性能算子、融合、内存布局、长上下文/动态计算 |
| A-I11 | SmartX/AI 训练推理平台 | AI 训练推理平台研发实习 | 采集 2026-08-04；页面已结束；起止日期未验证，不能判断是否属于近 6 月 | [牛客](https://www.nowcoder.com/jobs/detail/389660) | Ray 训推、调度、部署、混合编排、HA；Go/Python；vLLM/SGLang 为加分 |
| A-P1 | 快手/快Star | 高性能推理算子；特殊校招 | 2026-07-07—12-31；开放 | [牛客](https://www.nowcoder.com/jobs/detail/452689) | 低 bit、sparse attention、Nsight、DeepEP、CuTe/TileLang/Triton、分布式 |
| A-P2 | 快手/快Star | 大模型推理/训练优化；特殊校招 | 2026-07-07—12-31；开放 | [牛客](https://www.nowcoder.com/jobs/detail/452715) | AI compiler、融合/kernel、Codegen、异构、vLLM/TRT-LLM、MLIR/LLVM |
| A-P3 | 快手/快Star | 基础大模型推理引擎；特殊校招 | 2026-07-07—12-31；开放 | [牛客](https://www.nowcoder.com/jobs/detail/452683) | engine、异构、量化/蒸馏、并行、RL generation；框架/CUDA 为加分 |
| A-P4 | 阿里/阿里星 | KV Cache 全栈演进；特殊实习，博士 | 2026-04-24；未来截止日与“已结束”冲突；未验证 | [牛客](https://www.nowcoder.com/jobs/detail/446421)、[官方课题页](https://campus-talent.alibaba.com/campus/alistar) | HBM/主存/冷存多级池、预取/调度、量化/压缩、ROI、RDMA/NCCL 加分 |
| A-P5 | 阿里/阿里星 | KV Cache 分布式存储网络优化；特殊实习 | 2026-04-24；状态冲突；未验证 | [牛客](https://www.nowcoder.com/jobs/detail/439603)、[官方课题页](https://campus-talent.alibaba.com/campus/alistar) | KV 传输、RDMA/TCP、prefix、benchmark/监控、vLLM/HiCache、CUDA/NCCL |
| A-P6 | 阿里/阿里星 | 大模型推理优化；特殊实习，博士 | 2026-04-24；状态冲突；未验证 | [牛客](https://www.nowcoder.com/jobs/detail/439588)、[官方课题页](https://campus-talent.alibaba.com/campus/alistar) | SGLang 核心、低比特、投机、稀疏、分布式、算子/内存/KV、开源维护 |
| A-S1 | 百度/ACG MaaS | 大模型推理工程师 J101025；国内社招业务证据 | 发布 2026-07-21；开放 | [官方](https://talent.baidu.com/jobs/detail/SOCIAL/336e82e0-307f-49f1-ae1f-4831fb9d570e) | batching、KV、热加载、伸缩/隔离/均衡、重试熔断、SLA、压测与成本 |
| A-S2 | 百度/ACG 国产算力 | 异构训练推理 J96922；国内社招业务证据 | 发布 2026-07-21；开放 | [官方](https://talent.baidu.com/jobs/detail/SOCIAL/a93e562d-5bb3-4104-9875-9d68a4223335) | 国产 GPU、TP/PP/DP、kernel/低精度、回归、调度、KV、量化、多卡 |
| A-S3 | 华为/OTT2 系统部 | requisition 28183；社招，标题未验证 | 采集 2026-08-04；状态/发布日期未验证 | [官方](https://career.huawei.com/reccampportal/portal5/social-recruitment-detail.html?dataSource=1&jobId=28183) | 国产算力、量化/KV 压缩、投机、P/D、大 EP MoE、融合算子、serving |
| A-S4 | 美团/未披露 | 大模型推理优化；国内社招业务证据 | 采集 2026-08-04；页面已结束；日期未验证 | [牛客](https://www.nowcoder.com/jobs/detail/420726) | GPU/NPU、CUDA/Triton/AscendC、模型—框架协同、量化/剪枝/蒸馏 |

未计入国内矩阵但保留为业务参照：[字节 Storage for LLM（San Jose 社招）](https://joinbytedance.com/search/7499631716416932103)、[字节 2027 AI Compute + DPU 博士专项（Seattle）](https://joinbytedance.com/search/7633538176269306117)、[NVIDIA NCG 2026（Santa Clara）](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/AI-Inference-Performance-Engineer---New-College-Grad-2026_JR2014441)。它们没有进入国内校招/实习/社招频率。

## 附录 B：完整面经来源

14 个进入频率的流程已逐条列在 §3.1。以下页面只作补充或明确排除，均未混入 N=14：

| 日期 | 页面 | 处理 | 理由 |
|---|---|---|---|
| 2026-03-03 | [匿名 AI Infra 推理日常实习](https://www.nowcoder.com/feed/main/detail/ebeea95fa44a4eceb1c2890022a6bb2e) | 补充题型，不计频率 | 公司/轮次不明，呈聚合题纲；含 roofline、PagedAttention、Radix、量化、EAGLE、P/D、Triton/CUDA |
| 2026-03-02 | [小鹏 AI Infra](https://www.nowcoder.com/feed/main/detail/a79383aa92f64e8eb4e85959bf2660a0) | 不计 | 正文短、岗位/轮次不足，措辞模板化 |
| 2026-03-02 | [小鹏 AI Infra 一面](https://www.nowcoder.com/feed/main/detail/e4e725793a3f4c9197c36645bc63cf32) | 不计 | 有 C++/CUDA coding，但推理问题不足以稳定归类岗位族 |
| 2026-03-02 | [蔚来 AI Infra 一面](https://www.nowcoder.com/feed/main/detail/eeddf656bb364390ba936a7d26b01856) | 不计 | CPU/GPU/NPU、warp、GEMM、reduction；业务与流程元信息不足 |
| 2026-03-03 | [匿名 AI Infra](https://www.nowcoder.com/feed/main/detail/d695614a06424c148c04586ac3a66e78) | 不计 | 公司不明，混入 diffusion 等宽题，无法确认一次真实流程 |
| 2026-04-20 | [AI infra 26 秋招面经](https://zhuanlan.zhihu.com/p/2017740483217081305) | 明确排除 | 页面标注“包含 AI 辅助创作”；只可作为查找原帖的索引 |
| 2026，精确日见页面 | [“快手 AI infra”错位内容](https://www.nowcoder.com/discuss/904326953174323200) | 明确排除 | 正文把“量化策略”解释成股票交易，语义明显错位 |
| 2024-03-18 | [模型部署/推理优化/高性能社招汇总](https://www.nowcoder.com/discuss/599177965083054080) | 旧趋势 | 公司不明、社招多流程混合；只说明 kernel 岗会深问 CUDA，不作学生门槛 |
| 2024-10-09 | [C++ 菜鸡的暑期实习总结](https://www.nowcoder.com/discuss/620397328725299200) | 旧趋势 | 第一人称但超过窗口；只说明项目 + C++/GPU + 框架机制结构已存在 |

训练 infra 单列且不进入纯推理 N：同一篇 [2025 春招汇总](https://www.nowcoder.com/discuss/736868736837173248?sourceSSR=post) 中的字节 ML Systems/豆包方向流程，问题包括 RL、代码与“客户模型慢如何排查”，业务更接近训练平台。

## 附录 C：公开技术动作来源

C01–C15 与两条训练侧动作来自并行的信号 C 账本；C16 是总报告综合阶段新增并单独打开核验的 vLLM 官方一手证据，因此不回填为某家公司团队动作。

| ID | 团队/项目 | 日期 | 一手来源 | 本报告使用边界 |
|---|---|---|---|---|
| C01 | 阿里云 Tair KVCache / HiSim | 2026-05-22 | [官方博客](https://www.alibabacloud.com/blog/603164) | 证明 multi-turn/Agent workload、多级 cache、策略与 SLO 评估问题真实；不证明所有策略已生产启用 |
| C02 | 阿里云 Tair KVCache 产品对象 | 文档更新 2026-06-26 | [OpenAPI](https://www.alibabacloud.com/help/en/redis/developer-reference/api-r-kvstore-2015-01-01-describetairkvcacheinferinstances-redis) | 证明存在托管实例/控制面对象；不证明客户规模或 HC |
| C03 | AIBrix v0.7 | 博文 2026-06-16；release 06-18 | [官方博文](https://aibrix.github.io/posts/2026-06-16-v0.7.0-release/)、[release](https://github.com/vllm-project/aibrix/releases/tag/v0.7.0) | 证明社区多引擎 serving、KV-centric P/D、HA；不能全部归为字节内部成果 |
| C04 | AIBrix/InfiniStore | 2025-05-21 | [v0.3 官方博文](https://aibrix.github.io/posts/2025-05-21-v0.3.0-release/) | 文章明确把 InfiniStore 归为 ByteDance 开发，并列 offload/routing/benchmark；不证明内部覆盖率 |
| C05 | 腾讯云 TACO/FlexKV | 2025-12—2026-06；2026-03 上游合入 | [仓库](https://github.com/taco-project/FlexKV)、[vLLM PR](https://github.com/vllm-project/vllm/pull/34328)、[Dynamo PR](https://github.com/ai-dynamo/dynamo/pull/5858) | 证明分层 KV、传输、淘汰和上游集成；不证明当前校招 |
| C06 | Kimi/Mooncake | FAST ’25 | [论文](https://www.usenix.org/system/files/fast25-qin.pdf)、[仓库](https://github.com/kvcache-ai/Mooncake) | 论文明确 Mooncake 是 Kimi serving platform；规模为作者当时自报快照 |
| C07 | vLLM × Mooncake Store | 2026-05-06 | [vLLM 官方博客](https://vllm.ai/blog/2026-05-06-mooncake-store) | 证明 agent traces 下跨实例 KV sharing 的评测方法；不是 Kimi 单方内部 benchmark |
| C08 | 百度 FastDeploy 2.5 | 2026-04-09 | [release](https://github.com/PaddlePaddle/FastDeploy/releases/tag/v2.5.0)、[仓库](https://github.com/PaddlePaddle/FastDeploy) | 证明量化/P/D/KV store/router/trace/异构公开栈；不证明每项均由千帆生产采用 |
| C09 | 华为 MindIE 1.0.RC3 | 2026-06-05 | [官方开发指南 PDF](https://www.hiascend.com/doc_center/source/zh/mindie/10RC3/mindiellm/llmdev/MindIE%201.0.RC3%20LLM%E5%BC%80%E5%8F%91%E6%8C%87%E5%8D%97%2001.pdf) | 证明 Ascend 上 P/D、跨会话 prefix、KV INT8 与兼容边界；不是 GPU FP8 证据 |
| C10 | 阿里 MNN 3.5 | 2026-04-07 | [release](https://github.com/alibaba/MNN/releases/tag/3.5.0) | 证明端侧多轮 prompt cache 与低比特 KV；运行环境与云端项目不同 |
| C11 | DeepSeek online inference | 数据窗口结束 2025-02-28 | [官方 open-infra-index](https://github.com/deepseek-ai/open-infra-index/blob/main/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md) | 证明公开系统使用 P/D、EP 与磁盘 KV reuse；单日数据不可视为 2026 当前规模 |
| C12 | DeepSeek FlashMLA | 2025-09 更新 | [官方仓库](https://github.com/deepseek-ai/FlashMLA) | 证明 FP8 KV 与 kernel/attention layout 强绑定；调用现成能力不等于 kernel ownership |
| C13 | 美团 LongCat | 2026-07-12 | [官方技术文章](https://tech.meituan.com/2026/07/12/LongCat-2.0-Open-source.html) | 证明 KVP/KV 传输、P/D/EPLB、低精度与国产卡协同；规模不可外推到单卡 |
| C14 | NVIDIA Dynamo 1.0 | 2026-03-16 | [官方博客](https://developer.nvidia.com/blog/nvidia-dynamo-1-production-ready/) | 国际参照：agentic cache affinity、KV 生命周期、外部存储；不证明中国区 HC |
| C15 | SGLang HiCache | 2025-09-10 | [官方博客](https://www.lmsys.org/blog/2025-09-10-sglang-hicache/) | 生态校验多级 cache/prefetch/write policy/multi-turn benchmark；不归为某单一公司 |
| C16 | vLLM FP8 KV-cache validation | 2026-04-22 | [官方文章源文件](https://github.com/vllm-project/vllm-project.github.io/blob/main/_posts/2026-04-22-fp8-kvcache.md) | 验证 Hopper/Blackwell 上的容量/ITL/吞吐与精度，也公开 hybrid layers、长上下文累积精度和 `head_dim=256` prefill 回归；不能外推消费卡 |
| C-T1 | 阿里 ROLL | 2025–2026；2026-06-16 更新 | [官方仓库](https://github.com/alibaba/ROLL) | **训练 infra 单列**：agentic RL rollout、vLLM/SGLang/FP8；不作为纯推理项目门槛 |
| C-T2 | SGLang × Mooncake TransferEngine | 2026-04-29 | [官方博客](https://www.lmsys.org/blog/2026-04-29-p2p-update/) | **训推耦合单列**：RL 权重同步，不是 KV reuse |
