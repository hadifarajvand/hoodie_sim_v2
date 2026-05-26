# Feature 062 — Multi-Seed Campaign and Ablation Batch

## Batch rule

This feature batches the next five experimental expansion items into one implementation feature.

Covered items:

1. Multi-Seed Campaign Gate
2. Multi-Seed Campaign Execution
3. Multi-Seed Result Aggregation
4. Mechanism Ablation Gate
5. Mechanism Ablation Execution

## Purpose

Move from single-run comparison evidence to controlled multi-seed and ablation evidence. This feature must execute a bounded multi-seed campaign, aggregate seed-level results, define ablation variants, execute ablation runs, and generate auditable outputs without making paper reproduction or superiority claims.

## Required prior inputs

- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/campaign-integrity-evaluation-comparison-batch-report.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-evaluation-results.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/trained-policy-evaluation-results.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-vs-trained-policy-comparison.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json`
- `artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.json`

## Required output artifacts

- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.md`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-gate.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-aggregation.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/ablation-gate.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/ablation-results.json`

## Required report decisions

Required top-level fields:

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

## Passing behavior

Passing requires:

- Feature 061 final verdict is `campaign_integrity_evaluation_comparison_batch_passed`
- Feature 061 reports `remaining_blockers = []`
- multi-seed campaign scope is explicit and bounded
- at least three deterministic seeds are defined
- multi-seed campaign executes or materializes controlled seed-level results using the same metric schema
- aggregation includes mean, min, max, and sample count for supported metrics
- ablation variants are explicitly defined
- ablation execution produces result artifacts under the same trace-bank and metric-schema constraints
- all outputs are controlled experiment data, not paper reproduction or superiority claims
- no dependency, policy, environment, or reward-timing drift occurs
- no prior Feature 037–061 artifacts are rewritten

## Required ablation variants

Minimum variants:

- `full_mechanism`
- `no_deadline_awareness`
- `no_queue_awareness`
- `no_selected_action_outcome_evidence`
- `no_real_trainer_binding_control`

If any variant cannot execute, it must be marked as blocked with an exact blocker rather than silently skipped.

## Allowed final verdicts

- `multi_seed_campaign_ablation_batch_passed`
- `feature_061_prerequisite_blocked`
- `multi_seed_gate_blocked`
- `multi_seed_campaign_blocked`
- `multi_seed_aggregation_blocked`
- `ablation_gate_blocked`
- `ablation_execution_blocked`
- `artifact_manifest_blocked`
- `behavior_drift_detected`

## Routing

If all gates pass:

- `final_verdict = multi_seed_campaign_ablation_batch_passed`
- `recommended_next_feature = Feature 063 — Results Export, Reproducibility, and Final Documentation Batch`
- `remaining_blockers = []`

If any gate fails, blockers must name the exact failed gate and route to repair, not Feature 063.

## Hard scope

Allowed:

- multi-seed campaign gate
- bounded multi-seed campaign execution or controlled materialization
- seed-level result aggregation
- ablation gate
- ablation execution or controlled materialization
- batch report artifacts and tests

Forbidden:

- paper reproduction claim
- unsupported superiority claim
- dependency changes
- policy drift
- environment semantic changes
- reward timing changes
- prior Feature 037–061 artifact rewrites
- `.specify/feature.json` committed diff
- `AGENTS.md` rewrite
- uncontrolled campaign loops
- model checkpoint binaries unless already metadata-only and controlled by existing contract
