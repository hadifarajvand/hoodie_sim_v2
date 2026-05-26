# Results Export, Reproducibility, and Final Documentation Batch Report

- feature_id: `063-results-export-reproducibility-documentation-batch`
- final_verdict: `results_export_reproducibility_documentation_batch_passed`
- recommended_next_feature: `Feature 064 — Final Review and Release Gate`

## Final Integrity Audit Summary
{
  "claim_mappings": [
    {
      "claim": "multi_seed_campaign_ablation_batch_passed",
      "claim_type": "controlled_experiment_data",
      "source_artifact": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.json",
      "status": "supported"
    },
    {
      "claim": "source-backed results export",
      "claim_type": "controlled_experiment_data",
      "source_artifact": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json",
      "status": "supported"
    },
    {
      "claim": "aggregation mean/min/max",
      "claim_type": "controlled_experiment_data",
      "source_artifact": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-aggregation.json",
      "status": "supported"
    },
    {
      "claim": "ablation results",
      "claim_type": "controlled_experiment_data",
      "source_artifact": "artifacts/analysis/multi-seed-campaign-ablation-batch/ablation-results.json",
      "status": "supported"
    },
    {
      "claim": "paper reproduction",
      "claim_type": "unsupported",
      "source_artifact": null,
      "status": "unsupported"
    },
    {
      "claim": "unsupported superiority",
      "claim_type": "unsupported",
      "source_artifact": null,
      "status": "unsupported"
    }
  ],
  "no_paper_reproduction_claim": true,
  "no_training_rerun": true,
  "no_unsupported_superiority_claim": true,
  "source_mapping_complete": true,
  "unsupported_claims": [
    "paper reproduction",
    "unsupported superiority"
  ]
}

## Results Export Summary
{
  "controlled_experiment_data_only": true,
  "csv_export": "artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.csv",
  "figure_data": {
    "data_series": {
      "trained_drop_count": {
        "max": 6,
        "mean": 6,
        "min": 6,
        "not_claimed": false,
        "sample_count": 3,
        "std": 0.0,
        "variance": 0.0
      },
      "trained_reward": {
        "max": -80.0,
        "mean": -80.0,
        "min": -80.0,
        "not_claimed": false,
        "sample_count": 3,
        "std": 0.0,
        "variance": 0.0
      }
    },
    "no_invented_values": true,
    "source_artifacts": [
      "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json",
      "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-aggregation.json",
      "artifacts/analysis/multi-seed-campaign-ablation-batch/ablation-results.json"
    ],
    "unsupported_metrics": {
      "delay": {
        "status": "not_claimed"
      },
      "timeout": {
        "status": "not_claimed"
      }
    }
  },
  "figure_data_export": "artifacts/analysis/results-export-reproducibility-documentation-batch/figure-data-export.json",
  "markdown_export": "artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.md",
  "table_rows": [
    {
      "claim_type": "controlled_experiment_data",
      "limitation": "controlled materialization, not new training",
      "metric_name": "seed_count",
      "source_artifact": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json",
      "value_status": "3"
    },
    {
      "claim_type": "controlled_experiment_data",
      "limitation": "seed-level aggregation only",
      "metric_name": "trained_reward_mean",
      "source_artifact": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-aggregation.json",
      "value_status": "-80.0"
    },
    {
      "claim_type": "controlled_experiment_data",
      "limitation": "seed-level aggregation only",
      "metric_name": "trained_reward_min",
      "source_artifact": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-aggregation.json",
      "value_status": "-80.0"
    },
    {
      "claim_type": "controlled_experiment_data",
      "limitation": "seed-level aggregation only",
      "metric_name": "trained_reward_max",
      "source_artifact": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-aggregation.json",
      "value_status": "-80.0"
    },
    {
      "claim_type": "unsupported",
      "limitation": "schema-only metric not claimed",
      "metric_name": "delay",
      "source_artifact": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json",
      "value_status": "not_claimed"
    },
    {
      "claim_type": "unsupported",
      "limitation": "schema-only metric not claimed",
      "metric_name": "timeout",
      "source_artifact": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json",
      "value_status": "not_claimed"
    },
    {
      "claim_type": "unsupported",
      "limitation": "explicitly not claimed",
      "metric_name": "paper_reproduction",
      "source_artifact": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.json",
      "value_status": "false"
    }
  ]
}

