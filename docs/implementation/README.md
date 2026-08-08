# Implementation evidence and G0 execution materials

Documents in this directory must distinguish pinned-source facts, implementation plans,
open decisions, and runtime artifacts. None of them may upgrade claim state by themselves.

- [G0 source/runtime audit](G0_SOURCE_RUNTIME_AUDIT.md): pinned upstream source facts,
  observation limits, and the precise behavior seam.
- [G0 execution plan](G0_EXECUTION_PLAN.md): delegated runtime procedure and acceptance matrix.
- [T5 local preflight STOP](G0_T5_LOCAL_PREFLIGHT_STOP.md): retained environment failure
  artifact; blocks T6/T7 on this executor but does not decide target-Linux compatibility.
- [upstream patch provenance](../../patches/README.md): repository-owned ordered patch-series
  contract for external checkouts; current entries are `PLANNED`, not implemented patches.
- [G0 decision discussion list](G0_DISCUSSION_LIST.md): historical discussion prompts and
  unresolved implementation questions; D1/D9/D10 are resolved and link to the durable
  [decision record](../project/DECISIONS.md). It is not runtime evidence or current authority.

Do not copy planning statements here as if they were completed work. Runtime validation
requires retained artifacts and the corresponding Gate, not a source audit or `make check`.
