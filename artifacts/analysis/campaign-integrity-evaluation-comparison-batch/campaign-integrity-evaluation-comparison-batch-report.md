# Campaign Integrity Evaluation Comparison Batch Report

- feature_id: `061-campaign-integrity-evaluation-comparison-batch`
- final_verdict: `campaign_integrity_evaluation_comparison_batch_passed`
- recommended_next_feature: `Feature 062 — Multi-Seed Campaign and Ablation Batch`

## Campaign Integrity Summary
{
  "artifact_manifest_paths_agree": true,
  "feature_060_artifacts_refreshed": true,
  "feature_060_checkpoint_metadata_exist": true,
  "feature_060_evaluation_metrics_exist": true,
  "feature_060_report_exists": true,
  "feature_060_run_manifest_exist": true,
  "feature_060_sources": {
    "feature_058_report": "artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json",
    "feature_060_report": "artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json",
    "feature_060b_report": "artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.json"
  },
  "feature_060_training_metrics_exist": true,
  "real_trainer_binding_evidence_exists": true,
  "scalar_fallback_drives_campaign_claim": false,
  "seed_bundle_consistent": true,
  "trace_bank_ids_consistent": true
}

## Baseline Evaluation Summary
{
  "baseline_policy_metrics": {},
  "controlled_experiment_data": true,
  "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
  "metric_schema": {
    "metric_schema_complete": true,
    "missing_metric_fields": [],
    "present_metric_fields": [
      "delay",
      "drop",
      "timeout",
      "reward",
      "action_distribution",
      "local_action_count",
      "horizontal_action_count",
      "vertical_action_count",
      "per_episode_summary",
      "train_eval_separation",
      "baseline_policy_metrics"
    ],
    "required_metric_fields": [
      "delay",
      "drop",
      "timeout",
      "reward",
      "action_distribution",
      "local_action_count",
      "horizontal_action_count",
      "vertical_action_count",
      "per_episode_summary",
      "train_eval_separation",
      "baseline_policy_metrics"
    ]
  },
  "policies": [],
  "trace_ids": [
    "hoodie-43",
    "hoodie-44",
    "hoodie-45"
  ]
}

## Trained Policy Evaluation Summary
{
  "controlled_experiment_data": true,
  "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
  "metric_schema": {
    "metric_schema_complete": true,
    "missing_metric_fields": [],
    "present_metric_fields": [
      "delay",
      "drop",
      "timeout",
      "reward",
      "action_distribution",
      "local_action_count",
      "horizontal_action_count",
      "vertical_action_count",
      "per_episode_summary",
      "train_eval_separation",
      "baseline_policy_metrics"
    ],
    "required_metric_fields": [
      "delay",
      "drop",
      "timeout",
      "reward",
      "action_distribution",
      "local_action_count",
      "horizontal_action_count",
      "vertical_action_count",
      "per_episode_summary",
      "train_eval_separation",
      "baseline_policy_metrics"
    ]
  },
  "trace_ids": [
    "hoodie-43",
    "hoodie-44",
    "hoodie-45"
  ],
  "trained_policy_metrics": {
    "action_distribution": {
      "horizontal": 45,
      "local": 65,
      "vertical": 0
    },
    "delay": {
      "status": "not_claimed_in_feature_060",
      "value": null
    },
    "drop": {
      "count": 0
    },
    "reward": {
      "mean_reward": -452.0,
      "reward_bearing_transition_count": 244
    },
    "timeout": {
      "status": "not_claimed_in_feature_060",
      "value": null
    },
    "train_eval_separation": {
      "evaluation_on_training_traces": false,
      "trace_bank_disjoint": true,
      "trace_bank_ids": {
        "evaluation": "feature-058-evaluation-trace-bank",
        "training": "full-training-train-bank"
      }
    }
  }
}

## Comparison Readiness Summary
{
  "identical_action_contract": true,
  "identical_metric_schema": true,
  "no_paper_reproduction_claim": true,
  "no_training_traces_leak_into_evaluation": true,
  "no_unsupported_superiority_claim": true,
  "same_evaluation_trace_bank": true,
  "trace_ids_comparable": true
}

## Comparison Report Summary
{
  "action_distribution": {
    "baseline": null,
    "trained": {
      "horizontal": 45,
      "local": 65,
      "vertical": 0
    }
  },
  "baseline_policy_metrics": {},
  "controlled_experiment_data": true,
  "delay": {
    "baseline": null,
    "trained": {
      "status": "not_claimed_in_feature_060",
      "value": null
    }
  },
  "drop": {
    "baseline": null,
    "trained": {
      "count": 0
    }
  },
  "horizontal_action_count": {
    "baseline": null,
    "trained": 45
  },
  "local_action_count": {
    "baseline": null,
    "trained": 65
  },
  "paper_reproduction_claim": false,
  "per_episode_summary": {
    "baseline": null,
    "trained": {
      "evaluation_on_training_traces": false,
      "trace_bank_disjoint": true,
      "trace_bank_ids": {
        "evaluation": "feature-058-evaluation-trace-bank",
        "training": "full-training-train-bank"
      }
    }
  },
  "reward": {
    "baseline": null,
    "trained": {
      "mean_reward": -452.0,
      "reward_bearing_transition_count": 244
    }
  },
  "single_run_limitation": true,
  "superiority_claim": false,
  "timeout": {
    "baseline": null,
    "trained": {
      "status": "not_claimed_in_feature_060",
      "value": null
    }
  },
  "train_eval_separation": {
    "evaluation_on_training_traces": false,
    "trace_bank_disjoint": true,
    "trace_bank_ids": {
      "evaluation": "feature-058-evaluation-trace-bank",
      "training": "full-training-train-bank"
    }
  },
  "trained_policy_metrics": {
    "action_distribution": {
      "horizontal": 45,
      "local": 65,
      "vertical": 0
    },
    "delay": {
      "status": "not_claimed_in_feature_060",
      "value": null
    },
    "drop": {
      "count": 0
    },
    "reward": {
      "mean_reward": -452.0,
      "reward_bearing_transition_count": 244
    },
    "timeout": {
      "status": "not_claimed_in_feature_060",
      "value": null
    },
    "train_eval_separation": {
      "evaluation_on_training_traces": false,
      "trace_bank_disjoint": true,
      "trace_bank_ids": {
        "evaluation": "feature-058-evaluation-trace-bank",
        "training": "full-training-train-bank"
      }
    }
  },
  "vertical_action_count": {
    "baseline": null,
    "trained": 0
  }
}

## Artifact Manifest Summary
{
  "all_required_artifacts_exist": true,
  "artifact_exists": {
    "feature_058_report": true,
    "feature_060_checkpoint_metadata": true,
    "feature_060_evaluation_metrics": true,
    "feature_060_report": true,
    "feature_060_run_manifest": true,
    "feature_060_training_metrics": true,
    "feature_060b_report": true
  }
}

## Safety Summary
{
  "no_dependency_drift": false,
  "no_environment_contract_drift": true,
  "no_paper_reproduction_claim": true,
  "no_policy_drift": false,
  "no_prior_feature_artifact_rewrite": true,
  "no_reward_timing_change": true,
  "no_uncontrolled_campaign_loop": true,
  "no_unsupported_superiority_claim": true
}

## Remaining Blockers
[]
