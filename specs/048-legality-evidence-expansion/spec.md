# Feature Specification: Legality Evidence Expansion

**Feature Branch**: `048-legality-evidence-expansion`  
**Created**: 2026-05-22  
**Status**: Draft  
**Input**: User description: "Add passive legality evidence so the exposure matrix can measure legal-vs-selected action exposure without fake zeros or sample-only inference."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capture legality evidence without changing behavior (Priority: P1)

As an analyst, I want legality evidence recorded for each decision opportunity so that exposure analysis can distinguish legal action availability from selected action choice without inventing missing data.

**Why this priority**: Feature 047 cannot measure legal-vs-selected exposure until legality evidence exists for the same passive runs.

**Independent Test**: The feature can be validated by comparing behavior before and after instrumentation and confirming that the selected action sequence, rewards, terminal outcomes, queue progression, and deadline behavior remain unchanged while legality snapshots are present.

**Acceptance Scenarios**:

1. **Given** a paper-default passive run, **When** the feature records a decision opportunity, **Then** it stores the legality snapshot and selected action metadata for that opportunity.
2. **Given** the same passive run before and after this feature, **When** the trace outputs are compared, **Then** the selected action sequence and terminal outcomes are unchanged.
3. **Given** a decision opportunity where no action is selected, **When** the record is produced, **Then** the legality fields are marked unavailable instead of being invented.

---

### User Story 2 - Preserve the paper-default contract while exposing legality details (Priority: P2)

As a reviewer, I want the legality fields to reflect the existing runtime contract so that horizontal legality still depends on approved neighbors and vertical/cloud legality remains independent of Figure 7 topology.

**Why this priority**: The legality evidence must be faithful to the existing simulator contract, not a new interpretation of action rules.

**Independent Test**: The feature can be validated by confirming that local, horizontal, and vertical legality are reported for the same run contract used by prior features and that no runtime repair or semantic changes are introduced.

**Acceptance Scenarios**:

1. **Given** a task with an approved horizontal neighbor, **When** the legality record is written, **Then** the horizontal action is marked legal.
2. **Given** a task without an approved horizontal neighbor, **When** the legality record is written, **Then** the horizontal action is marked illegal.
3. **Given** a vertical or cloud action, **When** the legality record is written, **Then** the legality reflects the existing runtime contract rather than Figure 7 adjacency.

---

### User Story 3 - Enable Feature 049 rerun eligibility (Priority: P3)

As an analyst, I want the report to say whether the exposure matrix can be rerun with legality evidence so that the next feature is a rerun decision, not a guess.

**Why this priority**: Feature 048 is only useful if it clearly tells Feature 049 whether the exposure matrix can now be rerun with complete legality evidence.

**Independent Test**: The feature can be validated by confirming the report states the legality evidence coverage and routes to the next feature without recommending training or policy redesign.

**Acceptance Scenarios**:

1. **Given** full coverage of legality evidence, **When** the report is generated, **Then** it says Feature 049 can rerun the exposure matrix with legality evidence.
2. **Given** partial legality evidence coverage, **When** the report is generated, **Then** it says trace-depth expansion is required before the exposure-matrix rerun.
3. **Given** legality evidence that cannot be extracted without semantic changes, **When** the report is generated, **Then** it says a public legality helper feature is required before the exposure-matrix rerun.

### Edge Cases

