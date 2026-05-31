# Data Model: Feature 073

## ControlledEvaluationScenario

Fields:

- `scenario_id`
- `name`
- `description`
- `tasks`
- `expected_metrics`
- `actual_metrics`
- `paper_mode_only`
- `passed`

Validation:

- Scenario ID must be unique.
- Scenario must contain at least one task/event.
- Compatibility mode must be false by default.
- Expected and actual metrics must be comparable.

## ControlledEvaluationTaskRecord

Fields:

- `task_id`
- `source_agent_id`
- `action_type`
- `destination_agent_id`
- `arrival_slot`
- `phi`
- `completion_slot`
- `terminal_status`
- `reward_value`
- `delay`
- `illegal_action_rejected`
- `compatibility_mode_used`

Validation:

- Terminal status must be explicit.
- Compatibility mode must not be used in default batch scenarios.
- Illegal horizontal destinations must be counted.

## ControlledEvaluationMetrics

Fields:

- `completed_count`
- `dropped_timeout_count`
- `dropped_unavailable_count`
- `deadline_violation_count`
- `illegal_action_rejection_count`
- `average_delay`
- `average_reward`
- `paper_mode_success_count`
- `compatibility_mode_used`

Validation:

- Counts must be non-negative.
- Average delay and reward must be deterministic for each scenario.
- `compatibility_mode_used` must be false for default readiness batch.

## ControlledEvaluationBatchReport

Fields:

- `feature_name`
- `status`
- `passed`
- `changed_files`
- `scenarios`
- `aggregate_metrics`
- `feature_068r_regression_status`
- `feature_069_regression_status`
- `feature_070_regression_status`
- `feature_071_regression_status`
- `feature_072_regression_status`
- `paper_claim_boundary`
- `recommended_next_feature`

Validation:

- Report passes only if all scenarios pass and all prior regressions pass.
- Compatibility mode usage must be false in the default batch.
- No final evaluation or full paper reproduction claim is allowed.
