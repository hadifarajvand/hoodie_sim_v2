# Feature Specification: Environment Lifecycle Divergence Repair

**Feature Branch**: `[024-environment-lifecycle-divergence-repair]`  
**Created**: 2026-05-10  
**Status**: Draft  
**Input**: User description: "Feature 024 — Environment Lifecycle Divergence Repair.

Create a surgical repair feature for remaining HoodieGymEnvironment lifecycle divergences identified after Feature 019.

Scope:
- Repair local compute lifecycle divergence if confirmed against the reference lifecycle kernel.
- Repair deterministic ordering divergence if confirmed against the reference lifecycle kernel.
- Close delayed reward assumption only if paper/OCR and existing lifecycle evidence support the change.
- Regenerate the differential environment audit after repair.

Out of scope:
- No DRL training.
- No neural-network code.
- No TorchRL.
- No Gymnasium.
- No ns-3 or ns-3-gym.
- No baseline redesign.
- No metric formula changes.
- No policy redesign.
- No campaign reruns.
- No paper-validity claim.
- Do not fix horizontal/vertical offload instrumentation gaps in this feature; those remain for a later instrumentation feature unless the repair is strictly necessary for local/deterministic lifecycle correctness.
- Instrumentation changes are allowed only when they are strictly necessary to restore local-compute or deterministic-ordering correctness.

Source evidence:
- Feature 018 differential audit.
- Feature 019 mechanism repair summary.
- Reference lifecycle kernel under src/reference_model/.
- HOODIE paper OCR at resources/papers/hoodie/ocr/merged.tex only where reward timing or lifecycle assumptions require paper grounding.

Success condition:
The regenerated differential audit must no longer classify case-local-compute or case-deterministic-ordering as divergence / likely_environment_bug.

Failure condition:
If local compute or deterministic ordering cannot be repaired without policy, metric, baseline, training, or campaign changes, the feature must stop and report the blocker instead of expanding scope."

## User Scenarios & Testing *(mandatory)*

## Clarifications

### Session 2026-05-10

- Q: Should delayed reward timing be changed only when both the HOODIE paper OCR and lifecycle evidence explicitly support it, or should the reference lifecycle kernel override incomplete paper grounding? → A: Treat reward emission as strictly terminal and paper-backed only where the OCR and lifecycle evidence explicitly support it.

### User Story 1 - Repair Local Compute Lifecycle Divergence (Priority: P1)

A maintainer wants the environment to match the reference lifecycle kernel for local-compute behavior when the existing audit says the current implementation diverges. The maintainer needs a targeted repair, not a redesign of the simulator or policy stack.

**Why this priority**: Local compute is one of the remaining lifecycle divergences and blocks faithful environment behavior if it still differs from the reference kernel.

**Independent Test**: Can be fully tested by confirming the repaired lifecycle produces the reference-aligned local-compute outcome in the regenerated differential audit without changing policy, baseline, or metric behavior.

**Acceptance Scenarios**:

1. **Given** the reference lifecycle kernel and Feature 018 audit evidence are available, **When** the repair is applied, **Then** the regenerated differential audit no longer classifies `case-local-compute` as a divergence or `likely_environment_bug`.
2. **Given** the repair would require policy, metric, or campaign changes, **When** the feature is evaluated, **Then** it stops with a blocker instead of expanding scope.

### User Story 2 - Repair Deterministic Ordering Divergence (Priority: P1)

A maintainer wants the environment’s ordering behavior to match the reference lifecycle kernel when deterministic ordering still diverges. The maintainer needs the repair to remain local to lifecycle correctness.

**Why this priority**: Deterministic ordering is a core lifecycle property; if it remains divergent, subsequent audits and experiments are not trustworthy.

**Independent Test**: Can be independently tested by regenerating the differential audit and confirming `case-deterministic-ordering` is no longer reported as a divergence or `likely_environment_bug`.

**Acceptance Scenarios**:

1. **Given** the reference lifecycle kernel and existing audit evidence are available, **When** the repair is applied, **Then** the regenerated differential audit no longer classifies `case-deterministic-ordering` as a divergence or `likely_environment_bug`.
2. **Given** ordering cannot be repaired without campaign reruns, policy redesign, metric changes, or baseline changes, **When** the feature is evaluated, **Then** it reports the blocker instead of broadening scope.

### User Story 3 - Ground Reward Timing Only When Supported (Priority: P2)

A maintainer wants delayed reward assumptions to be tightened only if both the paper OCR and lifecycle evidence support the repair. The maintainer needs an evidence-bound decision, not a guess.

**Why this priority**: Reward timing changes can affect lifecycle correctness, but they must not be inferred beyond the available evidence.

