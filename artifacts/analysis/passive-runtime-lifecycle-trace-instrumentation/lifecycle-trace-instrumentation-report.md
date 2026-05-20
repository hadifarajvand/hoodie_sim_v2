# Passive Runtime Lifecycle Trace Instrumentation Report

- feature_id: `044-passive-runtime-lifecycle-trace-instrumentation`
- final_verdict: `passive_trace_instrumentation_incomplete`

## Trace Coverage Summary
{
  "completion_drop_ordering_observed": true,
  "event_types_missing": [
    "deadline_reached",
    "deadline_expired",
    "task_completed"
  ],
  "event_types_seen": [
    "execution_completed",
    "execution_progress",
    "execution_started",
    "pending_at_horizon",
    "reward_emitted",
    "task_admitted",
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
  ]
}

## Behavior Equivalence Checks
[
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  },
  {
    "details": "reward values must match",
    "name": "same_rewards",
    "verified": true
  },
  {
    "details": "finalized task payloads must match",
    "name": "same_finalized_tasks",
    "verified": true
  },
  {
    "details": "terminal flags must match",
    "name": "same_terminal_flags",
    "verified": true
  },
  {
    "details": "queue load must match",
    "name": "same_queue_load",
    "verified": true
  },
  {
    "details": "selected actions must match",
    "name": "same_action_sequence",
    "verified": true
  },
  {
    "details": "completion/drop outcomes must match",
    "name": "same_outcomes",
    "verified": true
  }
]

## Lifecycle Trace Sample
[
  {
    "absolute_deadline_slot": 2,
    "arrival_slot": 0,
    "cycles_required_gcycles": 236.0,
    "event_type": "task_generated",
    "legality_snapshot": {},
    "processing_density_gcycles_per_mbit": 4.0,
    "queue_type": "pending_arrival",
    "reward_available": false,
    "size_mbits": 59.0,
    "slot": 0,
    "source_agent_id": 1,
    "task_age_slots": 0,
    "task_id": 1,
    "trace_source_component": "traffic_generator"
  },
  {
    "absolute_deadline_slot": 2,
    "arrival_slot": 0,
    "cycles_required_gcycles": 236.0,
    "destination": "self",
    "event_type": "task_admitted",
    "host_node_id": "1",
    "legality_snapshot": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "processing_density_gcycles_per_mbit": 4.0,
    "queue_type": "private",
    "reward_available": false,
    "selected_action": "local",
    "size_mbits": 59.0,
    "slot": 0,
    "source_agent_id": 1,
    "task_age_slots": 0,
    "task_id": 1,
    "trace_source_component": "environment"
  },
  {
    "absolute_deadline_slot": 2,
    "arrival_slot": 0,
    "compute_capacity_gcycles_per_slot": 0.5,
    "cycles_after_gcycles": 235.5,
    "cycles_before_gcycles": 236.0,
    "cycles_consumed_gcycles": 0.5,
    "cycles_required_gcycles": 236.0,
    "destination": "self",
    "event_type": "execution_started",
    "host_node_id": "1",
    "legality_snapshot": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "processing_density_gcycles_per_mbit": 4.0,
    "queue_type": "private",
    "reward_available": false,
    "selected_action": "local",
    "size_mbits": 59.0,
    "slot": 0,
    "source_agent_id": 1,
    "task_age_slots": 0,
    "task_id": 1,
    "trace_source_component": "environment"
  },
  {
    "absolute_deadline_slot": 2,
    "arrival_slot": 0,
    "compute_capacity_gcycles_per_slot": 0.5,
    "cycles_after_gcycles": 235.5,
    "cycles_before_gcycles": 236.0,
    "cycles_consumed_gcycles": 0.5,
    "cycles_required_gcycles": 236.0,
    "destination": "self",
    "event_type": "execution_progress",
    "host_node_id": "1",
    "legality_snapshot": {
      "compute_local": true,
      "horizontal": true,
      "local": true,
      "offload_horizontal": true,
      "offload_vertical": true,
      "vertical": true
    },
    "processing_density_gcycles_per_mbit": 4.0,
    "queue_type": "private",
    "reward_available": false,
    "selected_action": "local",
    "size_mbits": 59.0,
    "slot": 0,
    "source_agent_id": 1,
    "task_age_slots": 0,
    "task_id": 1,
    "trace_source_component": "environment"
  },
  {
    "absolute_deadline_slot": 6,
    "arrival_slot": 1,
    "cycles_required_gcycles": 215.0,
    "event_type": "task_generated",
    "legality_snapshot": {},
    "processing_density_gcycles_per_mbit": 5.0,
    "queue_type": "pending_arrival",
    "reward_available": false,
    "size_mbits": 43.0,
    "slot": 1,
    "source_agent_id": 2,
    "task_age_slots": 0,
    "task_id": 2,
    "trace_source_component": "traffic_generator"
  }
]
