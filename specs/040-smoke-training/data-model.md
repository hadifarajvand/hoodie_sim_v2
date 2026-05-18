# Data Model: Smoke Training

## SmokeTrainingConfig

Represents the bounded smoke execution configuration.

### Fields

- `seed_bundle`: deterministic seed values for the smoke run
- `optimizer_steps`: fixed integer step budget, exactly `1`
- `use_fixture_transitions`: boolean flag indicating fixture-first smoke mode
- `enable_environment_rollout`: optional boolean for interface validation only
- `loss_mode`: smoke loss selector, expected to be minimal MSE
- `target_update_enabled`: must remain `false`
- `report_metrics_enabled`: must remain `false` for performance metrics

### Validation Rules

- `optimizer_steps` must equal `1`
- `target_update_enabled` must be `false`
- `use_fixture_transitions` must be `true` for the primary smoke path
- `loss_mode` must correspond to the bounded smoke loss contract
- `report_metrics_enabled` must not introduce performance metrics

## SmokeReplayTransition

Represents one smoke validation transition.

### Fields

- `state`: Feature 038 state vector for the smoke batch
- `action_index`: stable action index from Feature 038
- `reward_available`: whether the transition terminal reward is available
- `reward_value`: the reward value when available
- `next_state`: next state when applicable
- `is_terminal`: whether the transition is terminal
- `pending_at_horizon`: whether the transition is incomplete at the smoke horizon
- `source_type`: `fixture` or `environment_rollout`

### Validation Rules

- `reward_available` must be `false` for non-terminal transitions
- `reward_available` may be `true` only for terminal transitions
- `pending_at_horizon` must not be converted into a terminal reward
- `source_type=fixture` entries must be clearly labeled as smoke fixtures

## SmokeBatchSummary

Summarizes the bounded batch or rollout used by the smoke run.

### Fields

- `batch_size`
- `terminal_count`
- `non_terminal_count`
- `pending_count`
- `reward_bearing_count`
- `seed_signature`
- `source_type`

### Relationships

- Derived from one or more `SmokeReplayTransition` entries

## SmokeTrainingReport

Records smoke execution outcomes.

### Fields

- `feature_id`
- `dependency_status`
- `smoke_scope`
- `smoke_batch_summary`
- `optimizer_step_summary`
- `loss_summary`
- `parameter_update_summary`
- `deterministic_repeatability_verified`
- `target_update_blocked_reason`
- `feature_038_training_readiness_block_respected`
- `no_paper_reproduction_claim`
- `no_curve_fitting`
- `no_full_training`
- `no_campaign_execution`
- `no_baseline_comparison`
- `no_target_update_execution`
- `no_dependency_drift`
- `no_environment_contract_drift`
- `no_policy_drift`
- `no_reward_timing_change`
- `final_verdict`

### Relationships

- Aggregates the smoke config, smoke batch summary, and result summaries

## ParameterUpdateSummary

Records whether the smoke optimizer step changed the online network.

### Fields

- `changed_parameter_count`
- `changed_parameter_names`
- `all_checked_finite`
- `step_count`

### Validation Rules

- `step_count` must equal the configured smoke step budget
- `changed_parameter_count` must be at least `1`
- `all_checked_finite` must be `true`

## LossSummary

Records the smoke loss value and finiteness.

### Fields

- `loss_value`
- `is_finite`
- `loss_mode`

### Validation Rules

- `is_finite` must be `true`
- `loss_mode` must match the smoke MSE-style contract
