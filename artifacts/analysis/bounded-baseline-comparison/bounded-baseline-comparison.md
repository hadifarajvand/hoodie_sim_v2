# Bounded Baseline Comparison Evidence

- **Verdict**: `pass`
- **Constraint**: 3 episodes x 50 slots

## Legacy Path

### Config
- state_dim: `3`
- action_count: `3`
- lookback_w: `10`
- config_hash: `416829cf02594ff4`... (sha256 prefix)
- full_campaign_enabled: `False`

### Metrics
- episodes_completed: `3`
- total_transition_count: `150`
- average_reward: `-6.171429`
- loss_count: `87`
- loss_all_finite: `True`
- loss_no_nan: `True`
- loss_no_inf: `True` 
- loss_mean: `32.63337955255618`
- loss_min: `24.199623107910156`
- loss_max: `38.746185302734375`
- completed_task_count: `139`
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
- config_hash: `9d537ad29abb096c`... (sha256 prefix)
- full_campaign_enabled: `False`

### Metrics
- episodes_completed: `3`
- total_transition_count: `70`
- average_reward: `-7.437500`
- loss_count: `7`
- loss_all_finite: `True`
- loss_no_nan: `True`
- loss_no_inf: `True` 
- loss_mean: `16.051862035478866`
- loss_min: `15.407934188842773`
- loss_max: `16.416311264038086`
- completed_task_count: `60`
- dropped_task_count: `0`
- pending_at_horizon_count: `3`
- illegal_action_count: `0`
- legal_action_only: `True`
- optimizer_step_count: `7`
- target_sync_count: `0`
- replay_size: `70`
