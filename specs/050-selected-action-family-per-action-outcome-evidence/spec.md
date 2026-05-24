# Feature Specification: Selected-Action Family and Per-Action Outcome Evidence Expansion

**Feature Branch**: `050-selected-action-family-per-action-outcome-evidence`  
**Created**: 2026-05-24  
**Status**: Draft  
**Input**: User description: "Feature 050 must expand passive evidence so the system can compute selected local/horizontal/vertical counts and join selected actions to terminal outcomes without fake zeros, sample-derived counts, or placeholder rates."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capture Selected-Action Family Evidence (Priority: P1)

As an analysis consumer, I want the passive evidence pipeline to expose which action family was selected, so the exposure matrix can report selected local, horizontal, and vertical counts without inventing placeholder zeros.

**Why this priority**: Feature 049 is blocked until selected-action family evidence exists. Without this, the exposure matrix cannot distinguish unavailable evidence from genuine zero counts.

**Independent Test**: Run the passive evidence report on committed prior artifacts and verify the report exposes selected action family status, selected family counts when evidence exists, and explicit unavailability when it does not.

**Acceptance Scenarios**:

1. **Given** committed passive trace evidence, **When** Feature 050 generates its report, **Then** the report states whether selected-action family evidence is available and includes selected family counts only when they are trace-backed.
2. **Given** no trace-backed selected-action family evidence, **When** Feature 050 generates its report, **Then** the report marks the evidence as unavailable instead of fabricating zero counts.

---

### User Story 2 - Join Selected Actions to Terminal Outcomes (Priority: P2)

As an analysis consumer, I want selected actions to be joined to task identifiers and terminal outcomes, so completion, drop, and pending rates are based on passive evidence rather than placeholder rates.

**Why this priority**: Feature 049 remains blocked unless selected actions can be tied to terminal outcomes in a trace-backed way.

**Independent Test**: Feed the report generator committed passive evidence and verify it can map selected actions to task identifiers and terminal outcomes when the join keys are present, while reporting missing join evidence explicitly when they are not.

**Acceptance Scenarios**:

1. **Given** trace evidence that contains a selected action family and joinable task/outcome identifiers, **When** the report is generated, **Then** per-action completion, drop, and pending counts/rates are produced from the joined evidence.
2. **Given** terminal outcome data that cannot be joined to the selected action family, **When** the report is generated, **Then** the outcome evidence is marked unavailable and no fake zero rates are reported.

---

### User Story 3 - Assess Feature 049 Unblock Readiness (Priority: P3)

As a feature owner, I want a passive evidence summary that tells me whether Feature 049 can be rerun safely, so I can decide whether the exposure-matrix blocker is resolved or whether more trace evidence is still needed.

**Why this priority**: The next feature depends on a strict readiness decision, but only after evidence completeness and internal consistency are verified.

**Independent Test**: Generate the report and confirm it yields a readiness verdict plus a recommended next step that changes based on evidence completeness, consistency checks, and behavior drift status.

**Acceptance Scenarios**:

1. **Given** complete selected-action family evidence, outcome joins, and consistent exposure totals, **When** the report is generated, **Then** it recommends the Feature 049 rerun path.
2. **Given** missing selected-action family evidence or missing outcome joins, **When** the report is generated, **Then** it blocks the rerun and recommends evidence repair before training.

### Edge Cases

