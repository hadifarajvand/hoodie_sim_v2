# Evaluation Trace Bank Baseline Harness Report Contract

Required JSON artifact:

```text
artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json
```

Required Markdown artifact:

```text
artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.md
```

## Required top-level fields

```text
feature_id
prerequisite_tags_verified
feature_057_pilot_verified
evaluation_trace_bank_summary
train_eval_separation_summary
baseline_policy_registry_summary
baseline_evaluation_harness_summary
metric_schema_summary
determinism_summary
behavior_safety_summary
remaining_blockers
recommended_next_feature
final_verdict
```

## Required passing values

```text
feature_id = 058-evaluation-trace-bank-baseline-harness
feature_057_pilot_verified = true
remaining_blockers = []
recommended_next_feature = Feature 059 — Full Paper-Default Training Campaign Gate
final_verdict = evaluation_trace_bank_baseline_harness_ready
```

## Required safety fields

```text
no_training_execution
no_optimizer_execution
no_replay_mutation
no_checkpoint_binary_written
no_full_campaign
no_paper_reproduction_claim
no_performance_claim
no_policy_drift
no_dependency_drift
no_environment_contract_drift
no_reward_timing_change
no_prior_artifact_rewrite
```
