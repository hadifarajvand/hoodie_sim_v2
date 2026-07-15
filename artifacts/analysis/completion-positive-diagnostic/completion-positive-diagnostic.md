# Completion-Positive Diagnostic Evidence

- **Verdict**: `pass_completion_positive`
- **Constraint**: 3 episodes x 200 slots

## Config Confirmation

- state_dim: `74`
- action_count: `22`
- lookback_w: `10`
- learning_rate: `7e-07`
- gamma: `0.99`
- batch_size: `64`
- horizontal_data_rate_mbps: `30.0`
- vertical_data_rate_mbps: `10.0`
- full_campaign_enabled: `False`
- config_hash: `03e2f5694ae361f6`... (sha256 prefix)

## Metrics Summary

- episodes_completed: `3`
- episode_length: `200`
- total_transition_count: `600`
- average_reward: `-34.546318`
- total_reward: `-14544.000000`
- reward_count: `421`
- loss_count: `537`
- loss_all_finite: `True`
- loss_no_nan: `True`
- loss_no_inf: `True`
- loss_min: `778.672363`
- loss_max: `2723.016113`
- loss_mean: `1476.584312`
- completed_task_count: `43`
- dropped_task_count: `552`
- pending_at_horizon_count: `3`
- illegal_action_count: `0`
- legal_action_only: `True`
- optimizer_step_count: `537`
- target_sync_count: `0`
- replay_size: `600`

## Interpretation

Full-campaign readiness can proceed to final approval gate. Non-zero task completions observed in bounded diagnostic.