- What happens when a selected action is missing even though a decision opportunity existed?
- How does the feature behave when legality snapshots are available for some runs but not all runs?
- What happens when a horizontal action is chosen on a node with no approved neighbor?
- How does the report handle a decision opportunity that could support multiple legal actions?
- What happens when legality evidence can be read from the runtime contract but not from the trace snapshot?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST record a legality snapshot for every decision opportunity where an action is selected or could be selected.
- **FR-002**: The system MUST preserve the paper-default runtime contract from prior features, including `N = 20`, `T = 110`, `P = 0.5`, `slot_duration_seconds = 0.1`, `timeout_slots = 20`, task sizes in `[2.0, 5.0]` Mbits, processing density `0.297`, private/public/cloud CPU `0.5/0.5/3.0`, `R_H = 30 Mbps`, `R_V = 10 Mbps`, the approved Figure 7 topology, neighbor-only horizontal legality, and non-terminal pending-at-horizon behavior.
- **FR-003**: The system MUST store legality fields for `strategy`, `seed`, `slot`, `agent_id`, `task_id`, `selected_action`, `action_index`, `legal_local`, `legal_horizontal`, `legal_vertical`, `legal_action_mask`, `selected_was_legal`, `selected_illegal_reason`, `legal_horizontal_neighbors`, `horizontal_neighbor_count`, `vertical_available`, `cloud_available`, `private_queue_available`, `public_queue_available`, `legality_evidence_source`, and `legality_snapshot_schema_version`.
- **FR-004**: The system MUST mark legality evidence unavailable instead of inventing a legality result when no decision opportunity exists or when the selected action is unavailable.
- **FR-005**: The system MUST classify a local action as legal when local/private processing is allowed by the existing runtime contract.
- **FR-006**: The system MUST classify a horizontal action as legal only when a legal neighbor exists under the approved Figure 7 topology.
- **FR-007**: The system MUST classify a vertical or cloud action as legal according to the existing runtime action contract and independently of Figure 7 topology.
- **FR-008**: The system MUST not alter selected action behavior, reward timing, timeout behavior, queue progression, capacity behavior, transmission behavior, or terminal outcomes.
- **FR-009**: The system MUST not generate fake legal evidence, fake action masks, or fake legality snapshots.
- **FR-010**: The system MUST emit JSON and Markdown legality-evidence report artifacts.
- **FR-011**: The system MUST expose the following report fields: `feature_id`, `prerequisite_tags_verified`, `prior_feature_gates_verified`, `paper_default_runtime_verified`, `legal_evidence_coverage_ratio`, `legality_evidence_source`, `legality_snapshot_schema`, `legality_evidence_coverage_summary`, `per_strategy_seed_legality_coverage`, `action_mask_summary`, `selected_illegal_action_summary`, `selected_illegal_action_count`, `selected_illegal_local_count`, `selected_illegal_horizontal_count`, `selected_illegal_vertical_count`, `selected_illegal_action_rate`, `selected_illegal_action_examples`, `selected_illegal_action_evidence_status`, `behavior_equivalence_summary`, `exposure_matrix_unblocked`, `recommended_next_feature`, `no_runtime_repair_performed`, `no_training_started`, `no_optimizer_step`, `no_replay_training`, `no_target_update_execution`, `no_dependency_drift`, `no_policy_drift`, `no_reward_timing_change`, `no_timeout_contract_drift`, `no_capacity_contract_drift`, `no_transmission_contract_drift`, `no_action_legality_drift`, `no_action_selection_drift`, `no_curve_fitting`, `no_simulator_output_tuning`, `no_paper_reproduction_claim`, and `final_verdict`.
- **FR-011a**: The system MUST define `legal_evidence_coverage_ratio` as `legality_snapshot_count / decision_opportunity_count`, MUST return `0.0` when decision opportunities are known but no legality snapshots exist, and MUST return `null` when the denominator is zero.
- **FR-011b**: The system MUST include `legal_evidence_coverage_ratio` both as a top-level report field and inside `legality_evidence_coverage_summary`.
- **FR-011c**: The system MUST expose `selected_illegal_action_evidence_status` as a first-class report field and inside `selected_illegal_action_summary`.
- **FR-011d**: The system MUST expose `selected_illegal_action_count`, `selected_illegal_local_count`, `selected_illegal_horizontal_count`, `selected_illegal_vertical_count`, `selected_illegal_action_rate`, and `selected_illegal_action_examples` as first-class report fields and inside `selected_illegal_action_summary`.
- **FR-012**: The system MUST classify the final verdict as `legality_evidence_ready_for_exposure_matrix_rerun` only when full legality evidence coverage exists and behavior equivalence passes.
- **FR-013**: The system MUST classify the final verdict as `legality_evidence_partial_requires_trace_depth_expansion` when legality evidence coverage is partial.
- **FR-014**: The system MUST classify the final verdict as `legality_evidence_unavailable_requires_runtime_public_helper` when legality evidence cannot be extracted without changing runtime semantics.
- **FR-015**: The system MUST classify the final verdict as `behavior_drift_detected` if the addition of legality evidence changes selected action behavior, reward behavior, queue behavior, or terminal outcomes.
- **FR-016**: The system MUST recommend `Feature 049 — Exposure-Matrix Rerun with Legality Evidence` only when full legality evidence coverage exists and behavior equivalence passes.
- **FR-017**: The system MUST recommend trace-depth expansion before Feature 049 when legality evidence is partial.
- **FR-018**: The system MUST recommend a public legality helper feature before Feature 049 when legality evidence requires runtime semantic change to extract.
- **FR-018a**: The system MUST not recommend Feature 049 when `legal_evidence_coverage_ratio` is `0.0` or `null`.
- **FR-019**: The system MUST remain passive instrumentation only and MUST not repair runtime behavior, redesign policy, run training, or claim paper reproduction.
- **FR-020**: The system MUST preserve representative examples as examples only and MUST not use them as a substitute for legality coverage.
- **FR-021**: The system MUST include Feature 044, Feature 045, Feature 046, and Feature 047 artifacts as prior feature gates.
- **FR-022**: The system MUST explicitly report whether Feature 049 can rerun the exposure matrix with legality evidence.

