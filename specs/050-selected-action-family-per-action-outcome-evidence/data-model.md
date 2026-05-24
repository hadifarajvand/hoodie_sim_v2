# Data Model: Selected-Action Family and Per-Action Outcome Evidence Expansion

## Entities

### SelectedActionEvidenceRow

Represents one passive decision opportunity with enough information to identify the selected action family.

**Fields**

- `strategy`: analysis or probe strategy name
- `seed`: deterministic seed identifier
- `slot`: runtime slot or decision index
- `agent_id`: agent identifier
- `task_id`: task identifier
- `decision_event_id`: deterministic event identifier or equivalent
- `selected_action`: action label or code
- `selected_action_family`: one of `local`, `horizontal`, `vertical`
- `action_index`: numeric action position
- `selected_action_source`: provenance of the selected action record
- `selected_action_family_evidence_status`: `available` or `unavailable`

**Relationships**

- Joins to `TerminalOutcomeEvidenceRow` by `strategy`, `seed`, `slot`, `agent_id`, `task_id`, and `decision_event_id` or deterministic equivalent.
- Aggregates into `SelectedActionFamilyMatrix`.

### TerminalOutcomeEvidenceRow

Represents the terminal lifecycle result associated with a selected action.

**Fields**

- `strategy`
- `seed`
- `slot`
- `agent_id`
- `task_id`
- `decision_event_id`
- `terminal_state`: `completed`, `dropped`, or `pending_at_horizon`
- `terminal_state_source`
- `join_status`

**Relationships**

- Joins back to `SelectedActionEvidenceRow`.
- Aggregates into `PerActionOutcomeMatrix`.

### SelectedActionFamilyMatrix

Aggregated passive evidence by strategy/seed and by action family.

**Fields**

- `strategy`
- `seed`
- `decision_opportunity_count`
- `selected_local_count`
- `selected_horizontal_count`
- `selected_vertical_count`
- `selected_action_count`
- `selected_action_count_consistency_verified`
- `selected_illegal_action_count`
- `selected_illegal_action_rate`
- `legal_but_unselected_local_count`
- `legal_but_unselected_horizontal_count`
- `legal_but_unselected_vertical_count`
- `legal_but_unselected_consistency_verified`
- `exposure_matrix_internal_consistency_verified`

### PerActionOutcomeMatrix

Aggregated selected-action outcomes after joining to terminal lifecycle state.

**Fields**

- `per_action_completion_count`
- `per_action_drop_count`
- `per_action_pending_count`
- `per_action_completion_rate`
- `per_action_drop_rate`
- `per_action_pending_rate`
- `per_action_outcome_evidence_status`

### Feature049UnblockAssessment

Readiness summary for rerunning Feature 049.

**Fields**

- `selected_action_family_evidence_status`
- `per_action_outcome_evidence_status`
- `selected_action_count_consistency_verified`
- `legal_but_unselected_consistency_verified`
- `exposure_matrix_internal_consistency_verified`
- `behavior_equivalence_passed`
- `final_verdict`
- `recommended_next_feature`

## Validation Rules

- Selected family counts MUST be trace-backed or explicitly unavailable.
- Outcome rates MUST not be zero-filled when evidence is absent.
- Legal-but-unselected counts MUST be derived only from legal counts and selected-family counts when both are available.
- Internal consistency MUST fail when any required count or join cannot be verified.

