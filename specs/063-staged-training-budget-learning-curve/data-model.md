# Data Model: Feature 063 - Staged Training Budget Learning Curve and Comparison Analysis

## Entity: CheckpointMetric

- `training_budget`: one of `100`, `150`, `200`, `500`
- `cumulative_training_episode_count`: cumulative count at the checkpoint
- `evaluation_episode_count`: fixed at `100`
- `episode_length`: fixed at `110`
- `optimizer_step_count`: cumulative optimizer updates
- `replay_size`: cumulative replay size at the checkpoint
- `action_distribution`: action counts from real execution
- `action_count_total`: total action count used for reconciliation
- `action_accounting_reconciled`: boolean reconciliation flag
- `loss_count`: cumulative count of observed losses
- `last_loss`: most recent loss value or `null`
- `loss_finite`: whether all observed losses were finite
- `reward_summary`: reward summary from real execution
- `evaluation_reward_summary`: evaluation summary for the checkpoint
- `completed_task_count`: optional evaluation count
- `dropped_task_count`: optional evaluation count
- `pending_at_horizon_count`: optional training or evaluation count
- `comparison_ready`: readiness flag for the checkpoint
- `claim_safety_status`: claim-boundary status for the checkpoint

### Validation Rules

- Checkpoint budgets MUST be exactly `[100, 150, 200, 500]`.
- `action_count_total` MUST equal the replay size for the checkpoint snapshot.
- `loss_finite` MUST be true for a pass verdict.
- `comparison_ready` MAY be true only when the checkpoint has valid metrics and claim safety is clean.

## Entity: BaselineReferenceSummary

- `artifact_path`: source artifact used for reuse
- `baseline_policy_names`: list of policies in the baseline reference
- `evaluated_policy_count`: number of baseline policies
- `actual_baseline_evaluation_episode_count`: baseline evaluation episode count
- `baseline_metrics_real_execution`: whether the baseline evidence comes from real execution
- `no_baseline_superiority_claim`: claim boundary flag

### Validation Rules

- The baseline reference summary MUST be reused across all checkpoints.
- It MUST remain descriptive evidence, not a superiority claim.

## Entity: ComparisonReadinessSummary

- `comparison_ready`: overall readiness flag
- `checkpoint_budgets`: list of budgets used in the staged sweep
- `ready_checkpoint_budgets`: subset that passed readiness checks
- `unready_checkpoint_budgets`: subset that failed readiness checks
- `training_mode`: should be `cumulative_staged`
- `evaluation_episode_count_per_checkpoint`: should be `100`
- `episode_length`: should be `110`
- `baseline_reference_reused`: whether the same baseline reference was reused

## Entity: FigureManifest

- `figure_directory`: output figure directory
- `figure_files`: required figure filenames
- `figure_count`: number of generated figures
- `figures_generated`: boolean completeness flag

## Entity: ClaimSafetyStatus

- `paper_reproduction_claim_made`: boolean
- `performance_superiority_claim_made`: boolean
- `baseline_superiority_claim_made`: boolean
- `claim_safety_passed`: boolean

### Validation Rules

- All three claim flags MUST be false for a pass verdict.
- `claim_safety_passed` MUST be true only when the report stays inside descriptive analysis.
