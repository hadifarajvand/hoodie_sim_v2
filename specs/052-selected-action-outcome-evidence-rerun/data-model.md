# Data Model: Selected-Action Outcome Evidence Rerun

## Entities

### Feature 051 Trace Readiness Gate

- **Purpose**: Represents the upstream state proving the passive trace repair is ready for rerun analysis.
- **Fields**:
  - `evidence_readiness_for_feature_050_rerun`
  - `selected_action_family_evidence_status`
  - `selected_action_to_task_join_status`
  - `terminal_outcome_join_status`
  - `per_action_outcome_join_readiness`
  - `behavior_equivalence_summary.passed`

### Selected-Action Family Evidence Summary

- **Purpose**: Captures recomputed selected-action family evidence.
- **Fields**:
  - `selected_local_count`
  - `selected_horizontal_count`
  - `selected_vertical_count`
  - `selected_action_count`
  - `selected_action_count_consistency_verified`
  - `per_strategy_seed_selected_action_family_matrix`
  - `selected_action_family_evidence_status`

### Selected-Action-to-Task Join Summary

- **Purpose**: Captures join evidence from selected action to task identity.
- **Fields**:
  - `selected_action_to_task_join_count`
  - `selected_action_to_task_join_ratio`
  - `missing_selected_action_task_join_count`
  - `selected_action_to_task_join_status`

### Per-Action Outcome Evidence Summary

- **Purpose**: Captures terminal outcome evidence recomputed from the selected-action trace.
- **Fields**:
  - `per_action_completion_count`
  - `per_action_drop_count`
  - `per_action_pending_count`
  - `per_action_completion_rate`
  - `per_action_drop_rate`
  - `per_action_pending_rate`
  - `per_action_outcome_evidence_status`

### Per-Action Outcome Matrix

- **Purpose**: Records the evidence matrix used to support rerun conclusions.
- **Fields**:
  - strategy
  - seed
  - selected action family
  - task join keys
  - terminal outcome join keys
  - terminal outcome classification

### Legal-But-Unselected Consistency Summary

- **Purpose**: Captures the counts needed to prove unselected-but-legal action evidence is internally consistent.
- **Fields**:
  - `legal_but_unselected_local_count`
  - `legal_but_unselected_horizontal_count`
  - `legal_but_unselected_vertical_count`
  - `legal_but_unselected_consistency_verified`

### Exposure Matrix Internal Consistency Summary

- **Purpose**: Captures whether the recomputed evidence remains self-consistent.
- **Fields**:
  - `selected_action_count`
  - `selected_local_count`
  - `selected_horizontal_count`
  - `selected_vertical_count`
  - `selected_illegal_action_count`
  - `exposure_matrix_internal_consistency_verified`

### Feature 049 Unblock Assessment

- **Purpose**: Captures whether the recomputed evidence is sufficient to rerun Feature 049.
- **Fields**:
  - `feature_049_can_be_rerun`
  - `feature_049_remaining_blockers`
  - `recommended_next_feature`

## Relationships

- Feature 052 consumes Feature 051 trace readiness as a gate.
- Feature 052 recomputes evidence summaries from committed prior artifacts.
- The unblock assessment depends on family evidence, task joins, per-action outcomes, legal-but-unselected consistency, exposure consistency, and behavior equivalence.

## Validation Rules

- `selected_action_count` must equal `selected_local_count + selected_horizontal_count + selected_vertical_count`.
- `selected_illegal_action_count` must not exceed `selected_action_count`.
- Per-action terminal outcome counts must not exceed selected counts.
- Legal-but-unselected counts must be non-negative.
- No count may be fabricated from a placeholder zero when evidence is missing.
