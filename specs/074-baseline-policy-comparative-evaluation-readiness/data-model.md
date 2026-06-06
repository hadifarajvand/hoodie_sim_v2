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
- `decision_trace`
- `selected_action_id`
- `selected_action_family`
- `action_legality`
- `action_bound_terminal_status`
- `action_bound_reward_value`
- `action_bound_metrics_derived`
- `metrics`
- `compatibility_mode_used`
- `passed`

Validation:

- Scenario IDs must come from Feature 073.
- Metrics must be comparable across policies.
- Compatibility mode must be false in the default comparison.
- Selected action fields must be present for passing rows.
- Passing rows must derive metrics from the selected action-bound outcome.
- A row must fail if the selected action cannot be mapped to local, horizontal, vertical/cloud, or unavailable outcome semantics.

## PolicyActionBoundOutcome

Fields:

- `policy_id`
- `scenario_id`
- `selected_action_id`
- `selected_action_family`
- `action_legality`
- `terminal_status`
- `reward_value`
- `delay`
- `metrics`
- `evidence_source`

Validation:

- The selected action must be the direct source of terminal status and reward.
- Horizontal action legality must be computed from Figure 7 topology.
- Local and cloud actions must use Feature 071 paper-mode deadline and reward helpers.
- Illegal or unavailable action must produce dropped-unavailable metrics.

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
- `distinct_selected_action_families`
- `action_bound_metrics_derived`

Validation:

- Scenario count must match the number of controlled scenarios.
- Aggregate metrics must be computed from scenario metrics.
- Aggregate action families must be computed from scenario selected action families.
- `action_bound_metrics_derived` must be true only if all policy scenario rows derive metrics from selected actions.

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

- Report passes only if all required policies are available, all comparisons pass, all aggregate metrics match scenario metrics, all action-bound metrics are derived from selected actions, all prior regressions pass, and no overclaim is made.
