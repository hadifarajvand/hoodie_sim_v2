# Feature 076 Data Model

## Overview

Feature 076 defines a read-only data model for combining baseline policy comparison rows from Feature 074 and proposed-method rows from Feature 075 into one readiness matrix.

## CombinedPolicyRow

Represents one policy or method on one controlled scenario.

Required fields:

- policy_id
- policy_family
- scenario_id
- selected_action_id
- selected_action_family
- action_legality
- action_bound_terminal_status
- action_bound_reward_value
- action_bound_metrics_derived
- compatibility_mode_used
- decision_trace_present
- completed_count
- dropped_timeout_count
- dropped_unavailable_count
- deadline_violation_count
- illegal_action_rejection_count
- average_delay
- average_reward
- source_feature
- source_report_status

Validation rules:

- policy_id must be non-empty.
- policy_family must be non-empty.
- scenario_id must be one of the seven required controlled scenarios.
- selected_action_id must be non-empty.
- selected_action_family must be non-empty.
- action_bound_metrics_derived must be true for passing readiness.
- compatibility_mode_used must be false for passing readiness.
- decision_trace_present must be true for passing readiness.
- Count metrics must be non-negative integers.
- source_feature must be either Feature 074 or Feature 075.

## CombinedPolicyAggregate

Represents per-policy or per-method aggregate metrics across the required seven scenarios.

Required fields:

- policy_id
- policy_family
- scenario_count
- completed_count
- dropped_timeout_count
- dropped_unavailable_count
- deadline_violation_count
- illegal_action_rejection_count
- mean_delay
- mean_reward
- all_rows_action_bound
- compatibility_mode_used
- decision_trace_present

Validation rules:

- scenario_count must equal 7.
- all_rows_action_bound must be true.
- compatibility_mode_used must be false.
- decision_trace_present must be true.
- Aggregate counts must equal the sum of row-level counts for the same policy or method.
- mean_delay and mean_reward are descriptive readiness metrics only, not superiority evidence.

## CombinedRegressionEvidence

Represents targeted regression status for upstream features.

Required fields:

- feature_id
- status
- passed
- command_hint
- scope

Required feature IDs:

- 068R
- 069
- 070
- 071
- 072
- 073
- 074
- 075

Validation rules:

- All required feature IDs must be present.
- All required entries must have passed=true for Feature 076 readiness.

## CombinedComparativeReadinessReport

Top-level report entity.

Required fields:

- status
- passed
- rows
- aggregates
- regression_evidence
- required_policy_ids
- required_scenario_ids
- claim_boundary
- scope_evidence
- source_features

Ready status:

- combined_baseline_proposed_comparative_readiness_ready

Validation rules:

- rows must contain exactly 49 rows.
- Required policy IDs must be exactly FLC, VO, HO, RO, BCO, MLEO, and PROPOSED_DCQ.
- Required scenario IDs must be exactly the seven controlled scenario IDs from Feature 073.
- Every required policy or method must have every required scenario exactly once.
- Every row must be action-bound.
- No row may use compatibility mode.
- Every row must expose decision trace evidence.
- Aggregate count must equal 7.
- All upstream regression evidence must pass.
- claim_boundary must explicitly include no training claim, no superiority claim, no final evaluation claim, no statistical significance claim, and no full paper reproduction claim.

## Invalid States

The report must reject or fail readiness if:

- any required policy or method is missing
- any scenario is missing for any policy or method
- duplicate policy/scenario rows exist
- any selected action is empty
- any row lacks action-bound metrics
- compatibility mode is used
- decision trace is missing
- any upstream regression evidence is missing or failed
- claim boundaries are absent

## Non-Goals

This model must not represent training weights, replay buffers, optimizer state, stochastic campaign outputs, significance tests, winner declarations, plot artifacts, or full HOODIE reproduction claims.
