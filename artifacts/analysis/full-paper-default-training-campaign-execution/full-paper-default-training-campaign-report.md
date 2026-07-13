# Full Paper-Default Training Campaign Execution Report

- feature_id: `060-full-paper-default-training-campaign-execution`
- final_verdict: `full_paper_default_training_campaign_execution_passed`
- recommended_next_feature: `Feature 061 — Campaign Result Integrity and Comparison Readiness Audit`
- feature_059_gate_verified: `True`

## Campaign Execution Summary
{
  "actual_baseline_evaluation_episode_count": 1,
  "actual_budget_is_reduced_for_local_validation": true,
  "actual_evaluation_episode_count": 3,
  "actual_training_episode_count": 1,
  "baseline_harness_id": "feature-058-baseline-evaluation-harness",
  "configured_budget": {
    "baseline_evaluation_episode_count": 1,
    "evaluation_episode_count": 3,
    "training_episode_count": 1
  },
  "controlled_output_directory": "artifacts/analysis/full-paper-default-training-campaign-execution",
  "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
  "execution_completed": true,
  "local_validation_mode": true,
  "real_trainer_binding": {
    "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
    "real_trainer_import_used": true,
    "real_trainer_instantiated": true,
    "real_trainer_method_called": "DDQNTrainer.run_pilot",
    "real_trainer_update_or_train_called": true,
    "scalar_fallback_drives_campaign_claim": false,
    "torch_import_used": true,
    "torch_version": "2.12.1",
    "torchrl_available": true
  },
  "seed_bundle": {
    "action_exploration_seed": 53,
    "evaluation_trace_generation_seed": 43,
    "model_initialization_seed": 19,
    "python_seed": 59,
    "readiness_probe_seed": 31,
    "replay_sampling_seed": 47,
    "torch_seed": 61,
    "training_trace_generation_seed": 41
  },
  "training_trace_bank_id": "full-training-train-bank"
}

## Training Metrics Summary
{
  "action_distribution": {
    "horizontal": 45,
    "local": 65,
    "vertical": 0
  },
  "horizontal_action_count": 45,
  "local_action_count": 65,
  "loss_count": 1,
  "loss_finite": true,
  "loss_summary": {
    "all_losses_finite": true,
    "last_loss": 20.38028907775879,
    "loss_count": 1
  },
  "optimizer_step_count": 47,
  "real_trainer_binding": {
    "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
    "real_trainer_import_used": true,
    "real_trainer_instantiated": true,
    "real_trainer_method_called": "DDQNTrainer.run_pilot",
    "real_trainer_update_or_train_called": true,
    "scalar_fallback_drives_campaign_claim": false,
    "torch_import_used": true,
    "torch_version": "2.12.1",
    "torchrl_available": true
  },
  "replay_size": 110,
  "reward_summary": {
    "mean_reward": -4.402439024390244,
    "pending_at_horizon_count": 0,
    "reward_available_count": 82,
    "reward_count": 82,
    "total_reward": -361.0
  },
  "target_update_summary": {
    "target_sync_count": 0,
    "target_update_frequency": 2000,
    "target_update_unit": "optimizer_step"
  },
  "vertical_action_count": 0
}

## Evaluation Metrics Summary
{
  "action_distribution": {
    "horizontal": 45,
    "local": 65,
    "vertical": 0
  },
  "completed_task_count": 320,
  "delay": {
    "status": "not_claimed_in_feature_060",
    "value": null
  },
  "drop": {
    "count": 0
  },
  "evaluation_episode_count": 3,
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
    "mean_reward": -452.0,
    "reward_bearing_transition_count": 244
  },
  "terminal_transition_count": 244,
  "timeout": {
    "status": "not_claimed_in_feature_060",
    "value": null
  },
  "trace_ids": [
    "hoodie-43",
    "hoodie-44",
    "hoodie-45"
  ],
  "train_eval_separation": {
    "evaluation_on_training_traces": false,
    "trace_bank_disjoint": true,
    "trace_bank_ids": {
      "evaluation": "feature-058-evaluation-trace-bank",
      "training": "full-training-train-bank"
    }
  }
}

## Baseline Evaluation Summary
{
  "actual_baseline_evaluation_episode_count": 1,
  "baseline_metric_shells": {
    "local-only": {
      "action_distribution": null,
      "delay": null,
      "drop": null,
      "horizontal_action_count": 0,
      "local_action_count": 0,
      "per_episode_summary": null,
      "reward": null,
      "timeout": null,
      "vertical_action_count": 0
    }
  },
  "baseline_policy_names": [
    "local-only"
  ],
  "evaluated_policy_count": 1,
  "no_baseline_superiority_claim": true
}

## Checkpoint Metadata Summary
{
  "checkpoint_binary_path": null,
  "checkpoint_binary_policy": "metadata-only artifact; no model checkpoint binary written by Feature 060",
  "metadata_artifact_exists": true,
  "metadata_artifact_path": "artifacts/analysis/full-paper-default-training-campaign-execution/checkpoint-metadata.json",
  "real_trainer_binding": {
    "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
    "real_trainer_import_used": true,
    "real_trainer_instantiated": true,
    "real_trainer_method_called": "DDQNTrainer.run_pilot",
    "real_trainer_update_or_train_called": true,
    "scalar_fallback_drives_campaign_claim": false,
    "torch_import_used": true,
    "torch_version": "2.12.1",
    "torchrl_available": true
  },
  "replay_metadata": {
    "replay_size": 110,
    "source": "DDQNTrainer.replay_buffer"
  },
  "seed_bundle": {
    "action_exploration_seed": 53,
    "evaluation_trace_generation_seed": 43,
    "model_initialization_seed": 19,
    "python_seed": 59,
    "readiness_probe_seed": 31,
    "replay_sampling_seed": 47,
    "torch_seed": 61,
    "training_trace_generation_seed": 41
  },
  "target_update_metadata": {
    "optimizer_step_count": 47,
    "real_trainer_binding": {
      "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
      "real_trainer_import_used": true,
      "real_trainer_instantiated": true,
      "real_trainer_method_called": "DDQNTrainer.run_pilot",
      "real_trainer_update_or_train_called": true,
      "scalar_fallback_drives_campaign_claim": false,
      "torch_import_used": true,
      "torch_version": "2.12.1",
      "torchrl_available": true
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
    "checkpoint_metadata_json": true,
    "evaluation_metrics_json": true,
    "full_campaign_json_report": true,
    "full_campaign_markdown_report": true,
    "run_manifest_json": true,
    "training_metrics_json": true
  },
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
    "baseline_evaluation_episode_count": 1,
    "evaluation_episode_count": 3,
    "training_episode_count": 1
  },
  "configured_budget": {
    "baseline_evaluation_episode_count": 1,
    "evaluation_episode_count": 3,
    "training_episode_count": 1
  },
  "controlled_output_directory": "artifacts/analysis/full-paper-default-training-campaign-execution",
  "no_uncontrolled_campaign_loop": true,
  "resource_control_observed": true,
  "timeout_runtime_budget": {
    "enforced": false,
    "mode": "local_validation"
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