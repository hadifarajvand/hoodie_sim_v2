# Feature Specification: Runtime Adoption of Approved Assumption Registry

**Feature Branch**: `032-runtime-adoption-approved-assumption-registry`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: User description: "Apply Feature 031 approved assumptions to runtime configuration, runtime contracts, topology legality, link-rate configuration, timeout validation, and evaluation aggregation."

## Clarifications

### Session 2026-05-12

- Q: Should reward aggregation be implemented as a shared helper/contract or runtime-only? → A: Implement aggregation as a shared helper/contract that runtime and reporting can both call.
- Q: Should runtime topology load Figure 7 adjacency directly or from a copied artifact? → A: Load directly from `resources/papers/hoodie/recovered/user-approved-assumption-registry.json` to preserve provenance and avoid a copied runtime artifact.
- Q: Should the runtime use 0-based internal indexing or convert everything to 1-based? → A: Use the existing internal indexing convention, including 0-based indices if applicable.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Adopt Approved Runtime Parameters (Priority: P1)

As an operator, I want the runtime to consume the approved CPU, link-rate, and timeout values from Feature 031 so execution uses the same vetted assumptions everywhere they matter.

**Why this priority**: These values directly affect runtime execution and must be adopted before any downstream validation work can be trusted.

**Independent Test**: A reviewer can inspect runtime configuration and confirm the approved CPU capacities, cloud-facing vertical rate, horizontal rate, and timeout contract are loaded consistently without touching training.

**Acceptance Scenarios**:

1. **Given** the approved registry artifacts, **When** runtime configuration is loaded, **Then** private, public, and cloud CPU capacities reflect the approved values.
2. **Given** the approved registry artifacts, **When** runtime configuration is loaded, **Then** the cloud-facing vertical rate, horizontal rate, and timeout contract reflect the approved values.

### User Story 2 - Enforce Topology Legality (Priority: P2)

As an operator, I want runtime topology legality to use the approved Figure 7 adjacency so horizontal offloading follows the validated neighborhood constraints.

**Why this priority**: Topology legality controls which runtime actions are allowed and prevents invalid horizontal routing.

**Independent Test**: A reviewer can validate the topology contract independently by checking the approved adjacency, degree, symmetry, and legality rules.

**Acceptance Scenarios**:

1. **Given** the approved Figure 7 adjacency, **When** topology legality is validated, **Then** the runtime accepts only neighbor-only horizontal offloads and forbids self-offload.
2. **Given** the approved Figure 7 adjacency, **When** topology legality is validated, **Then** vertical/cloud offload remains separate from horizontal legality.

### User Story 3 - Preserve Audit Boundaries (Priority: P3)

As an auditor, I want the runtime adoption feature to prove it did not rewrite paper evidence or change reward emission semantics, so approved assumptions remain explicitly user-approved assumptions.

**Why this priority**: The runtime adoption feature must stay inside its boundary and must not claim paper recovery or silently change evaluation behavior.

**Independent Test**: A reviewer can inspect the report and confirm the feature consumed approved assumptions, preserved audit labels, and did not alter reward timing.

**Acceptance Scenarios**:

1. **Given** the adoption report, **When** it is reviewed, **Then** each adopted value is traced to an approved assumption and not to a paper-recovery claim.
2. **Given** the runtime evaluation path, **When** aggregation is applied, **Then** rewards remain delayed until task completion or drop and are reduced by per-agent episode sum followed by arithmetic mean across agents.

### Edge Cases

- Runtime topology must respect the existing internal indexing convention used by the codebase, including 0-based indices if applicable.
- The approved Figure 7 adjacency is loaded directly from `resources/papers/hoodie/recovered/user-approved-assumption-registry.json` to preserve provenance and avoid a copied runtime artifact.
- Reward aggregation must be implemented as a shared helper/contract that runtime and reporting can both call, not as a campaign rerun or duplicated reduction logic.

- What happens when a runtime contract references an assumption that is approved but not present in the registry snapshot?
- How does the runtime behave if topology legality and link-rate adoption disagree with each other?
- What happens if a timeout contract is missing a required slot-duration or timeout value?
- How are no-task, NaN, or omitted reward slots handled in runtime aggregation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST consume the approved assumption registry and report artifacts from Feature 031 as the source of runtime adoption truth.
- **FR-002**: The system MUST apply the approved CPU capacity values for private, public, and cloud runtime configuration.
- **FR-003**: The system MUST apply the approved Figure 7 adjacency as the source of topology legality for horizontal offloading.
- **FR-004**: The system MUST enforce neighbor-only horizontal offloading and forbid self-offload and non-neighbor horizontal offload.
- **FR-005**: The system MUST preserve vertical/cloud offload as a separate legality path from horizontal topology legality.
- **FR-006**: The system MUST apply the approved cloud-facing vertical rate `R_V = 10 Mbps` and preserve the horizontal rate contract without introducing a separate cloud-specific rate.
- **FR-007**: The system MUST apply the approved timeout contract end-to-end for runtime validation and drop handling using `timeout_slots = 20`, `slot_duration_seconds = 0.1`, and `timeout_seconds = 2.0`.
- **FR-008**: The system MUST preserve delayed reward emission and only emit reward on task completion or drop.
- **FR-009**: The system MUST reduce rewards by summing terminal task rewards per agent per episode and then taking the arithmetic mean across agents.
- **FR-010**: The system MUST exclude no-task, NaN, and omitted slots from numeric aggregation.
- **FR-011**: The system MUST keep approved assumptions explicitly labeled as user-approved assumptions and MUST NOT relabel them as paper-recovered facts.
- **FR-012**: The system MUST preserve dependency, training, baseline, policy, and campaign boundaries while adopting runtime assumptions.
- **FR-013**: The system MUST generate a runtime adoption report that lists each consumed approved assumption, the runtime component affected, the proof/tests used, and the final verdict.

### Key Entities *(include if feature involves data)*

- **Approved Assumption Snapshot**: The Feature 031 registry/report data used as the source of runtime adoption.
- **Runtime Adoption Contract**: The runtime-facing configuration or validation rule that consumes an approved assumption.
- **Adoption Report**: The generated summary that traces each adopted assumption to the runtime component and proof used.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All approved CPU, topology, link-rate, timeout, and aggregation assumptions are traceable in the runtime adoption report with 100% coverage.
- **SC-002**: 100% of runtime checks for approved assumptions pass without training, dependency, policy, or campaign changes.
- **SC-003**: 0 adopted values are labeled as paper-recovered facts.
- **SC-004**: Reward emission remains delayed until task completion or drop in 100% of tested scenarios.
- **SC-005**: Runtime adoption validation can be reproduced from the same registry artifacts with identical results.

## Assumptions

Any assumption that materially changes code, workflow, or repository state MUST be recorded and presented for user approval before implementation depends on it.

- Feature 031 is already merged to `main` and the 031 completion tag matches `main`.
- Approved assumptions are consumed only as runtime inputs and never rewritten as paper-recovered claims.
- No training or learning behavior changes are part of this feature.
- Reward emission semantics remain delayed and completion-based.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Environment reset/step
- [x] Policy interface
- [x] Task model
- [x] Topology interface
- [x] Runtime model interface
- [x] Evaluation metric interface
- [x] Config schema
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
- [ ] Debug traces
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
