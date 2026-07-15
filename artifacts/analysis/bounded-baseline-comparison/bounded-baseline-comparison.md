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
- average_reward: `-24.642105`
- loss_count: `87`
- loss_all_finite: `True`
- loss_no_nan: `True`
- loss_no_inf: `True` 
- loss_mean: `751.9430454297998`
- loss_min: `362.9549560546875`
- loss_max: `1136.5068359375`
- completed_task_count: `54`
- dropped_task_count: `92`
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
- average_reward: `-28.281250`
- loss_count: `87`
- loss_all_finite: `True`
- loss_no_nan: `True`
- loss_no_inf: `True` 
- loss_mean: `1171.7736297256645`
- loss_min: `337.815185546875`
- loss_max: `1884.0321044921875`
- completed_task_count: `42`
- dropped_task_count: `91`
- pending_at_horizon_count: `3`
- illegal_action_count: `0`
- legal_action_only: `True`
- optimizer_step_count: `87`
- target_sync_count: `0`
- replay_size: `150`
