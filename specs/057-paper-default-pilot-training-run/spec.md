# Feature 057 — Paper-Default Pilot Training Run

## Purpose

Run the first controlled paper-default pilot training run after Feature 056 validated replay sampling, optimizer-step counting, target-update contract behavior, and checkpoint metadata.

## Problem

Feature 055 proved the paper-default live training smoke path can populate replay and execute optimizer steps. Feature 056 proved replay sampling and the target-update schedule are valid. The project still needs a small real pilot run that is larger than a smoke test but explicitly smaller than a full campaign.

This feature must prove the training loop remains mechanically sane over multiple paper-default episodes without claiming paper reproduction or running a full scenario campaign.

## Required prior inputs

- `artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.json`
- `artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.json`
- `artifacts/analysis/training-readiness-contract/training-readiness-contract-report.json`

## Required output artifacts

- `artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.json`
- `artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.md`

## Required report decisions

The report must decide whether a controlled paper-default pilot training run is valid enough to proceed to an evaluation-trace-bank and baseline-evaluation harness.

Required top-level fields:

- `feature_id`
- `prerequisite_tags_verified`
- `feature_056_validation_verified`
- `pilot_scope`
- `live_environment_training_used`
- `fixture_training_used`
- `episode_summary`
- `replay_summary`
- `optimizer_summary`
- `target_update_summary`
- `loss_summary`
- `reward_summary`
- `legal_action_summary`
- `checkpoint_summary`
- `train_eval_contract_verified`
- `behavior_safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Required passing behavior

Passing verdict requires:

- Feature 056 final verdict is `target_update_replay_validation_passed`
- live environment training is used
- fixture-only training is not used
- pilot episode count is greater than the Feature 055 smoke count
- replay grows beyond Feature 055 smoke replay size
- optimizer steps increase beyond Feature 055 smoke optimizer count
- losses are finite
- selected actions are legal
- delayed reward contract remains preserved
- train/eval trace banks remain disjoint
- checkpoint metadata is valid
- no full campaign is run
- no baseline comparison is made
- no paper reproduction or performance claim is made

## Allowed final verdicts

- `paper_default_pilot_training_passed`
- `feature_056_prerequisite_blocked`
- `pilot_scope_blocked`
- `replay_growth_blocked`
- `optimizer_progress_blocked`
- `loss_or_reward_blocked`
- `legal_action_blocked`
- `checkpoint_metadata_blocked`
- `behavior_drift_detected`

## Routing

If all gates pass:

- `final_verdict = paper_default_pilot_training_passed`
- `recommended_next_feature = Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness`
- `remaining_blockers = []`

If any gate fails, `remaining_blockers` must name the exact failed gate and `recommended_next_feature` must route to the exact repair, not Feature 058.

## Hard scope

Allowed:

- controlled multi-episode paper-default pilot training
- replay, optimizer, loss, reward, legal-action, target-update, checkpoint metadata reporting
- metadata-only checkpoint evidence unless implementation already has a safe scoped checkpoint mechanism

Forbidden:

- full campaign execution
- baseline comparison claim
- paper reproduction claim
- performance claim
- policy drift
- dependency drift
- environment semantic changes
- reward timing changes
- prior Feature 037–056 artifact rewrites
- `.specify/feature.json` committed diff
- `AGENTS.md` rewrite
