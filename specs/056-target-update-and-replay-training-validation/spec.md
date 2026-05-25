# Feature 056 — Target Update and Replay Training Validation

## Purpose

Validate the paper-default replay and target-update mechanics after Feature 055 proved the live paper-default smoke run can populate replay and execute optimizer steps.

## Problem

Feature 055 passed the live training smoke path, but it reported `target_sync_count = 0`. That is expected for a one-episode smoke run because the approved target update frequency is 2000 optimizer steps. The repository still needs a dedicated validation feature proving that replay insertion, replay sampling, optimizer-step counting, and target-network synchronization obey the approved training contract.

## Required prior input

- `artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.json`
- `artifacts/analysis/training-readiness-contract/training-readiness-contract-report.json`
- Existing campaign trainer/replay/target-update implementation under `src/analysis/full_training_reproduction_campaign/`

## Required output artifacts

- `artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.json`
- `artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.md`

## Required report decisions

The report must decide whether replay and target-update mechanics are valid enough to proceed to a pilot training run.

Required top-level fields:

- `feature_id`
- `prerequisite_tags_verified`
- `feature_055_smoke_verified`
- `replay_insertion_validated`
- `replay_sampling_validated`
- `optimizer_step_counter_validated`
- `target_update_contract_validated`
- `target_sync_schedule_validated`
- `target_sync_before_threshold_blocked`
- `target_sync_at_threshold_validated`
- `checkpoint_metadata_validated`
- `behavior_safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Allowed final verdicts

- `target_update_replay_validation_passed`
- `feature_055_prerequisite_blocked`
- `replay_insertion_blocked`
- `replay_sampling_blocked`
- `optimizer_step_counter_blocked`
- `target_update_contract_blocked`
- `checkpoint_metadata_blocked`
- `behavior_drift_detected`

## Routing

If all gates pass:

- `final_verdict = target_update_replay_validation_passed`
- `recommended_next_feature = Feature 057 — Paper-Default Pilot Training Run`
- `remaining_blockers = []`

If any gate fails, the verdict must name the failing category and `recommended_next_feature` must route to the exact repair area, not to Feature 057.

## Hard scope

This is a validation feature, not a full campaign.

Allowed:

- controlled replay/target-update validation
- deterministic threshold simulation or minimal trainer-driven validation
- report artifacts and tests

Forbidden:

- full campaign execution
- paper reproduction claim
- baseline comparison claim
- policy drift
- dependency drift
- environment semantic changes
- reward timing changes
- prior Feature 037–055 artifact rewrites
- `.specify/feature.json` committed diff
- `AGENTS.md` rewrite
