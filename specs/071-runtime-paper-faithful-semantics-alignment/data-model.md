# Data Model: Feature 071

## RuntimeMode

Allowed values:

- `paper`
- `compatibility`

Validation:

- Feature 071 tests default to `paper`.
- Compatibility mode must be explicit.

## DeadlineEvidence

Fields:

- `arrival_slot`
- `phi`
- `absolute_deadline_slot`
- `completion_slot`
- `mode`
- `success_before_deadline`
- `terminal_status`
- `runtime_compatibility_note`

Validation:

- `absolute_deadline_slot = arrival_slot + phi - 1`
- paper mode requires `completion_slot < absolute_deadline_slot`
- compatibility mode may allow `completion_slot <= absolute_deadline_slot`

## TerminalStateEvidence

Fields:

- `task_id`
- `terminal_status`
- `terminal_slot`
- `drop_reason`
- `completion_slot`
- `mode`

Validation:

- Completed tasks must not have a drop reason.
- Dropped tasks must have terminal slot and drop reason.
- Pending tasks must not emit reward.

## RewardEquationRuntimeEvidence

Fields:

- `equation_20_implemented`
- `equation_21_implemented`
- `equation_22_implemented`
- `equation_23_implemented`
- `phi_private_example`
- `phi_public_example`
- `success_reward_example`
- `drop_reward_example`
- `inactive_reward_behavior`
- `mode`

Validation:

- Success reward equals `-Phi`.
- Drop reward equals `-C`.
- Inactive task behavior is explicit.
- `Phi_priv = psi_priv - t + 1`.
- `Phi_pub` sums only selected public placement terms.

## RuntimeCompatibilityEvidence

Fields:

- `legacy_behavior_name`
- `paper_behavior_name`
- `divergence_description`
- `compatibility_mode_available`
- `paper_mode_default_in_feature_071`

Validation:

- Runtime divergence must be named, not hidden.
- Compatibility mode must not be the default for Feature 071 tests.

## Feature071Report

Fields:

- `feature_name`
- `status`
- `passed`
- `changed_files`
- `deadline_evidence`
- `terminal_state_evidence`
- `reward_runtime_evidence`
- `compatibility_evidence`
- `feature_068r_regression_status`
- `feature_069_regression_status`
- `feature_070_regression_status`
- `paper_claim_boundary`
- `recommended_next_feature`

Validation:

- Must not claim full paper reproduction.
- Must report paper mode and compatibility mode separately.
- Must show Feature 070 runtime divergence is addressed in paper mode.
