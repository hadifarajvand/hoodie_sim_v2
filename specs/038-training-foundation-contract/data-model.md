# Data Model: Training Foundation Contract

## Entities

### StateContract

- **Purpose**: Defines the observation fields used as future training input.
- **Fields**:
  - `version`
  - `agent_key`
  - `field_order`
  - `field_types`
  - `normalization_rules`
  - `missing_value_encoding`
  - `history_buffer_policy`
  - `lookback_w`
  - `observable_only`
- **Relationships**:
  - Consumed by `ReplayTransition` and `TrainingFoundationReport`.

### ActionIndexContract

- **Purpose**: Maps integer actions to semantic actions for local/private, generic horizontal, and vertical/cloud offload.
- **Fields**:
  - `version`
  - `action_index`
  - `semantic_action`
  - `illegal_action_behavior`
  - `mask_surface`
  - `horizontal_resolution_rule`
  - `vertical_independence_rule`
- **Relationships**:
  - Used by `ReplayTransition` and the readiness gate audit.

### ReplayTransition

- **Purpose**: Captures a decision and its eventual delayed reward or pending state.
- **Fields**:
  - `state_t`
  - `action_index`
  - `action_semantics`
  - `legal_action_mask_t`
  - `reward_t_plus_k`
  - `reward_available`
  - `next_state`
  - `done`
  - `truncated`
  - `task_id`
  - `source_agent_id`
  - `selected_destination`
  - `arrival_slot`
  - `decision_slot`
  - `terminal_slot`
  - `terminal_outcome`
  - `delay_slots`
  - `seed`
  - `trace_id`
  - `episode_id`
  - `runtime_contract_version`
  - `pending_at_horizon`
- **State transitions**:
  - `reward_available=false` while non-terminal.
  - `reward_available=true` only after completion or drop.
  - `pending_at_horizon=true` when the task survives to episode end without terminal outcome.

### SeedBundle

- **Purpose**: Collects purpose-specific seeds.
- **Fields**:
  - `training_trace_generation_seed`
  - `evaluation_trace_generation_seed`
  - `replay_sampling_seed`
  - `model_initialization_seed`
  - `action_exploration_seed`
- **Relationships**:
  - Referenced by `TrainingFoundationReport` and `CheckpointMetadata`.

### TrainEvalSplit

- **Purpose**: Declares disjoint training and evaluation trace banks.
- **Fields**:
  - `training_trace_ids`
  - `evaluation_trace_ids`
  - `split_seed_bundle`
  - `leakage_guard`

### CheckpointMetadata

- **Purpose**: Records metadata for a future checkpoint, not model weights.
- **Fields**:
  - `feature_id`
  - `commit_sha`
  - `config_path`
  - `config_hash`
  - `state_contract_version`
  - `action_contract_version`
  - `replay_schema_version`
  - `seed_bundle`
  - `training_step_counter`
  - `target_update_counter`
  - `runtime_contract_refs`
  - `paper_default_parameter_refs`

### TerminalOutcomeExposureGate

- **Purpose**: Determines whether training is blocked.
- **Fields**:
  - `generated_arrivals`
  - `decisions_exposed`
  - `finalized_terminal_tasks`
  - `completed_tasks`
  - `dropped_tasks`
  - `pending_at_horizon`
  - `terminal_transition_ratio`
  - `reward_bearing_transition_ratio`
  - `pending_transition_ratio`
  - `per_policy_smoke_statistics`
  - `training_blocked`
  - `threshold_status`

### TrainingFoundationReport

- **Purpose**: Contract-level report describing readiness for future training.
- **Fields**:
  - `feature_id`
  - `prerequisite_tags_verified`
  - `state_contract`
  - `action_index_contract`
  - `replay_schema`
  - `target_update_frequency_contract`
  - `seed_protocol`
  - `train_eval_split_protocol`
  - `checkpoint_schema`
  - `terminal_outcome_exposure_gate`
  - `runtime_contracts_verified`
  - `no_training_started`
  - `no_neural_network_change`
  - `no_dependency_drift`
  - `no_environment_contract_drift`
  - `no_reward_timing_change`
  - `no_policy_drift`
  - `no_curve_fitting`
  - `no_paper_reproduction_claim`
  - `final_verdict`

## Validation Rules

- State contracts must not contain diagnostic-only fields.
- Action contracts must keep one generic horizontal action and one vertical/cloud action independent of Figure 7 adjacency.
- Replay transitions must distinguish terminal and pending-at-horizon cases.
- Thresholds for terminal exposure remain blocked until explicitly approved.
- Checkpoint metadata must remain metadata-only.

