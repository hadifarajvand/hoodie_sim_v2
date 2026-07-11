# Passive Runtime Lifecycle Trace Instrumentation Report

- feature_id: `044-passive-runtime-lifecycle-trace-instrumentation`
- final_verdict: `passive_trace_instrumentation_ready`

## Trace Coverage Summary
{
  "completion_drop_ordering_observed": true,
  "deadline_expired_observed": true,
  "deadline_expired_supported": true,
  "event_statuses": [
    {
      "event_type": "task_generated",
      "event_type_missing_from_instrumentation": false,
      "event_type_observed": true,
      "event_type_supported": true
    },
    {
      "event_type": "task_admitted",
      "event_type_missing_from_instrumentation": false,
      "event_type_observed": true,
      "event_type_supported": true
    },
    {
      "event_type": "transmission_started",
      "event_type_missing_from_instrumentation": false,
      "event_type_observed": true,
      "event_type_supported": true
    },
    {
      "event_type": "transmission_completed",
      "event_type_missing_from_instrumentation": false,
      "event_type_observed": true,
      "event_type_supported": true
    },
    {
      "event_type": "execution_started",
      "event_type_missing_from_instrumentation": false,
      "event_type_observed": true,
      "event_type_supported": true
    },
    {
      "event_type": "execution_progress",
      "event_type_missing_from_instrumentation": false,
      "event_type_observed": true,
      "event_type_supported": true
    },
    {
      "event_type": "execution_completed",
      "event_type_missing_from_instrumentation": false,
      "event_type_observed": true,
      "event_type_supported": true
    },
    {
      "event_type": "deadline_reached",
      "event_type_missing_from_instrumentation": false,
      "event_type_observed": true,
      "event_type_supported": true
    },
    {
      "event_type": "deadline_expired",
      "event_type_missing_from_instrumentation": false,
      "event_type_observed": true,
      "event_type_supported": true
    },
    {
      "event_type": "task_completed",
      "event_type_missing_from_instrumentation": false,
      "event_type_observed": true,
      "event_type_supported": true
    },
    {
      "event_type": "task_dropped",
      "event_type_missing_from_instrumentation": false,
      "event_type_observed": true,
      "event_type_supported": true
    },
    {
      "event_type": "reward_emitted",
      "event_type_missing_from_instrumentation": false,
      "event_type_observed": true,
      "event_type_supported": true
    },
    {
      "event_type": "pending_at_horizon",
      "event_type_missing_from_instrumentation": false,
      "event_type_observed": true,
      "event_type_supported": true
    }
  ],
  "event_type_missing_from_instrumentation": [],
  "event_type_observed": {
    "deadline_expired": true,
    "deadline_reached": true,
    "execution_completed": true,
    "execution_progress": true,
    "execution_started": true,
    "pending_at_horizon": true,
    "reward_emitted": true,
    "task_admitted": true,
    "task_completed": true,
    "task_dropped": true,
    "task_generated": true,
    "transmission_completed": true,
    "transmission_started": true
  },
  "event_type_supported": {
    "deadline_expired": true,
    "deadline_reached": true,
    "execution_completed": true,
    "execution_progress": true,
    "execution_started": true,
    "pending_at_horizon": true,
    "reward_emitted": true,
    "task_admitted": true,
    "task_completed": true,
    "task_dropped": true,
    "task_generated": true,
    "transmission_completed": true,
    "transmission_started": true
  },
  "event_types_seen": [
    "deadline_expired",
    "deadline_reached",
    "execution_completed",
    "execution_progress",
    "execution_started",
    "pending_at_horizon",
    "reward_emitted",
    "task_admitted",
    "task_completed",
    "task_dropped",
    "task_generated",
    "transmission_completed",
    "transmission_started"
  ],
  "execution_progress_observed": true,
  "pending_at_horizon_observed": true,
  "required_event_types": [
    "task_generated",
    "task_admitted",
    "transmission_started",
    "transmission_completed",
    "execution_started",
    "execution_progress",
    "execution_completed",
    "deadline_reached",
    "deadline_expired",
    "task_completed",
    "task_dropped",
    "reward_emitted",
    "pending_at_horizon"
  ],
  "task_completed_observed": true,
  "task_completed_supported": true
}

## Behavior Equivalence Checks
[
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
]

