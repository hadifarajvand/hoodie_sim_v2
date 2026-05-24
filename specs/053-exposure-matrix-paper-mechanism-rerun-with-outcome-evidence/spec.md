# Feature Specification: Exposure Matrix Paper Mechanism Rerun with Outcome Evidence

**Feature Branch**: `053-exposure-matrix-paper-mechanism-rerun-with-outcome-evidence`  
**Created**: 2026-05-24  
**Status**: Draft  
**Input**: User description: "Rerun the Feature 049 exposure-matrix paper-mechanism alignment now that Feature 052 proves selected-action family, selected-action-to-task join, and per-action outcome evidence are available. The goal is to decide whether the project is ready to move from diagnostic evidence work into the next paper-mechanism repair/training-readiness phase."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Re-run Paper Mechanism Alignment From Completed Evidence (Priority: P1)

As an analysis consumer, I want Feature 053 to rerun the exposure-matrix paper-mechanism alignment using the committed evidence reports from Features 048 through 052, so I can determine whether the earlier paper-mechanism blockers have been resolved.

**Why this priority**: This is the core purpose of the feature. Without the rerun, the project cannot decide whether it is ready to move beyond diagnostic evidence work.

**Independent Test**: Generate the Feature 053 report and verify that it consumes the committed prior reports, produces the required alignment statuses, and emits a single evidence-backed verdict.

**Acceptance Scenarios**:

1. **Given** the committed Feature 048 through 052 reports are available, **When** Feature 053 is run, **Then** it produces a rerun report that classifies paper-mechanism alignment status from those committed inputs.
2. **Given** the Feature 052 report does not support the rerun, **When** Feature 053 is run, **Then** it blocks readiness and explains the blocker instead of claiming training readiness.

---

### User Story 2 - Classify Alignment Blockers Clearly (Priority: P2)

As a feature owner, I want the report to separate observation-vector, formula/unit, exposure-matrix, and selected-action-outcome alignment statuses, so I can see exactly which layer remains blocked if the rerun is not ready.

**Why this priority**: A single yes/no answer is not enough. The report must pinpoint the specific layer that prevents progression.

**Independent Test**: Generate the report and confirm that each alignment layer is reported independently, with a blocker list that changes according to the failing layer.

**Acceptance Scenarios**:

1. **Given** one alignment layer fails while others pass, **When** Feature 053 runs, **Then** it reports the failing layer as the blocker and does not collapse all failures into a generic result.
2. **Given** all required alignment layers pass, **When** Feature 053 runs, **Then** it reports that the paper mechanism alignment is ready for the next phase.

---

### User Story 3 - Gate the Next Phase Responsibly (Priority: P3)

As a maintainer, I want the report to decide whether the project can move from diagnostic evidence work into the next paper-mechanism repair or training-readiness phase, so downstream work does not start on a weak or unsupported foundation.

**Why this priority**: The feature exists to prevent premature transition into the next phase. It must provide a clear next-step recommendation.

**Independent Test**: Generate the report and verify that the recommended next feature and final verdict match the alignment state without referencing implementation internals.

**Acceptance Scenarios**:

1. **Given** all alignment checks pass, **When** Feature 053 runs, **Then** it recommends Feature 054 as the next step and marks the report ready for the training contract phase.
2. **Given** selected-action outcome evidence is still incomplete or behavior drift is detected, **When** Feature 053 runs, **Then** it recommends the correct repair path instead of training readiness.

### Edge Cases

