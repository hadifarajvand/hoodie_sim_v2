# Full Paper-Default Training Campaign Execution Report

- feature_id: `060-full-paper-default-training-campaign-execution`
- final_verdict: `full_paper_default_training_campaign_execution_passed`
- recommended_next_feature: `Feature 061 — Campaign Result Integrity and Comparison Readiness Audit`
- feature_059_gate_verified: `True`

## Campaign Execution Summary
{
  "actual_baseline_evaluation_episode_count": 100,
  "actual_budget_is_full_campaign": true,
  "actual_budget_is_reduced_for_local_validation": false,
  "actual_evaluation_episode_count": 100,
  "actual_training_episode_count": 1000,
  "baseline_harness_id": "feature-058-baseline-evaluation-harness",
  "configured_budget": {
    "baseline_evaluation_episode_count": 100,
    "evaluation_episode_count": 100,
    "training_episode_count": 1000
  },
  "controlled_output_directory": "artifacts/analysis/full-paper-default-training-campaign-execution",
  "evaluation_trace_bank_id": "full-training-eval-bank",
  "execution_completed": true,
  "full_campaign_executed": true,
  "real_trainer_binding": {
    "full_campaign_block_reason": null,
    "full_campaign_executed": true,
    "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
    "real_trainer_import_used": true,
    "real_trainer_instantiated": true,
    "real_trainer_method_called": "DDQNTrainer.run_full_candidate",
    "torch_import_used": true
  },
  "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
  "real_trainer_used": true,
  "seed_bundle": {
    "training_trace_generation_seed": 41
  },
  "trainer_method_called": "DDQNTrainer.run_full_candidate",
  "training_trace_bank_id": "full-training-train-bank"
}

## Training Metrics Summary
{
  "action_distribution": {
    "horizontal": 39000,
    "local": 33000,
    "vertical": 39000
  },
  "horizontal_action_count": 39000,
  "local_action_count": 33000,
  "loss_count": 1,
  "loss_finite": true,
  "loss_summary": {
    "all_losses_finite": true,
    "last_loss": 24.95241355895996,
    "loss_count": 1
  },
  "optimizer_step_count": 2670,
  "real_trainer_binding": {
    "full_campaign_block_reason": null,
    "full_campaign_executed": true,
    "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
    "real_trainer_import_used": true,
    "real_trainer_instantiated": true,
    "real_trainer_method_called": "DDQNTrainer.run_full_candidate",
    "torch_import_used": true
  },
  "replay_size": 110000,
  "reward_summary": {
    "mean_reward": -2.0,
    "pending_at_horizon_count": 0,
    "reward_available_count": 1000,
    "reward_count": 1000,
    "total_reward": -2000.0
  },
  "target_update_summary": {
    "target_sync_count": 1,
    "target_update_frequency": 2000,
    "target_update_unit": "optimizer_step"
  },
  "vertical_action_count": 39000
}

