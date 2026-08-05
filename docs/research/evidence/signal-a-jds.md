# 信号源 A：AI Infra 推理岗位 JD 取证与关键词编码

> 快照日期：2026-08-04（Asia/Shanghai）  
> 范围：国内求职可投的推理引擎、推理优化、LLM Serving、异构计算、明确涉及推理侧的 AI Infra；训练 Infra 单独标注。  
> 用途：提供 JD 层证据。社招只表示团队业务方向，**不把年限或资深能力要求当作校招生门槛**。

## 1. 样本与判定口径

### 1.1 来源等级

- **A（官方）**：公司官方职位详情页或官方招聘项目页。
- **B（招聘平台）**：牛客等平台上由公司招聘账号发布的职位详情。用户允许使用这些渠道；它们仍弱于公司官网。
- **C（聚合镜像）**：只用于发现候选或补充，因发布日期、在招状态或原始职位 ID 不完整，**不进入主统计**。

用户提供的两份 2026-07-28 材料只作为候选索引。本轮已重新打开并核验其中的百度 5 个岗位、字节 `Storage for LLM`、字节 2027 AI Compute + DPU 博士项目、NVIDIA 中国 AI Infra 实习和阿里星页面；没有把旧文结论直接当成当前事实。

### 1.2 去重后的统计样本

去重键为 `公司 + requisition/职位 ID + 岗位名称`。同一 JD 的官网页、牛客页、搜索索引和镜像只计 1 条；北京/上海内容完全相同的同 title 岗位也只计 1 条。

| 样本层 | N | 说明 |
|---|---:|---|
| 常规校招 | 7 | 百度 5、小米 1、小红书 1；其中小米岗位已结束，作为近 6 个月趋势样本 |
| 常规实习 | 11 | NVIDIA 3、字节 1、快手 2、卓识基金 1、阿里巴巴 1、PDD 1、MiniMax 1、SmartX 1 |
| 特殊人才计划 | 6 | 快Star 校招 3、阿里星 2027 实习 3；单列，不混入普通校招门槛 |
| 国内社招业务方向证据 | 4 | 百度 2、华为 1、美团 1；只表示业务方向，不作为学生门槛 |
| **合计** | **28** | 按原类型合并为：校招 10、实习 14、国内社招 4 |

日期覆盖：20 条有 2026-02-04 之后的明确发布日期/投递起始日；1 条发布日期早于近 6 个月但截至 2026-07-31 仍可投；7 条只能确认页面存在，精确发布日期未验证，均记录采集日期 2026-08-04。

来源分布：官方 A 级 11 条，招聘平台 B 级 17 条。另有国际地点和业务参照记录不进统计，见第 6 节。

为避免把“页面存在”误写成“当前可投”，再按 2026-08-04 页面状态拆分：

| 状态层 | 常规校招 | 常规实习 | 说明 |
|---|---:|---:|---|
| 当前可投/官方仍显示投递入口 | 6 | 4 | 当前岗位主样本；实习为 NVIDIA 2、字节 1、PDD 1 |
| 近 6 个月已结束 | 1 | 6 | 趋势层；保留用于减轻只看当前开放窗口造成的公司偏差 |
| 状态冲突或仅能确认页面存在 | 0 | 1 | 阿里芯片框架岗同时显示未来截止日与“已结束” |

频率矩阵使用上述全部 18 条常规学生岗，因为它回答的是“近一轮招聘窗口写过什么”；判断**此刻能否投递**时只能使用第一行的 10 条。特殊人才计划和社招始终分列。

其余统计层状态：快Star 3 条为 `当前开放`，阿里星 3 条均为 `未验证`；国内社招 2 条百度岗位为 `当前开放`，华为与美团各 1 条为 `未验证`。因此主统计 28 条合计为：`当前开放` 15、`近期截止` 7、`未验证` 6。

### 1.3 `D / H / H* / B` 编码

- `D`（direction）：技术词出现在工作职责、课题方向或团队业务描述中。
- `H`（hard）：技术词是所有候选人都要满足的任职要求，且没有被“优先、加分、stand out”等限定。
- `H*`（alternative hard path）：JD 明确写“至少一个方向/至少一种框架/A 或 B”，该技术只是满足硬门槛的一条可选路径；**不能读成所有候选人都必须掌握**。
- `B`（bonus）：技术词只在“优先、加分、Preferred、Ways to stand out”中出现。
- 若候选项都落在同一归一化行（例如“C++/Python/Go 至少一门”都属于编程语言），该行仍记 `H`；只有候选项跨越不同技术行时才分别记 `H*`。
- 一个词可以在同一 JD 同时为 `H` 和 `B`：例如基础 CUDA 知识是 H，而 CUDA kernel 实战是 B。
- 只编码原文，不从 title 猜要求；职责中的词不会自动提升为 H。

