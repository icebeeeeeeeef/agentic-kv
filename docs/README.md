# Documentation map

## Authority

| Layer | Path | Meaning |
|---|---|---|
| Methodology constitution | project/PROJECT_EVALUATION_SOP.md | Stable project-evaluation method: position value, execution-path ownership, evidence, runtime completeness and claim boundaries |
| Canonical project contract | project/PROJECT_PLAN.md | Current problem, ownership, Gate, STOP and experiment contract; must conform to the SOP on methodology |
| Current state | ../STATUS.md | What has actually been implemented or validated |
| Short-term tasks | ../TASKS.md | Only work explicitly added by the user; not a roadmap |
| Implementation contracts/evidence | implementation/ | Pinned-source facts, execution contracts and retained runtime artifacts; low-level contracts cannot rewrite higher Gate/STOP or current state |
| Observability and measurement contract | [implementation/OBSERVABILITY_AND_MEASUREMENT_CONTRACT.md](implementation/OBSERVABILITY_AND_MEASUREMENT_CONTRACT.md) | Activation-gated event, ID/correlation, metric, missing/out-of-order/right-censoring, source-of-truth and non-interference contract; its existence does not mean trace is implemented or authorize D1, a behavior hook or a candidate; actual state remains in `STATUS.md` |
| Runtime invariant and failure matrix | [implementation/RUNTIME_INVARIANT_FAILURE_MATRIX.md](implementation/RUNTIME_INVARIANT_FAILURE_MATRIX.md) | Pre-implementation invariant, state-owner, failure-terminal, cleanup-responsibility and future-validation contract; `ROADMAP` scenarios are not current runtime coverage and require retained run artifacts |
| First-C0 deployment retrospective | [implementation/G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md](implementation/G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md) | Scoped retrospective of the blockers, minimal fixes and known-working combination observed in first-C0 r1–r6; not a new Gate, general dependency/compatibility lock, fresh-C1 qualification or performance evidence |
| Performance investigation method | [performance/PERFORMANCE_ENGINEERING_PLAYBOOK.md](performance/PERFORMANCE_ENGINEERING_PLAYBOOK.md) | Stable method from symptom, path truth and competing hypotheses through tool escalation, action—mediator—endpoint evidence and legal STOP; does not define Gate/current state, authorize trace/hook/candidate or rewrite `PROJECT_PLAN.md` |
| Performance path and optimization map | [performance/PERFORMANCE_PATH_AND_OPTIMIZATION_MAP.md](performance/PERFORMANCE_PATH_AND_OPTIMIZATION_MAP.md) | Project-specific service/write/restore paths, ownership, observability, critical-path relations and optimization surfaces; observable does not mean modifiable, upstream nodes are not owned code, and the map defines neither Gate nor current state |
| Performance RCA casebook | [performance/RCA_CASEBOOK.md](performance/RCA_CASEBOOK.md) | Admission, numbering, lifecycle, index and sealing rules for real performance incidents; `DRAFT` / `SEALED` / `SUPERSEDED` are case lifecycles, not Gate outcomes or claim states, and the index is authoritative for whether a real RCA exists |
| Performance RCA template | [performance/RCA_TEMPLATE.md](performance/RCA_TEMPLATE.md) | Template copied only for a real anomaly with citable evidence; it is not an existing RCA and does not imply that `RCA-0001` exists |
| Durable decisions | project/DECISIONS.md | Owner-confirmed constraints on implementation/claim; `DECIDED` is not runtime evidence or a substitute for Gate/STOP |
| Patch provenance | ../patches/README.md | Reviewable ordered upstream patch series; `PLANNED` entries are not patches or runtime evidence |
| Interview defense | project/INTERVIEW_QA.md | Evidence-derived Q&A; cannot upgrade claim state |
| Market research | research/JOB_MARKET_FIT.md | Hiring-market evidence and JD mapping; its earlier FP8/eviction scope is not current project instruction |
| Selection history | research/PROJECT_SELECTION_REVIEW.md | Historical adversarial selection record; its local-retention/eviction/FP8 proposal is superseded by the canonical L3-admission scope |
| G0 research contract | research/G0_PRELAUNCH_RESEARCH_CONTRACT.md | Delegable pre-launch source and runtime-contract investigations; not evidence of completion |
| G0 research results | research/G0_PRELAUNCH_RESEARCH_RESULTS.md | Fixed-source investigation results and explicit runtime blockers |
| Evidence | research/evidence/ | JD, interview, team-action and prior-art ledgers |
| Historical review | research/reviews/ | Adversarial reviews; may contain superseded proposals |
| Source material | research/source-material/ | Earlier user-provided or legacy documents |

Historical and source-material files are retained for provenance. They are not current project instructions. The SOP governs methodological conflicts; STATUS remains the factual record of what is actually completed or validated.

## Task-oriented reading routes

- Take over the project or determine current state: [Project Evaluation SOP](project/PROJECT_EVALUATION_SOP.md) → [Project Plan](project/PROJECT_PLAN.md) → [Status](../STATUS.md) → [Durable Decisions](project/DECISIONS.md).
- Prepare a fresh C1: [Status](../STATUS.md) → [C0 Restore Qualification Contract](implementation/G0_C0_RESTORE_QUALIFICATION_CONTRACT.md) → [D14 Survival Preregistration Contract](implementation/G0_D14_SURVIVAL_PREREGISTRATION_CONTRACT.md) → [First-C0 Deployment Retrospective](implementation/G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md).
- Investigate a performance anomaly: [Performance Engineering Playbook](performance/PERFORMANCE_ENGINEERING_PLAYBOOK.md) → [Performance Path and Optimization Map](performance/PERFORMANCE_PATH_AND_OPTIMIZATION_MAP.md), then the [Observability and Measurement Contract](implementation/OBSERVABILITY_AND_MEASUREMENT_CONTRACT.md) and [Runtime Invariant and Failure Matrix](implementation/RUNTIME_INVARIANT_FAILURE_MATRIX.md); create a real case only through the [RCA Casebook](performance/RCA_CASEBOOK.md) and [RCA Template](performance/RCA_TEMPLATE.md).
- Check first-C0 runtime facts: [Status](../STATUS.md) → [C0 Restore Qualification Contract](implementation/G0_C0_RESTORE_QUALIFICATION_CONTRACT.md) → [First-C0 Deployment Retrospective](implementation/G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md).

## Claim-state rule

- ROADMAP：planned only
- SOURCE_VERIFIED：fact observed in a pinned upstream source
- IMPLEMENTED_UNVALIDATED：code exists, required experiment not yet passed
- EXPERIMENTALLY_VALIDATED：reproducible result under an explicit manifest

No file inherits a higher state merely because it was migrated into this repository.

## Research-review qualifier

`RESEARCH_REVIEW / SOURCE_TO_REVERIFY` may be attached to an external discussion, historical PR/benchmark, or upstream dynamic that has not been independently checked against the repository's pinned source/runtime. It is a source-status qualifier, **not** a fifth claim state: it can motivate a source audit or experiment, but cannot support an upstream fact, compatibility claim, runtime result, or performance conclusion. The current use is documented in [D14](project/DECISIONS.md#d14--shared-l3-publication-admission-收敛与替代攻击).
