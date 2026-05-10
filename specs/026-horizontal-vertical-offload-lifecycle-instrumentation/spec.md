# Feature Specification: Horizontal and Vertical Offload Lifecycle Instrumentation

**Feature Branch**: `[026-horizontal-vertical-offload-lifecycle-instrumentation]`  
**Created**: 2026-05-10  
**Status**: Draft  
**Input**: User description: "Feature 026 — Horizontal/Vertical Offload Lifecycle Instrumentation."

## Clarifications

### Session 2026-05-10

- Q: How should the differential audit classify offload cases after lifecycle traces become visible? → A: Keep the audit split clean: observability problems should disappear from the classification, while any remaining blocker should be attributed to topology legality or adjacency unrecoverability.
- Q: What is the behavior-change boundary for instrumentation? → A: Instrument traces for all offload lifecycle stages, but enforce no-behavior-change by default and allow simulator behavior changes only if a bug is proven by tests.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Observe Offload Lifecycle Events (Priority: P1)

A maintainer wants horizontal and vertical offload lifecycle events to be visible in HoodieGymEnvironment traces, so differential audits can distinguish true topology or legality blockers from missing observability.

**Why this priority**: The current audit can only see `selected_action`, which collapses distinct lifecycle paths into the same unsupported trace gap. That makes offload analysis noisy and blocks meaningful diagnosis.

**Independent Test**: Can be fully tested by running a trace-producing scenario and confirming that horizontal and vertical paths emit the required lifecycle events in order without changing environment behavior.

**Acceptance Scenarios**:

1. **Given** a horizontal offload task path, **When** the environment trace is produced, **Then** the trace includes the required lifecycle events that make the offload visible end-to-end.
2. **Given** a vertical offload task path, **When** the environment trace is produced, **Then** the trace includes the required lifecycle events that make the offload visible end-to-end.

### User Story 2 - Preserve Existing Repairs and Audit Boundaries (Priority: P2)

A maintainer wants the new instrumentation to preserve earlier lifecycle repairs and paper-recovery conclusions, so the feature does not regress local-compute, timeout/drop, or paper-topology work.

**Why this priority**: Instrumentation changes are only useful if they do not destabilize already repaired lifecycle behavior or rewrite prior audit conclusions.

**Independent Test**: Can be tested independently by confirming prior repaired cases still behave as before and that topology-recovery conclusions remain unchanged.

**Acceptance Scenarios**:

1. **Given** local-compute and timeout/drop scenarios already repaired, **When** the instrumentation is added, **Then** those cases still behave consistently.
2. **Given** paper-topology recovery remains unrecoverable for Figure 7 adjacency, **When** the audit is regenerated, **Then** the instrumentation feature does not claim topology validation or topology recovery.

### User Story 3 - Regenerate Audit With Better Evidence (Priority: P3)

A maintainer wants the differential environment audit to reflect observable offload lifecycle traces instead of generic unsupported-trace gaps, so the remaining blockers are explicit and accurate.

**Why this priority**: The instrumentation is valuable only if the downstream audit can separate observability gaps from topology or legality gaps.

**Independent Test**: Can be fully tested by regenerating the differential audit and confirming the offload cases are no longer blocked solely by trace invisibility.

**Acceptance Scenarios**:

1. **Given** the new offload lifecycle traces exist, **When** the differential audit runs again, **Then** case-horizontal-offload and case-vertical-offload are no longer classified as unsupported only because lifecycle events were invisible.
2. **Given** topology legality is still not paper-validated, **When** the audit runs, **Then** any remaining blocker is stated honestly as a topology or legality issue rather than an observability issue.

### Edge Cases

