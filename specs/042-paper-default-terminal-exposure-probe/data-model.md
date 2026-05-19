# Data Model: Paper-default Terminal Exposure Probe

## ProbeConfiguration

Represents the diagnostic runtime and deterministic strategy settings.

### Fields

- `feature_id`: `042-paper-default-terminal-exposure-probe`
- `probe_horizon`: `110`
- `timeout_slots`: `20`
- `slot_duration_seconds`: `0.1`
- `paper_defaults`: `N`, `T`, `P`, `private_cpu`, `public_cpu`, `cloud_cpu`, `R_H`, `R_V`
- `seed_bundle`: deterministic seed set for repeated probe runs
- `probe_episodes_per_strategy`: `3`
- `probe_strategies`: ordered list of deterministic strategies

### Validation Rules

- `probe_horizon` must equal `110`
- `timeout_slots` must remain `20`
- `probe_episodes_per_strategy` must be deterministic and bounded
- paper-default runtime values must match the repaired contracts

## ProbeStrategy

Represents a deterministic action-selection mode for the exposure probe.

### Values

- `environment_default_policy_probe`
- `force_local_legal_probe`
- `force_horizontal_legal_probe`
- `force_vertical_legal_probe`
- `optional_mixed_legal_probe`

### Rules

- Strategies are diagnostic only
- Strategies must not alter policy behavior or environment semantics

## TerminalExposureCounters

Represents the counters collected per strategy and seed.

### Fields

- `episode_count`
- `episode_length`
- `seed`
- `generated_task_count`
- `exposed_decision_count`
- `selected_action_count`
- `legal_action_count`
- `illegal_action_count`
- `local_action_count`
- `horizontal_action_count`
- `vertical_action_count`
- `admitted_task_count`
- `transmission_started_count`
- `transmission_completed_count`
- `execution_started_count`
- `execution_completed_count`
- `completed_task_count`
- `dropped_task_count`
- `terminal_transition_count`
- `reward_bearing_transition_count`
- `pending_at_horizon_count`
- `terminal_transition_ratio`
- `reward_bearing_transition_ratio`
- `pending_at_horizon_ratio`
- `max_observed_task_age_slots`
- `max_queue_wait_slots`
- `deadline_reached_count`
- `deadline_expired_count`
- `reward_emitted_count`
- `nan_or_omitted_reward_count`
- `terminal_outcome_by_action_type`
- `pending_by_action_type`
- `lifecycle_trace_integrity_verified`

### Validation Rules

- terminal outcomes must be attributable to observed lifecycle events only
- reward-bearing outcomes must correspond to completion or drop
- pending-at-horizon must remain non-terminal
- lifecycle integrity must not be fabricated

## ProbeReport

Represents the diagnostic output for the feature.

### Fields

- `feature_id`
- `prerequisite_tags_verified`
- `prior_feature_gates_verified`
- `paper_default_runtime_verified`
- `probe_config`
- `probe_strategies`
- `per_strategy_results`
- `aggregate_terminal_exposure_summary`
- `no_training_started`
- `no_optimizer_step`
- `no_replay_training`
- `no_target_update_execution`
- `no_dependency_drift`
- `no_environment_contract_drift`
- `no_policy_drift`
- `no_reward_timing_change`
- `no_curve_fitting`
- `no_simulator_output_tuning`
- `no_paper_reproduction_claim`
- `reward_timing_contract_verified`
- `pending_at_horizon_contract_verified`
- `legal_action_mask_verified`
- `runtime_contracts_verified`
- `diagnosis`
- `recommended_next_feature`
- `final_verdict`

### Validation Rules

- JSON and Markdown reports must reflect the same data
- every audit flag must be present and true
- final verdict must not claim paper reproduction
