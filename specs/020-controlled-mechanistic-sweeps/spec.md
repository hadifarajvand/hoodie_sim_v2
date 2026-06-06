# Feature Specification: Controlled Mechanistic Sweeps

**Feature Branch**: `[020-controlled-mechanistic-sweeps]`  
**Created**: 2026-05-10  
**Status**: Draft  
**Input**: User description: "Feature 020 — Controlled Mechanistic Sweeps"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Qualitative Mechanistic Sweeps (Priority: P1)

A maintainer runs tiny deterministic sweeps over selected mechanism settings and reads a concise summary of whether the repaired system behaves in the expected qualitative direction.

**Why this priority**: This is the core value of the feature. Without the summary sweep, the feature has no diagnostic purpose.

**Independent Test**: Can be fully tested by running one tiny sweep family with fixed seeds and confirming the report either shows the expected qualitative direction or explicitly marks the result as warn or inconclusive.

**Acceptance Scenarios**:

1. **Given** fixed seeds and a controlled sweep set, **When** the sweep is executed, **Then** the report summarizes the observed trend deterministically.
2. **Given** a sweep dimension that the public interface cannot control, **When** the sweep is executed, **Then** the report marks it inconclusive or instrumentation_gap without changing simulator behavior.

### User Story 2 - Sweep Limitation Review (Priority: P2)

A maintainer reviews the report to confirm the sweeps are mechanistic validation only and do not claim paper-level completeness, reproduction validity, or baseline superiority.

**Why this priority**: The feature must remain diagnostic-only; the report must clearly delimit what the sweeps do and do not prove.

**Independent Test**: Can be independently verified by checking the generated summary includes the required disclaimers and does not reference campaign reruns or paper-validity claims.

**Acceptance Scenarios**:

1. **Given** a generated sweep summary, **When** the maintainer reviews it, **Then** the report clearly states that it is not a paper-reproduction claim.
2. **Given** the report output, **When** the maintainer inspects it, **Then** the report lists limitations, seeds, and controlled assumptions.

### Edge Cases

- What happens when a sweep dimension is not controllable through existing public configuration? It is reported as inconclusive or instrumentation_gap.
- How does the feature behave when evidence is insufficient to establish monotonic direction? The report warns rather than forcing a conclusion.
- What happens if a controlled setting produces no measurable offload evidence? The sweep records that limitation explicitly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support tiny deterministic sweeps over arrival probability, timeout, CPU capacity, link rate, and topology density.
- **FR-002**: The system MUST summarize each sweep using qualitative monotonic checks rather than reproduction claims or numerical optimization.
- **FR-003**: The system MUST make clear that the sweeps are mechanistic validation only and do not rerun baseline campaigns.
- **FR-004**: The system MUST produce deterministic summary artifacts in JSON and Markdown form.
- **FR-005**: The system MUST report pass, warn, or inconclusive status for each sweep dimension.
- **FR-006**: The system MUST classify any sweep dimension that cannot be controlled through existing public configuration or environment hooks as inconclusive or instrumentation_gap, without changing simulator behavior.
- **FR-007**: The system MUST include the fixed seeds and controlled input assumptions used for each sweep.
- **FR-008**: The system MUST include limitations and a no-paper-validity disclaimer in the report.
- **FR-009**: The system MUST include a no-campaign-rerun disclaimer in the report.
- **FR-010**: The system MUST avoid plotting, campaign orchestration changes, policy changes, metric formula changes, simulator changes, and dependency changes.

### Key Entities *(include if feature involves data)*

- **Sweep Definition**: A tiny controlled parameter family with fixed seed set, expected qualitative direction, and controlled assumptions.
- **Sweep Observation**: A deterministic observation summary produced for one sweep setting.
- **Sweep Result**: The qualitative check outcome for one sweep setting or sweep family.
- **Sweep Report**: The JSON and Markdown artifacts summarizing all sweep definitions, observations, limitations, and disclaimers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least five controlled sweeps can be summarized deterministically from the same inputs and fixed seeds with identical output on repeated runs.
- **SC-002**: 100% of sweep dimensions are labeled pass, warn, inconclusive, or instrumentation_gap, with no unclassified results.
- **SC-003**: The JSON and Markdown summary artifacts are produced in under 1 minute for the tiny sweep set under standard project conditions.
- **SC-004**: Users can read the report and distinguish mechanistic validation from paper-level reproduction in under 2 minutes.
- **SC-005**: The report includes explicit limitations, fixed seeds, and no-campaign-rerun/no-paper-validity disclaimers.

## Assumptions

- The sweeps use tiny fixed value sets for each parameter family so results remain deterministic and quick to validate.
- Existing public configuration and environment hooks are sufficient for any sweep dimension that is marked as controllable; otherwise the dimension is reported as inconclusive or instrumentation_gap.
- The feature is diagnostic only and does not re-run baseline campaigns, tune parameters to paper curves, or claim paper-level completeness.
- Any summary of monotonic behavior is qualitative and bounded by the current environment evidence available through the public interface.

## Clarifications

### Session 2026-05-10

- Q: What exact tiny value sets should the sweeps use? → A: Use a symmetric three-point sweep for each parameter family.
- Q: Which public configuration or public environment hooks can control each sweep dimension? → A: Treat each dimension as controlled only if it is already exposed through public configuration or the current environment interface.
- Q: What status rule should distinguish pass, warn, inconclusive, and instrumentation_gap? → A: Use a simple rule tied to observed monotonic direction and control availability.

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
