# Feature 076 Contract: Combined Comparative Report Schema

## Purpose

This contract defines the required schema and pass rules for Feature 076. The report combines Feature 074 baseline policy comparison rows and Feature 075 proposed-method rows into one controlled, action-bound readiness matrix.

This contract is not a final evaluation contract. It must not rank methods or claim superiority.

## Required Report Identity

The report must expose:

- `feature_name`: `Feature 076 - Combined Baseline + Proposed Comparative Readiness`
- `status`: `combined_baseline_proposed_comparative_readiness_ready` when ready
- `passed`: boolean
- `source_features`: Feature 074 and Feature 075

## Required Policy / Method Coverage

The combined report must include exactly these IDs:

- FLC
- VO
- HO
- RO
- BCO
- MLEO
- PROPOSED_DCQ

Readiness must fail if any ID is missing.

## Required Scenario Coverage

Every policy/method must contain exactly one row for every scenario:

- `light_load_no_deadline_pressure`
- `tight_deadline_pressure`
- `legal_horizontal_offload`
- `illegal_horizontal_destination_attempt`
- `cloud_vertical_fallback`
- `timeout_drop_case`
- `mixed_local_horizontal_cloud_candidates`

Expected matrix size:

- 7 policies/methods
- 7 scenarios
- 49 rows total

Readiness must fail if rows are missing or duplicated.

## Required Row Fields

Each normalized combined row must include:

- `policy_id`
- `policy_family`
- `scenario_id`
- `selected_action_id`
- `selected_action_family`
- `action_legality`
- `action_bound_terminal_status`
- `action_bound_reward_value`
- `action_bound_metrics_derived`
- `compatibility_mode_used`
- `decision_trace_present`
- `completed_count`
- `dropped_timeout_count`
- `dropped_unavailable_count`
- `deadline_violation_count`
- `illegal_action_rejection_count`
- `average_delay`
- `average_reward`
- `source_feature`
- `source_report_status`

## Row Pass Rules

A row is readiness-valid only if:

- selected action id is present
- selected action family is present
- action-bound terminal status is present
- action-bound reward value is present when the source row has terminal reward
- action-bound metrics are derived
- compatibility mode is false
- decision trace is present
- count metrics are non-negative
- source feature is either Feature 074 or Feature 075

## Required Aggregate Fields

Each aggregate row must include:

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
- `all_rows_action_bound`
- `compatibility_mode_used`
- `decision_trace_present`

## Aggregate Pass Rules

An aggregate is readiness-valid only if:

- scenario count equals 7
- aggregate counts equal sums from the normalized rows
- mean delay and mean reward are computed from row averages
- all rows are action-bound
- compatibility mode is false
- decision trace is present for all rows

## Required Regression Evidence

The report must include targeted regression evidence for:

- 068R
- 069
- 070
- 071
- 072
- 073
- 074
- 075

Report readiness must fail if any regression evidence is missing or failed.

## Required Claim Boundary

The rendered report and structured report must explicitly state:

- no training claim
- no superiority claim
- no final evaluation claim
- no statistical significance claim
- no full paper reproduction claim

## Pass Rule

The report may set `passed=True` only when:

- all 49 rows are present
- every required policy/method is present
- every required scenario is present for every policy/method
- every row is action-bound
- no row uses compatibility mode
- every row has decision trace evidence
- all aggregates match row-level metrics
- all upstream regressions pass
- claim boundaries are explicit
- scope guard passes

## Forbidden Claims

The report must not include:

- winner declaration
- best-policy ranking
- statistical significance claim
- final experiment claim
- training correctness claim
- full HOODIE reproduction claim
