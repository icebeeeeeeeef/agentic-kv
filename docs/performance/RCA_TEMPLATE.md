# Agentic-KV Performance RCA Template

> 仅用于已经发生且拥有可引用证据的真实性能、测量或运行时异常。删除所有占位说明后再封存具体案例。

<!-- 创建具体案例时删除本说明：将本文件复制为 docs/performance/rca/RCA-XXXX-<slug>.md。只有异常已发生、可复现且有可引用证据时才能创建案例。所有尖括号、破折号和说明文字均是占位内容，不是项目事实。不存在或不适用的值可写 N/A，但必须解释原因。 -->

# RCA-XXXX：<用症状或问题命名，不提前写根因>

> Case lifecycle: DRAFT
>
> 本案例不修改项目 Gate、STOP、scope 或 claim state；相关变化必须同步到 canonical 文档。

## Metadata

| Field | Value |
|---|---|
| Case ID | RCA-XXXX |
| Lifecycle | DRAFT |
| Opened at | YYYY-MM-DD |
| Sealed at | — |
| Related phase/gate | — |
| Primary symptom | — |
| Primary path | — |
| Affected endpoint | — |
| Scope relation | — |
| Project commit | — |
| SGLang commit | — |
| Mooncake commit | — |
| Baseline run IDs | — |
| Comparison run IDs | — |
| Manifest checksum | — |
| Raw evidence | — |
| Analysis commit | — |
| Profiler state | off / nsys / torch-profiler / ncu / other |
| Claim state before | — |
| Claim state after | — |
| Related decision | — |
| Supersedes | — |
| Superseded by | — |

## 1. Executive Summary

<!-- 创建具体案例时删除本说明：本节最后写。用少量段落说明异常、根因是否确认、根因是否受 admission 控制、采取的行动、最大允许 claim 和最重要限制。调查期间保持 DRAFT；不得只写“性能提升 X%”。 -->

—

## 2. Symptom

<!-- 创建具体案例时删除本说明：记录观察时间、expected、observed、受影响指标、差异大小、出现频率、首次 run、可复现性、workload/regime 边界和调查价值。把异常事实与原因猜测分开。 -->

### Symptom facts

- Observed at：—
- Expected：—
- Observed：—
- Affected metric/endpoint：—
- Effect size and interval：—
- Frequency：—
- First observed run：—
- Reproducibility：—
- Workload/regime boundary：—
- Why this warrants an RCA：—

### Initial interpretation

- 对原因的初始猜测：—
- 该猜测不是异常事实的理由：—

## 3. Reproduction Contract

<!-- 创建具体案例时删除本说明：不得写“使用默认配置”。记录足以重建异常的全部冻结输入；profile run 与 benchmark run 分开。 -->

| Item | Frozen value / evidence |
|---|---|
| Environment and topology | — |
| Project / upstream versions | — |
| Model / tokenizer | — |
| Workload / request / token hash | — |
| Arrival process | — |
| Worker assignment | — |
| L1 / L2 / L3 capacity and configuration | — |
| Store freshness / keyspace isolation | — |
| Policy / config | — |
| Warm-up / measurement / drain | — |
| Measurement and statistical unit | — |
| Profiler on/off and configuration | — |
| Reproduction command | — |
| Repeat budget | — |
| Successful reproduction criterion | — |
| Failed reproduction criterion | — |

## 4. Path Truth

<!-- 创建具体案例时删除本说明：先证明真实请求路径，再解释性能。缺少 path truth 时最大结论是“当前异常无法可靠归因”。 -->

| Check | Evidence | Result / limitation |
|---|---|---|
| Request success | — | — |
| Output correctness | — | — |
| Worker local coldness | — | — |
| L1 / L2 / L3 path | — | — |
| Put / Get terminal | — | — |
| storage-cached / uncached / recomputed token accounting | — | — |
| operation / batch / attempt / object correlation | — | — |
| queue / ref / protection closure | — | — |
| Trace completeness and loss | — | — |
| Paths still not observable | — | — |

**Path-truth verdict:** sufficient for this RCA / insufficient / partially sufficient with stated limitation

## 5. Expected Causal Model

<!-- 创建具体案例时删除本说明：在看区分实验结果前写出预期依赖。区分 source fact、待验证假设、可能 overlap 和不在 critical path 的工作。 -->

```text
action or upstream event
→ runtime / physical mediator
→ resource or useful-work change
→ endpoint
```

- Source-verified arrows：—
- Hypothesized arrows：—
- Potential overlap：—
- Direct request critical path：—
- Shared-resource indirect path：—
- Why the proposed root cause could produce the symptom：—

## 6. Competing Hypotheses

<!-- 创建具体案例时删除本说明：至少保留最可能解释、合理替代解释和测量/环境混淆解释。被证伪的假设不得删除。Final status 只用 supported、weakened、falsified、unresolved。 -->

