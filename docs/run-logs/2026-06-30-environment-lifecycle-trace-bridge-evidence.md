# Task-Arrival Completion Timing Audit Evidence

- **Verdict**: `audit_needs_deeper_instrumentation`
- **Constraint**: 3 episodes x 200 slots

## Config Confirmation

- state_dim: `74`
- action_count: `22`
- lookback_w: `10`
- full_campaign_enabled: `False`
- config_hash: `d96700af532d8849`... (sha256 prefix)

## Trace Info

- trace_collector_enabled: `True`
- trace_event_counts: `{'action_selected': 600, 'task_arrived': 600, 'queue_length_sampled': 12000, 'task_pending_at_horizon': 3, 'task_dropped': 4, 'reward_released': 4}`
- first_service_start_slot: `None`
- queue_length_samples: `12000`

## Observability Matrix

- first_arrival_slot: `observable`
- first_service_start_slot: `NOT observable`
- first_completion_slot: `observable`
- action_distribution: `observable`
- queue_lengths: `observable`
- reward_events: `observable`

## Metrics Summary

- episodes_completed: `3`
- episode_length: `200`
- total_transition_count: `600`
- completed_task_count: `0`
- dropped_task_count: `4`
- pending_at_horizon_count: `3`
- illegal_action_count: `0`
- legal_action_only: `True`
- reward_count: `4`
- average_reward: `-40.000000`
- loss_count: `537`
- replay_size: `600`

## Inferred Findings

### What is proven

- Task arrivals occur as early as slot 0 (mean 99.5)
- 4 tasks were dropped but 0 completed — tasks arrive but cannot finish within 200 slots
- 3 tasks were pending at horizon — episode truncation prevents completion accounting
- All rewards are negative (total=-160.0, avg=-40.00) — drop penalties dominate, no completion rewards

### What is not observable

- first_service_start_slot
- queue_lengths_over_time

### Most likely next hypothesis

Tasks arrive (first at slot 0) but are dropped (n=4) or pending (n=3) before completing. Most likely: the bounded horizon of 200 slots is too short for the service time of tasks given the current action selection policy, OR the action selection is not advancing task processing effectively.

## Recommended Next Step

minimal trainer instrumentation plan
