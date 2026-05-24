# Selected-Action Family and Per-Action Outcome Evidence Report

- feature_id: `050-selected-action-family-per-action-outcome-evidence`
- final_verdict: `exposure_matrix_internal_consistency_failed`
- recommended_next_feature: `selected-action family trace repair before training`
- selected_action_family_evidence_status: `unavailable`
- selected_action_to_task_join_status: `unavailable`
- per_action_outcome_evidence_status: `unavailable`
- behavior_equivalence_passed: `True`

## Feature 049 Unblock Assessment
{
  "behavior_equivalence_passed": true,
  "exposure_matrix_internal_consistency_verified": false,
  "feature_049_can_be_rerun": false,
  "feature_049_remaining_blockers": [
    "selected_action_family_evidence_incomplete",
    "selected_action_to_task_join_incomplete",
    "per_action_outcome_join_incomplete",
    "exposure_matrix_internal_consistency_failed"
  ],
  "per_action_outcome_evidence_status": "unavailable",
  "recommended_next_feature": "selected-action family trace repair before training",
  "selected_action_family_evidence_status": "unavailable",
  "selected_action_to_task_join_status": "unavailable"
}

## Selected Action Family Evidence Summary
{
  "evidence_status": "unavailable",
  "selected_action_count": null,
  "selected_action_count_consistency_verified": false,
  "selected_horizontal_count": null,
  "selected_local_count": null,
  "selected_vertical_count": null
}

## Selected Action To Task Join Summary
{
  "missing_selected_action_task_join_count": null,
  "selected_action_to_task_join_count": null,
  "selected_action_to_task_join_ratio": null,
  "selected_action_to_task_join_status": "unavailable"
}

## Per Action Outcome Join Summary
{
  "per_action_completion_count": {
    "horizontal": null,
    "local": null,
    "vertical": null
  },
  "per_action_completion_rate": {
    "horizontal": null,
    "local": null,
    "vertical": null
  },
  "per_action_drop_count": {
    "horizontal": null,
    "local": null,
    "vertical": null
  },
  "per_action_drop_rate": {
    "horizontal": null,
    "local": null,
    "vertical": null
  },
  "per_action_outcome_evidence_status": "unavailable",
  "per_action_pending_count": {
    "horizontal": null,
    "local": null,
    "vertical": null
  },
  "per_action_pending_rate": {
    "horizontal": null,
    "local": null,
    "vertical": null
  }
}

## Behavior Equivalence Summary
{
  "checks": [
    {
      "details": "reward values must match; sample_count=15",
      "name": "same_rewards",
      "verified": true
    },
    {
      "details": "finalized task payloads must match; sample_count=15",
      "name": "same_finalized_tasks",
      "verified": true
    },
    {
      "details": "terminal flags must match; sample_count=15",
      "name": "same_terminal_flags",
      "verified": true
    },
    {
      "details": "queue load must match; sample_count=15",
      "name": "same_queue_load",
      "verified": true
    },
    {
      "details": "selected actions must match; sample_count=15",
      "name": "same_action_sequence",
      "verified": true
    },
    {
      "details": "completion/drop outcomes must match; sample_count=15",
      "name": "same_outcomes",
      "verified": true
    }
  ],
  "passed": true
}