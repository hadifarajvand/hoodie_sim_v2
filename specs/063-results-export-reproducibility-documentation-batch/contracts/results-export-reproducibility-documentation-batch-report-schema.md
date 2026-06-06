# Feature 063 Report Contract

## Required artifacts

- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-export-reproducibility-documentation-batch-report.json`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-export-reproducibility-documentation-batch-report.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/final-experiment-integrity-audit.json`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.csv`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/figure-data-export.json`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/reproducibility-package.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/final-mechanism-documentation.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/final-artifact-index.json`

## Required top-level fields

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

## Passing verdict

- `feature_id = 063-results-export-reproducibility-documentation-batch`
- `feature_062_verified = true`
- `remaining_blockers = []`
- `recommended_next_feature = Feature 064 — Final Review and Release Gate`
- `final_verdict = results_export_reproducibility_documentation_batch_passed`

## Required safety fields

- `no_training_rerun`
- `no_dependency_drift`
- `no_policy_drift`
- `no_environment_contract_drift`
- `no_reward_timing_change`
- `no_prior_feature_artifact_rewrite`
- `no_paper_reproduction_claim`
- `no_unsupported_superiority_claim`
- `no_uncontrolled_outputs`
