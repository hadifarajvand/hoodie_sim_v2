# Selected-Action Outcome Evidence Rerun Report

- feature_id: `052-selected-action-outcome-evidence-rerun`
- final_verdict: `selected_action_outcome_evidence_ready_for_feature_049_rerun`
- recommended_next_feature: `Feature 053 — Exposure Matrix Paper Mechanism Rerun with Outcome Evidence`
- feature_051_trace_readiness_verified: `True`
- selected_action_family_evidence_status: `available`
- selected_action_to_task_join_status: `available`
- per_action_outcome_evidence_status: `available`
- feature_049_can_be_rerun: `True`

## Feature 049 Unblock Assessment
{
  "behavior_equivalence_passed": true,
  "exposure_matrix_internal_consistency_verified": true,
  "feature_049_can_be_rerun": true,
  "feature_049_remaining_blockers": [],
  "legal_but_unselected_consistency_verified": true,
  "per_action_outcome_evidence_status": "available",
  "recommended_next_feature": "Feature 053 — Exposure Matrix Paper Mechanism Rerun with Outcome Evidence",
  "selected_action_family_evidence_status": "available",
  "selected_action_to_task_join_status": "available"
}

## Selected Action Family Evidence Summary
{
  "per_strategy_seed_selected_action_family_matrix": [
    {
      "action_family": "local",
      "legal_action_count": 3,
      "legal_but_unselected_count": 0,
      "seed": 7,
      "selected_action_completed_count": 3,
      "selected_action_completion_rate": 1.0,
      "selected_action_count": 3,
      "selected_action_drop_rate": 0.0,
      "selected_action_dropped_count": 0,
      "selected_action_pending_count": 0,
      "selected_action_pending_rate": 0.0,
      "selected_action_to_task_join_key_count": 3,
      "strategy": "selected_action_outcome_evidence_rerun_probe",
      "terminal_outcome_join_key_count": 3
    },
    {
      "action_family": "horizontal",
      "legal_action_count": 3,
      "legal_but_unselected_count": 3,
      "seed": 7,
      "selected_action_completed_count": 0,
      "selected_action_completion_rate": null,
      "selected_action_count": 0,
      "selected_action_drop_rate": null,
      "selected_action_dropped_count": 0,
      "selected_action_pending_count": 0,
      "selected_action_pending_rate": null,
      "selected_action_to_task_join_key_count": 0,
      "strategy": "selected_action_outcome_evidence_rerun_probe",
      "terminal_outcome_join_key_count": 0
    },
    {
      "action_family": "vertical",
      "legal_action_count": 3,
      "legal_but_unselected_count": 3,
      "seed": 7,
      "selected_action_completed_count": 0,
      "selected_action_completion_rate": null,
      "selected_action_count": 0,
      "selected_action_drop_rate": null,
      "selected_action_dropped_count": 0,
      "selected_action_pending_count": 0,
      "selected_action_pending_rate": null,
      "selected_action_to_task_join_key_count": 0,
      "strategy": "selected_action_outcome_evidence_rerun_probe",
      "terminal_outcome_join_key_count": 0
    }
  ],
  "selected_action_count": 3,
  "selected_action_count_consistency_verified": true,
  "selected_action_family_evidence_status": "available",
  "selected_horizontal_count": 0,
  "selected_local_count": 3,
  "selected_vertical_count": 0
}

## Selected Action To Task Join Summary
{
  "missing_selected_action_task_join_count": 0,
  "selected_action_to_task_join_count": 3,
  "selected_action_to_task_join_ratio": 1.0,
  "selected_action_to_task_join_status": "available"
}

## Per Action Outcome Join Summary
{
  "per_action_completion_count": {
    "horizontal": 0,
    "local": 3,
    "vertical": 0
  },
  "per_action_completion_rate": {
    "horizontal": null,
    "local": 1.0,
    "vertical": null
  },
  "per_action_drop_count": {
    "horizontal": 0,
    "local": 0,
    "vertical": 0
  },
  "per_action_drop_rate": {
    "horizontal": null,
    "local": 0.0,
    "vertical": null
  },
  "per_action_outcome_evidence_status": "available",
  "per_action_pending_count": {
    "horizontal": 0,
    "local": 0,
    "vertical": 0
  },
  "per_action_pending_rate": {
    "horizontal": null,
    "local": 0.0,
    "vertical": null
  }
}

## Legal But Unselected Consistency Summary
{
  "legal_but_unselected_consistency_verified": true,
  "legal_but_unselected_horizontal_count": 3,
  "legal_but_unselected_local_count": 0,
  "legal_but_unselected_vertical_count": 3
}

## Exposure Matrix Internal Consistency Summary
{
  "exposure_matrix_internal_consistency_verified": true,
  "legal_but_unselected_consistency_verified": true,
  "per_action_outcome_evidence_status": "available",
  "selected_action_count_consistency_verified": true,
  "selected_action_to_task_join_status": "available",
  "selected_illegal_action_count": 0
}

## Behavior Equivalence Summary
{
  "checks": [
    {
      "details": "reward sequences compared for traced and untraced runs",
      "name": "same_rewards",
      "verified": true
    },
    {
      "details": "finalized task identifiers compared for traced and untraced runs",
      "name": "same_finalized_tasks",
      "verified": true
    },
    {
      "details": "terminated/truncated flags compared for traced and untraced runs",
      "name": "same_terminal_flags",
      "verified": true
    },
    {
      "details": "queue load progression compared for traced and untraced runs",
      "name": "same_queue_load",
      "verified": true
    },
    {
      "details": "selected action sequence compared for traced and untraced runs",
      "name": "same_action_sequence",
      "verified": true
    },
    {
      "details": "task outcomes compared for traced and untraced runs",
      "name": "same_outcomes",
      "verified": true
    }
  ],
  "passed": true
}