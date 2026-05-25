# Full Paper-Default Training Campaign Execution Report Contract

Required JSON artifact:

```text
artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json
```

Required Markdown artifact:

```text
artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.md
```

Required companion artifacts:

```text
artifacts/analysis/full-paper-default-training-campaign-execution/training-metrics.json
artifacts/analysis/full-paper-default-training-campaign-execution/evaluation-metrics.json
artifacts/analysis/full-paper-default-training-campaign-execution/checkpoint-metadata.json
artifacts/analysis/full-paper-default-training-campaign-execution/run-manifest.json
```

## Required top-level fields

```text
feature_id
prerequisite_tags_verified
feature_059_gate_verified
campaign_execution_summary
training_metrics_summary
evaluation_metrics_summary
baseline_evaluation_summary
checkpoint_metadata_summary
artifact_manifest_summary
resource_control_summary
safety_summary
remaining_blockers
recommended_next_feature
final_verdict
```

## Required passing values

```text
feature_id = 060-full-paper-default-training-campaign-execution
feature_059_gate_verified = true
remaining_blockers = []
recommended_next_feature = Feature 061 — Campaign Result Integrity and Comparison Readiness Audit
final_verdict = full_paper_default_training_campaign_execution_passed
```

## Required safety fields

```text
no_paper_reproduction_claim
no_performance_superiority_claim
no_baseline_superiority_claim
no_uncontrolled_campaign_loop
no_policy_drift
no_dependency_drift
no_environment_contract_drift
no_reward_timing_change
no_prior_artifact_rewrite
```