- What happens when the Feature 052 report says rerun readiness is true but the paper-mechanism alignment still fails? The report must block readiness and name the failing alignment layer.
- What happens when the observation-vector alignment passes but the formula/unit alignment does not? The report must return the formula/unit blocker, not a generic failure.
- What happens when the rerun evidence is complete but the report would otherwise imply training can start? The report must only recommend the training contract phase when every required alignment layer is available.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST use only committed evidence reports from Features 048, 049, 050, 051, and 052 as inputs for the Feature 053 rerun.
- **FR-002**: The system MUST NOT regenerate prior feature artifacts or depend on dirty-worktree-sensitive prior report builders.
- **FR-003**: The system MUST verify Feature 052 evidence readiness before evaluating paper-mechanism alignment.
- **FR-004**: The system MUST expose `paper_mechanism_alignment_ready` as the top-level readiness decision for the rerun.
- **FR-005**: The system MUST expose `observation_vector_alignment_status`, `formula_unit_alignment_status`, `exposure_matrix_alignment_status`, `selected_action_outcome_alignment_status`, and `training_readiness_contract_status` as top-level report fields.
- **FR-006**: Each alignment status field MUST use one of the following values: `available`, `partial`, or `unavailable`.
- **FR-007**: The system MUST expose `remaining_blockers` as a trace-backed list of the specific blockers that prevent readiness.
- **FR-008**: The system MUST expose `recommended_next_feature` and MUST route to Feature 054 only when all alignment layers are available.
- **FR-009**: The system MUST expose `final_verdict` using one of the approved verdict values and MUST keep the verdict consistent with the reported alignment statuses.
- **FR-010**: The system MUST mark the report as `paper_mechanism_alignment_ready_for_training_contract` only when observation-vector alignment, formula/unit alignment, exposure-matrix alignment, selected-action-outcome alignment, and training-readiness contract checks all pass.
- **FR-011**: The system MUST mark the report as `observation_vector_alignment_blocked` when the observation-vector layer fails, and it MUST name the observation-vector blocker in `remaining_blockers`.
- **FR-012**: The system MUST mark the report as `formula_unit_alignment_blocked` when the formula/unit layer fails, and it MUST name the formula/unit blocker in `remaining_blockers`.
- **FR-013**: The system MUST mark the report as `exposure_matrix_alignment_blocked` when the exposure-matrix layer fails, and it MUST name the exposure-matrix blocker in `remaining_blockers`.
- **FR-014**: The system MUST mark the report as `selected_action_outcome_alignment_blocked` when selected-action outcome evidence is insufficient, and it MUST name the selected-action outcome blocker in `remaining_blockers`.
- **FR-015**: The system MUST mark the report as `behavior_drift_detected` when the rerun evidence conflicts with the stable behavior baseline.
- **FR-016**: The system MUST mark the report as `prerequisite_blocked` when the required prior committed inputs are unavailable or inconsistent.
- **FR-017**: The system MUST not claim paper-mechanism readiness when any alignment layer is partial or unavailable.
- **FR-018**: The system MUST preserve evidence-rerun-only behavior and MUST not change policy behavior, runtime semantics, reward timing, timeout handling, queue behavior, execution behavior, transmission behavior, or capacity semantics.
- **FR-019**: The system MUST not run training, optimizer steps, replay training, target updates, checkpoints, campaigns, or paper-reproduction workflows.
- **FR-020**: The system MUST emit JSON and Markdown report artifacts that include the required decision fields and blocker summary.
- **FR-021**: The system MUST keep `.specify/feature.json` local-only and MUST not stage or commit it as part of this feature.

### Key Entities *(include if feature involves data)*

- **Committed Prior Evidence Inputs**: The Feature 048 through 052 reports used as the immutable inputs for the rerun.
- **Alignment Status Bundle**: The top-level status fields that classify each alignment layer independently.
- **Blocker List**: The trace-backed reasons that prevent readiness when any layer is incomplete.
- **Rerun Verdict**: The final decision that determines whether the project can move to the next phase.
- **Training Readiness Contract**: The report decision that indicates the project is ready to enter the next training-readiness phase.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every generated Feature 053 report contains both JSON and Markdown artifacts and includes all required decision fields.
- **SC-002**: The report identifies the exact failing alignment layer whenever readiness is blocked, rather than returning a generic failure.
- **SC-003**: The report never marks `paper_mechanism_alignment_ready` true unless all required alignment statuses are `available`.
- **SC-004**: Re-running Feature 053 with the same committed inputs produces the same verdict, blocker list, and next-feature recommendation.
- **SC-005**: The report provides a clear transition decision into Feature 054 only when the alignment evidence is complete enough to support that step.
- **SC-006**: The report never claims training or paper-reproduction readiness when the evidence chain is incomplete.

## Assumptions

- Feature 052 is the authoritative source for determining whether selected-action family, selected-action-to-task join, and per-action outcome evidence are sufficiently complete to support the rerun.
- The current `main` branch already includes the committed workflow-contract update, so the rerun must reason from the current baseline rather than a stale exact-commit equality gate.
- Missing or partial alignment evidence must be reported explicitly rather than inferred from placeholder values.
- The feature is diagnostic and evidence-rerun only; any training or runtime repair remains a separate feature.
- The active SpecKit pointer may remain locally dirty while pointing to the Feature 053 directory, but it must not be staged or committed.

## Production Constraints

- Preserve evidence-rerun-only scope.
- Keep prior-feature artifacts immutable.
- Avoid any runtime, policy, or dependency drift.
- Do not claim training readiness without complete alignment evidence.

## Public Interfaces Affected

- Runtime model interface
- Evaluation metric interface
- Config schema
- Artifact schema

## Config / Schema Impact

- Required report fields must include the alignment status bundle, blocker list, verdict, and next-feature recommendation.
- Alignment status values must be limited to the approved readiness vocabulary.
- Backward compatibility is limited to reading prior committed reports as inputs.

## Artifact Impact

- Reports
- Validation summaries
- Debug traces

## Security Considerations

- No secrets, tokens, or credentials are required for this rerun.
- No remote code execution or external network access should be introduced.
- External references must remain documented and limited to committed project artifacts.

## Definition of Done

- Spec matched by plan
- Tests identified
- Assumptions documented
- Configs validated or updated
- Paper-to-code mapping updated
- Artifacts handled per lifecycle rules
- Review and merge gate satisfied
