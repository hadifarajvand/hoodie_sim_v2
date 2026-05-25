# Paper Default Pilot Training Run Report Contract

Required JSON artifact:

```text
artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.json
```

Required Markdown artifact:

```text
artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.md
```

## Required top-level fields

```text
feature_id
prerequisite_tags_verified
feature_056_validation_verified
pilot_scope
live_environment_training_used
fixture_training_used
episode_summary
replay_summary
optimizer_summary
target_update_summary
loss_summary
reward_summary
legal_action_summary
checkpoint_summary
train_eval_contract_verified
behavior_safety_summary
remaining_blockers
recommended_next_feature
final_verdict
```

## Required passing values

```text
feature_id = 057-paper-default-pilot-training-run
feature_056_validation_verified = true
live_environment_training_used = true
fixture_training_used = false
remaining_blockers = []
recommended_next_feature = Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness
final_verdict = paper_default_pilot_training_passed
```

## Required passing relationships

```text
pilot_scope.pilot_episodes > 1
pilot_scope.full_campaign = false
pilot_scope.baseline_comparison = false
pilot_scope.paper_reproduction_claim = false
replay_summary.replay_size > replay_summary.feature_055_smoke_replay_size
optimizer_summary.optimizer_step_count > optimizer_summary.feature_055_smoke_optimizer_step_count
loss_summary.all_losses_finite = true
legal_action_summary.legal_action_only = true
checkpoint_summary.checkpoint_schema_valid = true
train_eval_contract_verified.train_eval_trace_banks_disjoint = true
```

## Allowed final verdicts

```text
paper_default_pilot_training_passed
feature_056_prerequisite_blocked
pilot_scope_blocked
replay_growth_blocked
optimizer_progress_blocked
loss_or_reward_blocked
legal_action_blocked
checkpoint_metadata_blocked
behavior_drift_detected
```

## Behavior safety fields

`behavior_safety_summary` must include:

```text
no_full_campaign
no_baseline_comparison
no_paper_reproduction_claim
no_performance_claim
no_policy_drift
no_dependency_drift
no_environment_contract_drift
no_reward_timing_change
no_prior_artifact_rewrite
```
