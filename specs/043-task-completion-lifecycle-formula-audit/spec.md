# Feature Specification: Task Completion Lifecycle and Formula Audit

**Feature Branch**: `043-task-completion-lifecycle-formula-audit`  
**Created**: 2026-05-19  
**Status**: Draft  
**Input**: User description: "Task Completion Lifecycle and Formula Audit"

## Clarifications

### Session 2026-05-19

- Q: Should this feature modify runtime behavior to make tasks complete? → A: No. Diagnostic only. Runtime repair must be a later feature if a bug is proven.
- Q: Should the audit use paper-default T=110? → A: Yes. Use T=110 because Feature 042 proved the short T=20 probe was misleading.
- Q: Which seeds should be used? → A: Use seeds 0, 1, 2 for consistency with Feature 042.
- Q: Which action strategies should be audited? → A: Use the same strategies as Feature 042: environment_default_policy_probe, force_local_legal_probe, force_horizontal_legal_probe, force_vertical_legal_probe, mixed_legal_round_robin_probe.
- Q: Should the feature include hand-calculated expected compute/transmission slots? → A: Yes. Without hand math, the audit is just logging noise.
- Q: Should zero completions be considered a failure? → A: Not automatically. It must be classified as legitimate queue pressure, counter bug, runtime lifecycle bug, formula/unit mismatch, or incomplete instrumentation.
- Q: If existing metadata is insufficient, should this feature add passive diagnostic wrappers inside src/analysis only? → A: Yes. Add analysis-side tracing only. Do not edit src/environment.
- Q: Does this feature approve training if completions appear? → A: No. It only diagnoses completion lifecycle.
- Q: If a runtime bug is found, what comes next? → A: Create a dedicated runtime repair feature. If only missing observation/exploration remains, proceed to observation vector or loss/exploration features.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explain Zero Completions (Priority: P1)

As an analyst, I want a diagnostic audit that explains why paper-default `T = 110` probes produce reward-bearing terminal drops but no task completions, so I can determine whether the issue is in lifecycle accounting, execution progress, or formula wiring.

**Why this priority**: This is the core purpose of the feature. Without a credible explanation for zero completions, the terminal-exposure result remains incomplete and cannot be trusted as a basis for later work.

**Independent Test**: Run the lifecycle audit against existing probe outputs and confirm it reports a clear classification for the zero-completion case without modifying runtime behavior.

**Acceptance Scenarios**:

1. **Given** paper-default probe outputs with reward-bearing terminal drops and zero completions, **When** the audit runs, **Then** it reports the lifecycle breakpoint classification and a diagnosis of the likely cause.
2. **Given** the same runtime outputs, **When** the audit runs repeatedly, **Then** it returns the same classification and hand-calculation results.

### User Story 2 - Verify Formula Expectations (Priority: P2)

As an analyst, I want hand-calculated compute and transmission expectations for local, horizontal, cloud, and mixed task paths, so I can compare what should happen with what the runtime actually reports.

**Why this priority**: Formula expectations are needed to separate a real queue-pressure outcome from a lifecycle or instrumentation bug.

**Independent Test**: Compare the feature’s hand-calculation outputs against the paper-default task sizes, processing density, CPU capacities, transmission rates, and timeout values, without altering any runtime logic.

**Acceptance Scenarios**:

1. **Given** the paper-default task size and capacity values, **When** the audit calculates expected compute slots, **Then** the result matches the documented hand-calculation examples.
2. **Given** the paper-default transmission rates and timeout window, **When** the audit calculates expected transmission and total slot bounds, **Then** the result is recorded for each action path.

### User Story 3 - Classify the Breakpoint (Priority: P3)

As a reviewer, I want the audit to classify whether zero completions are caused by queue pressure, a lifecycle bug, a runtime bug, or a formula mismatch, so I know what feature should come next.

**Why this priority**: Once the formula and lifecycle evidence are visible, the next action depends on whether the current runtime is behaving correctly or misreporting progress.

**Independent Test**: Inspect the report and confirm it names a single dominant breakpoint class or marks the result inconclusive when trace evidence is insufficient.

**Acceptance Scenarios**:

