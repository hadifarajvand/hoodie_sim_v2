# Feature Specification: Passive Selected-Action Trace Repair

**Feature Branch**: `051-passive-selected-action-trace-repair`  
**Created**: 2026-05-24  
**Status**: Draft  
**Input**: User description: "Feature 051 must repair the passive runtime trace so future evidence analysis can compute selected local/horizontal/vertical counts and join selected actions to task lifecycle outcomes. This is a passive trace repair feature, not a training feature and not a policy feature."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Emit Selected-Action Trace Evidence (Priority: P1)

As an analysis consumer, I want each decision opportunity to carry trace-backed selected-action identity and family information, so future evidence analysis can count selected local, horizontal, and vertical actions without inventing placeholder values.

**Why this priority**: Feature 050 cannot move forward until passive trace evidence exists for selected-action family reconstruction.

**Independent Test**: Generate the passive trace report and confirm that the trace schema and emission summary show selected action, action index, selected action family, strategy, seed, slot, agent identity, and decision-event identity for the required population.

**Acceptance Scenarios**:

1. **Given** passive runtime activity, **When** the trace repair report is generated, **Then** it records whether selected-action family evidence is emitted and identifies the trace source for each decision opportunity.
2. **Given** a decision opportunity with no trace-backed selected-action family evidence, **When** the report is generated, **Then** it marks the evidence as incomplete instead of fabricating counts or placeholder labels.

---

### User Story 2 - Preserve Join Keys for Task and Terminal Outcome Evidence (Priority: P2)

As an analysis consumer, I want selected actions to carry deterministic join keys for task identity and terminal outcomes, so future analysis can connect selected actions to task lifecycle outcomes.

**Why this priority**: The Feature 050 rerun path depends on a reliable selected-action-to-task join and a terminal-outcome join back to the selected action.

**Independent Test**: Generate the passive trace repair report and confirm it exposes join readiness for task identity and terminal outcome identity without changing runtime behavior.

**Acceptance Scenarios**:

1. **Given** a selected action with valid join keys, **When** the report is generated, **Then** the trace summary indicates the action can be joined to task identity and terminal outcome evidence.
2. **Given** a selected action without joinable keys, **When** the report is generated, **Then** the report marks the join incomplete rather than implying a successful join.

---

### User Story 3 - Assess Feature 050 Rerun Readiness (Priority: P3)

As a feature owner, I want a passive readiness summary that tells me whether Feature 050 can be rerun safely, so I can decide whether the selected-action evidence gap is repaired.

**Why this priority**: The next feature depends on evidence completeness and behavior stability, but the trace repair itself must remain passive.

**Independent Test**: Generate the report and confirm it includes a readiness verdict, blocker list, and recommended next feature based on trace completeness and behavior equivalence.

**Acceptance Scenarios**:

1. **Given** complete selected-action trace evidence and stable behavior, **When** the report is generated, **Then** it recommends the Feature 050 rerun path.
2. **Given** missing selected-action family emission or missing join keys, **When** the report is generated, **Then** it blocks the rerun and recommends continued trace repair.

### Edge Cases

