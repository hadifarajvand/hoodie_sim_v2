# Full Training/Reproduction Campaign Report

- feature_id: `041-full-training-reproduction-campaign`
- campaign_stage: `pilot_training`
- final_verdict: `pilot_training_passed`
- no_curve_fitting: `True`
- no_simulator_output_tuning: `True`
- no_dependency_drift: `True`
- no_environment_contract_drift: `True`
- no_policy_drift: `True`
- no_reward_timing_change: `True`

## Terminal Exposure Gate
{
  "action_count_by_type": {
    "local": 5
  },
  "completed_task_count": 0,
  "dropped_task_count": 0,
  "generated_task_count": 5,
  "horizontal_action_count": 0,
  "illegal_action_count": 0,
  "illegal_action_ratio": 0.0,
  "local_action_count": 5,
  "non_terminal_transition_count": 5,
  "pending_at_horizon_count": 1,
  "pending_at_horizon_ratio": 0.2,
  "probe_episode_count": 1,
  "probe_step_count": 5,
  "readiness_block_reason": null,
  "readiness_manual_approval_required": true,
  "readiness_manual_approval_status": "approved",
  "reward_bearing_transition_count": 0,
  "reward_bearing_transition_ratio": 0.0,
  "terminal_transition_count": 0,
  "terminal_transition_ratio": 0.0,
  "transition_count": 5,
  "vertical_action_count": 0
}

## Training Execution Summary
{
  "checkpoint_metadata": {
    "config_hash": "2919d4ad1843ff15eb684044c508d1c21b11375e735fe08b4d3b173a57b34a93",
    "eval_trace_bank_id": "full-training-eval-bank",
    "feature_id": "041-full-training-reproduction-campaign",
    "full_campaign_enabled": false,
    "optimizer_step_count": 37,
    "replay_size": 100,
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
    "stage": "pilot_training",
    "target_update_unit": "optimizer_step",
    "train_trace_bank_id": "full-training-train-bank"
  },
  "checkpoint_schema_valid": true,
  "delayed_reward_contract_preserved": true,
  "episodes_completed": 10,
  "episodes_requested": 10,
  "evaluation_summary": {
    "candidate_reproduction_supported": false,
    "completed_task_count": 0,
    "dropped_task_count": 0,
    "evaluation_episode_count": 3,
    "evaluation_on_training_traces": false,
    "mean_reward": 0.0,
    "reward_bearing_transition_count": 0,
    "terminal_transition_count": 0,
    "trace_bank_disjoint": true,
    "trace_bank_ids": {
      "evaluation": "full-training-eval-bank",
      "training": "full-training-train-bank"
    },
    "trace_ids": [
      "hoodie-43",
      "hoodie-44",
      "hoodie-45"
    ]
  },
  "full_campaign_block_reason": "full campaign not requested during pilot",
  "full_campaign_executed": false,
  "legal_action_only": true,
  "loss_is_finite": true,
  "loss_value": 4.02426394430222e-07,
  "optimizer_step_count": 37,
  "pending_at_horizon_preserved": true,
  "replay_size": 100,
  "stage": "pilot_training",
  "target_sync_count": 0,
  "train_eval_trace_banks_disjoint": true
}

## Evaluation Summary
{
  "candidate_reproduction_supported": false,
  "completed_task_count": 0,
  "dropped_task_count": 0,
  "evaluation_episode_count": 3,
  "evaluation_on_training_traces": false,
  "mean_reward": 0.0,
  "reward_bearing_transition_count": 0,
  "terminal_transition_count": 0,
  "trace_bank_disjoint": true,
  "trace_bank_ids": {
    "evaluation": "full-training-eval-bank",
    "training": "full-training-train-bank"
  },
  "trace_ids": [
    "hoodie-43",
    "hoodie-44",
    "hoodie-45"
  ]
}

## Baseline Reference Summary
{
  "mutated": false,
  "reference_artifacts": [
    "artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.json",
    "artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.md"
  ],
  "reference_only": true,
  "rerun_requested": false
}

## Reproduction Claim Status
{
  "automatic_claim": false,
  "candidate_reproduction_supported": false,
  "status": "no_claim"
}
