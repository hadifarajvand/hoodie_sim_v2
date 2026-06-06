# Feature 063 — Results Export, Reproducibility, and Final Documentation Batch

## Batch rule

This feature batches the final packaging/export items into one implementation feature.

Covered items:

1. Final Experiment Integrity Audit
2. Paper/Thesis Results Table Export
3. Reproducibility Package
4. Final Mechanism Documentation
5. Final Artifact Index and Handoff Report

## Purpose

Convert the validated campaign, comparison, multi-seed, and ablation artifacts into exportable thesis/paper-ready tables, reproducibility documentation, final mechanism documentation, and a complete artifact index without inflating claims.

## Required prior inputs

- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-aggregation.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/ablation-results.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-vs-trained-policy-comparison.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json`

## Required output artifacts

- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-export-reproducibility-documentation-batch-report.json`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-export-reproducibility-documentation-batch-report.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/final-experiment-integrity-audit.json`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.csv`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/figure-data-export.json`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/reproducibility-package.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/final-mechanism-documentation.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/final-artifact-index.json`

## Required report decisions

Required top-level fields:

- `feature_id`
- `batch_items_covered`
- `prerequisite_tags_verified`
- `feature_062_verified`
- `final_integrity_audit_summary`
- `results_export_summary`
- `reproducibility_package_summary`
- `mechanism_documentation_summary`
- `artifact_index_summary`
- `claim_boundary_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Passing behavior

Passing requires:

- Feature 062 final verdict is `multi_seed_campaign_ablation_batch_passed`
- Feature 062 reports `remaining_blockers = []`
- all final export artifacts exist
- integrity audit maps every claim to a source artifact or marks it unsupported
- results table exports controlled experiment data only
- figure data export is generated from committed artifacts
- reproducibility package includes exact commands, branch/tag assumptions, artifact list, seed set, trace-bank IDs, and known limitations
- final mechanism documentation explains faithful HOODIE-style components, implemented simplifications, and non-claims
- no paper reproduction claim
- no unsupported superiority claim
- no dependency, policy, environment, or reward-timing drift
- no prior Feature 037–062 artifacts are rewritten

## Allowed final verdicts

- `results_export_reproducibility_documentation_batch_passed`
- `feature_062_prerequisite_blocked`
- `final_integrity_audit_blocked`
- `results_export_blocked`
- `reproducibility_package_blocked`
- `mechanism_documentation_blocked`
- `artifact_index_blocked`
- `claim_boundary_blocked`
- `behavior_drift_detected`

## Routing

If all gates pass:

- `final_verdict = results_export_reproducibility_documentation_batch_passed`
- `recommended_next_feature = Feature 064 — Final Review and Release Gate`
- `remaining_blockers = []`

If any gate fails, blockers must name the exact failed gate and route to repair, not Feature 064.

## Hard scope

Allowed:

- final experiment integrity audit
- result table export
- figure-data export
- reproducibility package
- final mechanism documentation
- final artifact index
- batch report artifacts and tests

Forbidden:

- rerunning training campaigns
- modifying experiment outputs from prior features
- paper reproduction claim
- unsupported superiority claim
- dependency changes
- policy drift
- environment semantic changes
- reward timing changes
- prior Feature 037–062 artifact rewrites
- `.specify/feature.json` committed diff
- `AGENTS.md` rewrite
