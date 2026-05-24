# Passive Selected-Action Trace Repair Report

- feature_id: `051-passive-selected-action-trace-repair`
- final_verdict: `selected_action_family_trace_incomplete`
- recommended_next_feature: `selected-action family trace repair continuation`
- behavior_equivalence_passed: `True`
- selected_action_family_evidence_status: `unavailable`
- selected_action_to_task_join_status: `unavailable`
- terminal_outcome_join_status: `unavailable`
- per_action_outcome_join_readiness: `unavailable`
- evidence_readiness_for_feature_050_rerun: `False`

## Selected Action Trace Schema
{
  "decision_point_fields": [
    "strategy",
    "seed",
    "slot",
    "agent_id",
    "task_id",
    "selected_action",
    "action_index",
    "selected_action_family",
    "decision_event_id"
  ],
  "join_key_fields": [
    "selected_action_to_task_join_key",
    "terminal_outcome_join_key"
  ],
  "required_fields": [
    "selected_action",
    "action_index",
    "selected_action_family",
    "selected_action_trace_source",
    "decision_event_id",
    "selected_action_to_task_join_key",
    "terminal_outcome_join_key"
  ],
  "trace_source_fields": [
    "selected_action_trace_source",
    "trace_source_component"
  ]
}

## Selected Action Trace Emission Summary
{
  "selected_action_emitted_at_decision_point": true,
  "selected_action_family_guessed_from_legality_mask": false,
  "selected_action_metadata_emitted_after_outcome": false,
  "selected_action_to_task_join_key_emitted": true,
  "selected_action_trace_source_emitted": true,
  "terminal_outcome_join_key_emitted": true
}

## Selected Action Family Trace Summary
{
  "per_strategy_seed_selected_action_family_matrix": [],
  "selected_action_count": null,
  "selected_action_count_consistency_verified": false,
  "selected_action_family_evidence_status": "unavailable",
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

## Terminal Outcome Join Key Summary
{
  "missing_terminal_outcome_join_count": null,
  "terminal_outcome_join_count": null,
  "terminal_outcome_join_ratio": null,
  "terminal_outcome_join_status": "unavailable"
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

## Evidence Readiness
{
  "evidence_readiness_for_feature_050_rerun": false,
  "per_action_outcome_join_readiness": "unavailable",
  "remaining_blockers": [
    "selected_action_family_evidence_incomplete",
    "selected_action_to_task_join_incomplete",
    "terminal_outcome_join_key_incomplete",
    "per_action_outcome_join_incomplete"
  ],
  "selected_action_family_evidence_status": "unavailable",
  "selected_action_to_task_join_status": "unavailable",
  "terminal_outcome_join_status": "unavailable"
}