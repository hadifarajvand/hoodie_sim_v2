# Data Model: Feature 075

## ProposedMethodDescriptor

Fields:

- `policy_id`
- `policy_family`
- `registry_key`
- `available`
- `decision_trace_supported`

Validation:

- `policy_id` must be `PROPOSED_DCQ`.
- `policy_family` must be `proposed_deadline_queueing`.
- The proposed method must be available in readiness mode.

## ProposedMethodCandidate

Fields:

- `action_id`
- `action_family`
- `legal`
- `estimated_delay`
- `deadline_slack`
- `queue_or_load_value`
- `reward_risk_value`
- `ranking_score`
- `selected`

Validation:

- Candidate evidence must be explicit and deterministic.
- Horizontal candidates must record topology legality.
- Illegal candidates must not be selected in passing rows.

## ProposedMethodScenarioEvaluation

Fields:

- `scenario_id`
- `candidate_evidence`
- `candidate_ranking_trace`
- `candidate_ranking_trace_present`
- `deadline_slack_evidence_present`
- `queue_or_load_evidence_present`
- `topology_legality_enforced`
- `selected_action_id`
- `selected_action_family`
- `action_bound_terminal_status`
- `action_bound_reward_value`
- `action_bound_metrics_derived`
- `metrics`
- `compatibility_mode_used`
- `passed`

Validation:

- Every required scenario must have one evaluation row.
- Passing rows must have selected action evidence and derived metrics.
- Passing rows must not use compatibility mode.
- Candidate ranking, deadline slack, and queue/load evidence must be present.

## ProposedMethodAggregateComparison

Fields:

- `policy_id`
- `policy_family`
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
- `candidate_ranking_trace_present`
- `deadline_slack_evidence_present`
- `queue_or_load_evidence_present`
- `topology_legality_enforced`
- `action_bound_metrics_derived`

Validation:

- Scenario count must equal 7.
- Aggregate metrics must be computed from scenario rows.
- Candidate and evidence flags must be true when all scenario rows satisfy the action-bound contract.

## ProposedMethodIntegrationReadinessReport

Fields:

- `feature_name`
- `status`
- `passed`
- `changed_files`
- `proposed_method_descriptor`
- `scenario_evaluations`
- `policy_aggregate_metrics`
- `feature_068r_regression_status`
- `feature_069_regression_status`
- `feature_070_regression_status`
- `feature_071_regression_status`
- `feature_072_regression_status`
- `feature_073_regression_status`
- `feature_074_regression_status`
- `paper_claim_boundary`
- `recommended_next_feature`

Validation:

- Report passes only if all required scenarios are evaluated, selected actions exist for every passing scenario, candidate ranking traces exist, deadline slack evidence exists, topology legality is enforced, action-bound metrics are derived, compatibility mode is excluded, and Feature 068R through Feature 074 regressions pass.
