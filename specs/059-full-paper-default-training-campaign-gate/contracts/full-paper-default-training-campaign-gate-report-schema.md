# Full Paper Default Training Campaign Gate Report Contract

Required JSON artifact:

```text
artifacts/analysis/full-paper-default-training-campaign-gate/full-paper-default-training-campaign-gate-report.json
```

Required Markdown artifact:

```text
artifacts/analysis/full-paper-default-training-campaign-gate/full-paper-default-training-campaign-gate-report.md
```

## Required top-level fields

```text
feature_id
prerequisite_tags_verified
feature_058_harness_verified
campaign_scope_summary
training_execution_gate_summary
evaluation_harness_gate_summary
artifact_output_contract_summary
resource_control_summary
checkpoint_contract_summary
metric_collection_contract_summary
safety_summary
remaining_blockers
recommended_next_feature
final_verdict
```

## Required passing values

```text
feature_id = 059-full-paper-default-training-campaign-gate
feature_058_harness_verified = true
remaining_blockers = []
recommended_next_feature = Feature 060 — Full Paper-Default Training Campaign Execution
final_verdict = full_paper_default_training_campaign_gate_ready
```

## Required safety fields

```text
no_training_execution
no_optimizer_execution
no_replay_mutation
no_checkpoint_binary_written
no_full_campaign_execution
no_paper_reproduction_claim
no_performance_claim
no_baseline_superiority_claim
no_policy_drift
no_dependency_drift
no_environment_contract_drift
no_reward_timing_change
no_prior_artifact_rewrite
```