## Reproducibility Package Summary
{
  "branch_tag_assumptions": {
    "branch_name": "063-results-export-reproducibility-documentation-batch",
    "tag_assumed_absent": true
  },
  "commands": [
    "python3 -m unittest tests.unit.test_results_export_reproducibility_documentation_batch_schema tests.unit.test_results_export_reproducibility_documentation_batch_metrics tests.unit.test_results_export_reproducibility_documentation_batch_behavior_equivalence tests.integration.test_results_export_reproducibility_documentation_batch tests.integration.test_results_export_reproducibility_documentation_batch_report tests.integration.test_results_export_reproducibility_documentation_batch_scope_guard",
    "python3 -m src.analysis.results_export_reproducibility_documentation_batch"
  ],
  "final_artifacts": [
    "artifacts/analysis/results-export-reproducibility-documentation-batch/results-export-reproducibility-documentation-batch-report.json",
    "artifacts/analysis/results-export-reproducibility-documentation-batch/results-export-reproducibility-documentation-batch-report.md",
    "artifacts/analysis/results-export-reproducibility-documentation-batch/final-experiment-integrity-audit.json",
    "artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.csv",
    "artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.md",
    "artifacts/analysis/results-export-reproducibility-documentation-batch/figure-data-export.json",
    "artifacts/analysis/results-export-reproducibility-documentation-batch/reproducibility-package.md",
    "artifacts/analysis/results-export-reproducibility-documentation-batch/final-mechanism-documentation.md",
    "artifacts/analysis/results-export-reproducibility-documentation-batch/final-artifact-index.json"
  ],
  "known_limitations": [
    "controlled materialization only",
    "schema-only metrics are not claimed",
    "no paper reproduction claim",
    "no superiority claim"
  ],
  "non_claim_boundaries": [
    "not a paper reproduction",
    "not a production performance report",
    "not an unsupported superiority claim"
  ],
  "runtime_environment_assumptions": {
    "controlled_experiment_data_only": true,
    "no_training_rerun": true
  },
  "seed_set": [
    43,
    44,
    45
  ],
  "source_artifacts": [
    "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.json",
    "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json",
    "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-aggregation.json",
    "artifacts/analysis/multi-seed-campaign-ablation-batch/ablation-results.json",
    "artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-vs-trained-policy-comparison.json",
    "artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json"
  ],
  "trace_bank_ids": {
    "evaluation": "feature-058-evaluation-trace-bank",
    "training": "full-training-train-bank"
  }
}

## Mechanism Documentation Summary
{
  "deviation_notes": [
    "documentation package exports only committed evidence",
    "schema-only metrics are explicitly not claimed"
  ],
  "faithful_components": [
    "real Torch trainer binding",
    "selected-action/outcome evidence",
    "multi-seed campaign gate",
    "mechanism ablation controls"
  ],
  "implemented_simplifications": [
    "controlled materialization of prior artifacts",
    "no new training loop",
    "no new evaluation semantics"
  ],
  "multi_seed_and_ablation_limits": [
    "controlled experiment data only",
    "ablation blocked variants remain blocked with exact blockers"
  ],
  "non_claims": [
    "no paper reproduction claim",
    "no unsupported superiority claim",
    "no production performance claim"
  ],
  "real_torch_trainer_binding": {
    "real_trainer_binding_verified": true,
    "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer"
  },
  "selected_action_outcome_evidence": {
    "source": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json",
    "status": "documented"
  }
}

## Artifact Index Summary
{
  "all_required_artifacts_exist": true,
  "artifact_entries": [
    {
      "exists": true,
      "path": "artifacts/analysis/results-export-reproducibility-documentation-batch/results-export-reproducibility-documentation-batch-report.json",
      "role": "final_export",
      "source_relationship": "derived_from_committed_sources"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/results-export-reproducibility-documentation-batch/results-export-reproducibility-documentation-batch-report.md",
      "role": "final_export",
      "source_relationship": "derived_from_committed_sources"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/results-export-reproducibility-documentation-batch/final-experiment-integrity-audit.json",
      "role": "final_export",
      "source_relationship": "derived_from_committed_sources"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.csv",
      "role": "final_export",
      "source_relationship": "derived_from_committed_sources"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.md",
      "role": "final_export",
      "source_relationship": "derived_from_committed_sources"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/results-export-reproducibility-documentation-batch/figure-data-export.json",
      "role": "final_export",
      "source_relationship": "derived_from_committed_sources"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/results-export-reproducibility-documentation-batch/reproducibility-package.md",
      "role": "final_export",
      "source_relationship": "derived_from_committed_sources"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/results-export-reproducibility-documentation-batch/final-mechanism-documentation.md",
      "role": "final_export",
      "source_relationship": "derived_from_committed_sources"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/results-export-reproducibility-documentation-batch/final-artifact-index.json",
      "role": "final_export",
      "source_relationship": "derived_from_committed_sources"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.json",
      "role": "source_artifact",
      "source_relationship": "committed_input"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json",
      "role": "source_artifact",
      "source_relationship": "committed_input"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-aggregation.json",
      "role": "source_artifact",
      "source_relationship": "committed_input"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/multi-seed-campaign-ablation-batch/ablation-results.json",
      "role": "source_artifact",
      "source_relationship": "committed_input"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-vs-trained-policy-comparison.json",
      "role": "source_artifact",
      "source_relationship": "committed_input"
    },
    {
      "exists": true,
      "path": "artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json",
      "role": "source_artifact",
      "source_relationship": "committed_input"
    }
  ]
}

## Claim Boundary Summary
{
  "controlled_experiment_data": true,
  "paper_reproduction_claim": false,
  "production_performance_claim": false,
  "source_mapping_complete": true,
  "unsupported_claims_marked": true,
  "unsupported_superiority_claim": false
}

## Safety Summary
{
  "no_dependency_drift": true,
  "no_environment_contract_drift": true,
  "no_paper_reproduction_claim": true,
  "no_policy_drift": true,
  "no_prior_feature_artifact_rewrite": true,
  "no_reward_timing_change": true,
  "no_training_rerun": true,
  "no_uncontrolled_outputs": true,
  "no_unsupported_superiority_claim": true
}

## Remaining Blockers
[]
