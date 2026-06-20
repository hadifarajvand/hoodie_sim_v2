# Data Model: Feature 064 - Final Review and Release Gate Batch

## Entity: ArtifactPrerequisiteStatus

- `path`: source artifact path
- `exists`: whether the artifact exists
- `verified`: whether the artifact passed feature-specific validation
- `details`: short evidence note

## Entity: RewardStabilityReview

- `evaluation_reward_static_across_budget`: whether the checkpoint mean reward is constant across 100/150/200/500
- `checkpoint_budgets`: staged checkpoint budgets
- `evaluation_mean_rewards`: mean reward by checkpoint
- `same_evaluation_trace_bank`: whether the same evaluation trace bank is reused
- `deterministic_evaluation_path`: whether the code path is deterministic enough to explain the invariant reward
- `likely_causes`: evidence-backed candidate causes

## Entity: ActionCollapseReview

- `vertical_action_collapse_detected`: whether the 500 checkpoint is dominated by vertical actions
- `action_distributions`: action counts by checkpoint
- `vertical_share_by_budget`: vertical share by checkpoint
- `possible_causes`: evidence-backed candidate causes

## Entity: ReplayBufferReview

- `replay_buffer_capacity`: configured replay capacity from the trainer config
- `observed_replay_size_by_checkpoint`: replay size by checkpoint
- `replay_size_cap_detected`: whether the replay size plateaus at the capacity
- `is_cap_expected`: whether the cap is configured and intentional
- `is_cap_blocking_larger_training`: whether the cap is a likely bottleneck for longer runs

## Entity: EvaluationSignalReview

- `reward_available`
- `drop_count_available`
- `completed_task_count_available`
- `delay_metric_available`
- `timeout_metric_available`
- `train_eval_separation_available`
- `baseline_metrics_available`
- `thesis_level_sufficient`

## Entity: NextActionDecision

- `recommended_next_action`: exactly one allowed next action
- `decision_reason`: concise rationale

## Validation Rules

- The gate must never claim superiority.
- A blocked verdict is required when the evidence shows static reward plus policy collapse or when the required artifacts are missing.
- A ready verdict is only acceptable when the evidence supports a thesis drafting next step without unsupported claims.
