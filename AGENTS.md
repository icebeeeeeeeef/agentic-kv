# AGENTS.md

## 先读什么

任何新对话或 agent 在修改本仓库前，必须依次完整阅读：

1. README.md
2. STATUS.md
3. docs/project/PROJECT_PLAN.md
4. docs/README.md

只在任务需要时再读取 research/evidence 或 historical reviews。不要用旧评审覆盖 canonical plan。

## 权威顺序

1. docs/project/PROJECT_PLAN.md：项目宪法与 Gate
2. STATUS.md：实际完成状态
3. docs/implementation 下的 pinned-source/runtime 证据
4. docs/research/JOB_MARKET_FIT.md 与 PROJECT_SELECTION_REVIEW.md
5. docs/research/evidence
6. docs/research/reviews 与 source-material

低层文件不得反向升级高层 claim state。

## 当前唯一主线

唯一 behavior-changing mechanism 是：

    L2 DMA ack 完成
      → prefix-closure 检查
      → ADMIT_TO_L3 | DROP
      → upstream Mooncake Put 或直接返回

Prefix-DAG 是 workload；Mooncake 是 upstream shared-L3 substrate；conditional admission ledger 只是给定 eligibility stream 的 action/payload 对账与 rejection filter。

## 实施纪律

- 任何源码事实都绑定明确 commit；先读真实源码，再回答或修改。
- 当前 SGLang source anchor 是 b058dc910619c9d4bce9e9e24117104ffc491fa6；Mooncake exact commit 尚待 G0 pin。
- 行为 hook 与纯观测 instrumentation 分开设计、分开测试。
- 固定 L2 指算法、容量、配置、write-through 和 eviction 实现固定；不要求不同 treatment 的 L2 内容或 event sequence 相同。
- 不使用某一 arm 的 eligibility stream 作为另一 policy 的闭环反事实。
- G2b conditional ledger 只能拒绝候选；G3 双 worker 在线 A/B 是唯一策略裁决。
- 每个性能数字必须能追到 manifest、commit、raw log 和统计方法。
- 负结果、losing workload 和 STOP 与正结果同等重要。
- 不把 upstream SGLang/Mooncake 能力写成个人实现。

## Scope 默认拒绝

除非先修改 PROJECT_PLAN.md 并重新过 Gate，否则不得加入：

- L1/L2 或 L3 eviction
- router / affinity / load balancing
- SSD L4 或第二 cache backend
- RDMA/GDR/NIXL 数据面
- KV 量化、稀疏化、kernel
- metadata HA、复制、故障恢复
- PD disaggregation、Kubernetes、GPUStack
- 通用 policy DSL、动态 RPC policy service

## 修改与验证

- 小步修改，避免提前抽象。
- 新功能先写最小失败测试，再实现。
- 修改 claim、Gate 或实验口径时，必须同步 STATUS.md。
- 声称完成前运行 make check，并报告实际命令和结果。
- 不提交私有 source material；private 目录已由 .gitignore 保护。
