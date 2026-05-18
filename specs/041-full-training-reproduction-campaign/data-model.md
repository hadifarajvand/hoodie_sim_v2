# Data Model: Full Training/Reproduction Campaign

## CampaignConfig

Represents the staged campaign configuration.

### Fields

- `feature_id`: `041-full-training-reproduction-campaign`
- `target_update_unit`: approved unit for target sync, `optimizer_step`
- `readiness_mode`: readiness probe policy
- `pilot_budgets`: ordered list of pilot budgets, starting at 10 and optionally extending to 25 episodes
- `full_campaign_budget`: paper default of 5000 episodes, executable only behind explicit command or flag
- `seed_bundle`: reproducibility seeds for train and eval
- `reward_policy`: delayed reward contract inherited from prior features
- `evaluation_trace_bank_id`: disjoint eval trace bank identifier
- `baseline_reference_set`: reference-only Feature 037 artifacts

### Validation Rules

- `target_update_unit` must be explicitly approved
- `pilot_budgets` must include a first bounded budget of 10 episodes
- `full_campaign_budget` must not auto-execute
- `seed_bundle` must separate train and eval seeds

## CampaignStage

Represents a bounded campaign phase.

### Values

- `readiness_probe`
- `pilot_training`
- `full_training_candidate`
- `final_reproduction_campaign`

### Rules

- `readiness_probe` must run before any pilot or full campaign stage
- `pilot_training` must pass before `full_training_candidate`
- `final_reproduction_campaign` requires explicit readiness approval and supporting metrics

## ReadinessProbeResult

Represents the outcome of the preflight gate.

### Fields

- `gate_status`: blocked, pilot-ready, or full-training-eligible
- `manual_approval_required`: boolean
- `probe_episode_count`
- `probe_step_count`
- `generated_task_count`
- `transition_count`
- `completed_task_count`
- `dropped_task_count`
- `pending_at_horizon_count`
- `terminal_transition_count`
- `reward_bearing_transition_count`
- `non_terminal_transition_count`
- `terminal_transition_ratio`
- `reward_bearing_transition_ratio`
- `pending_at_horizon_ratio`
- `illegal_action_count`
- `illegal_action_ratio`
- `action_count_by_type`
- `local_action_count`
- `horizontal_action_count`
- `vertical_action_count`
- `readiness_manual_approval_required`
- `readiness_manual_approval_status`
- `target_update_unit`
- `block_reason`

### Validation Rules

- `probe_episode_count`, `probe_step_count`, `generated_task_count`, and transition counters must be reported exactly
- `gate_status` must be reproducible from the same seed bundle and trace evidence
- `block_reason` must be explicit when blocked
- `readiness_manual_approval_status` must reflect the manual approval decision

## ReplayTransition

Represents one training transition.

### Fields

- `state`
- `action_index`
- `action_mask`
- `reward_available`
- `reward_value`
- `next_state`
- `is_terminal`
- `pending_at_horizon`
- `source_type`

### Validation Rules

- `source_type` must be `environment_rollout`
- `pending_at_horizon` must remain non-terminal
- `reward_available` must be true only for completion or drop
- `action_mask` must not be bypassed

## TraceBank

Represents a disjoint evaluation trace collection.

### Fields

- `trace_bank_id`
- `seed_signature`
- `trace_ids`
- `role`: train or eval

### Rules

- Train and eval trace banks must be disjoint
- Eval trace banks must not overlap training traces

## CheckpointMetadata

Represents reproducible checkpoint metadata.

### Fields

- `stage`
- `seed_bundle`
- `target_update_unit`
- `config_hash`
- `train_trace_bank_id`
- `eval_trace_bank_id`

### Validation Rules

- Metadata must be sufficient to reproduce the same stage decision and trace selection

## CampaignReport

Represents readiness, pilot, and final campaign reporting.

### Fields

- `campaign_stage`
- `readiness_summary`
- `pilot_summary`
- `training_execution_summary`
- `evaluation_summary`
- `baseline_reference_summary`
- `reproduction_claim_status`
- `final_verdict`

### Rules

- Reports must distinguish readiness evidence from pilot evidence
- Reports must never claim reproduction automatically
- Reports must preserve no-curve-fitting and no-simulator-output-tuning flags
