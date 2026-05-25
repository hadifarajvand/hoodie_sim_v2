# Feature 061 — Campaign Integrity, Evaluation Execution, and Comparison Batch

## Batch rule

This feature batches the next five post-campaign items instead of splitting them into five small features.

Covered items:

1. Campaign Result Integrity and Comparison Readiness Audit
2. Baseline Evaluation Execution
3. Trained Policy Evaluation Execution
4. Baseline vs Trained Policy Comparison Readiness Audit
5. Baseline vs Trained Policy Comparison Report

## Purpose

Validate Feature 060 campaign outputs, execute baseline and trained-policy evaluation on the deterministic evaluation trace bank, verify comparability, and produce the first controlled comparison report.

## Required prior inputs

- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json`
- `artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.json`
- `artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/training-metrics.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/evaluation-metrics.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/checkpoint-metadata.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/run-manifest.json`

## Required output artifacts

- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/campaign-integrity-evaluation-comparison-batch-report.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/campaign-integrity-evaluation-comparison-batch-report.md`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-evaluation-results.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/trained-policy-evaluation-results.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/comparison-readiness-audit.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-vs-trained-policy-comparison.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-vs-trained-policy-comparison.md`

## Required report decisions

Required top-level fields:

- `feature_id`
- `batch_items_covered`
- `prerequisite_tags_verified`
- `feature_060_verified`
- `campaign_integrity_summary`
- `baseline_evaluation_summary`
- `trained_policy_evaluation_summary`
- `comparison_readiness_summary`
- `comparison_report_summary`
- `artifact_manifest_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Passing behavior

Passing requires:

- Feature 060 final verdict is `full_paper_default_training_campaign_execution_passed`
- Feature 060B final verdict is `real_torch_trainer_binding_repair_passed`
- Feature 060 artifacts are internally consistent
- baseline evaluation executes on the Feature 058 evaluation trace bank
- trained policy evaluation executes on the same evaluation trace bank
- train/eval trace separation remains preserved
- baseline and trained-policy metrics share the same schema
- comparison report is generated without claiming paper reproduction or superiority
- all output artifacts exist
- no dependency, policy, environment, or reward-timing drift occurs

## Allowed final verdicts

- `campaign_integrity_evaluation_comparison_batch_passed`
- `feature_060_prerequisite_blocked`
- `campaign_integrity_blocked`
- `baseline_evaluation_blocked`
- `trained_policy_evaluation_blocked`
- `comparison_readiness_blocked`
- `comparison_report_blocked`
- `artifact_manifest_blocked`
- `behavior_drift_detected`

## Routing

If all gates pass:

- `final_verdict = campaign_integrity_evaluation_comparison_batch_passed`
- `recommended_next_feature = Feature 062 — Multi-Seed Campaign and Ablation Batch`
- `remaining_blockers = []`

If any gate fails, blockers must name the exact failed gate and route to repair, not Feature 062.

## Hard scope

Allowed:

- campaign artifact integrity audit
- baseline evaluation execution
- trained-policy evaluation execution
- comparison readiness audit
- comparison report generation
- report artifacts and tests

Forbidden:

- paper reproduction claim
- superiority claim unless explicitly marked as unsupported/non-claim comparison data
- dependency changes
- policy drift
- environment semantic changes
- reward timing changes
- prior Feature 037–060B artifact rewrites
- `.specify/feature.json` committed diff
- `AGENTS.md` rewrite