### Key Entities *(include if feature involves data)*

- **Legality Snapshot**: The per-decision evidence describing which action families were legal and why.
- **Legality Evidence Coverage**: The portion of the strategy/seed decision population that has trace-backed legality data.
- **Behavior Equivalence Summary**: The report component that confirms legality instrumentation did not change selected actions, rewards, queue progression, terminal outcomes, or timing behavior.
- **Action Mask Summary**: The summary of legal local, horizontal, and vertical availability across the passive runs.
- **Selected Illegal Action Summary**: The report component that describes whether illegal selections are observable and whether they can be used for rerun eligibility.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The report captures legality evidence for every available decision opportunity without inventing values for missing opportunities.
- **SC-002**: The report shows whether legality evidence covers the full strategy/seed decision population, a partial population, or no population at all.
- **SC-003**: The report confirms that selected action sequences, rewards, terminal outcomes, and queue progression remain unchanged after legality evidence is added.
- **SC-004**: The report clearly states whether Feature 049 can rerun the exposure matrix with legality evidence.
- **SC-005**: The feature introduces no runtime changes, no training, no optimizer activity, no replay training, no target updates, and no paper reproduction claim.
- **SC-006**: The report remains readable as both JSON and Markdown and is produced for every evaluated strategy/seed run.
- **SC-007**: If legality evidence is partial, the final verdict resolves to `legality_evidence_partial_requires_trace_depth_expansion`.
- **SC-008**: If legality evidence cannot be extracted without runtime semantic change, the final verdict resolves to `legality_evidence_unavailable_requires_runtime_public_helper`.
- **SC-009**: If behavior changes after adding legality evidence, the final verdict resolves to `behavior_drift_detected`.
- **SC-010**: If full legality evidence coverage exists and behavior equivalence passes, the report routes to `Feature 049 — Exposure-Matrix Rerun with Legality Evidence`.

## Assumptions

Feature 047 already identified the exposure-matrix gap and committed evidence from Features 044 through 047 is sufficient to evaluate whether legality snapshots can be added passively. Any legality field that cannot be recovered from existing runtime behavior must be reported as unavailable rather than synthesized. If legality evidence cannot be captured without changing runtime semantics, that limitation must be documented and routed to a separate public legality helper feature.

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