- What happens when a path emits `selected_action` but not the later lifecycle events? The trace must mark the offload as incomplete instead of silently flattening it into a generic unsupported case.
- How does the system handle a case that is still blocked by topology legality after instrumentation? The audit must classify that blocker explicitly and not confuse it with missing visibility.
- What happens when a task follows a local-compute path? The new instrumentation must not overwrite or obscure the existing local-compute lifecycle trace.
- What happens when instrumentation uncovers a simulator bug? The fix may adjust simulator behavior only when a test proves the bug and the change is narrowly scoped to trace correctness.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST make horizontal and vertical offload lifecycle events observable in HoodieGymEnvironment traces using the required event sequence: `selected_action`, `queued_public`, `offloaded_cloud`, `transmission_started`, `transmission_completed`, `execution_started`, `execution_completed`, `dropped_timeout`, and `reward_emitted`.
- **FR-002**: The system MUST preserve existing simulator behavior unless a bug is explicitly proven by tests, and any such change MUST be limited to the bug under test.
- **FR-003**: The system MUST regenerate the differential environment audit after instrumentation so offload-case classifications reflect the new trace observability.
- **FR-004**: The system MUST preserve Feature 024 local-compute and deterministic-ordering repairs, Feature 019 timeout/drop repair, and Feature 025 paper-topology conclusions.
- **FR-005**: The system MUST not fabricate topology, topology legality, or paper validation for horizontal destinations.
- **FR-006**: The system MUST produce an instrumentation summary artifact that states which offload lifecycle events are visible, which remain incomplete, and which blockers are still topology or paper-evidence related.
- **FR-007**: The system MUST keep any remaining horizontal-offload or vertical-offload blockers explicit if they are due to topology legality, adjacency unrecoverability, or other documented non-observability reasons.
- **FR-008**: The system MUST not claim that horizontal destination legality is paper-validated.
- **FR-009**: The system MUST not change policy logic, metric formulas, baseline definitions, training behavior, neural-network code, or dependency/lockfile state.
- **FR-010**: The system MUST attach sufficient trace provenance so audit users can tell which lifecycle events were emitted for each offload path.
- **FR-011**: The system MUST reclassify offload cases away from unsupported-trace once lifecycle observability exists, and MUST reserve remaining blockers for explicit topology legality or adjacency unrecoverability.
- **FR-012**: The system MUST allow simulator behavior changes only when a test proves a bug and the fix is narrowly scoped to trace correctness.

### Key Entities *(include if feature involves data)*

- **Offload Lifecycle Trace**: A recorded sequence of lifecycle events for a task path, including action selection, queueing, transmission, execution, completion, timeout, and reward emission.
- **Instrumentation Summary**: A frozen audit artifact that summarizes which lifecycle events are visible and which remain blocked.
- **Audit Case**: A differential environment audit scenario whose classification may change when lifecycle traces become observable.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can inspect the regenerated audit and identify offload lifecycle paths without relying on a generic unsupported-trace label for more than 2 minutes.
- **SC-002**: 100% of horizontal and vertical offload traces include the required lifecycle events when the path reaches those stages.
- **SC-003**: The regenerated differential audit no longer classifies `case-horizontal-offload` or `case-vertical-offload` as unsupported solely because lifecycle events were invisible.
- **SC-004**: Existing repaired cases remain stable, with zero regressions in previously validated local-compute and timeout/drop behavior.
- **SC-005**: The instrumentation summary artifact clearly separates observability gaps from topology or legality gaps in every regenerated run.

## Assumptions

- The feature is diagnostic and observational, not a redefinition of simulator behavior.
- Offload lifecycle traces can be added without inventing topology or claiming paper validation of destination legality.
- If a bug is proven by tests, any corrective change must be narrowly scoped to the minimum needed for trace correctness.
- Feature 025 topology conclusions remain authoritative: Figure 7 adjacency and legal horizontal destinations are still unrecoverable from paper evidence.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [ ] Environment reset/step
- [ ] Policy interface
- [ ] Task model
- [ ] Topology interface
- [x] Runtime model interface
- [ ] Evaluation metric interface
- [ ] Config schema
- [x] Artifact schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [ ] Raw metrics
- [ ] Plots
- [x] Reports
- [ ] Checkpoints
- [x] Debug traces
- [x] Validation summaries

## Security Considerations

- [x] Secrets / tokens / credentials reviewed
- [x] Remote code execution reviewed
- [x] External references documented

## Definition of Done

- [x] Spec matched by plan
- [x] Tests identified
- [x] Assumptions documented
- [x] Configs validated or updated
- [x] Paper-to-code mapping updated
- [x] Artifacts handled per lifecycle rules
- [x] Review and merge gate satisfied
