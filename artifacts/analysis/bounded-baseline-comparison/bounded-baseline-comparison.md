# Bounded Baseline Comparison Evidence

- **Verdict**: `pass`
- **Constraint**: 3 episodes x 50 slots

## Legacy Path

### Config
- state_dim: `3`
- action_count: `3`
- lookback_w: `10`
- config_hash: `65b1c807a78a3833`... (sha256 prefix)
- full_campaign_enabled: `False`

### Metrics
- episodes_completed: `3`
- total_transition_count: `150`
- average_reward: `-4.514286`
- loss_count: `87`
- loss_all_finite: `True`
- loss_no_nan: `True`
- loss_no_inf: `True` 
- loss_mean: `18.253358884789478`
- loss_min: `12.803314208984375`
- loss_max: `23.08195686340332`
- completed_task_count: `143`
- dropped_task_count: `0`
- pending_at_horizon_count: `3`
- illegal_action_count: `0`
- legal_action_only: `True`
- optimizer_step_count: `87`
- target_sync_count: `0`
- replay_size: `150`

## Paper_default Path

### Config
- state_dim: `74`
- action_count: `22`
- lookback_w: `10`
- config_hash: `03e2f5694ae361f6`... (sha256 prefix)
- full_campaign_enabled: `False`

### Metrics
- episodes_completed: `3`
- total_transition_count: `150`
- average_reward: `-8.724490`
- loss_count: `87`
- loss_all_finite: `True`
- loss_no_nan: `True`
- loss_no_inf: `True` 
- loss_mean: `55.0221658465506`
- loss_min: `41.22209548950195`
- loss_max: `69.2023696899414`
- completed_task_count: `132`
- dropped_task_count: `0`
- pending_at_horizon_count: `3`
- illegal_action_count: `0`
- legal_action_only: `True`
- optimizer_step_count: `87`
- target_sync_count: `0`
- replay_size: `150`