- What happens when selected-action family evidence exists only for some strategies or seeds? The report must show partial emission rather than flattening missing rows into zero values.
- What happens when selected-action family evidence exists but task or terminal outcome join keys are absent? The report must mark join readiness incomplete rather than implying a full join.
- What happens when the passive trace is behaviorally stable but still incomplete for join purposes? The report must separate behavior equivalence from join readiness.
- What happens when trace evidence contradicts itself? The report must mark the readiness summary as blocked and explain the contradiction.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST use committed passive evidence from the prior feature artifacts as the only input source for Feature 051 analysis.
- **FR-002**: The system MUST expose a `selected_action_trace_schema` summary describing the passive fields available for selected-action repair.
- **FR-003**: The system MUST expose a `selected_action_trace_emission_summary` that identifies whether selected action, action index, selected action family, strategy, seed, slot, agent identity, and decision-event identity are trace-backed.
- **FR-004**: The system MUST expose a `selected_action_family_trace_summary` that reports whether selected-action family evidence is fully emitted, partially emitted, or incomplete.
- **FR-005**: The system MUST expose `selected_action_to_task_join_summary` that reports whether selected actions can be joined to `task_id` through deterministic join keys.
- **FR-006**: The system MUST expose `terminal_outcome_join_key_summary` that reports whether terminal outcome join keys are available for linking task lifecycle outcomes back to the selected action.
- **FR-007**: The system MUST preserve `selected_action_trace_source` so downstream analysis can distinguish committed passive trace evidence from any derived or inferred values.
- **FR-008**: The system MUST expose `selected_action_family_evidence_status`, `selected_action_to_task_join_status`, and `terminal_outcome_join_status` using the status vocabulary `available`, `partial`, and `unavailable` as appropriate to the passive trace evidence.
- **FR-009**: The system MUST expose `per_action_outcome_join_readiness` that describes whether future analysis can join selected actions to terminal outcomes without placeholder inference.
- **FR-010**: The system MUST expose `behavior_equivalence_summary` and `behavior_equivalence_passed` so the trace repair can be audited for runtime drift without changing behavior.
- **FR-011**: The system MUST expose `evidence_readiness_for_feature_050_rerun` that summarises whether the trace repair is sufficient to unblock Feature 050 analysis.
- **FR-012**: The system MUST expose `remaining_blockers` when trace repair is incomplete and MUST leave the blocker list non-empty whenever the final verdict is not ready for Feature 050 rerun.
- **FR-013**: The system MUST expose `recommended_next_feature` and MUST point to Feature 052 only when the passive trace repair is complete enough to support the Feature 050 rerun path.
- **FR-019**: The report MUST expose `selected_action_family_evidence_status`, `selected_action_to_task_join_status`, `terminal_outcome_join_status`, and `per_action_outcome_join_readiness` as top-level fields in addition to the supporting summary objects.
- **FR-014**: The system MUST never fabricate selected-action family counts, join keys, or readiness states when the passive trace evidence is missing.
- **FR-015**: The system MUST preserve passive-only behavior and MUST not change action selection, action legality, reward timing, timeout behavior, queue behavior, execution behavior, transmission behavior, or capacity semantics.
- **FR-016**: The system MUST not run training, optimizer steps, replay training, target updates, checkpoints, campaigns, or paper reproduction workflows.
- **FR-017**: The system MUST emit JSON and Markdown reports containing the required sections and evidence-readiness fields needed to audit Feature 050 rerun readiness.
- **FR-018**: The system MUST keep `.specify/feature.json` local-only when used as the active SpecKit pointer and MUST not stage or commit it as part of the feature.

### Key Entities *(include if feature involves data)*

- **Selected-Action Trace Record**: Passive trace evidence for a decision opportunity, including selected action, action index, selected action family, and trace source.
- **Selected-Action Join Key**: Deterministic evidence that links a selected action to task identity and downstream terminal outcome evidence.
- **Terminal Outcome Join Key**: Passive evidence that links a task lifecycle outcome back to the selected action that led to it.
- **Trace Repair Readiness Summary**: A report-level summary that explains whether the passive trace is sufficient to unblock Feature 050 rerun analysis.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The report identifies trace-backed selected-action family evidence for every emitted decision opportunity in 100% of generated Feature 051 runs.
- **SC-002**: The report distinguishes available, partial, and unavailable join readiness for selected-action-to-task and terminal-outcome evidence without substituting placeholder values.
- **SC-003**: The report includes behavior-equivalence results that remain stable across repeated passive runs, with no runtime drift introduced by the trace repair.
- **SC-004**: The report produces a clear Feature 050 readiness verdict and blocker list in every run, and the blocker list is non-empty whenever the verdict is not ready.
- **SC-005**: The report artifacts are generated in both JSON and Markdown form and include all required trace-schema, emission, join, readiness, and drift sections.

## Assumptions

- The hard prerequisite for implementation is that `main` equals `050-selected-action-family-per-action-outcome-evidence-complete^{}`.
- The authoritative prior evidence inputs are the committed Feature 044 passive lifecycle trace report, Feature 048 legality evidence report, Feature 049 exposure matrix paper mechanism report, and Feature 050 selected-action family/per-action outcome evidence report.
- Missing trace evidence must be reported explicitly rather than inferred from zero-valued placeholders.
- The feature is diagnostic and passive only; any future runtime repair remains a separate feature.
- The active SpecKit pointer may remain locally dirty while pointing to the Feature 051 directory, but it must not be staged or committed.

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
