# Feature Specification: Exposure-Matrix Review

**Feature Branch**: `047-exposure-matrix-review`  
**Created**: 2026-05-22  
**Status**: Draft  
**Input**: User description: "Generate and validate the full-population legal-vs-selected action exposure matrix that Feature 046 could not produce from committed artifacts."

## Clarifications

### Session 2026-05-22

- Q: Should Feature 047 modify runtime to expose legal masks? → A: No. It must first try existing trace info, environment info, or public helper paths; runtime changes require a separate feature.
- Q: Should Feature 047 rerun the environment to collect a fresh exposure matrix? → A: Yes, using existing runtime behavior and passive analysis only; this is diagnostic execution, not training.
- Q: Should the exposure matrix use `T = 110`? → A: Yes.
- Q: Should Feature 047 use the same grid as Features 042-046? → A: Yes. Seeds `[0, 1, 2]` and the five existing probe strategies.
- Q: What source should be used for legal action evidence? → A: Priority order is trace `legality_snapshot` from Feature 044 instrumentation if available during fresh runs, then environment `action mask`, then existing public legality helper, otherwise legal evidence is unavailable.
- Q: Should unavailable legal exposure be reported as zero? → A: No. Use null/unavailable and mark the report incomplete.
- Q: Should Feature 047 recommend runtime repair? → A: No, unless a verified contradiction against Feature 45 or Feature 46 appears.
- Q: What is the next-feature routing rule? → A: Complete exposure matrix routes to `Feature 048 — Paper HOODIE Observation Vector`; incomplete legal evidence routes to legality evidence expansion before Feature 048.
- Q: Should dirty-worktree-sensitive older report tests be run? → A: No. Validate prior features through committed artifacts and safe tests only.
- Q: Should AGENTS.md be ignored? → A: No. It must be clean or stashed before report generation, and it must not be committed or added to `.gitignore`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validate full-population legal-vs-selected exposure coverage (Priority: P1)

As an analyst, I want to validate the complete legal-vs-selected action exposure matrix across the paper-default strategy and seed grid so that I can tell whether action exposure is real or simply unavailable in the committed evidence.

**Why this priority**: Feature 046 ended with an inconclusive verdict because the committed artifacts did not provide enough legal-mask evidence to support a full exposure matrix.

**Independent Test**: The review can be validated by confirming that every decision opportunity in the paper-default grid is counted, every legal action family is traced back to evidence, and sample-only slices never replace the full population in aggregate metrics or verdict routing.

**Acceptance Scenarios**:

1. **Given** the approved paper-default strategy/seed grid and full passive traces, **When** the review is generated, **Then** the report produces a complete legal-vs-selected exposure matrix with evidence-backed counts for all decision opportunities.
2. **Given** that legal-mask or equivalent legality evidence is unavailable for some or all decisions, **When** the review is generated, **Then** the report marks the exposure matrix incomplete instead of inventing zero counts or overclaiming completeness.

---

### User Story 2 - Distinguish action exposure from load and offload dominance (Priority: P2)

As a reviewer, I want the matrix to show whether action exposure, load dominance, or offload underexposure explains the observed completion weakness so that the next diagnostic step is defensible.

**Why this priority**: The next feature should differ depending on whether the system is underexposed to legal actions, dominated by load, or starved by offload-path pressure.

**Independent Test**: The review can be validated by confirming that the report ranks exposure bias, load dominance, and offload underexposure from the same full evidence population and produces a defensible routing recommendation.

**Acceptance Scenarios**:

1. **Given** a complete exposure matrix and measurable legal-vs-selected differences, **When** the review is generated, **Then** the report identifies whether action exposure bias is present.
2. **Given** a complete exposure matrix in which load dominates independently of action selection, **When** the review is generated, **Then** the report identifies load dominance and does not falsely route the feature toward runtime repair.
3. **Given** legal offload actions that exist but are rarely selected, **When** the review is generated, **Then** the report identifies offload underexposure as a distinct cause.

---

### User Story 3 - Preserve diagnostic-only scope and honest routing (Priority: P3)

As an analyst, I want the feature to remain diagnostic only so that it closes the evidence gap without changing runtime behavior.

**Why this priority**: The project needs evidence, not repair, and the next feature route must remain honest about missing or partial legality evidence.

**Independent Test**: The review can be validated by confirming that it does not modify runtime behavior, does not recommend repair, and reports incomplete evidence explicitly when needed.

**Acceptance Scenarios**:

1. **Given** an incomplete legality evidence set, **When** the review is generated, **Then** the report identifies the missing coverage and recommends legality evidence expansion before Feature 048.
2. **Given** a complete exposure matrix with no dominant action bias, **When** the review is generated, **Then** the report routes toward `Feature 048 — Paper HOODIE Observation Vector` only when the exposure matrix is actually complete and actionable.

### Edge Cases

