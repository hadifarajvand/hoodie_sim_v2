# Paper-Default Pilot Training Run Report

- feature_id: `057-paper-default-pilot-training-run`
- final_verdict: `feature_056_prerequisite_blocked`
- recommended_next_feature: `Feature 056 validation repair before pilot training`
- feature_056_validation_verified: `False`
- live_environment_training_used: `False`
- fixture_training_used: `False`

## Pilot Scope
{
  "baseline_comparison": false,
  "full_campaign": false,
  "paper_reproduction_claim": false,
  "pilot_episode_length": 110,
  "pilot_episodes": 3
}

## Episode Summary
{
  "completed_all_episodes": false,
  "episodes_completed": 0,
  "episodes_requested": 3,
  "pilot_episode_length": 110,
  "pilot_episodes": 3,
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
  "seed_signature": "probe=31|train=41|eval=43|replay=47|model=19|explore=53|python=59|torch=61"
}

## Replay Summary
{
  "delayed_reward_semantics_preserved": false,
  "feature_055_smoke_replay_size": 0,
  "pending_at_horizon_preserved": false,
  "replay_growth_count": 0,
  "replay_growth_validated": false,
  "replay_inserted": false,
  "replay_size": 0,
  "reward_available_count": 0,
  "sample_transitions": [],
  "sampled_batch_size": 0,
  "sampled_field_coverage": {
    "action": false,
    "legal_action_mask": false,
    "next_state": false,
    "pending_at_horizon": false,
    "reward": false,
    "reward_available": false,
    "state": false,
    "terminal": false
  },
  "sampled_transition_count": 0
}

## Optimizer Summary
{
  "feature_055_smoke_optimizer_step_count": 0,
  "optimizer_progress_validated": false,
  "optimizer_step_count": 0,
  "optimizer_step_growth_count": 0,
  "optimizer_step_monotonic": false,
  "optimizer_steps_executed": false,
  "target_sync_count": 0
}

## Target Update Summary
{
  "target_sync_at_threshold_validated": false,
  "target_sync_before_threshold_blocked": false,
  "target_sync_count": 0,
  "target_update_contract_validated": false,
  "target_update_frequency": 2000,
  "target_update_schedule_within_pilot": true,
  "target_update_unit": "optimizer_step"
}

## Loss Summary
{
  "all_losses_finite": false,
  "loss_count": 0,
  "loss_values": [],
  "max_loss": null,
  "mean_loss": null,
  "min_loss": null
}

## Reward Summary
{
  "delayed_reward_contract_preserved": false,
  "mean_reward": 0.0,
  "pending_at_horizon_preserved": false,
  "reward_available_count": 0,
  "reward_count": 0,
  "total_reward": 0.0
}

## Legal Action Summary
{
  "illegal_action_count": 0,
  "legal_action_only": false
}

## Checkpoint Summary
{
  "checkpoint_metadata": {},
  "checkpoint_schema_valid": false,
  "keys_present": {
    "config_hash": false,
    "eval_trace_bank_id": false,
    "optimizer_step_count": false,
    "replay_size": false,
    "seed_bundle": false,
    "target_update_unit": false,
    "train_trace_bank_id": false
  },
  "metadata_only": true,
  "model_checkpoint_written": false
}

## Train/Eval Contract
{
  "candidate_reproduction_supported": false,
  "evaluation_on_training_traces": false,
  "trace_bank_ids": {
    "evaluation": "full-training-eval-bank",
    "training": "full-training-train-bank"
  },
  "train_eval_trace_banks_disjoint": false
}

## Behavior Safety Summary
{
  "no_baseline_comparison": true,
  "no_dependency_drift": false,
  "no_environment_contract_drift": true,
  "no_full_campaign": true,
  "no_paper_reproduction_claim": true,
  "no_performance_claim": true,
  "no_policy_drift": false,
  "no_prior_artifact_rewrite": false,
  "no_reward_timing_change": true
}

## Remaining Blockers
[
  "feature_056_validation_failed",
  "prerequisite_tags_failed"
]