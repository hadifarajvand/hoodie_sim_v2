# Reproducibility Package

## Commands
- `python3 -m unittest tests.unit.test_results_export_reproducibility_documentation_batch_schema tests.unit.test_results_export_reproducibility_documentation_batch_metrics tests.unit.test_results_export_reproducibility_documentation_batch_behavior_equivalence tests.integration.test_results_export_reproducibility_documentation_batch tests.integration.test_results_export_reproducibility_documentation_batch_report tests.integration.test_results_export_reproducibility_documentation_batch_scope_guard`
- `python3 -m src.analysis.results_export_reproducibility_documentation_batch`

## Branch Assumptions
{
  "branch_name": "063-results-export-reproducibility-documentation-batch",
  "tag_assumed_absent": true
}

## Source Artifacts
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-aggregation.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/ablation-results.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-vs-trained-policy-comparison.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json`

## Final Artifacts
- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-export-reproducibility-documentation-batch-report.json`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-export-reproducibility-documentation-batch-report.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/final-experiment-integrity-audit.json`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.csv`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/figure-data-export.json`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/reproducibility-package.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/final-mechanism-documentation.md`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/final-artifact-index.json`

## Seed Set
[43, 44, 45]

## Trace Bank IDs
{
  "evaluation": "feature-058-evaluation-trace-bank",
  "training": "full-training-train-bank"
}

## Limitations
- controlled materialization only
- schema-only metrics are not claimed
- no paper reproduction claim
- no superiority claim

## Non-Claim Boundaries
- not a paper reproduction
- not a production performance report
- not an unsupported superiority claim