**Independent Test**: Can be independently verified by checking that any reward-timing adjustment is justified by the paper OCR and lifecycle evidence, and that the differential audit is regenerated after the repair.

**Acceptance Scenarios**:

1. **Given** the paper OCR and lifecycle evidence both support delayed reward grounding, **When** the repair is applied, **Then** the audit is regenerated with the supported reward timing assumption reflected in the lifecycle behavior.
2. **Given** paper or lifecycle evidence is insufficient, **When** the feature is evaluated, **Then** reward timing remains unchanged and the blocker is reported rather than inferred.

### Edge Cases

- What happens when local compute or deterministic ordering cannot be repaired without policy, metric, baseline, training, or campaign changes? The feature must stop and report the blocker.
- How does the repair handle incomplete paper/OCR evidence for reward timing? The feature must preserve the existing assumption and report the evidence gap.
- What happens when horizontal or vertical offload instrumentation is still missing but not strictly required for local/deterministic lifecycle correctness? The feature must leave those gaps for a later instrumentation feature.
- What happens when the regenerated differential audit still reports the same divergences after attempted repair? The feature must classify the effort as blocked and surface the remaining lifecycle defect.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST use the Feature 018 differential audit, Feature 019 mechanism repair summary, and the reference lifecycle kernel under `src/reference_model/` as the primary evidence for lifecycle repair decisions.
- **FR-002**: The system MUST repair local compute lifecycle behavior only when the reference lifecycle kernel confirms the divergence is lifecycle-related and not a policy, metric, baseline, or campaign issue.
- **FR-003**: The system MUST repair deterministic ordering behavior only when the reference lifecycle kernel confirms the divergence is lifecycle-related and not a policy, metric, baseline, or campaign issue.
- **FR-004**: The system MUST keep reward emission strictly terminal and update delayed reward assumptions only when the HOODIE paper OCR at `resources/papers/hoodie/ocr/merged.tex` and the existing lifecycle evidence jointly support the change.
- **FR-005**: The system MUST regenerate the differential environment audit after any accepted repair and use the regenerated audit to determine success.
- **FR-006**: The system MUST classify `case-local-compute` and `case-deterministic-ordering` as repaired only when the regenerated differential audit no longer labels them as divergence / `likely_environment_bug`.
- **FR-007**: The system MUST stop and report a blocker if the required repair would require training, DRL, neural-network code, policy redesign, baseline redesign, metric formula changes, campaign reruns, or simulator scope expansion.
- **FR-008**: The system MUST leave horizontal and vertical offload instrumentation gaps unrepaired unless they are strictly necessary for local-compute or deterministic-ordering correctness.
- **FR-009**: The system MUST preserve deterministic, read-only evidence handling and MUST not mutate the paper OCR, reference lifecycle kernel, or prior audit artifacts.
- **FR-010**: The system MUST produce a diagnostic repair outcome that distinguishes repaired lifecycle behavior from blocked repair, without claiming paper-validity or reproduction completeness.

### Key Entities *(include if feature involves data)*

- **Lifecycle Divergence Case**: A named audit finding describing a mismatch between the current environment and the reference lifecycle kernel.
- **Reference Lifecycle Kernel**: The source of truth for lifecycle ordering and local-compute behavior under Feature 019.
- **Repair Decision**: The evidence-backed decision to repair a divergence or stop with a blocker.
- **Regenerated Differential Audit**: The updated Feature 018-style audit output used to confirm whether a divergence remains.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The regenerated differential audit no longer classifies `case-local-compute` as divergence / `likely_environment_bug` when local compute repair is justified by the evidence.
- **SC-002**: The regenerated differential audit no longer classifies `case-deterministic-ordering` as divergence / `likely_environment_bug` when deterministic ordering repair is justified by the evidence.
- **SC-003**: Any delayed reward change is traceable to both the HOODIE paper OCR and lifecycle evidence, or the feature stops with a blocker.
- **SC-004**: A reviewer can determine within 2 minutes whether the feature repaired the lifecycle divergence or stopped due to a blocked scope expansion.
- **SC-005**: The repair remains confined to lifecycle correctness and does not introduce policy, metric, baseline, or training changes.

## Assumptions

- The Feature 018 differential audit and Feature 019 mechanism repair summary are available and can be used as evidence.
- The reference lifecycle kernel under `src/reference_model/` is authoritative for local compute and deterministic ordering.
- If the evidence does not support a lifecycle repair, blocked repair is the correct outcome.
- The feature is diagnostic and surgical, not a general environment refactor.
- Horizontal and vertical offload instrumentation gaps are deferred unless strictly required for local compute or deterministic ordering correctness.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Environment reset/step
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