- What happens when legality evidence exists for only a subset of decisions?
- How does the review behave when sample traces show exposure patterns but the full population does not?
- What happens when load and action exposure both appear plausible and the matrix cannot isolate a dominant cause?
- How does the report handle offload actions that are legal but practically never selected?
- What happens when no trace-backed legality snapshot or action mask is available?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST consume the committed paper-default passive evidence and evaluate the strategy/seed grid consisting of seeds `[0, 1, 2]` and the strategies `environment_default_policy_probe`, `force_local_legal_probe`, `force_horizontal_legal_probe`, `force_vertical_legal_probe`, and `mixed_legal_round_robin_probe`.
- **FR-002**: The system MUST preserve the paper-default runtime contract from Feature 046, including `N = 20`, `T = 110`, `P = 0.5`, `slot_duration_seconds = 0.1`, `timeout_slots = 20`, task sizes in `[2.0, 5.0]` Mbits, processing density `0.297`, private/public/cloud CPU `0.5/0.5/3.0`, `R_H = 30 Mbps`, `R_V = 10 Mbps`, the approved Figure 7 topology, neighbor-only horizontal legality, and non-terminal pending-at-horizon behavior.
- **FR-003**: The system MUST collect a full-population exposure matrix for every decision opportunity in the evaluated strategy/seed grid, including decision opportunity count, generated task count, admitted task count, selected action count, terminal task count, completed task count, dropped task count, and pending-at-horizon count.
- **FR-004**: The system MUST collect trace-backed legal action exposure evidence for local, horizontal, and vertical actions, including legal counts, selected counts, legal-but-unselected counts, and action entropy.
- **FR-005**: The system MUST compute per-action outcome rates for completion, drop, pending, mean wait slots, mean execution-progress slots, and mean task age at terminal outcome from the same evidence population used for the exposure matrix.
- **FR-006**: The system MUST compute queue-family counts for private, public, and cloud admissions from the same evidence population used for the exposure matrix.
- **FR-007**: The system MUST compute offload-path exposure metrics, including transmission-started counts, transmission-completed counts, offloaded completions, offloaded drops, and offloaded pending outcomes.
- **FR-008**: The system MUST use trace-backed legality evidence from a legality snapshot, environment action mask, or an approved public legality helper when determining legal action counts.
- **FR-009**: The system MUST mark the exposure matrix incomplete if legal action evidence is unavailable for all or part of the decision opportunities and MUST not invent zero legal counts.
- **FR-010**: The system MUST report the coverage ratio of legal action evidence when legality evidence is only available for a subset of decisions.
- **FR-011**: The system MUST distinguish action exposure bias, load dominance, and offload underexposure in the diagnosis when the evidence supports that separation.
- **FR-012**: The system MUST recommend `Feature 048 — Paper HOODIE Observation Vector` only when the exposure matrix is complete and action exposure is measurable.
- **FR-013**: The system MUST recommend legality evidence expansion before Feature 048 when legal-mask evidence is unavailable or too sparse to support a defensible matrix.
- **FR-014**: The system MUST recommend load/admission assumption review before training when the complete matrix shows load dominance independent of action exposure.
- **FR-015**: The system MUST recommend `Feature 048 — Paper HOODIE Observation Vector` when offload actions are legal but rarely selected and that underexposure is trace-backed.
- **FR-016**: The system MUST remain diagnostic only and MUST not repair runtime behavior, redesign policy, run training, or claim paper reproduction.
- **FR-017**: The system MUST not change reward timing, timeout semantics, capacity semantics, transmission semantics, action legality, queue legality, or topology legality.
- **FR-018**: The system MUST not use sample-only aggregates as a substitute for full-population exposure metrics.
- **FR-019**: The system MUST explicitly state when the exposure matrix is incomplete because only a subset of legality evidence is available.
- **FR-020**: The system MUST emit JSON and Markdown report artifacts for review and downstream planning.
- **FR-021**: The system MUST expose illegal-selection tracking as a first-class metric family, including `selected_illegal_action_count`, `selected_illegal_local_count`, `selected_illegal_horizontal_count`, `selected_illegal_vertical_count`, `selected_illegal_action_examples`, and `selected_illegal_action_rate`.
- **FR-022**: The system MUST define a selected action as illegal when the chosen action family is illegal under the corresponding legality evidence, when the selected action is outside the supported action set, or when a required selection is missing without an explicit unavailable marker.
- **FR-023**: The system MUST treat illegal-selection counts and rates as unavailable rather than zero when legal action evidence is unavailable.
- **FR-024**: The system MUST compute illegal-selection counts and rates over the full strategy/seed decision population when full legal evidence is available.
- **FR-025**: The system MUST include illegal selections in the per-strategy seed matrix and aggregate exposure matrix when full legal evidence is available.
- **FR-026**: The system MUST report `illegal_action_summary.selected_illegal_action_count`, `illegal_action_summary.selected_illegal_local_count`, `illegal_action_summary.selected_illegal_horizontal_count`, `illegal_action_summary.selected_illegal_vertical_count`, `illegal_action_summary.selected_illegal_action_examples`, `illegal_action_summary.selected_illegal_action_rate`, and `illegal_action_summary.evidence_status` as explicit fields in the feature output.
- **FR-027**: The system MUST include `selected_illegal_action_count` in both `aggregate_exposure_matrix` and `per_strategy_seed_matrix` when full legal evidence is available.
- **FR-028**: The system MUST include Feature 044, Feature 045, and Feature 046 artifacts as the prior feature gates.
- **FR-029**: The system MUST expose the following report fields: `feature_id`, `prerequisite_tags_verified`, `prior_feature_gates_verified`, `paper_default_runtime_verified`, `exposure_matrix_input_sources`, `exposure_matrix_population`, `legal_action_evidence_source`, `legal_action_evidence_coverage_ratio`, `per_strategy_seed_matrix`, `aggregate_exposure_matrix`, `per_action_outcome_matrix`, `per_queue_matrix`, `offload_exposure_matrix`, `illegal_action_summary`, `exposure_bias_summary`, `load_vs_exposure_summary`, `matrix_completeness_summary`, `dominant_exposure_findings`, `diagnosis`, `recommended_next_feature`, `no_runtime_repair_performed`, `no_training_started`, `no_optimizer_step`, `no_replay_training`, `no_target_update_execution`, `no_dependency_drift`, `no_environment_contract_drift`, `no_policy_drift`, `no_reward_timing_change`, `no_timeout_contract_drift`, `no_capacity_contract_drift`, `no_transmission_contract_drift`, `no_action_legality_drift`, `no_curve_fitting`, `no_simulator_output_tuning`, `no_paper_reproduction_claim`, and `final_verdict`.
- **FR-030**: The system MUST classify the final verdict as `exposure_matrix_incomplete_requires_legality_evidence` when legal action exposure evidence is unavailable.
- **FR-031**: The system MUST classify the final verdict as `exposure_matrix_incomplete_requires_full_trace_collection` when the evaluated strategy/seed grid cannot be fully covered by committed passive traces.
- **FR-032**: The system MUST classify the final verdict as `exposure_matrix_complete_ready_for_observation_vector`, `exposure_matrix_identifies_action_exposure_bias`, `exposure_matrix_identifies_load_dominance`, or `exposure_matrix_identifies_offload_underexposure` only when the evidence supports that conclusion.
- **FR-033**: The system MUST preserve representative sample slices only as examples and MUST not use them to replace missing aggregate matrix coverage.