| ID | Hypothesis | Why plausible | Expected evidence | Discriminating experiment | Falsifier | Final status |
|---|---|---|---|---|---|---|
| H1 | — | — | — | — | — | unresolved |
| H2 | — | — | — | — | — | unresolved |
| H3 | measurement / workload / order / environment confound | — | — | — | — | unresolved |

## 7. Investigation Timeline

<!-- 创建具体案例时删除本说明：按决策顺序保留最初误判、为何合理、什么证据推翻，以及为何升级或停止某工具；不要记录每条 shell 命令。 -->

| Step | Question | Action/tool | Observation | Interpretation at the time | Next decision |
|---|---|---|---|---|---|
| T1 | — | — | — | — | — |

## 8. Discriminating Experiments

<!-- 创建具体案例时删除本说明：每个关键实验单独记录。明确实验是否真的区分假设，区间/噪声是否具有排除能力；canonical signal、valid false 和 INCONCLUSIVE 定义优先。 -->

### Experiment E1：<要区分的问题>

**Hypotheses distinguished**

—

**Control variables**

—

**Only changed variable**

—

**Fresh state / coldness**

—

**Profiler state**

—

**Expected outcomes**

| Hypothesis | Expected observation |
|---|---|
| H1 | — |
| H2 | — |

**Actual runs**

—

**Actual evidence**

—

**Interpretation**

—

**Exclusion power**

—

**Remaining ambiguity / invalidation condition**

—

## 9. Tool and Profile Evidence

<!-- 创建具体案例时删除本说明：解释为何使用该工具和为何需要或不需要下一层工具。profile run 不进入正式 benchmark；没有使用 profiler 时写 N/A 并说明原因。 -->

| Tool | Why used | Capture config | Overhead/limitations | Key observation | Raw artifact |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

- CUDA Graph / eager / execution-mode differences：—
- Profile runs separated from benchmark runs：—
- Multi-rank captures and alignment：—
- Screenshot-to-raw-trace mapping：—
- ncu kernel and shape, if applicable：—

## 10. Source Mapping

<!-- 创建具体案例时删除本说明：绑定 pinned commit，区分 SOURCE_VERIFIED、runtime observed、inference 和 unresolved；这些标签用于证据说明，不创造新 claim state。 -->

```text
Observed stage
→ runtime object
→ source path
→ function/class
→ state transition
```

| Repository | Commit | Path/symbol | Source fact | Runtime evidence | Ownership |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

- SOURCE_VERIFIED：—
- Runtime observed：—
- Inference：—
- Unresolved：—

## 11. Root Cause Status

<!-- 创建具体案例时删除本说明：只有达到根因确认标准时，才把本节标题改为“Root Cause”并填写确定性结论；否则必须保留“根因未确认”。 -->

**根因未确认。**

### Confirmed root cause

—

### Why it explains the symptom

—

### Why competing explanations were rejected

—

### Regime boundary

—

### Remaining uncertainty

—

## 12. Controllability and Scope

<!-- 创建具体案例时删除本说明：回答根因与 Shared-L3 Publication Admission 的控制关系；不得在 RCA 内顺便扩大实现范围。 -->

- Directly controlled by admission：—
- Indirectly affected by admission：—
- Upstream observe-only：—
- Out-of-scope：—
- Blocks the current project：—
- Impact on S1 / S2 / S3 / G2 / G3：—
- Owner decision required：—
- Suitable for upstream issue/handoff：—
- Why scope was not expanded：—

## 13. Fix, Mitigation, or STOP

<!-- 创建具体案例时删除本说明：只保留实际采用的终局。Fix 是范围内最小修改；Mitigation 只降低影响；STOP/Handoff 用于不可控或无裁决权的根因。 -->

### Selected disposition

Fix / Mitigation / STOP / Handoff / No change

### Rationale

- Why selected：—
- Alternatives considered：—
- Why a more complex option was not selected：—
- Rollback：—
- Deletion test：—
- New failure modes：—
- Ownership change：—

## 14. Before/After Validation

<!-- 创建具体案例时删除本说明：没有真实数字时删除未使用行，不得保留伪造值。每行引用 run IDs；profile run 不进入正式表；统计单元是独立 run 或 paired run，不能只报最有利分位数。 -->

| Metric | Baseline | After | Effect | Interval | Materiality threshold | Verdict |
|---|---:|---:|---:|---:|---:|---|
| <真实指标> | — | — | — | — | — | — |

### Action

—

### Mediator

—

### Endpoint

—

### Policy/instrumentation overhead

—

### Correctness

—

### TPOT and resource guardrails

—

### Losing workloads

—

## 15. Manipulation Check

<!-- 创建具体案例时删除本说明：三层未共同成立时，必须降低最大允许结论。 -->

