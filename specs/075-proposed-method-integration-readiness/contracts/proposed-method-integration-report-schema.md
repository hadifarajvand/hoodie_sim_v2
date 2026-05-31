# Contract: Feature 075 Proposed Method Integration Report Schema

## Required Fields

- `feature_name`: must be `Feature 075 - Proposed Method Integration Readiness`.
- `status`: proposed-method readiness status.
- `passed`: final pass/fail value.
- `changed_files`: changed file list.
- `proposed_method_descriptor`: proposed method contract descriptor.
- `scenario_evaluations`: per-scenario proposed-method rows.
- `policy_aggregate_metrics`: aggregate proposed-method metrics.
- `feature_068r_regression_status`: Feature 068R targeted gate.
- `feature_069_regression_status`: Feature 069 targeted gate.
- `feature_070_regression_status`: Feature 070 targeted gate.
- `feature_071_regression_status`: Feature 071 targeted gate.
- `feature_072_regression_status`: Feature 072 targeted gate.
- `feature_073_regression_status`: Feature 073 targeted gate.
- `feature_074_regression_status`: Feature 074 targeted gate.
- `paper_claim_boundary`: explicit claim boundary.
- `recommended_next_feature`: expected next feature.

## Proposed Method Identity

The proposed method must be represented as:

- `policy_id`: `PROPOSED_DCQ`
- `policy_family`: `proposed_deadline_queueing`

## Scenario Rule

Every required scenario must have exactly one evaluation row.

Each row must expose:

- `selected_action_id`
- `selected_action_family`
- `candidate_ranking_trace_present`
- `deadline_slack_evidence_present`
- `queue_or_load_evidence_present`
- `topology_legality_enforced`
- `action_bound_terminal_status`
- `action_bound_reward_value`
- `action_bound_metrics_derived`
- `compatibility_mode_used`

## Action-Bound Rule

The proposed method must not merely attach Feature 073 scenario metrics unchanged. It must bind the selected action to the terminal status, reward, and metrics through controlled-outcome evidence.

## Pass Rule

The report may have `passed=True` only if:

- all required scenarios are evaluated
- every passing row has a selected action
- candidate ranking trace evidence exists
- deadline slack evidence exists
- queue/load evidence exists
- topology legality is enforced for horizontal candidates
- action-bound metrics are derived
- compatibility mode is excluded
- Feature 068R through Feature 074 regressions pass
- no final evaluation claim is made
- no training claim is made
- no superiority claim is made
- no full paper reproduction claim is made

## Claim Boundary Rule

The report may claim proposed-method integration readiness only. It must not claim final evaluation, policy superiority, statistical significance, training correctness, or full HOODIE reproduction.
