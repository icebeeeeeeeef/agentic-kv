# Evidence Ledger

本文件只记录已经存在的 evidence artifact 与 claim traceability。它不定义 Gate、STOP、scope 或当前状态，不创建新的 claim state，也不把 evidence summary 变成新的事实来源。

- 实际项目状态以 [`STATUS.md`](../STATUS.md) 为准。
- owner decision 以 [`docs/project/DECISIONS.md`](../docs/project/DECISIONS.md) 为准。
- Gate、STOP 与实验合同以 [`docs/project/PROJECT_PLAN.md`](../docs/project/PROJECT_PLAN.md) 为准。
- 下表中的 checksum 只标识既有 artifact；artifact 内容与 verdict 仍须按对应 implementation evidence 复核。

Traceability chain：

```text
claim -> run/source audit -> artifact -> SHA-256 -> analysis/verdict -> allowed claim ceiling
run   -> supported claim -> affected Gate/decision
```

## Claim → Evidence Index

| Claim | State | Run / source | Evidence | Analysis / verdict | Allowed statement | Forbidden statement |
|---|---|---|---|---|---|---|
| SGLang pinned source seam: L2 ack 后、`write_storage` 前存在 behavior-changing seam | `SOURCE_VERIFIED` | SGLang `b058dc910619c9d4bce9e9e24117104ffc491fa6`; no runtime run | [`G0_SOURCE_RUNTIME_AUDIT.md`](../docs/implementation/G0_SOURCE_RUNTIME_AUDIT.md) | 固定源码审计定位了 seam 及其 queue/protection 边界；source audit 不是 hook runtime evidence | “source audit verified the seam” | “implemented or runtime-validated the hook” |
| first-C0 stock shared-L3 restore qualification | `EXPERIMENTALLY_VALIDATED` (scoped) | `first-c0-20260813-r6` | `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r6/c0-raw-evidence.tar`; SHA-256 `a155afe674d7a0fa76ad4e14a3b02a5cbeabf3ba22b437fd67ce79310b43f35c`; [`deployment retrospective`](../docs/implementation/G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md); [`C0 contract`](../docs/implementation/G0_C0_RESTORE_QUALIFICATION_CONTRACT.md) | `execution_status=EXECUTED`; `gate_outcome=PASS`; `RESTORE_PATH_PASS=PASS`; `REMOTE_VALUE_SURVIVES=PASS` | “the fixed r6 stock TCP/direct-I/O/L20 topology demonstrated restore qualification and remote KV substituted non-zero prefill tokens” | “fresh C1 or S1 passed”; “complete G0 passed”; “performance, Goodput or TTFT improved”; “general compatibility”; “cross-GPU, multi-host or production validated” |
| trace correlation and D1 new-physical-Put observation | `ROADMAP` | none | No implementation or runtime artifact | D1 defines an allowed future observation boundary; no trace/hook is implemented or validated | “planned and gated by the existing contract” | “trace correlation exists”; “new physical Put payload is measured” |
| `ALWAYS_ADMIT` / `ALWAYS_DROP` behavior hook | `ROADMAP` | none | No implementation or runtime artifact | Source seam exists; forced-action behavior and async lifecycle remain untested | “planned forced-action validation” | “hook implemented”; “DROP avoids Put at runtime”; “ALWAYS_ADMIT is upstream-equivalent” |
| candidate policy and conditional admission ledger | `ROADMAP` | none | No implementation or runtime artifact | Candidate design remains frozen; ledger is gated behind G2a and O1 | “candidate and ledger remain gated roadmap work” | “candidate exists or wins”; “ledger proves cross-policy causality” |
| S1–S3 outcome, Goodput improvement, TTFT improvement, or payload-efficiency result | `ROADMAP` | none | No result artifact | first-C0 r6 is only restore qualification / S1 input | “future experiment contract only” | Any positive or negative S1–S3 outcome; any Goodput, TTFT, or payload-efficiency result |

`SOURCE_VERIFIED` evidence has a pinned source commit rather than a runtime run or raw-archive checksum. `ROADMAP` rows intentionally have no run, artifact, checksum, or outcome; this ledger does not create future-result entries.

## Run Index