- What happens when selected-action family evidence exists for only some strategies or seeds? The report must surface partial availability rather than flattening missing rows into zeros.
- What happens when a selected action exists but no terminal outcome can be joined? The report must mark the outcome evidence unavailable for that selection.
- What happens when legal counts are available but selected-family counts are not? The report must not compute legal-but-unselected counts from placeholders.
- What happens when evidence is internally contradictory? The report must mark internal consistency as failed and block Feature 049 rerun readiness.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST use committed passive evidence from the prior feature artifacts as the only input source for Feature 050 analysis.
- **FR-002**: The system MUST expose a `selected_action_family_evidence_status` field that distinguishes available evidence from unavailable evidence.
- **FR-003**: The system MUST compute `selected_local_count`, `selected_horizontal_count`, and `selected_vertical_count` only from trace-backed selected-action family evidence.
- **FR-004**: The system MUST compute `selected_action_count` from the selected family counts and MUST verify that the total is internally consistent.
- **FR-005**: The system MUST expose `selected_action_count_consistency_verified` and MUST set it to false when the selected family total cannot be verified.
- **FR-006**: The system MUST join selected actions to `task_id` when the join key is present in the passive evidence.
- **FR-007**: The system MUST join selected actions to terminal outcome state when the evidence contains a trace-backed outcome key.
- **FR-008**: The system MUST expose `per_action_outcome_evidence_status` to indicate whether completion, drop, and pending evidence can be joined to selected actions.
- **FR-009**: The system MUST compute `per_action_completion_count`, `per_action_drop_count`, and `per_action_pending_count` only when the selected-action family and terminal outcome evidence can be joined.
- **FR-010**: The system MUST compute `per_action_completion_rate`, `per_action_drop_rate`, and `per_action_pending_rate` only when the corresponding counts are evidence-backed.
- **FR-011**: The system MUST expose `legal_but_unselected_by_action` only when both legal counts and selected family counts are available and must verify the result is consistent with those inputs.
- **FR-012**: The system MUST expose `legal_but_unselected_consistency_verified` and MUST set it to false when legal-but-unselected counts cannot be verified.
- **FR-013**: The system MUST expose `exposure_matrix_internal_consistency_verified` and MUST set it to false whenever selected-family totals, legal-but-unselected totals, or action-outcome joins cannot be verified.
- **FR-014**: The system MUST classify each strategy/seed/task/slot row in the selected-action family matrix so evidence can be traced without sample-derived aggregation.
- **FR-015**: The system MUST provide a `feature_049_unblock_assessment` umbrella object that reports `feature_049_can_be_rerun`, `feature_049_remaining_blockers`, `selected_action_family_evidence_status`, `selected_action_to_task_join_status`, `per_action_outcome_evidence_status`, `exposure_matrix_internal_consistency_verified`, and `recommended_next_feature`.
- **FR-016**: The system MUST expose `selected_action_family_evidence_status`, `selected_action_to_task_join_status`, `per_action_outcome_evidence_status`, `feature_049_can_be_rerun`, and `feature_049_remaining_blockers` as top-level report fields as well as inside `feature_049_unblock_assessment`.
- **FR-017**: The system MUST use the status vocabulary `available`, `partial`, and `unavailable` for selected-action family evidence, selected-action-to-task join evidence, and per-action outcome evidence.
- **FR-018**: The system MUST set `feature_049_can_be_rerun = true` only when selected-action family evidence, selected-action-to-task joins, per-action outcome evidence, internal consistency, behavior equivalence, action-selection drift, and action-legality drift all pass.
- **FR-019**: The system MUST expose `behavior_equivalence_passed` as a required readiness field and define it exactly as `behavior_equivalence_summary.passed`.
- **FR-020**: The system MUST expose `behavior_equivalence_passed` both at the top level of the report and inside `feature_049_unblock_assessment`, and both values MUST match `behavior_equivalence_summary.passed`.
- **FR-021**: The system MUST set `feature_049_can_be_rerun = true` only when selected-action family evidence, selected-action-to-task joins, per-action outcome evidence, internal consistency, `behavior_equivalence_passed`, action-selection drift, and action-legality drift all pass.
- **FR-022**: The system MUST set `feature_049_can_be_rerun = false` and populate `feature_049_remaining_blockers` whenever any required evidence status is unavailable or partial, or when internal consistency or `behavior_equivalence_passed` fails.
- **FR-023**: The system MUST require `feature_049_remaining_blockers` to include `behavior_equivalence_failed` whenever `behavior_equivalence_passed = false`.
- **FR-024**: The system MUST recommend `Feature 051 — Exposure Matrix Paper Mechanism Rerun with Outcome Evidence` only when `feature_049_can_be_rerun = true`.
- **FR-025**: The system MUST recommend evidence repair before training when selected-action family evidence is incomplete, selected-action-to-task joins are incomplete, per-action outcome joins are incomplete, or internal consistency fails.
- **FR-026**: The system MUST never fabricate zero counts or zero rates to stand in for unavailable evidence.
- **FR-027**: The system MUST never derive selected counts or outcome rates from sample assumptions when trace-backed evidence is missing.
- **FR-028**: The system MUST preserve passive-only behavior and MUST not change action legality, action selection, reward timing, timeout behavior, queue behavior, execution behavior, transmission behavior, or capacity semantics.
- **FR-029**: The system MUST not run training, optimizer steps, replay training, target updates, campaigns, or paper reproduction workflows.
- **FR-030**: The system MUST emit JSON and Markdown reports containing the required sections and the evidence-status fields needed to audit Feature 049 unblock readiness.
- **FR-031**: The system MUST keep `.specify/feature.json` local-only when used as the active SpecKit pointer and MUST not stage or commit it as part of the feature.

### Key Entities *(include if feature involves data)*

- **Selected-Action Family Evidence**: Passive trace evidence that identifies the selected action family and counts selected local, horizontal, and vertical actions.
- **Terminal Outcome Evidence**: Passive trace evidence that links selected actions to completion, drop, or pending terminal outcomes.
- **Exposure Matrix Internal Consistency**: A consistency summary that verifies selected totals, legal-but-unselected totals, and outcome joins do not contradict each other.
- **Feature 049 Unblock Assessment**: A readiness decision summarizing whether the passive evidence is sufficient to rerun the exposure-matrix and paper-mechanism audit.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The report distinguishes available from unavailable selected-action family evidence in 100% of generated Feature 050 runs.
- **SC-002**: The report produces selected family counts only when evidence is trace-backed and otherwise marks them unavailable instead of substituting zeros.
- **SC-003**: The report joins selected actions to terminal outcomes whenever the passive evidence provides the required keys, and reports join incompleteness otherwise.
- **SC-004**: The report never emits fake all-zero completion, drop, or pending rates when the evidence is unavailable.
- **SC-005**: The report blocks Feature 049 rerun readiness unless selected-action family evidence, selected-action-to-task joins, per-action outcome joins, internal consistency, behavior equivalence, action-selection drift, and action-legality drift all pass.
- **SC-006**: The report artifacts are generated in both JSON and Markdown form and include all required evidence-status and consistency sections.

## Assumptions

- The hard prerequisite for implementation is that `main` equals `049-exposure-matrix-paper-mechanism-alignment-complete^{}`.
- The authoritative passive evidence inputs are the committed Feature 044 passive lifecycle trace report, Feature 048 legality evidence report, and Feature 049 exposure matrix paper mechanism report.
- Missing evidence must be reported explicitly rather than inferred from zero-valued placeholders.
- The feature is diagnostic and evidence-expansion only; any future runtime repair remains a separate feature.
- The active SpecKit pointer may remain locally dirty while pointing to the Feature 050 directory, but it must not be staged or committed.

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
- [x] Evaluation metric interface
- [x] Config schema
- [x] Artifact schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [x] Raw metrics
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
