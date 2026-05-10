# Research: Horizontal and Vertical Offload Lifecycle Instrumentation

## Decision 1: Trace Exposure Strategy

- Decision: Expose horizontal and vertical offload lifecycle events as trace/ledger entries at the environment boundary, not as policy or metric changes.
- Rationale: The current audit failure is observability-driven, not a reward or policy semantics issue.
- Alternatives considered: Leaving the audit unchanged and calling the traces unsupported; this would preserve ambiguity and block diagnosis.

## Decision 2: Behavior-Change Boundary

- Decision: Preserve simulator behavior by default and allow behavior changes only if a test proves a specific bug.
- Rationale: The feature is meant to add observability, not rewrite simulator semantics.
- Alternatives considered: Broad simulator cleanup alongside instrumentation; rejected because it would widen scope and risk regressions.

## Decision 3: Audit Classification Rule

- Decision: Reclassify offload cases away from unsupported-trace once lifecycle visibility exists; any residual blocker must be labeled explicitly as topology legality, adjacency unrecoverability, or another documented non-observability reason.
- Rationale: This keeps the audit honest and prevents observability gaps from masking real topology issues.
- Alternatives considered: Keeping the combined unsupported label; rejected because it would hide the distinction between visibility and legality.

## Decision 4: Regression Protection

- Decision: Add regression checks for Feature 019 timeout/drop behavior and Feature 024 local-compute and deterministic ordering.
- Rationale: Instrumentation must not destabilize already repaired lifecycle cases.
- Alternatives considered: Relying on manual review alone; rejected because it would not catch subtle trace-side regressions.

## Decision 5: Topology Boundary

- Decision: Preserve Feature 025 conclusions that Figure 7 adjacency and legal horizontal destinations are unrecoverable from paper evidence.
- Rationale: Trace instrumentation must not be used as a back door to invent topology or paper validation.
- Alternatives considered: Claiming the richer traces validate destination legality; rejected as fabricated paper evidence.

