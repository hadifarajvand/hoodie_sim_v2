# Feature Specification: Baseline Fairness Rebuild

**Feature Branch**: `[021-baseline-fairness-rebuild]`  
**Created**: 2026-05-10  
**Status**: Draft  
**Input**: User description: "Feature 021 — Baseline Fairness Rebuild"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rebuild Baseline Fairness Matrix (Priority: P1)

A maintainer reruns a small fairness validation matrix using existing baseline policies after the mechanism has passed prior credibility gates. The maintainer wants to see whether baseline collapse is reduced, unchanged, worsened, or still inconclusive under the repaired mechanism.

**Why this priority**: This is the core purpose of the feature. Without the matrix rerun and collapse assessment, there is no fairness rebuild.

**Independent Test**: Can be fully tested by running a small baseline matrix through the shared environment interface and confirming the rebuild report classifies collapse signatures deterministically.

**Acceptance Scenarios**:

1. **Given** the Feature 018 differential audit, Feature 019 repair, and Feature 020 mechanistic sweeps indicate the mechanism is credible, **When** the baseline matrix is rerun, **Then** the report is generated and includes the source gate status.
2. **Given** existing baseline policies and shared environment settings, **When** the matrix is evaluated, **Then** the report summarizes whether collapse is reduced, unchanged, worsened, or inconclusive.

### User Story 2 - Interpret Collapse Conservatively (Priority: P2)

A maintainer reviews the rebuild and understands that a persistent collapse can be a mechanism property rather than a bug. The report must avoid implying that every baseline must improve.

**Why this priority**: The feature must not overclaim. A fair rebuild can legitimately show unchanged or worsened collapse.

**Independent Test**: Can be independently verified by checking the report includes the no-training, no-policy-redesign, and no-paper-validity disclaimers and does not force an improvement conclusion.

**Acceptance Scenarios**:

1. **Given** a rebuild report with persistent collapse, **When** the maintainer inspects it, **Then** the report frames the result as evidence for further mechanism investigation or policy-definition audit rather than an automatic bug.
2. **Given** a rebuild report with no collapse improvement, **When** the maintainer inspects it, **Then** the report still records the outcome as valid and does not claim success through policy redesign or training.

### Edge Cases

- What happens when the source gates are not satisfied? The rebuild is not treated as credible and the report must state that the gate was not met.
- How does the feature behave when baseline collapse remains unchanged or worsens? The report records that result directly rather than treating it as failure of the feature.
- What happens if the rebuild matrix cannot differentiate baselines? The report marks the outcome inconclusive and explains the limitation.

## Clarifications

### Session 2026-05-10

- Q: Which baseline policies should the rebuild include? → A: Include all existing baseline policies used by the current baseline evaluation framework.
- Q: Which scenarios or traces should the fairness rebuild use? → A: Reuse the smallest existing baseline-evaluation scenarios/traces that already exercise collapse signatures.
- Q: Should the rebuild use the existing baseline evaluation runner directly or a wrapper? → A: Reuse the existing baseline evaluation framework’s runner directly in read-only mode.
- Q: How should collapse be classified? → A: Use the existing baseline evaluation framework’s collapse indicators and compare them against the prior baseline state using a simple qualitative rule: reduced if differentiation improves, unchanged if the collapse signature stays materially the same, worsened if differentiation degrades, and inconclusive if the evidence is mixed or incomplete.
- Q: Is a CSV summary required? → A: JSON and Markdown are required; CSV is optional only if already consistent with project conventions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST gate the baseline fairness rebuild on the mechanism being credible after prior differential audit, timeout/drop repair, and controlled mechanistic sweep analysis.
- **FR-002**: The system MUST rerun a small baseline fairness validation matrix through the shared environment interface using existing baseline policies only.
- **FR-003**: The system MUST reuse the same environment, task generation, topology, deadline rules, reward timing, and metric definitions for all baselines in the rebuild matrix.
- **FR-004**: The system MUST summarize baseline collapse behavior as reduced, unchanged, worsened, or inconclusive.
- **FR-005**: The system MUST preserve the possibility that baseline collapse is a mechanism property and MUST NOT automatically label persistent collapse as a bug.
- **FR-006**: The system MUST exclude policy redesign unless prior analysis proves it is necessary.
- **FR-007**: The system MUST limit rebuild scope to baselines and MUST NOT expand into training foundation work.
- **FR-008**: The system MUST produce deterministic fairness rebuild artifacts in JSON and Markdown form.
- **FR-009**: The system MUST include the source gate status, baseline policies included, scenarios/traces used, fairness controls, reused metrics, collapse indicators, anti-collapse assessment, unchanged-collapse explanation, limitations, reproducibility details, and no-training/no-policy-redesign/no-paper-validity disclaimers in the report.
- **FR-010**: The system MUST avoid metric formula changes, simulator/environment changes, campaign-scale paper reproduction, paper-curve fitting, dependency changes, and plotting.

### Key Entities *(include if feature involves data)*

- **Source Gate**: The prior credibility evidence that must be satisfied before the rebuild is considered valid.
- **Baseline Policy Set**: The existing baseline policies included in the small fairness matrix.
- **Collapse Indicator**: A qualitative signal describing whether the baseline set shows reduced, unchanged, worsened, or inconclusive collapse behavior.
- **Fairness Rebuild Report**: The JSON and Markdown artifacts that summarize the baseline fairness matrix and its interpretation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The rebuild report can be generated deterministically from the same inputs with identical output on repeated runs.
- **SC-002**: The report classifies every baseline fairness result as reduced, unchanged, worsened, or inconclusive with no unclassified outcomes.
- **SC-003**: The fairness rebuild artifacts are produced in under 1 minute under standard local project conditions.
- **SC-004**: A reviewer can determine from the report whether collapse remained reduced, unchanged, worsened, or inconclusive in under 2 minutes.
- **SC-005**: The report includes explicit source-gate status, limitations, and no-training/no-policy-redesign/no-paper-validity disclaimers.

## Assumptions

- The baseline fairness rebuild uses a small matrix of existing baseline policies and existing scenarios/traces only.
- Existing baseline evaluation utilities are sufficient to summarize collapse signatures without introducing new evaluation definitions.
- If collapse persists, that outcome is reported as evidence for further mechanism investigation or policy-definition audit rather than automatically as a simulator bug.
- The rebuild remains diagnostic and does not imply paper-level completeness or baseline superiority.

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
