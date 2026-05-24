# Data Model: Passive Selected-Action Trace Repair

## SelectedActionTraceRecord

Represents one decision opportunity captured in the passive trace.

### Fields

- `decision_event_id`: deterministic identifier for the decision event
- `selected_action`: action actually chosen by the environment
- `action_index`: index or ordinal position of the chosen action in the decision context
- `selected_action_family`: normalized family label: `local`, `horizontal`, `vertical`, or `unknown`
- `selected_action_trace_source`: origin label for the passive trace record
- `strategy`: strategy label associated with the decision
- `seed`: run seed associated with the decision
- `slot`: slot or placement identifier associated with the decision
- `agent_id`: agent identifier associated with the decision
- `task_id`: task identifier associated with the decision
- `selected_action_to_task_join_key`: deterministic join key for task linkage
- `terminal_outcome_join_key`: deterministic join key for terminal-outcome linkage

### Validation Rules

- `selected_action_family` MUST be derived from the selected action actually used.
- `selected_action_family` MUST NOT be inferred from legality masks or downstream outcomes.
- `selected_action_to_task_join_key` MUST remain deterministic for the same decision opportunity.
- `terminal_outcome_join_key` MUST preserve a deterministic path to completed, dropped, or pending-at-horizon outcomes.

## SelectedActionFamilyTraceSummary

Summarizes whether the trace contains complete, partial, or incomplete selected-action family evidence.

### Fields

- `selected_action_family_evidence_status`
- `selected_action_count`
- `selected_local_count`
- `selected_horizontal_count`
- `selected_vertical_count`
- `selected_action_count_consistency_verified`
- `per_strategy_seed_selected_action_family_matrix`

### Validation Rules

- Counts MUST not be fabricated when evidence is incomplete.
- `selected_action_count` MUST equal the sum of local, horizontal, and vertical selected counts when available.

## SelectedActionJoinSummary

Summarizes whether selected actions can be joined to task identity and terminal outcomes.

### Fields

- `selected_action_to_task_join_status`
- `selected_action_to_task_join_count`
- `missing_selected_action_task_join_count`
- `terminal_outcome_join_status`
- `per_action_outcome_evidence_status`

### Validation Rules

- Join status MUST be `available`, `partial`, or `unavailable`.
- Join counts MUST be null when the join keys are unavailable.

## BehaviorEquivalenceSummary

Summarizes whether passive trace repair altered runtime behavior.

### Fields

- `passed`
- `checks`

### Validation Rules

- `checks` MUST contain unique names.
- The summary MUST show no drift in selected action sequence, rewards, terminal outcomes, queue progression, timeout/deadline outcomes, transmission outcomes, or execution progress counts.

## Feature050ReadinessSummary

Summarizes whether passive trace repair is sufficient to unblock Feature 050 rerun analysis.

### Fields

- `evidence_readiness_for_feature_050_rerun`
- `remaining_blockers`
- `recommended_next_feature`

### Validation Rules

- Readiness MUST be false when any required trace or join evidence is incomplete.
- `remaining_blockers` MUST be non-empty when readiness is false.