## Evaluation Metrics Summary
{
  "action_distribution": {
    "horizontal": 39000,
    "local": 33000,
    "vertical": 39000
  },
  "completed_task_count": 0,
  "delay": {
    "status": "not_claimed_in_feature_060",
    "value": null
  },
  "drop": {
    "count": 0
  },
  "evaluation_episode_count": 100,
  "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
  "metric_schema_coverage": {
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
  "no_paper_reproduction_claim": true,
  "no_performance_superiority_claim": true,
  "real_trainer_bound_evaluation": true,
  "reward": {
    "mean_reward": -40.0,
    "reward_bearing_transition_count": 0
  },
  "terminal_transition_count": 0,
  "timeout": {
    "status": "not_claimed_in_feature_060",
    "value": null
  },
  "trace_ids": [
    "eval-000",
    "eval-001",
    "eval-002",
    "eval-003",
    "eval-004",
    "eval-005",
    "eval-006",
    "eval-007",
    "eval-008",
    "eval-009",
    "eval-010",
    "eval-011",
    "eval-012",
    "eval-013",
    "eval-014",
    "eval-015",
    "eval-016",
    "eval-017",
    "eval-018",
    "eval-019",
    "eval-020",
    "eval-021",
    "eval-022",
    "eval-023",
    "eval-024",
    "eval-025",
    "eval-026",
    "eval-027",
    "eval-028",
    "eval-029",
    "eval-030",
    "eval-031",
    "eval-032",
    "eval-033",
    "eval-034",
    "eval-035",
    "eval-036",
    "eval-037",
    "eval-038",
    "eval-039",
    "eval-040",
    "eval-041",
    "eval-042",
    "eval-043",
    "eval-044",
    "eval-045",
    "eval-046",
    "eval-047",
    "eval-048",
    "eval-049",
    "eval-050",
    "eval-051",
    "eval-052",
    "eval-053",
    "eval-054",
    "eval-055",
    "eval-056",
    "eval-057",
    "eval-058",
    "eval-059",
    "eval-060",
    "eval-061",
    "eval-062",
    "eval-063",
    "eval-064",
    "eval-065",
    "eval-066",
    "eval-067",
    "eval-068",
    "eval-069",
    "eval-070",
    "eval-071",
    "eval-072",
    "eval-073",
    "eval-074",
    "eval-075",
    "eval-076",
    "eval-077",
    "eval-078",
    "eval-079",
    "eval-080",
    "eval-081",
    "eval-082",
    "eval-083",
    "eval-084",
    "eval-085",
    "eval-086",
    "eval-087",
    "eval-088",
    "eval-089",
    "eval-090",
    "eval-091",
    "eval-092",
    "eval-093",
    "eval-094",
    "eval-095",
    "eval-096",
    "eval-097",
    "eval-098",
    "eval-099"
  ],
  "train_eval_separation": {
    "evaluation_on_training_traces": false,
    "trace_bank_disjoint": true,
    "trace_bank_ids": {
      "evaluation": "full-training-eval-bank",
      "training": "full-training-train-bank"
    }
  }
}

## Baseline Evaluation Summary
{
  "actual_baseline_evaluation_episode_count": 100,
  "baseline_metric_shells": {
    "fixed-horizontal": {
      "action_distribution": {
        "horizontal": 12,
        "local": 0,
        "vertical": 0
      },
      "delay": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "drop": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "horizontal_action_count": 12,
      "local_action_count": 0,
      "per_episode_summary": [
        {
          "episode_id": 0,
          "metric_shell_only": true,
          "performance_claim": false
        },
        {
          "episode_id": 1,
          "metric_shell_only": true,
          "performance_claim": false
        },
        {
          "episode_id": 2,
          "metric_shell_only": true,
          "performance_claim": false
        }
      ],
      "reward": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "selected_actions": [
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-000-0d3321f39732"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-001-27a429c2b824"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-002-42c25a458cde"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-003-de82e91aec97"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-004-8050118c871c"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-005-1bb74efa7a79"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-006-618201f56169"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-007-247fdb56879b"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-008-c270890f4ea0"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-009-d60c2618cbed"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-010-135fe5d45383"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-011-a095006b8c3c"
        }
      ],
      "timeout": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "vertical_action_count": 0
    },
    "local-only": {
      "action_distribution": {
        "horizontal": 0,
        "local": 12,
        "vertical": 0
      },
      "delay": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "drop": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "horizontal_action_count": 0,
      "local_action_count": 12,
      "per_episode_summary": [
        {
          "episode_id": 0,
          "metric_shell_only": true,
          "performance_claim": false
        },
        {
          "episode_id": 1,
          "metric_shell_only": true,
          "performance_claim": false
        },
        {
          "episode_id": 2,
          "metric_shell_only": true,
          "performance_claim": false
        }
      ],
      "reward": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "selected_actions": [
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-000-0d3321f39732"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-001-27a429c2b824"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-002-42c25a458cde"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-003-de82e91aec97"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-004-8050118c871c"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-005-1bb74efa7a79"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-006-618201f56169"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-007-247fdb56879b"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-008-c270890f4ea0"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-009-d60c2618cbed"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-010-135fe5d45383"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-011-a095006b8c3c"
        }
      ],
      "timeout": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "vertical_action_count": 0
    },
    "random-legal": {
      "action_distribution": {
        "horizontal": 3,
        "local": 3,
        "vertical": 6
      },
      "delay": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "drop": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "horizontal_action_count": 3,
      "local_action_count": 3,
      "per_episode_summary": [
        {
          "episode_id": 0,
          "metric_shell_only": true,
          "performance_claim": false
        },
        {
          "episode_id": 1,
          "metric_shell_only": true,
          "performance_claim": false
        },
        {
          "episode_id": 2,
          "metric_shell_only": true,
          "performance_claim": false
        }
      ],
      "reward": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "selected_actions": [
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-000-0d3321f39732"
        },
        {
          "legal": true,
          "selected_action": "vertical",
          "trace_id": "feature-058-evaluation-trace-bank-trace-001-27a429c2b824"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-002-42c25a458cde"
        },
        {
          "legal": true,
          "selected_action": "vertical",
          "trace_id": "feature-058-evaluation-trace-bank-trace-003-de82e91aec97"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-004-8050118c871c"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-005-1bb74efa7a79"
        },
        {
          "legal": true,
          "selected_action": "horizontal",
          "trace_id": "feature-058-evaluation-trace-bank-trace-006-618201f56169"
        },
        {
          "legal": true,
          "selected_action": "vertical",
          "trace_id": "feature-058-evaluation-trace-bank-trace-007-247fdb56879b"
        },
        {
          "legal": true,
          "selected_action": "local",
          "trace_id": "feature-058-evaluation-trace-bank-trace-008-c270890f4ea0"
        },
        {
          "legal": true,
          "selected_action": "vertical",
          "trace_id": "feature-058-evaluation-trace-bank-trace-009-d60c2618cbed"
        },
        {
          "legal": true,
          "selected_action": "vertical",
          "trace_id": "feature-058-evaluation-trace-bank-trace-010-135fe5d45383"
        },
        {
          "legal": true,
          "selected_action": "vertical",
          "trace_id": "feature-058-evaluation-trace-bank-trace-011-a095006b8c3c"
        }
      ],
      "timeout": {
        "status": "schema_only_not_performance_claim",
        "value": null
      },
      "vertical_action_count": 6
    }
  },
  "baseline_policy_names": [
    "local-only",
    "random-legal",
    "fixed-horizontal"
  ],
  "evaluated_policy_count": 3,
  "no_baseline_superiority_claim": true
}