| Run | Execution status | Artifact / SHA-256 | Supported claim | Gate / decision impact |
|---|---|---|---|---|
| `first-c0-20260813-r1` | Pre-classification deployment/install attempt; no Gate status is assigned retroactively | `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r1/preflight-blocker-evidence.tar`<br>SHA-256 `460d64e5b2d3a97b0c1b88622bebfa95ed22aac7a01007ca9fb5e31a16eed955` | Preserves the `cargo is required` installation blocker and the evidence-driven hardening input | No C0 predicate or Gate outcome; does not support restore or performance claims |
| `first-c0-20260813-r2` | `BLOCKED_BEFORE_C0`; predicates `NOT_EVALUATED` | `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r2/preflight-blocker-evidence.tar`<br>SHA-256 `3aa100909584371a4825d39c943d34b983be30173dac391097b178d420aec5f8` | Preserves target-admission blockers, including missing Python headers; informs the next fresh runbook | No C0 Gate outcome; does not support restore or performance claims |
| `first-c0-20260813-r3` | `BLOCKED_BEFORE_C0`; predicates `NOT_EVALUATED` | `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r3/preflight-blocker-evidence.tar`<br>SHA-256 `a3bbce6a5d642c8bf5961b5ad1bbe1da9483c46fb83a9e82b5833ea83b4833b8` | Preserves the launch-environment `ninja` discovery blocker; informs the next fresh runbook | No C0 Gate outcome; does not support restore or performance claims |
| `first-c0-20260813-r4` | `BLOCKED_BEFORE_C0`; predicates `NOT_EVALUATED` | `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r4/preflight-blocker-evidence.tar`<br>SHA-256 `075adaacb1caaf1e97b91ad94d293501d1fa662773f041fe14ce01f6264717fa` | Preserves the missing OpenSSL headers blocker; informs the next fresh runbook | No C0 Gate outcome; does not support restore or performance claims |
| `first-c0-20260813-r5` | `BLOCKED_BEFORE_C0`; predicates `NOT_EVALUATED` | `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r5/preflight-blocker-evidence.tar`<br>SHA-256 `15a9f081f22d967acbec9bc6d33ecde52305e9c520dfc773ca44a155258b326a` | Preserves the stock kernel D2H segfault before response/completed Put; supports using the separately admitted stock direct-I/O path in a fresh run | No C0 Gate outcome; does not support restore or performance claims |
| `first-c0-20260813-r6` | `EXECUTED / PASS`; `RESTORE_PATH_PASS=PASS`; `REMOTE_VALUE_SURVIVES=PASS` | `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r6/c0-raw-evidence.tar`<br>SHA-256 `a155afe674d7a0fa76ad4e14a3b02a5cbeabf3ba22b437fd67ce79310b43f35c` | Supports only first-C0 scoped stock restore qualification and non-zero prefill substitution in the recorded topology | Qualifies the restore premise and permits `next_action=REVIEW_C1`; cannot substitute fresh C1, S1, complete G0, trace/hook/candidate, or performance evidence |

Run classifications, blocker analysis, artifact locations, and independently matched readback hashes are derived from [`G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md`](../docs/implementation/G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md). The r6 predicate interpretation is bounded by [`G0_C0_RESTORE_QUALIFICATION_CONTRACT.md`](../docs/implementation/G0_C0_RESTORE_QUALIFICATION_CONTRACT.md) and the current state in [`STATUS.md`](../STATUS.md).

## Evidence Rules

### Artifact before summary

Raw retained artifact and its verified checksum take precedence over a manual summary. A checksum establishes artifact identity and integrity; it does not by itself prove the artifact satisfies a predicate. The applicable contract and analysis/verdict must still be consulted.

### Gate outcome and claim state are separate

`execution_status`, `gate_outcome`, and claim state answer different questions. `PASS` upgrades only the specific claim supported by that run; it does not automatically upgrade all claims, a broader Gate, or a performance conclusion.

### Scoped runtime evidence does not extrapolate

The first-C0 r6 artifact is bound to its recorded stock TCP/direct-I/O/L20 topology and sequential, independently cold worker lifecycles. It cannot substitute a fresh C1 cohort or support cross-GPU, multi-host, production, general compatibility, S1, complete G0, Goodput, TTFT, or payload-efficiency claims.

### Failure and blocker evidence is retained

Deployment blockers and negative evidence remain indexed alongside successful runs. A run stopped before a C0 request chain is `BLOCKED_BEFORE_C0` with predicates `NOT_EVALUATED`, not `C0 FAIL`. The r1 pre-classification attempt remains unclassified rather than being assigned a Gate status retroactively.
