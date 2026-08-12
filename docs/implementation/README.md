# Implementation evidence and G0 execution materials

Documents in this directory must distinguish pinned-source facts, implementation plans,
open decisions, and runtime artifacts. None of them may upgrade claim state by themselves.

- [G0 source/runtime audit](G0_SOURCE_RUNTIME_AUDIT.md): pinned upstream source facts,
  observation limits, and the precise behavior seam.
- [G0 execution plan](G0_EXECUTION_PLAN.md): delegated runtime procedure and acceptance matrix.
- [C0 Restore Qualification Contract](G0_C0_RESTORE_QUALIFICATION_CONTRACT.md): owner-decided
  request/control/observation contract for `RESTORE_PATH_PASS` and
  `REMOTE_VALUE_SURVIVES`; not a runtime result.
- [D14 Survival Preregistration Contract](G0_D14_SURVIVAL_PREREGISTRATION_CONTRACT.md):
  owner-decided C1 source-audit, S1–S3 and X* freezing contract; not a runtime result.
- [G0 First-C0 Minimal Execution Contract](G0_PRE_RENTAL_EXECUTION_CONTRACT.md):
  owner-decided content-addressed input, one-shot runbook/raw capture/off-host handoff and
  rental-day admission boundary; not an implemented harness, a rental authorization, or runtime evidence.
- [T5 local preflight STOP](G0_T5_LOCAL_PREFLIGHT_STOP.md): retained environment failure
  artifact; blocks T6/T7 on this executor but does not decide target-Linux compatibility.
- [upstream patch provenance](../../patches/README.md): repository-owned ordered patch-series
  contract for external checkouts; current entries are `PLANNED`, not implemented patches.
- [G0 decision discussion list](G0_DISCUSSION_LIST.md): historical discussion prompts and
  unresolved implementation questions; D1/D9/D10/D12/D13/D14/D15/D16/D17/D18 are resolved and link to the durable
  [decision record](../project/DECISIONS.md). It is not runtime evidence or current authority.
- [G0 deployment environment contract](G0_DEPLOYMENT_ENVIRONMENT_DISCUSSION.md): an
  owner-decided but non-authoritative contract for the first TCP C0/C1 cohorts, ephemeral
  evidence, candidate/rollback constraints, and owner-gated conditions for any future RDMA
  scope review; it neither proves compatibility nor authorizes a data-plane expansion.

Do not copy planning statements here as if they were completed work. Runtime validation
requires retained artifacts and the corresponding Gate, not a source audit or `make check`.
