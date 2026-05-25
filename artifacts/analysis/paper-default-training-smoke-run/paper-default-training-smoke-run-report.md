# Paper-Default Training Smoke Run Report

- feature_id: `055-paper-default-training-smoke-run`
- final_verdict: `paper_default_training_smoke_passed`
- recommended_next_feature: `Feature 056 — Target Update and Replay Training Validation`
- feature_054_readiness_verified: `True`
- live_environment_training_used: `True`
- fixture_training_used: `False`

## Smoke Scope
{
  "baseline_comparison": false,
  "full_campaign": false,
  "paper_reproduction_claim": false,
  "smoke_episode_length": 110,
  "smoke_episodes": 1
}

## Replay Summary
{
  "pending_at_horizon_preserved": true,
  "replay_inserted": true,
  "replay_size": 110
}

## Optimizer Step Summary
{
  "optimizer_step_count": 47,
  "optimizer_steps_executed": true,
  "target_sync_count": 0
}

## Loss Summary
{
  "loss_is_finite": true,
  "loss_value": 25.033153533935547
}

## Checkpoint Summary
{
  "checkpoint_schema_valid": true,
  "metadata_only": true,
  "model_checkpoint_written": false
}

## Legal Action Summary
{
  "legal_action_only": true
}

## Delayed Reward Contract
{
  "delayed_reward_contract_preserved": true,
  "pending_at_horizon_preserved": true
}

## Train/Eval Contract
{
  "evaluation_on_training_traces": false,
  "trace_bank_ids": {
    "evaluation": "full-training-eval-bank",
    "training": "full-training-train-bank"
  },
  "train_eval_trace_banks_disjoint": true
}

## Behavior Safety Summary
{
  "no_baseline_comparison": true,
  "no_dependency_drift": true,
  "no_environment_contract_drift": true,
  "no_full_campaign": true,
  "no_paper_reproduction_claim": true,
  "no_policy_drift": true
}

## Remaining Blockers
[]