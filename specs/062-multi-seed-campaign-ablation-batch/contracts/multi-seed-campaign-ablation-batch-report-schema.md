# Feature 062 Report Contract

## Required artifacts

- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.md`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-gate.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-aggregation.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/ablation-gate.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/ablation-results.json`

## Required top-level fields

- `feature_id`
- `batch_items_covered`
- `prerequisite_tags_verified`
- `feature_061_verified`
- `multi_seed_gate_summary`
- `multi_seed_campaign_summary`
- `multi_seed_aggregation_summary`
- `ablation_gate_summary`
- `ablation_execution_summary`
- `artifact_manifest_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Passing verdict

- `feature_id = 062-multi-seed-campaign-ablation-batch`
- `feature_061_verified = true`
- `remaining_blockers = []`
- `recommended_next_feature = Feature 063 — Results Export, Reproducibility, and Final Documentation Batch`
- `final_verdict = multi_seed_campaign_ablation_batch_passed`

## Required safety fields

- `no_dependency_drift`
- `no_policy_drift`
- `no_environment_contract_drift`
- `no_reward_timing_change`
- `no_prior_feature_artifact_rewrite`
- `no_paper_reproduction_claim`
- `no_unsupported_superiority_claim`
- `no_uncontrolled_campaign_loop`
- `no_checkpoint_binary_created`
