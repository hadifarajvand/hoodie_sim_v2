# Feature Specification: Computation Delay and CPU Unit Validation

**Feature Branch**: `[028-computation-delay-unit-validation]`  
**Created**: 2026-05-11  
**Status**: Draft  
**Input**: User description: "Feature 028 — Computation Delay / CPU Capacity Unit Validation.

Create a validation and contract feature that locks down computation-delay, CPU-capacity, processing-density, task-size, and seconds-to-slots unit semantics for the HOODIE reproduction.

Critical issue:
Feature 027 exposed transmission delay and link-rate controls, but its generated contract report used slot_duration_seconds = 1.0. The paper default recovered earlier uses Δ = 0.1 seconds. Feature 028 must audit and resolve this mismatch explicitly. Do not silently keep 1.0 if the paper-backed contract requires 0.1. If the runtime currently uses 1.0 for implementation reasons, classify it as a runtime/paper mismatch and produce a repair or blocker recommendation.

Primary goal:
Make unit semantics explicit and test-backed:
- task size units
- processing density units
- cycles required
- private EA CPU capacity
- public EA CPU capacity
- cloud CPU capacity
- seconds-to-slots conversion
- completion-slot calculation
- slot duration Δ, especially paper default Δ = 0.1 sec vs current runtime/report behavior

Required source evidence:
- Feature 016 paper mechanism registry
- Feature 025 paper parameter registry
- Feature 027 link-rate contract report
- HOODIE paper OCR: resources/papers/hoodie/ocr/merged.tex
- current environment compute/time configuration

Required outputs:
- artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.json
- artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.md

Allowed implementation scope:
- audit/analysis helpers
- unit tests and integration tests
- environment config/contract files only if a narrow, evidence-backed unit bug is proven
- link-rate contract update only if required to correct the slot duration contract

Out of scope:
- no policy redesign
- no baseline redesign
- no metric redesign beyond explicit unit contract correction
- no training
- no neural-network/model/trainer code
- no TorchRL
- no Gymnasium
- no ns-3 or ns-3-gym
- no dependency or lockfile changes
- no campaign reruns
- no paper-validity claim
- no curve fitting

Success condition:
The repo has deterministic, test-backed unit contracts for computation delay and CPU capacity semantics. The Δ slot-duration mismatch is either repaired with evidence or explicitly classified as a blocker with exact affected formulas.

Failure condition:
If CPU capacities cannot be recovered reliably from paper evidence, mark them unrecoverable instead of inventing values. If changing slot duration would invalidate existing behavior broadly, stop and report a blocker instead of silently mutating the simulator."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Audit Unit Semantics (Priority: P1)

As a HOODIE reproduction maintainer, I want computation-delay and CPU-capacity units to be explicitly audited so that the model semantics are not silently mixed or assumed.

**Why this priority**: If the unit semantics are wrong, every downstream delay and capacity claim is suspect.

**Independent Test**: Can be tested by recovering the unit meanings from source evidence and verifying the audit report labels recovered, unrecovered, and mismatched semantics explicitly.

**Acceptance Scenarios**:

1. **Given** the recovered paper evidence, **When** the unit audit runs, **Then** task size, processing density, cycles required, and CPU capacity units are reported explicitly.
2. **Given** a paper/runtime disagreement on slot duration, **When** the unit audit runs, **Then** the mismatch is reported rather than silently normalized.

---

### User Story 2 - Validate Computation Delay (Priority: P2)

As a HOODIE reproduction maintainer, I want computation delay and completion-slot calculations to be validated so that the environment’s timing semantics are deterministic and test-backed.

**Why this priority**: Unit semantics matter only if they are connected to actual completion-slot behavior and seconds-to-slots conversion.

**Independent Test**: Can be tested by verifying the completion-slot calculation and seconds-to-slots conversion against recovered slot duration semantics.

**Acceptance Scenarios**:

1. **Given** a task size, processing density, and CPU capacity, **When** computation delay is evaluated, **Then** the completion-slot calculation is deterministic and reproducible.
2. **Given** the paper default Δ = 0.1 seconds versus a runtime setting of 1.0 seconds, **When** the validation runs, **Then** the report classifies the difference explicitly as repaired, unrecoverable, or blocked.

---

### User Story 3 - Preserve Honest Boundaries (Priority: P3)

As a researcher, I want unresolved unit or timing gaps to remain honestly labeled so that the reproduction does not overstate what is paper-backed.

**Why this priority**: This feature is about evidence and semantics, not about inventing a cleaner simulator story.

**Independent Test**: Can be tested by verifying the report distinguishes recovered values from unresolved or conflicting ones, without fabricating missing capacities or slot durations.

