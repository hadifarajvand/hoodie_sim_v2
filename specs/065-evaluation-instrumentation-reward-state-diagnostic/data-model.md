# Data Model: Feature 065 - Evaluation Instrumentation and Reward/State Diagnostic Repair

## Entity: CheckpointInstrumentedMetrics

- `training_budget`
- `cumulative_training_episode_count`
- `evaluation_episode_count`
- `episode_length`
- `max_training_budget`
- `training_mode`
- `optimizer_step_count`
- `replay_size`
- `loss_count`
- `last_loss`
- `loss_finite`
- `evaluation_action_distribution`
- `evaluation_decision_count`
- `evaluation_action_sequence_sample`
- `evaluation_legal_action_mask_distribution`
- `evaluation_action_by_trace_id`
- `evaluation_action_by_episode_id`
- `replay_window_action_distribution`
- `cumulative_training_action_distribution`
- `replay_window_is_full_training_history`
- `replay_window_capacity`
- `replay_window_interpretation_warning`
- `per_action_outcome_summary`
- `reward_decomposition`

## Entity: StateFeatureCoverageAuditEntry

- `field_name`
- `available_in_environment_observation`
- `included_in_policy_state_vector`
- `included_in_replay_transition`
- `included_in_evaluation_diagnostics`
- `thesis_relevance`
- `risk_if_missing`

## Entity: PolicyEffectDiagnostic

- `policy_name`
- `mean_reward`
- `completed_count`
- `dropped_count`
- `pending_at_horizon_count`
- `action_distribution`
- `per_action_outcome_summary`
- `reward_decomposition`

## Validation Rules

- Evaluation action logging must come from evaluation episodes, not replay.
- Replay-window action counts must be labeled as rolling-window only.
- All unsupported claims remain disallowed.