岗位状态只使用三种标签：`当前开放`（页面当前有有效投递入口）、`近期截止`（本招聘窗口已结束，作为趋势样本）、`未验证`（页面存在但发布日期/可投状态不清，或页面状态自相矛盾）。

## 2. 常规校招（N=7）

### C1 百度｜基座研发方向｜AI Infra 强化学习工程师（J101228）

- 类型：校招；**训练 Infra（含推理 rollout/serving 子系统）**；北京。
- 日期：发布 2026-07-21；采集 2026-08-04；状态 `当前开放`。
- 来源 A：[百度官方 JD](https://talent.baidu.com/jobs/detail/GRADUATE/127e69e3-6b3b-440e-83d6-080076768c13)
- D：异步 RL 训推解耦、vLLM/SGLang、推理调度、动态 batching、KV Cache 复用、Mooncake 分布式 KV pool、高速传输、K8s/Ray、容错与可观测性。
- H：Python/Go/C++ 至少一种；PyTorch/DeepSpeed/Megatron/MSSwift 使用经验；分布式训练、并行策略或大规模系统调度至少一个领域。
- B：vLLM/SGLang 引擎优化；K8s/Ray 调度研发；veRL/Slime；开源贡献或系统/ML 顶会论文。

### C2 百度｜团队未披露｜AI Infra 工程师（J100730）

- 类型：校招；**训推混合 Infra**；北京。
- 日期：发布 2026-07-21；采集 2026-08-04；状态 `当前开放`。
- 来源 A：[百度官方 JD](https://talent.baidu.com/jobs/detail/GRADUATE/59d9bb54-46e5-4d3c-aa26-e59b1dea387a)
- D：分布式训练框架、推理引擎、模型压缩部署、INT8/FP16、KV Cache、GPU/NPU、CUDA/XLA、算子融合、吞吐与稳定性。
- H：C++/Python；PyTorch/PaddlePaddle；分布式系统与并行计算；理解量化、推理优化、显存管理。
- B：CUDA/HPC；大模型训练/推理系统项目或实习。

### C3 百度｜团队未披露｜AI 异构计算工程师（J101236）

- 类型：校招；**训推混合、推理优化明确**；北京。
- 日期：发布 2026-07-21；采集 2026-08-04；状态 `当前开放`。
- 来源 A：[百度官方 JD](https://talent.baidu.com/jobs/detail/GRADUATE/f0c02346-05c2-4742-aa52-2a8d50cf0792)
- D：推理引擎极致优化、P/D 分离、KV Cache、投机解码、量化压缩、TTFT、decode 吞吐、RL rollout。
- H：C/C++/Python 至少一种；算法基础；PyTorch、Megatron、DeepSpeed；GPU 集群性能调优；CUDA、算子优化；vLLM/SGLang；计算通信效率分析。
- B：未单列技术加分项。

### C4 百度｜基座研发方向｜AI Infra 推理工程师（J101235）

- 类型：校招；**纯度最高的推理基建岗位之一**；北京。
- 日期：发布 2026-07-21；采集 2026-08-04；状态 `当前开放`。
- 来源 A：[百度官方 JD](https://talent.baidu.com/jobs/detail/GRADUATE/7753cdb4-70b0-462b-a634-ee53818c7c9a)
- D：文心推理基建、推理引擎/HPC 库/通信库、GPU 性能调优、模型-系统协同、批调度、分离部署、Cache 池化与传输。
- H：C++/Python；CUDA/CUTLASS/CuTe/Triton/TileLang；并行计算、分布式系统、存储；注意力/矩阵计算优化；批调度、分离部署、Cache 池化与传输。
- B：CUDA/HPC、计算通信/编译/巨型算子；vLLM/SGLang/TensorRT-LLM；Agent 场景 Cache 池化；低比特量化、投机解码、稀疏注意力；推理系统/大规模调度项目；开源贡献或顶会论文。

### C5 百度｜自动驾驶｜大规模 AI 系统优化与异构计算工程师（J100724）

- 类型：校招；**训推混合、kernel/编译偏重**；北京。
- 日期：发布 2026-07-21；采集 2026-08-04；状态 `当前开放`。
- 来源 A：[百度官方 JD](https://talent.baidu.com/jobs/detail/GRADUATE/15a59bf3-83f9-4c35-8d5e-bce6c50c59cc)
- D：NVIDIA GPU 推理算子、显存优化、Kernel Fusion、NCCL、千卡分布式训练、Triton/vLLM/Megatron。
- H：硕士及以上；精通 C/C++ 与 CUDA；底层硬件架构；并行计算、分布式系统或 TVM/TensorRT 编译器至少一条路径。
- B：深度学习框架底层开发，或 PyTorch/Triton 核心开源贡献。

### C6 小米｜MiMo｜大模型推理框架开发工程师

- 类型：2026 届校招；北京；**近 6 个月已结束趋势样本**。
- 日期：投递起始 2026-03-12，截止 2026-06-19；采集 2026-08-04；状态 `近期截止`。
- 来源 B：[牛客 JD](https://www.nowcoder.com/jobs/detail/440140)
- D：基于 vLLM/SGLang 的推理引擎研发、性能评估与调优、性能监控、CUDA kernel 与 GPU 算子、跨硬件性能优化。
- H：硕士及以上；C++/Python；PyTorch；Transformer/深度学习原理；大模型推理框架基本原理；GPU/加速硬件使用与基础性能调优。
- B：FastTransformer、CUDA、TensorRT、Triton；vLLM/SGLang 核心技术和实现经验。

### C7 小红书｜中台 AI Infra｜大模型训练/压缩/推理 Infra 研发工程师（position 17015）

- 类型：2026 校园招聘；北京/上海；**训推混合，推理/Serving 子方向明确**。
- 日期：官方页当前仍显示“投递简历”；采集 2026-08-04；状态 `当前开放`；**精确发布日期未验证**。
- 来源 A：[小红书官方 JD](https://job.xiaohongshu.com/campus/position/17015?referer_code=C09UF8OCSZ4M)
- D：RedServing 推理引擎、DirectLLM MaaS；分布式/异构调度、并行推理、请求调度、日志/监控、工作流；量化/蒸馏/剪枝；GPU/NPU 适配；算子、通信库和 AI 编译。
- H：本科及以上；Linux/Unix 上的 C++/Python/Rust；至少一种训推框架源码修改或深度使用；量化/蒸馏/剪枝实践；NCCL/RDMA/IB/RoCE；性能调优和 CUDA kernel 研发。开源框架开发经验与前沿论文成果是二选一硬路径，并非两项都必须有。
- B：JD 未单列“加分项”；上述技术均写在未加“优先”的任职资格中。

## 3. 常规实习（N=11）

### I1 NVIDIA｜Solution Architecture｜Solution Architecture Intern, AI Infra - 2026（JR2019909）

- 类型：实习；北京/上海。
- 日期：第三方公司页镜像记录 2026-06-16 发布；官方页只显示相对时间，精确日期非官方静态字段；采集 2026-08-04；状态 `当前开放`。
- 来源 A：[NVIDIA 官方 JD](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Solution-Architecture-Intern--AI-Infra---2026_JR2019909)；[发布日期镜像](https://www.iagora.com/work/en/offer/internship-work-from-home-construction/6197696)（日期只由镜像补足）
- D：SGLang/vLLM 社区开发；CUDA GEMM/attention 算子；CPU/SSD/远端存储多级 KV offload/reuse（FlexKV）；分布式训练性能。
- H：本/硕/博在读；编程、数据结构和计算机系统基础；对加速/并行/异构计算有明确兴趣。
- B：异构/分布式/并行/HPC；性能分析、建模或优化；开源框架贡献。

### I2 NVIDIA｜Solution Architecture｜Solution Architecture Intern, AI in Industry - 2026（JR2014186）

- 类型：实习；北京/上海/深圳。
- 日期：官方仅显示 `Posted 30+ Days Ago`；采集 2026-08-04；状态 `当前开放`；**精确发布日期未验证**。
- 来源 A：[NVIDIA 官方 JD](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Solution-Architecture-Intern--AI-in-Industry---2026_JR2014186)
- D：训练/推理搭建、瓶颈定位、优化验证、模型与业务场景加速。
- H：Linux；Python/C++；至少一种 TensorRT/TRT-LLM、ONNX Runtime、PyTorch、vLLM、SGLang、Dynamo；语言/视频/多模态等模型理解。
- B：GEMM/attention 算子优化；KV-cache 与多模态性能建模；vLLM/SGLang 或分离式推理。

### I3 NVIDIA｜团队未披露｜LLM 推理优化实习（可转正）

- 类型：实习；北京/上海/深圳。
- 日期：投递起始 2025-09-17，截止 2026-07-31；采集 2026-08-04；状态 `近期截止`；**发布日期超过近 6 个月，仅作趋势参考**。
- 来源 B：[牛客 JD](https://www.nowcoder.com/jobs/detail/418691)
- D：TensorRT-LLM runtime/API/服务层/自定义算子/分布式优化；低比特与 KV Cache 量化、稀疏化、投机解码、Streaming-LLM；AI compiler/kernel。
- H：有大模型推理优化相关经验；可实习约 3 个月、每周至少 3 天。
- B：未单列。

### I4 字节跳动｜基础设施计算团队｜AI Infra 后端开发实习生-计算

- 类型：2027 届转正实习；北京（牛客页面；官方职位页未输出可读正文）。
- 日期：采集 2026-08-04；状态 `当前开放`；**精确发布日期未验证**。
- 来源 B：[牛客可读 JD](https://www.nowcoder.com/jobs/detail/431803)；[字节官方职位页](https://jobs.bytedance.com/campus/m/position/7599649121267927349/detail)
- D：IaaS AI Infra 开发/优化和前沿技术验证；团队方向覆盖异构算力调度、云原生运行体系、大模型训推性能、AI Agent Infra。
- H：2027 届本科及以上；数据结构与算法；C/C++/Python/Go 至少一种。
- B：PyTorch/TensorFlow、vLLM/SGLang、GPU 编程、高性能网络。

### I5 快手｜Model Serving｜Model Serving 开发工程师-杭州（留用实习）

- 类型：实习；杭州。
- 日期：投递起始 2026-03-25，截止 2026-07-02；采集 2026-08-04；状态 `近期截止`。
- 来源 B：[牛客 JD](https://www.nowcoder.com/jobs/detail/442015)
- D：Serverless Model、GPU 池化、秒级启停、显存复用；分布式 KV Cache 传输、主存预取、CUDA Graph；分布式 KV 池与 Prefix Cache 命中；批量/异步推理和资源调度。
- H：Go/Java/Python；系统编程与性能调优；Kubernetes/Docker、Serverless、GPU 调度；PyTorch/TensorFlow；vLLM/TensorRT-LLM/FasterTransformer/SGLang；GPU/CUDA/显存/Kernel/CUDA Graph 基础。
- B：大规模在线服务；大模型推理加速。

### I6 快手｜视频生成/多模态推理优化｜大模型推理优化工程师-北京（留用实习）

- 类型：实习；北京。
- 日期：投递起始 2026-03-25，截止 2026-07-02；采集 2026-08-04；状态 `近期截止`。
- 来源 B：[牛客 JD](https://www.nowcoder.com/jobs/detail/441925)
- D：高性能算子、量化、分布式并行推理、投机推理。
- H：Linux；Python；算法与数据结构；深度学习基础；常见大模型推理优化技术。
- B：NVIDIA GPU 算子；vLLM/SGLang/TensorRT-LLM/xDiT 与并行推理；顶会论文。

### I7 卓识基金｜大模型团队｜大模型推理与应用工程师

- 类型：面向 2027 届的校招实习；北京。
- 日期：投递起始 2026-06-08，截止 2026-07-31；采集 2026-08-04；状态 `近期截止`。
- 来源 B：[牛客 JD](https://www.nowcoder.com/jobs/detail/450144)
- D：vLLM/SGLang 在线推理集群、网关、监控、高可用、GPU 基线与硬件评估；包含 Agent 实例接入，但底层 serving 职责明确。
- H：Python；vLLM/SGLang；并行推理；部署与调优；Linux、Docker、Kubernetes。
- B：C++；量化、KV Cache 优化；Agent/RAG 经验（该项不计入目标岗位核心词）。

### I8 阿里巴巴｜芯片框架｜芯片框架开发工程师

- 类型：阿里巴巴 2027 届实习；上海；**普通实习，不是阿里星课题**。
- 日期：投递起始 2026-03-18，页面给出的截止日 2027-03-18；采集 2026-08-04；状态 `未验证`（牛客同时显示“已结束”）。
- 来源 B：[牛客 JD](https://www.nowcoder.com/jobs/detail/439560)
- D：vLLM/SGLang/vLLM-Omni 适配与优化；PyTorch/TensorFlow 集成；模型性能评估与 benchmark；AI 芯片。
- H：Python/C++；Linux/系统基础；主流 Transformer/Diffusion 架构。
- B：vLLM/SGLang 推理优化；GPU/AI 芯片架构；CUDA。

### I9 PDD｜云弧计划｜AI Infra 研发工程师（实习）

- 类型：27 届校招转正实习；上海；**训练 Infra 为主但明确包含在线推理平台/推理优化，单独标注训推混合**。
- 日期：投递起始 2026-07-20，截止 2026-12-31；采集 2026-08-04；状态 `当前开放`。
- 来源 B：[牛客 JD](https://www.nowcoder.com/jobs/detail/454371)
- D：分布式训推平台、集群资源调度、高性能通信、显存优化、MoE 训推优化、量化与推理加速、高并发低延迟在线推理、弹性伸缩与稳定性。
- H：硕士/博士；C/C++、Python；OS/网络/分布式/编译基础；深入理解分布式系统；PyTorch/Megatron/DeepSpeed/vLLM/TVM 至少一种。
- B：Go/Rust；GPU/异构集群；RDMA/NVLink/InfiniBand；系统/架构论文、竞赛或有影响力系统项目。

### I10 MiniMax｜团队未披露｜大模型推理研发实习生-2027 届

- 类型：2027 届及以后实习；上海；**已结束趋势样本**。
- 日期：页面显示已结束；采集 2026-08-04；状态 `近期截止`；**投递起止/发布日期未验证**。
- 来源 B：[牛客 JD](https://www.nowcoder.com/jobs/detail/429159)
- D：推理框架核心模块、高性能算子、计算图/算子融合、内存布局优化、真实系统性能极限验证。
- H：C/C++、算法与数据结构；PyTorch/DeepSpeed/Megatron 等框架运行机制。
- B：ACM/NOI/ISC 竞赛成绩；未单列其他技术加分项。

### I11 SmartX｜AI 训练推理平台｜AI 训练推理平台研发实习生

- 类型：日常实习；北京（另有同文上海页，按同 title/同正文去重）；**已结束趋势样本**。
- 日期：页面显示已结束；采集 2026-08-04；状态 `近期截止`；**投递起止/发布日期未验证**。
- 来源 B：[牛客 JD](https://www.nowcoder.com/jobs/detail/389660)
- D：基于 Ray 的分布式训推服务、任务调度、模型部署、在线/离线混合编排、高可用与扩展性、企业 AI 平台工具链。
- H：Python/Go、数据结构与算法；Linux 与 Git；本科/硕士在读。
- B：Ray/Kubernetes；vLLM/SGLang/llama.cpp 源码与原理；PyTorch/TensorFlow 工程落地。

## 4. 特殊人才计划（N=6，单列）

这些岗位可证明公司正在投入哪些技术问题，但不能与普通本科/硕士校招混算门槛。尤其阿里星的部分具体 JD 明确要求博士。

### P1 快手｜快Star｜大模型高性能推理算子工程师

- 类型：27 届 Special Offer 校招；上海/北京。
- 日期：投递起始 2026-07-07，截止 2026-12-31；采集 2026-08-04；状态 `当前开放`。
- 来源 B：[牛客 JD](https://www.nowcoder.com/jobs/detail/452689)
- D：低 bit 量化、通算融合、高性能 sparse attention 算子、视频/多模态大模型推理。
- H：Linux/Python/算法与数据结构；NSYS/NCU；vLLM/SGLang/TensorRT-LLM/xDiT；分布式推理通信、DeepEP/Triton-distributed。
- B：Hopper/Blackwell 算子；CuTe/TileLang/Triton DSL；低 bit kernel；顶会论文。

### P2 快手｜快Star｜大模型推理/训练优化工程师

- 类型：27 届 Special Offer 校招；北京。
- 日期：投递起始 2026-07-07，截止 2026-12-31；采集 2026-08-04；状态 `当前开放`。
- 来源 B：[牛客 JD](https://www.nowcoder.com/jobs/detail/452715)
- D：AI Compiler、图优化、算子融合、GPU kernel、Codegen、异构硬件推理、日常推理服务部署。
- H：硕士及以上；Python/C++、Linux、算法与数据结构；AI Infra 训推优化实战；vLLM/TensorRT-LLM/MLC-LLM/TensorFlow/PyTorch 至少一种。
- B：CUDA/ROCm、Nsight、GPU/ASIC 算子；XLA/TVM/MLIR/LLVM；顶会论文；二次开发或开源贡献。

### P3 快手｜快Star｜基础大模型推理引擎研发工程师

- 类型：27 届 Special Offer 校招；北京。
- 日期：投递起始 2026-07-07，截止 2026-12-31；采集 2026-08-04；状态 `当前开放`。
- 来源 B：[牛客 JD](https://www.nowcoder.com/jobs/detail/452683)
- D：大模型推理引擎设计研发；开源/自研模型部署；算子与编译优化、异构推理、量化/蒸馏、分布式并行；RL 多样化采样与 generation 性能。
- H：编程能力、数学与学习能力；JD 未把某个具体推理框架或 CUDA 写成硬性要求。
- B：vLLM/SGLang/TRT-LLM 使用或优化；CUDA/Triton GPU 算子开发优化。

### P4 阿里巴巴｜阿里星｜大模型推理 KV Cache 系统：从存储架构到软硬协同的全栈演进

- 类型：阿里星 2027 届实习；杭州/北京；**JD 明确博士在读或即将毕业**。
- 日期：投递起始 2026-04-24，页面给出的截止日 2027-04-24；采集 2026-08-04；状态 `未验证`（牛客同时显示“已结束”）。
- 来源 B：[牛客具体 JD](https://www.nowcoder.com/jobs/detail/446421)；[阿里星官方课题页](https://campus-talent.alibaba.com/campus/alistar)
- D：显存/主存/分布式冷存储多级池、计算存储分离、预取、数据调度、KV 资源治理、量化/压缩/调度、成本与 ROI。
- H：博士；大模型推理/数据库/存储系统实践；分布式系统、存储协议/硬件；C/C++/Python/Go/Rust。
- B：KV Cache 研究/落地；vLLM/SGLang 或数据库/存储开源；Redis/Alluxio/JuiceFS；NVLink/RDMA/NCCL/GPU Direct；顶会论文。

### P5 阿里巴巴｜阿里星｜KV Cache 分布式存储的网络优化

- 类型：阿里星 2027 届实习；杭州。
- 日期：投递起始 2026-04-24，页面给出的截止日 2027-04-24；采集 2026-08-04；状态 `未验证`（牛客同时显示“已结束”）。
- 来源 B：[牛客具体 JD](https://www.nowcoder.com/jobs/detail/439603)；[阿里星官方课题页](https://campus-talent.alibaba.com/campus/alistar)
- D：KV 传输、RDMA/TCP、MoE/Prefix KV Cache、benchmark/监控、vLLM/HiCache 开源贡献。
- H：GPU 系统/CUDA；PyTorch/vLLM 架构与优化；CUDA/NCCL 通信；大规模分布式系统。
- B：核心开源贡献；系统/HPC 论文；云上 AI 推理优化；NVLink/RDMA 优化。

### P6 阿里巴巴｜阿里星｜大模型推理优化

- 类型：阿里星 2027 届实习；杭州/北京；**JD 明确相关专业博士**。
- 日期：投递起始 2026-04-24，页面给出的截止日 2027-04-24；采集 2026-08-04；状态 `未验证`（牛客同时显示“已结束”）。
- 来源 B：[牛客具体 JD](https://www.nowcoder.com/jobs/detail/439588)；[阿里星官方课题页](https://campus-talent.alibaba.com/campus/alistar)
- D：SGLang 引擎核心模块；Transformer/MoE/DiffusionLLM；低比特量化、投机采样、稀疏、分布式推理；算子/内存/KV 管理；开源维护。
- H：博士；模型推理过程；剪枝/量化/蒸馏/模型并行；TensorFlow/PyTorch/PaddlePaddle；Python/C++/Go。
- B：图优化/HPC；大模型推理优化；政企业务经验。

## 5. 国内社招：只作业务方向证据（N=4）

### S1 百度｜ACG/MaaS｜大模型推理工程师（J101025）

- 类型：社招；北京。
- 日期：发布 2026-07-21；采集 2026-08-04；状态 `当前开放`。
- 来源 A：[百度官方 JD](https://talent.baidu.com/jobs/detail/SOCIAL/336e82e0-307f-49f1-ae1f-4831fb9d570e)
- 业务方向：MaaS 推理部署与服务化、批调度、KV Cache、模型热加载、扩缩容、隔离/负载均衡/重试/熔断、SLA、压测、资源与计费。
- 技术词：Python/Linux/Shell、网络/并发；vLLM/TGI/TensorRT；INT4/INT8、PagedAttention、动态 batching；FastAPI/gRPC、Docker/K8s；GPU/显存/吞吐/延迟。

### S2 百度｜ACG/国产算力｜大模型异构训练推理研发工程师（J96922）

- 类型：社招；上海/深圳。
- 日期：发布 2026-07-21；采集 2026-08-04；状态 `当前开放`。
- 来源 A：[百度官方 JD](https://talent.baidu.com/jobs/detail/SOCIAL/a93e562d-5bb3-4104-9875-9d68a4223335)
- 业务方向：国产 GPU 适配、TP/PP/DP、算子/内核、低精度、性能/精度/稳定性回归；推理侧含调度、KV Cache、量化、多卡/异构。
- 技术词：Python/C/C++、容器/云原生、PyTorch、Megatron-LM/vLLM/SGLang/TensorRT-LLM/DeepSpeed、GPU 架构与显存模型。

### S3 华为｜OTT2 系统部｜官方 requisition 28183（训练/推理优化方向）

- 类型：社招；北京；官方静态页/索引未暴露岗位标题，**标题未验证，不自行补写**。
- 日期：官方页当前存在；采集 2026-08-04；状态 `未验证`；**精确发布日期未验证**。
- 来源 A：[华为官方 JD](https://career.huawei.com/reccampportal/portal5/social-recruitment-detail.html?dataSource=1&jobId=28183)
- 业务方向：国产算力上的量化、KV 压缩、投机推理、P/D 分离、大 EP MoE；融合算子；性能分析；推理服务引擎/框架。
- 技术词：Python/C++、系统/软件/集合通信、vLLM/SGLang、GPU/国产卡算子；同时含训练/RL，属于训推混合。

### S4 美团｜团队未披露｜大模型推理优化工程师

- 类型：社招；北京。
- 日期：页面显示已结束；采集 2026-08-04；状态 `未验证`；**投递起止/发布日期未验证**。
- 来源 B：[牛客 JD](https://www.nowcoder.com/jobs/detail/420726)
- 业务方向：GPU/NPU 推理性能、CUDA/Triton/AscendC 算子、模型-框架协同。
- 技术词：Python/C++、HPC、多线程/分布式、PyTorch/TensorFlow、TensorRT/OneFlow/ONNX Runtime、量化/剪枝/蒸馏。

## 6. 未进入统计的补充记录

1. [字节 Research Engineer / Scientist - Storage for LLM（A244964）](https://joinbytedance.com/search/7499631716416932103)：官方，San Jose 社招，状态 `当前开放`，采集 2026-08-04，精确发布日期未验证。职责是跨 GPU/节点分布式 KV 层、eviction/一致性/分片复制、cache-aware scheduling、RDMA/GDR；因美国地点移出国内社招统计，只作业务参照。
2. [NVIDIA Senior Deep Learning Solution Architect（JR2015694）](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Senior-Deep-Learning-Solution-Architect_JR2015694)：官方，北京/上海，状态 `当前开放`，官方仅显示 `Posted 30+ Days Ago`，采集 2026-08-04。职责含 SGLang/vLLM 社区开发、FlexKV 多级 offload/reuse 和分布式训练性能；因岗位族是资深 Solution Architecture、不是核心研发职位，移出国内推理研发社招矩阵，仅作团队技术动作参照。
3. [字节 2027 AI Compute + DPU 博士专项](https://joinbytedance.com/search/7633538176269306117)：官方、2027 Start、PhD、Seattle；业务明确含 KV cache systems、multimodal serving、advanced scheduling、disaggregated execution、RDMA/DPDK/NCCL。因海外地点且为博士专项，不与国内普通校招计数。
4. [NVIDIA AI Inference Performance Engineer - New College Grad 2026](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/AI-Inference-Performance-Engineer---New-College-Grad-2026_JR2014441)：官方、Santa Clara；职责含 agent/multi-turn workload、量化、调度、内存与分布式推理。因不在国内地点，不计入国内样本。
5. [快手可灵平台算法工程实习生](https://watchjobs.net/zh/explore/job/kwai_31196/%E5%8F%AF%E7%81%B5%E5%B9%B3%E5%8F%B0%E7%AE%97%E6%B3%95%E5%B7%A5%E7%A8%8B%E5%AE%9E%E4%B9%A0%E7%94%9F-%E5%BF%AB%E6%89%8B)：约 2026-07，职责含模型服务框架、vLLM/SGLang 和软硬协同性能优化；只有聚合镜像可读，精确官方职位 ID/日期未取到，故不计数。
6. [快手高性能 GPU 调度推理研发实习生](https://watchjobs.net/zh/explore/job/kwai_30751/%E9%AB%98%E6%80%A7%E8%83%BDGPU%E8%B0%83%E5%BA%A6%E6%8E%A8%E7%90%86%E7%A0%94%E5%8F%91%E5%AE%9E%E4%B9%A0%E7%94%9F-%E5%8F%AF%E7%81%B5AI%E4%B8%93%E9%A1%B9-%E5%BF%AB%E6%89%8B)：约 2026-06，职责含万卡 GPU 调度、混部、弹性伸缩、vLLM/SGLang、Kubernetes；同样因只有聚合镜像可读而不计数。

## 7. 关键词频率矩阵

### 7.1 任职要求中的 H/H*/B

单元格为 `H/H*/B`，分母见表头；同一 JD 可同时出现 H 与 B。`H*` 是可选硬路径，不是人人必备。社招列仅描述团队选人画像，禁止用来评价校招生竞争力。

| 归一化关键词 | 常规校招 N=7 | 常规实习 N=11 | 快Star N=3 | 阿里星 N=3 | 国内社招 N=4 |
|---|---:|---:|---:|---:|---:|
| 编程语言/数据结构 | 7/0/0 | 10/0/2 | 3/0/0 | 2/0/0 | 4/0/0 |
| Linux/OS/计算机系统基础 | 3/0/0 | 9/0/0 | 2/0/0 | 2/0/0 | 4/0/0 |
| vLLM/SGLang/TRT-LLM 等推理引擎 | 2/1/3 | 2/2/4 | 1/1/1 | 1/0/1 | 4/0/0 |
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

### 7.2 工作职责/业务方向中的 D

这里统计“该技术是工作内容”，而非“应聘者必须已掌握”。

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

### 7.3 只基于信号 A 可下的结论

1. **普通学生岗位的工作面与硬门槛不是一回事。** 在常规校招+实习 N=18 中，KV/Prefix/offload 是 8/18 条的工作内容，但只有 1/18 作为所有人必备的 H，另有 3/18 作为 B；没有 H*。它更像真实业务方向和差异化项目证据，而不是统一筛选门槛。
2. **最稳定的筛选底座仍是编程与系统基础。** 编程/数据结构为 H 的 17/18，Linux/系统基础为 H 的 12/18。推理引擎只有 H=4、H*=3、B=7；DL 框架为 H=6、H*=3、B=3。把 H* 混进 H 会明显夸大“人人必须会框架源码”的程度。
3. **推理优化与分布式是稳定工作面，但硬门槛分层明显。** 常规学生岗中，推理优化 D=18/18、H=7、B=2；分布式/并行/通信 D=13/18、H=6、H*=2、B=5。职责高频不等于每个岗位都以同样深度筛选。
4. **CUDA 是岗位分层器，不是全市场统一前置。** 常规学生岗 CUDA/GPU/kernel 为 D=15/18、H=5、B=8。纯引擎、异构、算子岗更容易写成 H；Serving/backend 岗更常放在 B 或职责背景。
5. **量化、投机解码与可靠性仍多为工作内容或加分。** 常规学生岗：量化 D=6、H=2、B=2；投机解码 D=3、H=0、B=1；可靠性/可观测性 D=9、H=0、B=1。Profiling 则是 D=10，但只有 H=2、B=1，说明“会测量”常被工作默认承接，却未必单独写成筛选词。
6. **特殊人才计划必须隔离。** 阿里星 3 条中 2 条明确博士，且 3 条都围绕 KV/网络/推理引擎专项；快Star 3 条覆盖 kernel、compiler 与基础推理引擎。它们能证明业务投入，不能代替普通校招市场画像。
7. **当前开放与趋势窗口不可混读。** 18 条常规学生岗里，当前开放 10、近期截止 7、状态未验证 1；本矩阵用于描述一轮招聘窗口，不能据此声称 18 条此刻都可投。常规校招仍有百度 5/7 的公司偏差，跨公司结论应优先看“方向是否重复出现”，不把原始频数当总体市场占比。

## 8. 无法完全验证的条目

主统计 28 条中，共 7 条没有可确认的精确发布日期，均已给出采集日期 2026-08-04：

1. 小红书 `大模型训练/压缩/推理 Infra 研发工程师`（官方页仍有投递入口，无发布日期）。
2. NVIDIA `Solution Architecture Intern, AI in Industry - 2026`（官方只显示 `30+ Days Ago`）。
3. 字节 `AI Infra 后端开发实习生-计算`（官方页面存在，正文由牛客招聘账号页补足）。
4. MiniMax `大模型推理研发实习生-2027 届`（牛客显示已结束，无投递起止日期）。
5. SmartX `AI 训练推理平台研发实习生`（牛客显示已结束，无投递起止日期）。
6. 华为 requisition 28183（官方页面存在；精确发布日期和岗位标题未被静态页/索引暴露）。
7. 美团 `大模型推理优化工程师`（牛客显示已结束，无投递起止日期）。

另有 4 个阿里职位（普通实习 1、阿里星 3）出现“投递截止在 2027 年”与页面“已结束”同时存在的状态冲突，统一标为 `未验证`，不能据此声称仍开放。

## 9. 局限性（信号 A）

- 样本不是随机抽样，百度官方站可索引性最好，快手/阿里在牛客上的发布密度高，因而公司权重不均。
- 字节、快手、腾讯等官网大量使用客户端渲染；无法读取详情时，本轮宁可记录“未验证”或使用公司招聘账号的牛客页，也不补写缺失内容。
- 近期 2027 校招仍在滚动开放，2026-08-04 之后可能新增岗位；本文件是时间点快照。
- JD 的 `H/H*/B` 是文本编码，不等价于真实筛选权重；公司可能在简历筛选或面试中考察未写入 JD 的能力。
- 社招只用于说明团队业务面；其年限、深度和独立负责要求不能用于评价学生竞争力。
- A-Star、快Star、全球博士专项的选人机制与普通校招不同，已单列；若混合统计会系统性高估博士、论文、CUDA/kernel、RDMA 的普遍性。
