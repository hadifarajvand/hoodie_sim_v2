# Feature Specification: Exposure Matrix Rerun and Paper Mechanism Alignment

**Feature Branch**: `049-exposure-matrix-paper-mechanism-alignment`  
**Created**: 2026-05-23  
**Status**: Draft  
**Input**: User description: "Bundle the next related diagnostic/alignment work into one feature instead of splitting every small issue into separate features. Feature 049 must use the legality evidence from Feature 048 to rerun the exposure matrix and then audit whether the current simulator/network interface matches the paper HOODIE mechanism before training is attempted."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Re-run the exposure matrix with legality evidence and summarize exposure gaps (Priority: P1)

As an analyst, I want the exposure matrix rerun with legality evidence so that I can see how selected actions compare with legal action availability across strategies, seeds, and actions before any training work begins.

**Why this priority**: This is the gate that turns Feature 048 legality evidence into actionable exposure diagnosis.

**Independent Test**: The feature can be validated by checking the rerun summary, the legal-vs-selected action matrix, and the per-strategy/per-seed/per-action summaries without starting training.

**Acceptance Scenarios**:

1. **Given** legality evidence from Feature 048 and the committed Feature 047 exposure matrix report, **When** the exposure matrix is rerun, **Then** the report summarizes legal-vs-selected action exposure across strategies, seeds, and actions.
2. **Given** a completed rerun with legality evidence, **When** the report is generated, **Then** it identifies whether exposure bias is present and whether the matrix is complete enough for the next alignment step.
3. **Given** incomplete legality evidence, **When** the rerun is evaluated, **Then** the report says the exposure matrix is insufficient for readiness and does not recommend training.

---

### User Story 2 - Audit the paper HOODIE mechanism against the current simulator interface (Priority: P2)

As a reviewer, I want the simulator/network interface audited against the paper mechanism so that I can see whether the observation vector, timing equations, and terminal-state handling still match the paper before training is attempted.

**Why this priority**: The next training bundle should not start until the simulator contract is aligned with the paper-level mechanism.

**Independent Test**: The feature can be validated by inspecting the observation vector audit and formula/unit audit without running a training campaign.

**Acceptance Scenarios**:

1. **Given** the current simulator contract, **When** the paper observation vector is audited, **Then** the report states which required paper mechanism inputs are present or missing.
2. **Given** the current runtime formulas, **When** local execution time, transmission delay, queue wait, task age, deadline/timeout, reward timing, and terminal-state handling are audited, **Then** the report identifies any formula or unit mismatch.
3. **Given** a mismatch in the paper mechanism audit, **When** the report is generated, **Then** it routes to repair before any training contract is attempted.

---

### User Story 3 - Decide readiness for the next training-contract bundle (Priority: P3)

As an analyst, I want a final readiness decision so that the next feature can focus on training contracts only if the matrix rerun and paper-mechanism audits are clean enough.

**Why this priority**: Feature 049 is a readiness gate; it should stop the project from moving into training prematurely.

**Independent Test**: The feature can be validated by reading the final verdict and recommended next feature without any training or campaign execution.

**Acceptance Scenarios**:

1. **Given** a complete exposure matrix rerun and passing observation/formula audits, **When** the report is generated, **Then** it recommends the next training-contract bundle.
2. **Given** an observation vector gap, **When** the report is generated, **Then** it recommends observation-vector repair before training.
3. **Given** a formula/unit mismatch, **When** the report is generated, **Then** it recommends formula/unit repair before training.

### Edge Cases

