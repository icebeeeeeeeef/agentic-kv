# Implementation evidence and G0 execution materials

Documents in this directory must distinguish pinned-source facts, implementation plans,
open decisions, and runtime artifacts. None of them may upgrade claim state by themselves.

- [G0 source/runtime audit](G0_SOURCE_RUNTIME_AUDIT.md): pinned upstream source facts,
  observation limits, and the precise behavior seam.
- [G0 execution plan](G0_EXECUTION_PLAN.md): delegated runtime procedure and acceptance matrix.
- [G0 decision discussion list](G0_DISCUSSION_LIST.md): dependency-ordered unresolved
  decisions to settle before implementation; it is not runtime evidence.

Do not copy planning statements here as if they were completed work. Runtime validation
requires retained artifacts and the corresponding Gate, not a source audit or `make check`.
