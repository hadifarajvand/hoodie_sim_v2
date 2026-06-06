# Feature Specification: HOODIE Training Foundation Readiness Audit

**Feature Branch**: `[023-training-foundation-readiness-audit]`  
**Created**: 2026-05-10  
**Status**: Draft  
**Input**: User description: "Feature 023 — HOODIE Training Foundation Readiness Audit. Create a diagnostic-only feature specification for auditing whether the current HOODIE reproduction project is ready to begin future DRL training work."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Assess Training Readiness Gaps (Priority: P1)

A maintainer wants a diagnostic audit that says whether the current HOODIE reproduction project is ready to begin future DRL training work. The maintainer needs a clear answer on readiness blockers, not a training implementation plan.

**Why this priority**: This is the primary value of the feature. If the project is not ready, the maintainer needs a concrete blocker list before any training loop is written.

**Independent Test**: Can be fully tested by inspecting the audit report after it reviews the current paper OCR, mechanism registry, differential audit, mechanism repair summary, controlled sweeps, baseline fairness rebuild, and baseline rebuild sensitivity audit artifacts, then verifying whether the result is ready or blocked.

**Acceptance Scenarios**:

1. **Given** the project artifacts are available, **When** the readiness audit runs, **Then** it reports whether the project is ready for future DRL training work or blocked by specific gaps.
2. **Given** state representation, action-space legality, delayed reward timing, or episode protocol is not ready, **When** the audit runs, **Then** it identifies those as blockers rather than claiming readiness.

### User Story 2 - Expose Mechanism Gaps Before Training (Priority: P2)

A maintainer wants to understand whether the paper mechanisms needed for DQN, Double-DQN, Dueling-DQN, and LSTM-style training are already present or still missing. The maintainer needs a diagnostic gap list, not a training recipe.

**Why this priority**: Training should not begin until the mechanism gaps are visible. Hiding those gaps would make future training work unreliable.

**Independent Test**: Can be independently tested by checking that the audit explicitly reports readiness gaps for the required mechanism families and keeps training/evaluation separation intact.

**Acceptance Scenarios**:

1. **Given** the mechanism registry and prior audits are available, **When** the readiness audit runs, **Then** it identifies the mechanism gaps for DQN, Double-DQN, Dueling-DQN, and LSTM paper requirements.
2. **Given** the project lacks a clean training/evaluation separation or reproducibility evidence, **When** the audit runs, **Then** it classifies readiness as blocked instead of manufacturing approval.

### User Story 3 - Preserve No-Training Boundaries (Priority: P3)

A maintainer reviews the readiness audit and needs confidence that it does not cross into training implementation, environment redesign, or metric changes.

**Why this priority**: The audit must be a gate, not a back door into training. Its value is in proving blockers honestly.

**Independent Test**: Can be independently verified by checking the report for no-training, no-policy-redesign, no-environment-change, no-metric-change, and no-paper-validity disclaimers.

**Acceptance Scenarios**:

1. **Given** the audit completes, **When** the maintainer inspects the report, **Then** it states that no training loop has been written and no readiness claim is manufactured.
2. **Given** the audit identifies blockers, **When** the maintainer inspects the report, **Then** the blockers are described as readiness gaps and not disguised as implementation tasks.

### Edge Cases

- What happens when one or more source artifacts are missing or inconsistent? The audit must fail closed and report blocked readiness.
- How does the audit handle unsupported evidence for a readiness dimension? The audit must mark that dimension blocked or inconclusive rather than inventing coverage.
- What happens if the project appears partially ready but still lacks training/evaluation separation? The audit must classify the overall result as blocked readiness.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST gate the readiness audit on the HOODIE paper OCR, mechanism registry, differential audit, mechanism repair summary, controlled sweeps, baseline fairness rebuild, and baseline rebuild sensitivity audit artifacts being present and internally consistent.
- **FR-002**: The system MUST assess readiness for state representation, action-space legality, delayed reward timing, episode protocol, replay/log artifact requirements, DQN mechanism gaps, Double-DQN mechanism gaps, Dueling-DQN mechanism gaps, LSTM mechanism gaps, training/evaluation separation, reproducibility requirements, and pre-training blockers.
- **FR-003**: The system MUST classify the overall outcome as ready or blocked readiness, and MUST preserve the specific blockers that caused the blocked result.
- **FR-004**: The system MUST treat missing, inconsistent, or unsupported evidence as blocked readiness or inconclusive evidence rather than manufacturing approval.
- **FR-005**: The system MUST compare the audit inputs against the existing HOODIE paper OCR and prior mechanism/audit artifacts without redesigning policies, changing metrics, changing environment behavior, or adding training.
- **FR-006**: The system MUST produce deterministic JSON and Markdown audit artifacts, with optional deterministic CSV only if already conventional and appropriate for this audit class.
- **FR-007**: The system MUST include report sections for metadata, source gate status, readiness dimensions, included source artifacts, mechanism gaps, blockers before any training loop can be written, training/evaluation separation, reproducibility requirements, limitations, and no-training/no-policy-redesign/no-metric-change/no-paper-validity disclaimers.
- **FR-008**: The system MUST avoid campaign-scale reproduction, paper-curve fitting, dependency changes, and plotting.

### Key Entities *(include if feature involves data)*

- **Source Gate Bundle**: The collection of source artifacts required before the readiness audit can be considered valid.
- **Readiness Dimension**: A specific aspect of the project that must be checked before future training work can begin.
- **Mechanism Gap**: A missing or incomplete paper mechanism needed for future DRL training approaches.
- **Readiness Audit Report**: The JSON and Markdown artifacts that summarize blocked readiness or readiness approval.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The readiness audit report can be generated deterministically from the same inputs with identical output on repeated runs.
- **SC-002**: The report classifies the overall result as blocked readiness unless all required readiness dimensions are supported by the source artifacts.
- **SC-003**: A reviewer can identify the blocker list for future training work in under 2 minutes from the report.
- **SC-004**: The report clearly separates training readiness from training implementation and includes explicit no-training and no-paper-validity disclaimers.

## Assumptions

- The HOODIE paper OCR and the prior audit artifacts are already present in the repository and can serve as source truth for readiness evaluation.
- The audit remains diagnostic only and does not imply paper-level completeness or a recommendation to begin training.
- If the evidence base is incomplete, the audit should prefer blocked readiness over optimistic inference.
- The feature is intended to determine whether future training work can begin, not to define the training implementation itself.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Environment reset/step
- [x] Policy interface
- [ ] Task model
- [ ] Topology interface
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
