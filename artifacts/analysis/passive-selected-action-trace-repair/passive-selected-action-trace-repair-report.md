# Passive Selected-Action Trace Repair Report

- feature_id: `051-passive-selected-action-trace-repair`
- final_verdict: `passive_selected_action_trace_ready_for_feature_050_rerun`
- recommended_next_feature: `Feature 052 — Selected-Action Outcome Evidence Rerun`
- behavior_equivalence_passed: `True`
- decision_opportunity_count: `3`
- selected_action_trace_record_count: `3`
- selected_action_family_trace_record_count: `3`
- selected_action_to_task_join_key_count: `3`
- terminal_outcome_join_key_count: `3`
- selected_action_family_evidence_status: `available`
- selected_action_to_task_join_status: `available`
- terminal_outcome_join_status: `available`
- per_action_outcome_join_readiness: `ready`
- evidence_readiness_for_feature_050_rerun: `True`
- selected_action_trace_coverage_ratio: `1.0`
- selected_action_family_coverage_ratio: `1.0`
- selected_action_to_task_join_coverage_ratio: `1.0`
- terminal_outcome_join_key_coverage_ratio: `1.0`

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
  "decision_opportunity_count": 3,
  "missing_selected_action_family_count": 0,
  "missing_selected_action_trace_count": 0,
  "per_strategy_seed_selected_action_family_matrix": [
    {
      "decision_opportunity_count": 3,
      "seed": 7,
      "selected_action_family_coverage_ratio": 1.0,
      "selected_action_family_trace_record_count": 3,
      "strategy": "passive_selected_action_trace_repair_probe"
    }
  ],
  "selected_action_count": 3,
  "selected_action_count_consistency_verified": true,
  "selected_action_family_coverage_ratio": 1.0,
  "selected_action_family_evidence_status": "available",
  "selected_action_family_trace_record_count": 3,
  "selected_action_trace_coverage_ratio": 1.0,
  "selected_action_trace_record_count": 3,
  "selected_horizontal_count": 0,
  "selected_local_count": 3,
  "selected_vertical_count": 0
}

## Selected Action To Task Join Summary
{
  "missing_selected_action_to_task_join_key_count": 0,
  "selected_action_to_task_join_count": 3,
  "selected_action_to_task_join_coverage_ratio": 1.0,
  "selected_action_to_task_join_status": "available"
}

## Terminal Outcome Join Key Summary
{
  "missing_terminal_outcome_join_key_count": 0,
  "terminal_outcome_join_key_count": 3,
  "terminal_outcome_join_key_coverage_ratio": 1.0,
  "terminal_outcome_join_status": "available"
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

## Evidence Readiness
{
  "decision_opportunity_count": 3,
  "evidence_readiness_for_feature_050_rerun": true,
  "per_action_outcome_join_readiness": "ready",
  "remaining_blockers": [],
  "selected_action_family_coverage_ratio": 1.0,
  "selected_action_family_evidence_status": "available",
  "selected_action_family_trace_record_count": 3,
  "selected_action_to_task_join_coverage_ratio": 1.0,
  "selected_action_to_task_join_key_count": 3,
  "selected_action_to_task_join_status": "available",
  "selected_action_trace_coverage_ratio": 1.0,
  "selected_action_trace_record_count": 3,
  "terminal_outcome_join_key_count": 3,
  "terminal_outcome_join_key_coverage_ratio": 1.0,
  "terminal_outcome_join_status": "available"
}