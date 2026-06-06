# Feature Specification: Selected-Action Outcome Evidence Rerun

**Feature Branch**: `052-selected-action-outcome-evidence-rerun`  
**Created**: 2026-05-24  
**Status**: Draft  
**Input**: User description: "Feature 052 must rerun the selected-action family and per-action outcome evidence analysis using the populated Feature 051 trace evidence. The goal is to prove whether Feature 050 blockers are resolved and whether Feature 049 can now be rerun."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recompute Selected-Action Evidence From Populated Traces (Priority: P1)

As an analysis consumer, I want Feature 052 to recompute selected-action family and task-join evidence from the repaired Feature 051 trace population, so I can verify whether the previous blockers are actually resolved instead of relying on stale report outputs.

**Why this priority**: This is the core rerun evidence path. Without it, the feature cannot prove whether the trace repair changed the evidence state.

**Independent Test**: Generate the rerun report and verify that selected-action family evidence, selected-action-to-task joins, and per-action outcome joins are computed from populated Feature 051 evidence and reported with explicit counts and statuses.

**Acceptance Scenarios**:

1. **Given** Feature 051 reports readiness and populated trace evidence, **When** Feature 052 is run, **Then** it recomputes selected-action family evidence and selected-action-to-task join metrics from the evidence population.
2. **Given** selected-action family evidence is still incomplete, **When** Feature 052 is run, **Then** it reports the incomplete state explicitly and does not fake a rerun-ready result.

---

### User Story 2 - Reassess Per-Action Outcome Evidence and Exposure Consistency (Priority: P2)

As a feature owner, I want Feature 052 to recompute per-action completion, drop, and pending evidence together with legal-but-unselected consistency checks, so I can decide whether Feature 049 can now be rerun.

**Why this priority**: Feature 049 depends on the integrity of the selected-action outcome evidence chain and the consistency of legal-but-unselected counts.

**Independent Test**: Generate the rerun report and confirm it includes outcome counts, rates, legal-but-unselected consistency checks, and exposure-matrix internal consistency results.

**Acceptance Scenarios**:

1. **Given** populated selected-action trace evidence, **When** Feature 052 runs, **Then** it reports per-action completion, drop, and pending counts and rates from the rerun analysis.
2. **Given** the legal-but-unselected counts or exposure matrix consistency fail, **When** Feature 052 runs, **Then** it blocks the Feature 049 rerun path and explains why.

### Edge Cases

- What happens when Feature 051 readiness is true but the rerun still finds an incomplete join? The report must mark the specific rerun evidence as incomplete rather than claiming success.
- What happens when legal-but-unselected evidence is internally inconsistent? The report must mark the exposure matrix consistency as failed and block the rerun path.
- What happens when behavior remains stable but the exposure evidence is incomplete? The report must separate behavior equivalence from rerun readiness.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST use the committed Feature 051 repair report and the populated selected-action trace evidence it enables as the only input source for Feature 052 analysis.
- **FR-002**: The system MUST expose `feature_051_trace_readiness_verified` proving Feature 051 ended in the ready state with populated trace evidence.
- **FR-003**: The system MUST expose `selected_action_family_evidence_summary` that reports selected-action family evidence counts, ratios, and status.
- **FR-004**: The system MUST expose `selected_action_to_task_join_summary` that reports selected-action-to-task join counts, ratios, and status.
- **FR-005**: The system MUST expose `per_action_outcome_join_summary` that reports completion, drop, and pending counts and rates.
- **FR-006**: The system MUST expose `per_action_outcome_matrix` that preserves the per-action evidence needed to evaluate the rerun.
- **FR-007**: The system MUST expose `legal_but_unselected_consistency_summary` that reports local, horizontal, and vertical legal-but-unselected counts and consistency verification.
- **FR-008**: The system MUST expose `exposure_matrix_internal_consistency_summary` that reports whether the exposure matrix remains internally consistent after rerun evidence is recomputed.
- **FR-009**: The system MUST expose `feature_049_unblock_assessment` and `feature_049_remaining_blockers` so the report can state whether Feature 049 may be rerun.
- **FR-010**: The system MUST expose `behavior_equivalence_summary` and `behavior_equivalence_passed` so the rerun can be audited for drift without changing runtime behavior.
- **FR-011**: The system MUST expose `feature_049_can_be_rerun` that summarizes whether Feature 049 is unblocked by the rerun evidence.
- **FR-012**: The system MUST expose `recommended_next_feature` and MUST point to Feature 053 only when the rerun evidence is complete enough to support the next exposure-matrix pass.
- **FR-013**: The system MUST expose `selected_action_family_evidence_status`, `selected_action_to_task_join_status`, and `per_action_outcome_evidence_status` as top-level fields in addition to supporting summaries.
- **FR-019**: The report MUST expose `per_action_outcome_evidence_status` as a top-level field and MUST align it with the supporting per-action outcome summary.
- **FR-014**: The system MUST never fabricate counts, rates, blockers, or readiness states when the rerun evidence is incomplete.
- **FR-015**: The system MUST preserve evidence-rerun-only behavior and MUST not change action selection, action legality, reward timing, timeout behavior, queue behavior, execution behavior, transmission behavior, capacity semantics, or policy behavior.
- **FR-016**: The system MUST not run training, optimizer steps, replay training, target updates, checkpoints, campaigns, or paper reproduction workflows.
- **FR-017**: The system MUST emit JSON and Markdown reports containing the required sections and evidence-readiness fields needed to audit Feature 049 rerun readiness.
- **FR-018**: The system MUST keep `.specify/feature.json` local-only when used as the active SpecKit pointer and MUST not stage or commit it as part of the feature.