### Key Entities *(include if feature involves data)*

- **Exposure Matrix**: The complete set of decision-opportunity counts and action-family exposure counts for each strategy and seed.
- **Legal Action Evidence**: Trace-backed evidence showing which actions were legal at each decision opportunity.
- **Selected Action Distribution**: The action families actually selected under each strategy and seed.
- **Per-Action Outcome Matrix**: The outcome rates and timing summaries associated with each action family.
- **Per-Queue Matrix**: The admission and terminal outcome counts associated with private, public, and cloud queues.
- **Offload Exposure Matrix**: The transmission and offload outcome counts for legal offload-capable actions.
- **Exposure Bias Summary**: The analytical summary describing whether action exposure, load dominance, or offload underexposure best explains the observed weakness.
- **Matrix Completeness Summary**: The report component describing whether the full-population matrix is complete or limited by missing legality evidence.
- **Diagnosis Report**: The final passive analysis artifact that names the dominant exposure story and recommends the next feature or evidence-expansion step.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The report evaluates the full paper-default strategy/seed grid or explicitly reports the missing coverage.
- **SC-002**: The report includes trace-backed legal-vs-selected action exposure for every decision opportunity when legality evidence is available.
- **SC-003**: The report never reports fake zero legal action counts when legality evidence is unavailable.
- **SC-004**: The report identifies action exposure bias, load dominance, or offload underexposure whenever the evidence supports one of those conclusions.
- **SC-005**: The report clearly states when the matrix is incomplete and what evidence is missing.
- **SC-006**: The report recommends a defensible next feature or evidence-expansion step without recommending runtime repair.
- **SC-007**: The feature introduces no runtime changes, no training, no optimizer activity, no replay training, no target updates, and no paper reproduction claim.
- **SC-008**: The report remains readable as both JSON and Markdown and is produced for every evaluated strategy/seed run.
- **SC-009**: If legal action evidence is unavailable, the final verdict resolves to `exposure_matrix_incomplete_requires_legality_evidence`.
- **SC-010**: If the matrix is complete and action exposure is measurable, the report routes to `Feature 048 — Paper HOODIE Observation Vector`.

## Assumptions

The committed passive trace bank from Feature 044 and the committed Feature 045 diagnostics are sufficient to evaluate the baseline paper-default grid, even if they do not contain complete legality evidence for every decision opportunity. Any missing legality data must be treated as a first-class evidence gap rather than inferred from sample traces. Representative samples may illustrate behavior, but they do not substitute for full-population exposure evidence. Runtime changes remain out of scope unless a separate, verified contradiction against Features 045 or 046 is found.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Environment reset/step
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
- [x] Debug traces
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
