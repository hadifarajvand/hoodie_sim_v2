# Staged Training Budget Learning Curve Report

- feature_id: `063-staged-training-budget-learning-curve`
- final_verdict: `staged_training_budget_learning_curve_ready`
- recommended_next_feature: `Feature 064 — Final Review and Release Gate Batch`

## Training Mode
{
  "checkpoint_budgets": [
    100,
    150,
    200,
    500
  ],
  "episode_length": 110,
  "evaluation_episode_count_per_checkpoint": 100,
  "total_max_training_budget": 500,
  "training_mode": "cumulative_staged",
  "training_rerun_from_scratch": false
}

## Checkpoint Metrics
| budget | cumulative episodes | eval episodes | optimizer steps | replay size | loss finite | comparison ready |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| 100 | 100 | 100 | 10937 | 10000 | True | True |
| 150 | 150 | 100 | 16437 | 10000 | True | True |
| 200 | 200 | 100 | 21937 | 10000 | True | True |
| 500 | 500 | 100 | 54937 | 10000 | True | True |

## Comparison Readiness Summary
{
  "baseline_reference_artifact_path": "artifacts/analysis/full-paper-default-training-campaign-execution/baseline-evaluation-metrics.json",
  "baseline_reference_reused": true,
  "baseline_reference_summary": {
    "actual_baseline_evaluation_episode_count": 100,
    "artifact_path": "artifacts/analysis/full-paper-default-training-campaign-execution/baseline-evaluation-metrics.json",
    "available": true,
    "baseline_metrics_real_execution": true,
    "baseline_policy_episode_counts": {
      "fixed-horizontal": 100,
      "local-only": 100,
      "random-legal": 100
    },
    "baseline_policy_names": [
      "local-only",
      "random-legal",
      "fixed-horizontal"
    ],
    "evaluated_policy_count": 3,
    "no_baseline_superiority_claim": true
  },
  "checkpoint_budgets": [
    100,
    150,
    200,
    500
  ],
  "comparison_ready": true,
  "descriptive_only": true,
  "episode_length": 110,
  "evaluation_episode_count_per_checkpoint": 100,
  "no_baseline_superiority_claim": true,
  "no_paper_reproduction_claim": true,
  "no_performance_superiority_claim": true,
  "ready_checkpoint_budgets": [
    100,
    150,
    200,
    500
  ],
  "training_mode": "cumulative_staged",
  "unready_checkpoint_budgets": []
}

## Staged Comparative Table Summary
{
  "baseline_reference_reused": true,
  "comparison_ready": true,
  "comparison_scope": "comparison readiness and descriptive trend analysis only",
  "rows": [
    {
      "action_accounting_reconciled": true,
      "action_count_total": 10000,
      "claim_safety_passed": true,
      "comparison_ready": true,
      "cumulative_training_episode_count": 100,
      "evaluation_mean_reward": -4181.2,
      "last_loss": 983.4915771484375,
      "loss_count": 10937,
      "optimizer_step_count": 10937,
      "replay_size": 10000,
      "training_budget": 100
    },
    {
      "action_accounting_reconciled": true,
      "action_count_total": 10000,
      "claim_safety_passed": true,
      "comparison_ready": true,
      "cumulative_training_episode_count": 150,
      "evaluation_mean_reward": -4181.2,
      "last_loss": 767.7593383789062,
      "loss_count": 16437,
      "optimizer_step_count": 16437,
      "replay_size": 10000,
      "training_budget": 150
    },
    {
      "action_accounting_reconciled": true,
      "action_count_total": 10000,
      "claim_safety_passed": true,
      "comparison_ready": true,
      "cumulative_training_episode_count": 200,
      "evaluation_mean_reward": -4181.2,
      "last_loss": 780.3190307617188,
      "loss_count": 21937,
      "optimizer_step_count": 21937,
      "replay_size": 10000,
      "training_budget": 200
    },
    {
      "action_accounting_reconciled": true,
      "action_count_total": 10000,
      "claim_safety_passed": true,
      "comparison_ready": true,
      "cumulative_training_episode_count": 500,
      "evaluation_mean_reward": -4181.2,
      "last_loss": 916.686279296875,
      "loss_count": 54937,
      "optimizer_step_count": 54937,
      "replay_size": 10000,
      "training_budget": 500
    }
  ]
}

## Figure Manifest
{
  "figure_count": 5,
  "figure_directory": "artifacts/analysis/staged-training-budget-learning-curve/figures",
  "figure_files": [
    "figure_01_eval_reward_by_training_budget.png",
    "figure_02_replay_size_and_optimizer_steps_by_budget.png",
    "figure_03_action_distribution_by_training_budget.png",
    "figure_04_loss_by_training_budget.png",
    "figure_05_comparison_readiness_by_budget.png"
  ],
  "figures_generated": true
}

## Claim Safety Status
{
  "baseline_superiority_claim_made": false,
  "claim_safety_passed": true,
  "paper_reproduction_claim_made": false,
  "performance_superiority_claim_made": false
}

## Remaining Blockers
[]
