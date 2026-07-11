# Task-Arrival Completion Timing Audit Evidence

- **Verdict**: `bridge_needs_service_progress_audit`
- **Constraint**: 3 episodes x 200 slots

## Config Confirmation

- state_dim: `74`
- action_count: `22`
- lookback_w: `10`
- full_campaign_enabled: `False`
- config_hash: `9d537ad29abb096c`... (sha256 prefix)

## Trace Info

- trace_collector_enabled: `True`
- trace_event_counts: `{'action_selected': 289, 'task_arrived': 289, 'task_generated': 584, 'task_admitted': 578, 'transmission_started': 578, 'queue_length_sampled': 12000, 'transmission_completed': 568, 'service_started': 1428, 'execution_progress': 1428, 'execution_completed': 560, 'task_completed': 840, 'reward_emitted': 560, 'reward_released': 235, 'pending_at_horizon': 18, 'task_pending_at_horizon': 3}`
- lifecycle_event_counts: `{'task_generated': 584, 'task_admitted': 578, 'transmission_started': 578, 'transmission_completed': 568, 'execution_started': 714, 'execution_progress': 1428, 'execution_completed': 560, 'task_completed': 840, 'reward_emitted': 560, 'pending_at_horizon': 18, 'action_selected': 289, 'task_arrived': 289, 'queue_length_sampled': 12000, 'reward_released': 235, 'task_pending_at_horizon': 3, 'service_started': 714}`
- first_service_start_slot: `3`
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
- total_transition_count: `289`
- completed_task_count: `280`
- dropped_task_count: `0`
- pending_at_horizon_count: `3`
- illegal_action_count: `0`
- legal_action_only: `True`
- reward_count: `109`
- average_reward: `-7.688073`
- loss_count: `226`
- replay_size: `289`

## Inferred Findings

### What is proven

- Task arrivals occur as early as slot 0 (mean 99.3)
- All rewards are negative (total=-838.0, avg=-7.69) — drop penalties dominate, no completion rewards

### What is not observable


### Most likely next hypothesis



## Recommended Next Step

service progress audit
