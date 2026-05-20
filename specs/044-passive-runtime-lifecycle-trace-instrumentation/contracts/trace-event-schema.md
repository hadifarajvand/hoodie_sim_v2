# Trace Event Schema Contract

## Purpose

Define the passive lifecycle trace event shape that the environment exposes through existing runtime info paths.

## Required event types

- `task_generated`
- `task_admitted`
- `transmission_started`
- `transmission_completed`
- `execution_started`
- `execution_progress`
- `execution_completed`
- `deadline_reached`
- `deadline_expired`
- `task_completed`
- `task_dropped`
- `reward_emitted`
- `pending_at_horizon`

## Required event attributes

When applicable, each event MUST carry:

- `event_type`
- `slot`
- `task_id`
- `source_agent_id`
- `selected_action`
- `destination`
- `queue_type`
- `host_node_id`
- `arrival_slot`
- `absolute_deadline_slot`
- `task_age_slots`
- `size_mbits`
- `processing_density_gcycles_per_mbit`
- `cycles_required_gcycles`
- `cycles_before_gcycles`
- `cycles_consumed_gcycles`
- `cycles_after_gcycles`
- `compute_capacity_gcycles_per_slot`
- `transmission_started_at`
- `transmission_completed_at`
- `transmission_delay_slots`
- `terminal_outcome`
- `reward`
- `reward_available`
- `pending_at_horizon`
- `legality_snapshot`
- `trace_source_component`

## Contract notes

- The schema is passive-only.
- The schema MUST support ordering analysis for completion vs drop vs deadline events.
- The schema MUST support execution progress visibility when compute capacity is consumed.