- What happens when legality evidence is sufficient but the exposure matrix still shows bias?
- How does the report behave when the observation vector is partially present but not paper-complete?
- What happens when the formula audit passes but terminal-state readiness still contradicts the paper mechanism?
- How does the feature route when the exposure matrix is rerun but evidence remains insufficient for a readiness decision?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST rerun the exposure matrix using legality evidence from Feature 048 and summarize the resulting legal-vs-selected action exposure.
- **FR-002**: The system MUST summarize exposure by strategy, seed, and action so that selected action behavior can be compared with legal action availability.
- **FR-003**: The system MUST report whether the exposure matrix is complete enough for readiness before any training is attempted.
- **FR-004**: The system MUST audit the paper HOODIE observation vector for alignment with the simulator/network interface used by the current runtime.
- **FR-005**: The system MUST audit formula and unit behavior for local execution time, horizontal transmission delay, vertical/cloud transmission delay, queue wait, task age, deadline/timeout handling, reward timing, and completion/drop/pending state.
- **FR-006**: The system MUST classify the readiness decision using only diagnostic/alignment evidence and MUST not start training, optimizer steps, replay training, or target updates.
- **FR-007**: The system MUST not recommend the full training campaign, figure reproduction, or runtime repair unless that is separately routed to a future feature.
- **FR-008**: The system MUST use the committed Feature 043, 044, 045, 046, 047, and 048 artifacts as prior evidence inputs.
- **FR-009**: The system MUST expose report fields for `feature_id`, `prerequisite_tags_verified`, `prior_feature_gates_verified`, `legality_evidence_verified`, `exposure_matrix_rerun_summary`, `legal_vs_selected_action_matrix`, `per_strategy_seed_matrix`, `per_action_outcome_matrix`, `selected_illegal_action_summary`, `observation_vector_audit`, `paper_formula_unit_audit`, `runtime_semantic_drift_check`, `training_readiness_decision`, `recommended_next_feature`, the no-drift/no-training flags, and `final_verdict`.
- **FR-010**: The system MUST classify the final verdict as `paper_mechanism_alignment_ready_for_training_contract` only when the exposure matrix is complete and the observation/formula audits pass.
- **FR-011**: The system MUST classify the final verdict as `observation_vector_gap_blocks_training` when the observation vector is incomplete.
- **FR-012**: The system MUST classify the final verdict as `formula_unit_gap_blocks_training` when a formula or unit mismatch is detected.
- **FR-013**: The system MUST classify the final verdict as `exposure_bias_blocks_training` when legal-vs-selected exposure shows a dominant bias that still blocks readiness.
- **FR-014**: The system MUST classify the final verdict as `runtime_semantic_contradiction_requires_repair` when the current simulator contract contradicts the paper mechanism.
- **FR-015**: The system MUST classify the final verdict as `insufficient_legality_or_trace_evidence` when the legality or trace evidence is not sufficient to support the rerun or audit.
- **FR-016**: The system MUST classify the final verdict as `prerequisite_blocked` when required prior artifacts or validation gates are missing.
- **FR-017**: The system MUST recommend `Feature 050 — DDQN Training Contract Bundle` only when the exposure matrix is complete and the observation/formula audits pass.
- **FR-018**: The system MUST recommend observation vector repair before training when the observation vector is incomplete.
- **FR-019**: The system MUST recommend formula/unit repair before training when a formula or unit mismatch is detected.
- **FR-020**: The system MUST recommend observation vector or action exposure repair before training when exposure bias dominates.
- **FR-021**: The system MUST not perform paper figure reproduction, training, optimizer, replay training, or target update work in this feature.
- **FR-022**: The system MUST preserve diagnostic/alignment scope and MUST not change runtime semantics unless a future feature separately approves the repair path.
- **FR-023**: The system MUST require `.specify/feature.json` to be non-commit-capable before implementation begins.
- **FR-024**: For Feature 049, `.specify/feature.json` is non-commit-capable only when it is not staged, does not appear in `git diff --name-only main...HEAD`, is not committed as part of Feature 049, and is either clean or explicitly local-only and excluded from the committed feature surface.
- **FR-025**: If `.specify/feature.json` is dirty, implementation MUST stop before any Feature 049 work starts, MUST ask the user for explicit approval before restoring it, and the only allowed restore action is `git restore .specify/feature.json`.
- **FR-026**: When `.specify/feature.json` is restored under approved hygiene handling, the system MUST require a follow-up `git status --short` and a rerun of `/speckit-analyze` before implementation may proceed.

### Key Entities *(include if feature involves data)*

- **Exposure Matrix Rerun Summary**: The diagnostic output that compares legal action availability with selected action behavior by strategy, seed, and action.
- **Legal-vs-Selected Action Matrix**: The structure that shows where legal availability and chosen actions align or diverge.
- **Observation Vector Audit**: The audit that checks whether the simulator observation still matches the paper HOODIE mechanism.
- **Paper Formula/Unit Audit**: The audit that checks timing and state formulas against the paper contract.
- **Training Readiness Decision**: The final recommendation about whether the next training-contract bundle may proceed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The report identifies whether the exposure matrix is complete enough for readiness without starting training.
- **SC-002**: The report includes strategy/seed/action exposure summaries that can be reviewed independently of any training run.
- **SC-003**: The observation vector audit and formula/unit audit each produce a clear pass/fail readiness signal.
- **SC-004**: The final verdict routes to one of the declared readiness or repair outcomes with no ambiguity.
- **SC-005**: The feature introduces no training, optimizer, replay, target update, or reproduction campaign activity.
- **SC-006**: The report is produced in both JSON and Markdown and is suitable for the next planning phase.
- **SC-007**: If exposure bias remains dominant, the report does not recommend the next training-contract bundle.
- **SC-008**: If the observation vector is incomplete, the report routes to observation vector repair before training.
- **SC-009**: If a formula or unit mismatch is detected, the report routes to formula/unit repair before training.
- **SC-010**: If the exposure matrix is complete and the audits pass, the report recommends `Feature 050 — DDQN Training Contract Bundle`.

## Assumptions

Feature 048 already provides sufficient legality evidence to rerun the exposure matrix without training. This feature is diagnostic and alignment-focused only; any runtime repair discovered here must be deferred to a future feature. The next training-contract bundle is not part of this feature and must not be started here.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Evaluation metric interface
- [x] Artifact schema
- [x] Report generation interface

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
