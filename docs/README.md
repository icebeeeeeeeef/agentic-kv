# Documentation map

## Authority

| Layer | Path | Meaning |
|---|---|---|
| Methodology constitution | project/PROJECT_EVALUATION_SOP.md | Stable project-evaluation method: position value, execution-path ownership, evidence, runtime completeness and claim boundaries |
| Canonical project contract | project/PROJECT_PLAN.md | Current problem, ownership, Gate, STOP and experiment contract; must conform to the SOP on methodology |
| Current state | ../STATUS.md | What has actually been implemented or validated |
| Durable decisions | project/DECISIONS.md | Owner-confirmed constraints on implementation/claim; not runtime evidence or a substitute for Gate/STOP |
| Patch provenance | ../patches/README.md | Reviewable ordered upstream patch series; `PLANNED` entries are not patches or runtime evidence |
| Short-term tasks | ../TASKS.md | Only work explicitly added by the user; not a roadmap |
| Interview defense | project/INTERVIEW_QA.md | Evidence-derived Q&A; cannot upgrade claim state |
| Market research | research/JOB_MARKET_FIT.md | Hiring-market evidence and JD mapping; its earlier FP8/eviction scope is not current project instruction |
| Selection history | research/PROJECT_SELECTION_REVIEW.md | Historical adversarial selection record; its local-retention/eviction/FP8 proposal is superseded by the canonical L3-admission scope |
| G0 research contract | research/G0_PRELAUNCH_RESEARCH_CONTRACT.md | Delegable pre-launch source and runtime-contract investigations; not evidence of completion |
| G0 research results | research/G0_PRELAUNCH_RESEARCH_RESULTS.md | Fixed-source investigation results and explicit runtime blockers |
| Evidence | research/evidence/ | JD, interview, team-action and prior-art ledgers |
| Historical review | research/reviews/ | Adversarial reviews; may contain superseded proposals |
| Source material | research/source-material/ | Earlier user-provided or legacy documents |

Historical and source-material files are retained for provenance. They are not current project instructions. The SOP governs methodological conflicts; STATUS remains the factual record of what is actually completed or validated.

## Claim-state rule

- ROADMAP：planned only
- SOURCE_VERIFIED：fact observed in a pinned upstream source
- IMPLEMENTED_UNVALIDATED：code exists, required experiment not yet passed
- EXPERIMENTALLY_VALIDATED：reproducible result under an explicit manifest

No file inherits a higher state merely because it was migrated into this repository.
