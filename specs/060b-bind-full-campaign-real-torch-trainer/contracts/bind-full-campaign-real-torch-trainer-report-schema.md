# Feature 060B Report Contract

## Required artifacts

- `artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.json`
- `artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.md`

## Required top-level fields

- `feature_id`
- `prerequisite_tags_verified`
- `feature_060a_audit_verified`
- `torch_environment_summary`
- `real_trainer_binding_summary`
- `feature_060_repair_summary`
- `campaign_execution_summary`
- `training_metrics_summary`
- `evaluation_metrics_summary`
- `artifact_regeneration_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Passing verdict

- `feature_id = 060b-bind-full-campaign-real-torch-trainer`
- `feature_060a_audit_verified = true`
- `real_trainer_binding_summary.real_binding_verified = true`
- `feature_060_repair_summary.feature_060_claim_supported = true`
- `remaining_blockers = []`
- `recommended_next_feature = Feature 061 — Campaign Result Integrity and Comparison Readiness Audit`
- `final_verdict = real_torch_trainer_binding_repair_passed`

## Blocked verdicts

- `feature_060a_prerequisite_blocked`
- `torch_environment_blocked`
- `real_trainer_binding_blocked`
- `feature_060_repair_blocked`
- `artifact_regeneration_blocked`
- `behavior_drift_detected`
