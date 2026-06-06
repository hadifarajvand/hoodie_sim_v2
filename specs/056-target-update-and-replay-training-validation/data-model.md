# Data Model: Feature 056

## TargetUpdateReplayValidationReport

Represents the complete validation outcome.

Fields:

- `feature_id`: constant `056-target-update-and-replay-training-validation`
- `prerequisite_tags_verified`: list of prerequisite gate checks
- `feature_055_smoke_verified`: boolean
- `replay_insertion_validated`: boolean
- `replay_sampling_validated`: boolean
- `optimizer_step_counter_validated`: boolean
- `target_update_contract_validated`: boolean
- `target_sync_schedule_validated`: boolean
- `target_sync_before_threshold_blocked`: boolean
- `target_sync_at_threshold_validated`: boolean
- `checkpoint_metadata_validated`: boolean
- `replay_summary`: replay metrics and sample schema evidence
- `optimizer_step_summary`: optimizer counter and monotonicity evidence
- `target_update_summary`: target unit/frequency/sync-threshold evidence
- `checkpoint_metadata_summary`: checkpoint metadata schema evidence
- `behavior_safety_summary`: no-drift/no-campaign/no-claim evidence
- `remaining_blockers`: exact blocker list
- `recommended_next_feature`: next routed feature
- `final_verdict`: final status

## ReplaySummary

Must prove replay insertion and replay sampling are available without fabricating terminal rewards.

Expected evidence:

- replay size from Feature 055 is positive
- sampled batch size is positive
- sampled fields include state, action, legal mask, next state, reward, terminal, reward availability, and pending-at-horizon
- delayed reward semantics remain intact

## TargetUpdateSummary

Must prove the approved target-update contract:

- target update unit: `optimizer_step`
- update frequency: `2000`
- no target sync before threshold
- exactly one target sync at threshold in deterministic validation

## CheckpointMetadataSummary

Must prove checkpoint metadata includes:

- target update unit
- optimizer step count
- replay size
- config hash
- training trace bank ID
- evaluation trace bank ID
- seed bundle

## BehaviorSafetySummary

Must prove no forbidden work occurred:

- no full campaign
- no baseline comparison
- no paper reproduction claim
- no policy drift
- no dependency drift
- no environment contract drift
- no reward timing change
- no prior artifact rewrite
