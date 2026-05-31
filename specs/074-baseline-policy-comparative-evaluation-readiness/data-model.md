# Data Model: Feature 074

## BaselinePolicyDescriptor

Fields:

- `policy_id`
- `policy_family`
- `registry_key`
- `available`
- `decision_trace_supported`

Validation:

- Every required baseline policy must have a descriptor.
- Missing policies block readiness.

## PolicyScenarioComparison

Fields:

- `policy_id`
- `scenario_id`
- `policy_action_family`
- `policy_decision_trace_present`
- `metrics`
- `compatibility_mode_used`
- `passed`

Validation:

- Scenario IDs must come from Feature 073.
- Metrics must be comparable across policies.
- Compatibility mode must be false in the default comparison.

## PolicyAggregateComparison

Fields:

- `policy_id`
- `scenario_count`
- `completed_count`
- `dropped_timeout_count`
- `dropped_unavailable_count`
- `deadline_violation_count`
- `illegal_action_rejection_count`
- `mean_delay`
- `mean_reward`
- `compatibility_mode_used`

Validation:

- Scenario count must match the number of controlled scenarios.
- Aggregate metrics must be computed from scenario metrics.

## BaselineComparativeReadinessReport

Fields:

- `feature_name`
- `status`
- `passed`
- `changed_files`
- `policy_descriptors`
- `scenario_comparisons`
- `policy_aggregate_metrics`
- `feature_068r_regression_status`
- `feature_069_regression_status`
- `feature_070_regression_status`
- `feature_071_regression_status`
- `feature_072_regression_status`
- `feature_073_regression_status`
- `paper_claim_boundary`
- `recommended_next_feature`

Validation:

- Report passes only if all required policies are available, all comparisons pass, all aggregate metrics match scenario metrics, all prior regressions pass, and no overclaim is made.
