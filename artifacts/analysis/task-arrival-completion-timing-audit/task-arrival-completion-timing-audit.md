# Task-Arrival Completion Timing Audit Evidence

- **Verdict**: `bridge_needs_service_progress_audit`
- **Constraint**: 3 episodes x 200 slots

## Config Confirmation

- state_dim: `74`
- action_count: `22`
- lookback_w: `10`
- full_campaign_enabled: `False`
- config_hash: `03e2f5694ae361f6`... (sha256 prefix)

## Trace Info

- trace_collector_enabled: `True`
- trace_event_counts: `{'action_selected': 600, 'task_arrived': 30, 'task_generated': 1206, 'task_admitted': 1200, 'transmission_started': 554, 'queue_length_sampled': 12000, 'transmission_completed': 554, 'service_started': 3196, 'execution_progress': 3196, 'execution_completed': 1190, 'task_completed': 129, 'reward_released': 421, 'reward_emitted': 1190, 'task_dropped': 1656, 'deadline_reached': 1104, 'deadline_expired': 1104, 'pending_at_horizon': 16, 'task_pending_at_horizon': 3}`
- lifecycle_event_counts: `{'task_generated': 1206, 'task_admitted': 1200, 'transmission_started': 554, 'transmission_completed': 554, 'execution_started': 1598, 'execution_progress': 3196, 'execution_completed': 1190, 'task_completed': 129, 'reward_emitted': 1190, 'deadline_reached': 1104, 'deadline_expired': 1104, 'task_dropped': 1656, 'pending_at_horizon': 16, 'action_selected': 600, 'task_arrived': 30, 'queue_length_sampled': 12000, 'reward_released': 421, 'task_pending_at_horizon': 3, 'service_started': 1598}`
- first_service_start_slot: `2`
- queue_length_samples: `12000`
- service_started_observable: `True`
- lifecycle_events_absent_even_when_trace_enabled: `False`

## Observability Matrix

- first_arrival_slot: `observable`
- first_service_start_slot: `observable`
- first_completion_slot: `observable`
- action_distribution: `observable`
- queue_lengths: `observable`
- reward_events: `observable`
- service_started_observable: `observable`

## Metrics Summary

- episodes_completed: `3`
- episode_length: `200`
- total_transition_count: `600`
- completed_task_count: `43`
- dropped_task_count: `552`
- pending_at_horizon_count: `3`
- illegal_action_count: `0`
- legal_action_only: `True`
- reward_count: `421`
- average_reward: `-34.546318`
- loss_count: `537`
- replay_size: `600`

## Inferred Findings

### What is proven

- Task arrivals occur as early as slot 0 (mean 4.5)
- All rewards are negative (total=-14544.0, avg=-34.55) — drop penalties dominate, no completion rewards

### What is not observable


### Most likely next hypothesis



## Recommended Next Step

service progress audit