**Acceptance Scenarios**:

1. **Given** missing or unrecoverable CPU evidence, **When** validation runs, **Then** the capacities remain unrecoverable instead of being invented.
2. **Given** a runtime/paper mismatch on slot duration, **When** validation runs, **Then** the report recommends repair or blocks the change explicitly.

### Edge Cases

- What happens when paper evidence supports one slot duration but runtime config uses another?
- How does the system report a capacity unit that is visible in runtime but not recoverable from the paper?
- What happens when completion-slot calculation changes if slot duration changes?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST audit and report task-size, processing-density, cycles-required, and CPU-capacity unit meanings explicitly.
- **FR-002**: The system MUST audit seconds-to-slots conversion and completion-slot calculation semantics explicitly.
- **FR-003**: The system MUST compare paper-backed slot duration evidence against current runtime configuration and classify any mismatch explicitly.
- **FR-004**: The system MUST preserve unrecoverable status for CPU capacities unless paper evidence supports recovery.
- **FR-005**: The system MUST preserve unrecoverable status for any computation-delay parameter that is not directly supported by evidence.
- **FR-006**: The system MUST produce a deterministic validation artifact summarizing recovered, unrecoverable, and mismatched unit semantics.
- **FR-007**: The system MUST not silently normalize a runtime slot duration to a paper-backed value or vice versa.
- **FR-008**: The system MUST recommend repair or blocker handling if the paper-backed slot duration conflicts with the runtime contract.
- **FR-009**: The system MUST keep any unit-contract correction scoped to the narrow evidence-backed formulas only.
- **FR-010**: The system MUST not require policy redesign, baseline redesign, training, neural-network code, TorchRL, Gymnasium, ns-3, ns-3-gym, dependency changes, lockfile changes, campaign reruns, or paper-validity claims.
- **FR-011**: The system MUST expose the current environment compute/time configuration as part of validation evidence.
- **FR-012**: The system MUST keep Feature 027 link-rate contract behavior visible if a slot-duration correction affects it.

### Key Entities *(include if feature involves data)*

- **Computation-Delay Contract**: The explicit relationship between task size, processing density, CPU capacity, and completion-slot timing.
- **Unit Evidence Record**: A recovered or runtime-derived statement of what a quantity means and whether it is paper-backed.
- **Slot-Duration Contract**: The explicit statement of Δ used for seconds-to-slots conversion.
- **Mismatch Record**: A documented runtime/paper disagreement with a repair or blocker recommendation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The validation artifact clearly labels every key unit as recovered, unrecoverable, or mismatched.
- **SC-002**: 100% of slot-duration mismatches are either repaired with evidence or explicitly blocked with a recommendation.
- **SC-003**: 100% of CPU-capacity values used in the report are backed by evidence or labeled unrecoverable.
- **SC-004**: The validation report includes the recovered paper Δ and the current runtime Δ when they differ.
- **SC-005**: The completion-slot and seconds-to-slots semantics are reproducible across repeated validation runs.

## Assumptions

- Feature 025 remains the source of recovered paper parameter evidence.
- Feature 027 remains the source of the link-rate report and any cross-feature slot-duration mismatch reference.
- Current runtime configuration is treated as authoritative for runtime behavior unless a narrow, evidence-backed repair is warranted.
- If CPU capacities cannot be recovered from paper evidence, they remain unrecoverable.
- If runtime and paper disagree on Δ, the mismatch is reported instead of being hand-waved away.

## Production Constraints

- [ ] Performance budgets identified
- [ ] Artifact handling rules identified
- [ ] Security and secret-hygiene constraints identified
- [ ] CI quality gate impact identified

## Public Interfaces Affected

- [ ] Environment reset/step
- [ ] Policy interface
- [ ] Task model
- [ ] Topology interface
- [ ] Runtime model interface
- [ ] Evaluation metric interface
- [ ] Config schema
- [ ] Artifact schema

## Config / Schema Impact

- [ ] Required config fields identified
- [ ] Validation rules identified
- [ ] Backward-compatibility impact identified

## Artifact Impact

- [ ] Raw metrics
- [ ] Plots
- [ ] Reports
- [ ] Checkpoints
- [ ] Debug traces
- [ ] Validation summaries

## Security Considerations

- [ ] Secrets / tokens / credentials reviewed
- [ ] Remote code execution reviewed
- [ ] External references documented

## Definition of Done

- [ ] Spec matched by plan
- [ ] Tests identified
- [ ] Assumptions documented
- [ ] Configs validated or updated
- [ ] Paper-to-code mapping updated
- [ ] Artifacts handled per lifecycle rules
- [ ] Review and merge gate satisfied
