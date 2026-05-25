# Data Model: Feature 057

## PaperDefaultPilotTrainingRunReport

Represents the complete pilot-run validation outcome.

Fields:

- `feature_id`: constant `057-paper-default-pilot-training-run`
- `prerequisite_tags_verified`: list of prerequisite checks
- `feature_056_validation_verified`: boolean
- `pilot_scope`: controlled pilot scope and anti-campaign flags
- `live_environment_training_used`: boolean
- `fixture_training_used`: boolean
- `episode_summary`: episode count, length, completion status, and deterministic seed evidence
- `replay_summary`: replay growth and sample availability evidence
- `optimizer_summary`: optimizer-step growth and finite training-step evidence
- `target_update_summary`: target sync count and threshold metadata
- `loss_summary`: finite loss evidence across pilot steps
- `reward_summary`: reward-bearing transition and delayed reward contract evidence
- `legal_action_summary`: legal selected-action evidence
- `checkpoint_summary`: checkpoint metadata schema evidence
- `train_eval_contract_verified`: trace-bank separation evidence
- `behavior_safety_summary`: no-drift/no-claim/no-campaign evidence
- `remaining_blockers`: exact blocker list
- `recommended_next_feature`: next routed feature
- `final_verdict`: final status

## PilotScope

Defines the controlled pilot run. It must be larger than Feature 055 smoke and smaller than a full campaign.

Expected defaults:

- `pilot_episodes = 3`
- `pilot_episode_length = 110`
- `full_campaign = false`
- `baseline_comparison = false`
- `paper_reproduction_claim = false`

## ReplaySummary

Must prove replay grew beyond Feature 055:

- `feature_055_smoke_replay_size`
- `replay_size`
- `replay_growth_count`
- `replay_growth_validated`
- `sampled_batch_size`

## OptimizerSummary

Must prove optimizer progress grew beyond Feature 055:

- `feature_055_smoke_optimizer_step_count`
- `optimizer_step_count`
- `optimizer_step_growth_count`
- `optimizer_progress_validated`

## LossSummary

Must prove losses remain finite:

- `loss_count`
- `all_losses_finite`
- `min_loss`
- `max_loss`
- `mean_loss`

## RewardSummary

Must prove reward handling remains sane and delayed reward contract is preserved:

- `reward_count`
- `reward_available_count`
- `delayed_reward_contract_preserved`
- `pending_at_horizon_preserved`

## BehaviorSafetySummary

Must prove:

- no full campaign
- no baseline comparison
- no paper reproduction claim
- no performance claim
- no policy drift
- no dependency drift
- no environment contract drift
- no reward timing change
- no prior artifact rewrite