### Key Entities *(include if feature involves data)*

- **Feature 051 Trace Readiness Gate**: The upstream readiness state proving that passive trace population was repaired.
- **Selected-Action Family Evidence Summary**: Counts, ratios, and status describing family evidence recomputation.
- **Selected-Action-to-Task Join Summary**: Counts, ratios, and status describing task-join evidence recomputation.
- **Per-Action Outcome Evidence Summary**: Counts, rates, and status describing terminal outcome evidence recomputation.
- **Exposure Matrix Consistency Summary**: Internal consistency evidence for the legal-but-unselected and exposure-matrix rerun path.
- **Feature 049 Unblock Assessment**: A report-level decision on whether the exposure-matrix paper mechanism rerun is now feasible.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The report recomputes selected-action family evidence from populated Feature 051 trace evidence for every generated Feature 052 run.
- **SC-002**: The report distinguishes available, partial, and unavailable join readiness for selected-action-to-task and per-action outcome evidence without substituting placeholder values.
- **SC-003**: The report includes behavior-equivalence results that remain stable across repeated reruns, with no runtime drift introduced by the evidence rerun.
- **SC-004**: The report produces a clear Feature 049 rerun verdict and blocker list in every run, and the blocker list is non-empty whenever Feature 049 is not ready.
- **SC-005**: The report artifacts are generated in both JSON and Markdown form and include all required evidence-population, join, consistency, readiness, and drift sections.
- **SC-006**: The report proves that a Feature 051-ready trace population can be consumed without inventing counts, rates, or join keys.
- **SC-007**: The report does not claim Feature 049 rerun readiness unless selected-action family evidence, selected-action-to-task joins, per-action outcome joins, legal-but-unselected consistency, exposure-matrix internal consistency, and behavior equivalence all pass.

## Assumptions

- The hard prerequisite for implementation is that `main` equals `051-passive-selected-action-trace-repair-complete^{}`.
- The authoritative prior evidence inputs are the committed Feature 048 legality evidence report, Feature 049 exposure matrix paper mechanism report, Feature 050 selected-action family/per-action outcome evidence report, and Feature 051 passive selected-action trace repair report.
- Missing rerun evidence must be reported explicitly rather than inferred from zero-valued placeholders.
- The feature is diagnostic and passive only; any future runtime repair or training rerun remains a separate feature.
- The active SpecKit pointer may remain locally dirty while pointing to the Feature 052 directory, but it must not be staged or committed.

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