## Lifecycle Trace Sample
[
  {
    "absolute_deadline_slot": 20,
    "agent_id": 3,
    "arrival_slot": 0,
    "cycles_required_gcycles": 0.594,
    "event_type": "task_generated",
    "legality_snapshot": {},
    "processing_density_gcycles_per_mbit": 0.297,
    "queue_type": "pending_arrival",
    "reward_available": false,
    "size_mbits": 2.0,
    "slot": 0,
    "source_agent_id": 3,
    "task_age_slots": 0,
    "task_id": 1,
    "trace_source_component": "traffic_generator"
  },
  {
    "absolute_deadline_slot": 20,
    "action_index": 0,
    "agent_id": 3,
    "arrival_slot": 0,
    "cycles_required_gcycles": 0.594,
    "decision_event_id": "paper_default-0:0:1",
    "destination": "self",
    "event_type": "task_admitted",
    "host_node_id": "3",
    "legality_snapshot": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "processing_density_gcycles_per_mbit": 0.297,
    "queue_type": "private",
    "reward_available": false,
    "selected_action": "local",
    "selected_action_family": "local",
    "selected_action_to_task_join_key": "paper_default-0:1",
    "selected_action_trace_source": "decision_point",
    "size_mbits": 2.0,
    "slot": 0,
    "source_agent_id": 3,
    "strategy": "HOODIE",
    "task_age_slots": 0,
    "task_id": 1,
    "terminal_outcome_join_key": "paper_default-0:1:terminal_outcome",
    "trace_source_component": "environment"
  },
  {
    "absolute_deadline_slot": 20,
    "action_index": 0,
    "agent_id": 3,
    "arrival_slot": 0,
    "compute_capacity_gcycles_per_slot": 0.5,
    "cycles_after_gcycles": 0.09399999999999997,
    "cycles_before_gcycles": 0.594,
    "cycles_consumed_gcycles": 0.5,
    "cycles_required_gcycles": 0.594,
    "decision_event_id": "paper_default-0:0:1",
    "destination": "self",
    "event_type": "execution_started",
    "host_node_id": "3",
    "legality_snapshot": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "processing_density_gcycles_per_mbit": 0.297,
    "queue_type": "private",
    "reward_available": false,
    "selected_action": "local",
    "selected_action_family": "local",
    "selected_action_to_task_join_key": "paper_default-0:1",
    "selected_action_trace_source": "decision_point",
    "size_mbits": 2.0,
    "slot": 0,
    "source_agent_id": 3,
    "strategy": "HOODIE",
    "task_age_slots": 0,
    "task_id": 1,
    "terminal_outcome_join_key": "paper_default-0:1:terminal_outcome",
    "trace_source_component": "environment"
  },
  {
    "absolute_deadline_slot": 20,
    "action_index": 0,
    "agent_id": 3,
    "arrival_slot": 0,
    "compute_capacity_gcycles_per_slot": 0.5,
    "cycles_after_gcycles": 0.09399999999999997,
    "cycles_before_gcycles": 0.594,
    "cycles_consumed_gcycles": 0.5,
    "cycles_required_gcycles": 0.594,
    "decision_event_id": "paper_default-0:0:1",
    "destination": "self",
    "event_type": "execution_progress",
    "host_node_id": "3",
    "legality_snapshot": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "processing_density_gcycles_per_mbit": 0.297,
    "queue_type": "private",
    "reward_available": false,
    "selected_action": "local",
    "selected_action_family": "local",
    "selected_action_to_task_join_key": "paper_default-0:1",
    "selected_action_trace_source": "decision_point",
    "size_mbits": 2.0,
    "slot": 0,
    "source_agent_id": 3,
    "strategy": "HOODIE",
    "task_age_slots": 0,
    "task_id": 1,
    "terminal_outcome_join_key": "paper_default-0:1:terminal_outcome",
    "trace_source_component": "environment"
  },
  {
    "absolute_deadline_slot": 20,
    "agent_id": 4,
    "arrival_slot": 0,
    "cycles_required_gcycles": 0.6237,
    "event_type": "task_generated",
    "legality_snapshot": {},
    "processing_density_gcycles_per_mbit": 0.297,
    "queue_type": "pending_arrival",
    "reward_available": false,
    "size_mbits": 2.1,
    "slot": 1,
    "source_agent_id": 4,
    "task_age_slots": 1,
    "task_id": 2,
    "trace_source_component": "traffic_generator"
  }
]