| Layer | Expected change | Observed change | Evidence | Verdict |
|---|---|---|---|---|
| Action | — | — | — | — |
| Physical/runtime mediator | — | — | — | — |
| Resource/useful-work mediator | — | — | — | — |
| Endpoint | — | — | — | — |
| Guardrails | no regression | — | — | — |

**Maximum conclusion if the chain is incomplete:** —

## 16. Correctness and Runtime Invariants

<!-- 创建具体案例时删除本说明：逐项引用证据。不适用时写 N/A 并解释原因，不能用 N/A 掩盖未完成的必要验证。 -->

| Invariant | Evidence | Verdict / N/A reason |
|---|---|---|
| Request success | — | — |
| Output token/hash | — | — |
| L2 correctness | — | — |
| Prefix closure | — | — |
| ALWAYS_ADMIT equivalence, if applicable | — | — |
| ALWAYS_DROP absence oracle, if applicable | — | — |
| Queue terminal | — | — |
| Ongoing backup | — | — |
| Host protection | — | — |
| Buffer/reference | — | — |
| Failure path | — | — |
| Shutdown/detach | — | — |
| Trace loss | — | — |
| Orphan operation | — | — |
| Late callback | — | — |

## 17. Claim Ceiling

<!-- 创建具体案例时删除本说明：从 path truth、mechanism truth、resource truth、payload/capacity efficiency、endpoint performance、external validity 中选择当前证据真正支持的最高层。 -->

**Current maximum allowed claim:** —

**Evidence supporting that ceiling:** —

**Claims explicitly not supported:**

- —

## 18. Retained Artifacts

<!-- 创建具体案例时删除本说明：每个图表都应回到输入和生成脚本；失败 run 和原始证据不得被聚合结果替代。 -->

| Artifact | Location | Checksum | Produced by | Purpose |
|---|---|---|---|---|
| Manifest | — | — | — | Frozen run contract |
| Raw logs | — | — | — | Direct runtime evidence |
| Trace | — | — | — | Lifecycle/path evidence |
| Profile | — | — | — | Diagnostic evidence |
| Analysis input | — | — | — | Reproducible analysis |
| Analysis script | — | — | — | Derivation |
| Derived result | — | — | — | Table/chart/statistics |
| Environment | — | — | — | Runtime identity |
| Output oracle | — | — | — | Correctness |
| Source patch | — | — | — | Fix/instrumentation provenance |
| Test result | — | — | — | Regression evidence |

## 19. Falsified Hypotheses and Negative Results

<!-- 创建具体案例时删除本说明：成功修复后也不得删除本节。保留无效优化、无价值 profiler 路径、losing workload、payload-only、INCONCLUSIVE 和 scope 外限制。 -->

- Falsified hypotheses：—
- Weakened but unresolved hypotheses：—
- Optimizations with no effect：—
- Profiler paths not worth continuing：—
- Workloads that do not support the conclusion：—
- Payload-only results：—
- `INCONCLUSIVE` experiments：—
- Limitations outside the current project：—

## 20. Follow-up and Canonical Updates

<!-- 创建具体案例时删除本说明：只列出后续，不在本 RCA 中越权修改 canonical 合同。 -->

- `STATUS.md` update required：yes / no，理由：—
- Owner decision required：yes / no，理由：—
- `DECISIONS.md` update required：yes / no，理由：—
- Eligible for `INTERVIEW_QA.md` derivation：yes / no，理由：—
- Future Results Index update：yes / no，理由：—
- Cross-case method suitable for Playbook：yes / no，理由：—
- Superseding RCA required：yes / no，理由：—
- Follow-ups explicitly outside this RCA：—

## 21. Seal Checklist

<!-- 创建具体案例时删除本说明：未满足时保持 DRAFT，除非未满足项本身就是正文已解释的不可裁决终局。只有 owner 或当前任务明确授权才能 SEALED。 -->

- [ ] Symptom 可复现或不可复现边界已明确
- [ ] Path truth 足以支持当前结论
- [ ] 竞争假设和 falsifier 已保留
- [ ] 区分实验真正具有排除能力
- [ ] Source mapping 绑定 pinned commit
- [ ] Root cause 或未确认边界写清
- [ ] Controllability 和 scope 已裁决
- [ ] Before/after 使用相同 workload
- [ ] Action、mediator、endpoint 分开报告
- [ ] Correctness 和 TPOT guardrail 已检查
- [ ] Instrumentation/profiler 干扰已排除
- [ ] 负结果和 losing workload 已保留
- [ ] Claim ceiling 与证据一致
- [ ] Raw artifacts、checksum 和 analysis commit 可追溯
- [ ] Canonical 文档需要的后续更新已列出
- [ ] Owner 明确授权 SEALED