1. **Given** observable task traces and terminal outcomes, **When** the audit finishes, **Then** it names the most likely root-cause category.
2. **Given** incomplete trace evidence, **When** the audit cannot distinguish runtime from instrumentation failure, **Then** it returns an inconclusive verdict and recommends trace instrumentation.

### Edge Cases

- What happens when completions remain zero but tasks are still admitted and transmitted?
- How does the audit classify cases where deadline expiration happens before execution starts?
- What happens when queue pressure is high enough that every task drops legitimately?
- How does the audit behave if the trace only exposes generated counts rather than lifecycle progress?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST produce a diagnostic lifecycle audit for paper-default `T = 110` probe runs without changing runtime behavior.
- **FR-002**: The audit MUST compare observed lifecycle counts against hand-calculated expectations for local, horizontal, cloud, and mixed task paths.
- **FR-003**: The audit MUST report the expected compute slots, transmission slots, and minimum total slots for each audited path.
- **FR-004**: The audit MUST report observed generated, admitted, transmission, execution, completion, drop, pending, reward, and terminal counts.
- **FR-005**: The audit MUST classify zero-completion behavior as one of: lifecycle counter bug, runtime bug, queue pressure, formula mismatch, or inconclusive trace evidence.
- **FR-006**: The audit MUST preserve delayed-reward semantics and MUST NOT convert pending-at-horizon outcomes into terminal completions.
- **FR-007**: The audit MUST reject any attempt to silently repair completion behavior, tune simulator outputs, or alter task lifecycle semantics.
- **FR-008**: The audit MUST document the paper-default runtime assumptions used in the hand-calculation examples, including task size, processing density, CPU capacities, transmission rates, timeout, horizon, and topology context.
- **FR-009**: The audit MUST record whether the observed lifecycle from task generation to terminal or pending state is internally consistent.
- **FR-010**: The audit MUST emit an explicit recommended next feature when the zero-completion cause is identified or when the trace remains inconclusive.
- **FR-011**: The audit MUST require the following report audit flags to be true: `no_training_started`, `no_optimizer_step`, `no_replay_training`, `no_target_update_execution`, `no_dependency_drift`, `no_environment_contract_drift`, `no_policy_drift`, `no_reward_timing_change`, `no_timeout_contract_drift`, `no_capacity_contract_drift`, `no_transmission_contract_drift`, `no_curve_fitting`, `no_simulator_output_tuning`, and `no_paper_reproduction_claim`.
- **FR-012**: The audit MUST not claim paper reproduction.
- **FR-013**: The audit MUST use passive analysis-side tracing only when existing metadata is insufficient, and MUST NOT edit `src/environment`.
- **FR-014**: The audit MUST treat runtime repair as out of scope and route any proven runtime bug to a later dedicated repair feature.

### Key Entities *(include if feature involves data)*

- **Lifecycle Trace**: A recorded sequence of task-level events from generation through terminal or pending outcome.
- **Formula Audit Record**: A hand-calculation summary that lists expected compute, transmission, and total slot bounds for each path type.
- **Breakpoint Classification**: A diagnostic label describing the most likely reason completions are absent.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The audit report contains hand-calculated slot expectations for all audited path types and can be reproduced across repeated runs with identical inputs.
- **SC-002**: The report distinguishes zero-completion cases into a single primary diagnostic class or an explicit inconclusive state.
- **SC-003**: The audit records observed lifecycle counts from generation through terminal or pending state for every strategy in scope.
- **SC-004**: The report includes all required no-training, no-drift, no-tuning, and no-reproduction audit flags and marks them true.
- **SC-005**: The feature produces no runtime changes, no training changes, and no paper-reproduction claim.

## Assumptions

- The paper-default task sizes span the documented range from 2 Mbit to 5 Mbit, and the audit may use representative values from that range for examples.
- The existing runtime outputs and metadata are sufficient to perform a diagnostic audit without changing runtime execution.
- If trace evidence is insufficient to distinguish a lifecycle bug from instrumentation loss, the audit should report that limitation instead of guessing.
- The audit does not approve training even if a runtime bug is found; it only classifies the lifecycle failure mode.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Evaluation metric interface
- [x] Config schema
- [x] Artifact schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [x] Raw metrics
- [x] Reports
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
