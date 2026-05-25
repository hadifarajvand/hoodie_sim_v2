# Target Update Replay Validation Report Contract

Required JSON artifact:

```text
artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.json
```

Required Markdown artifact:

```text
artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.md
```

## Required top-level fields

```text
feature_id
prerequisite_tags_verified
feature_055_smoke_verified
replay_insertion_validated
replay_sampling_validated
optimizer_step_counter_validated
target_update_contract_validated
target_sync_schedule_validated
target_sync_before_threshold_blocked
target_sync_at_threshold_validated
checkpoint_metadata_validated
replay_summary
optimizer_step_summary
target_update_summary
checkpoint_metadata_summary
behavior_safety_summary
remaining_blockers
recommended_next_feature
final_verdict
```

## Required passing values

```text
feature_id = 056-target-update-and-replay-training-validation
feature_055_smoke_verified = true
replay_insertion_validated = true
replay_sampling_validated = true
optimizer_step_counter_validated = true
target_update_contract_validated = true
target_sync_schedule_validated = true
target_sync_before_threshold_blocked = true
target_sync_at_threshold_validated = true
checkpoint_metadata_validated = true
remaining_blockers = []
recommended_next_feature = Feature 057 — Paper-Default Pilot Training Run
final_verdict = target_update_replay_validation_passed
```

## Allowed final verdicts

```text
target_update_replay_validation_passed
feature_055_prerequisite_blocked
replay_insertion_blocked
replay_sampling_blocked
optimizer_step_counter_blocked
target_update_contract_blocked
checkpoint_metadata_blocked
behavior_drift_detected
```

## Safety fields

`behavior_safety_summary` must explicitly include:

```text
no_full_campaign
no_baseline_comparison
no_paper_reproduction_claim
no_policy_drift
no_dependency_drift
no_environment_contract_drift
no_reward_timing_change
no_prior_artifact_rewrite
```
