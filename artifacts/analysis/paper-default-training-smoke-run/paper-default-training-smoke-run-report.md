# Paper-Default Training Smoke Run Report

- feature_id: `055-paper-default-training-smoke-run`
- final_verdict: `paper_default_training_smoke_blocked`
- recommended_next_feature: `paper-default training smoke repair`
- feature_054_readiness_verified: `False`
- live_environment_training_used: `False`
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
  "pending_at_horizon_preserved": false,
  "replay_inserted": false,
  "replay_size": 0
}

## Optimizer Step Summary
{
  "optimizer_step_count": 0,
  "optimizer_steps_executed": false,
  "target_sync_count": 0
}

## Loss Summary
{
  "loss_is_finite": false,
  "loss_value": null
}

## Checkpoint Summary
{
  "checkpoint_schema_valid": false,
  "metadata_only": true,
  "model_checkpoint_written": false
}

## Legal Action Summary
{
  "legal_action_only": false
}

## Delayed Reward Contract
{
  "delayed_reward_contract_preserved": false,
  "pending_at_horizon_preserved": false
}

## Train/Eval Contract
{
  "evaluation_on_training_traces": false,
  "trace_bank_ids": {},
  "train_eval_trace_banks_disjoint": false
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
[
  "feature_054_readiness_failed",
  "prerequisite_tags_failed"
]