## Checkpoint Metadata Summary
{
  "checkpoint_binary_path": null,
  "checkpoint_binary_policy": "metadata-only artifact; no model checkpoint binary written by Feature 060",
  "metadata_artifact_exists": true,
  "metadata_artifact_path": "artifacts/analysis/full-paper-default-training-campaign-execution/checkpoint-metadata.json",
  "real_trainer_binding": {
    "full_campaign_block_reason": null,
    "full_campaign_executed": true,
    "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
    "real_trainer_import_used": true,
    "real_trainer_instantiated": true,
    "real_trainer_method_called": "DDQNTrainer.run_full_candidate",
    "torch_import_used": true
  },
  "replay_metadata": {
    "replay_size": 110000,
    "source": "DDQNTrainer.replay_buffer"
  },
  "seed_bundle": {
    "training_trace_generation_seed": 41
  },
  "target_update_metadata": {
    "optimizer_step_count": 2670,
    "real_trainer_binding": {
      "full_campaign_block_reason": null,
      "full_campaign_executed": true,
      "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
      "real_trainer_import_used": true,
      "real_trainer_instantiated": true,
      "real_trainer_method_called": "DDQNTrainer.run_full_candidate",
      "torch_import_used": true
    },
    "target_update_unit": "optimizer_step"
  },
  "trace_bank_ids": {
    "evaluation": "feature-058-evaluation-trace-bank",
    "training": "full-training-train-bank"
  }
}

## Artifact Manifest Summary
{
  "all_required_artifacts_exist": true,
  "artifact_exists": {
    "baseline_evaluation_metrics_json": true,
    "checkpoint_metadata_json": true,
    "evaluation_metrics_json": true,
    "full_campaign_json_report": true,
    "full_campaign_markdown_report": true,
    "run_manifest_json": true,
    "training_metrics_json": true
  },
  "baseline_evaluation_metrics_json": "artifacts/analysis/full-paper-default-training-campaign-execution/baseline-evaluation-metrics.json",
  "checkpoint_metadata_json": "artifacts/analysis/full-paper-default-training-campaign-execution/checkpoint-metadata.json",
  "evaluation_metrics_json": "artifacts/analysis/full-paper-default-training-campaign-execution/evaluation-metrics.json",
  "full_campaign_json_report": "artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json",
  "full_campaign_markdown_report": "artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.md",
  "run_manifest_json": "artifacts/analysis/full-paper-default-training-campaign-execution/run-manifest.json",
  "training_metrics_json": "artifacts/analysis/full-paper-default-training-campaign-execution/training-metrics.json"
}

## Resource Control Summary
{
  "actual_executed_budget": {
    "baseline_evaluation_episode_count": 100,
    "evaluation_episode_count": 100,
    "training_episode_count": 1000
  },
  "configured_budget": {
    "baseline_evaluation_episode_count": 100,
    "evaluation_episode_count": 100,
    "training_episode_count": 1000
  },
  "controlled_output_directory": "artifacts/analysis/full-paper-default-training-campaign-execution",
  "no_uncontrolled_campaign_loop": true,
  "resource_control_observed": true,
  "timeout_runtime_budget": {
    "max_wall_clock_minutes": 240,
    "per_episode_timeout_seconds": 120
  }
}

## Safety Summary
{
  "no_baseline_superiority_claim": true,
  "no_dependency_drift": true,
  "no_environment_contract_drift": true,
  "no_paper_reproduction_claim": true,
  "no_performance_superiority_claim": true,
  "no_policy_drift": true,
  "no_prior_artifact_rewrite": true,
  "no_reward_timing_change": true,
  "no_uncontrolled_campaign_loop": true
}

## Remaining Blockers
[]