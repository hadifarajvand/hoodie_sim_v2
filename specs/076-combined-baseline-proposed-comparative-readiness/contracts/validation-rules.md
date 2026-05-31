# Feature 076 Contract: Validation Rules

## Purpose

This file defines the validation rules that implementation must enforce for Feature 076. These rules are binding for the report model, report builder, renderer, tests, and scope guard.

## Upstream Readiness Rules

Feature 076 must consume Feature 074 and Feature 075 reports.

Validation must fail if:

- Feature 074 report is missing.
- Feature 075 report is missing.
- Feature 074 report has `passed=False`.
- Feature 075 report has `passed=False`.
- Feature 074 status is not its readiness status.
- Feature 075 status is not its readiness status.

## Required Policy / Method Coverage

The combined matrix must contain exactly these policy/method IDs:

- FLC
- VO
- HO
- RO
- BCO
- MLEO
- PROPOSED_DCQ

Validation must fail if:

- any required ID is missing
- any unexpected ID is present unless explicitly marked non-comparative and excluded from readiness
- any policy/scenario pair is duplicated

## Required Scenario Coverage

Every policy/method must contain exactly one row for each required scenario:

- light_load_no_deadline_pressure
- tight_deadline_pressure
- legal_horizontal_offload
- illegal_horizontal_destination_attempt
- cloud_vertical_fallback
- timeout_drop_case
- mixed_local_horizontal_cloud_candidates

Validation must fail if:

- any policy/method has fewer than 7 rows
- any policy/method has more than 7 rows
- any required scenario is missing for any policy/method
- any duplicate scenario exists for one policy/method

## Row Validation Rules

Every combined row must satisfy:

- `policy_id` is non-empty
- `policy_family` is non-empty
- `scenario_id` is valid
- `selected_action_id` is non-empty
- `selected_action_family` is non-empty
- `action_legality` is non-empty
- `action_bound_terminal_status` is non-empty
- `action_bound_metrics_derived=True`
- `compatibility_mode_used=False`
- `decision_trace_present=True`
- all count metrics are integers and non-negative
- `source_feature` is either `074` or `075`

Validation must fail if any row violates these rules.

## Aggregate Validation Rules

Each policy/method aggregate must satisfy:

- `scenario_count=7`
- aggregate counts equal row-level sums
- `mean_delay` is computed from row average delays where delay is available
- `mean_reward` is computed from row average rewards where reward is available
- `all_rows_action_bound=True`
- `compatibility_mode_used=False`
- `decision_trace_present=True`

Validation must fail if any aggregate is inconsistent with its rows.

## Regression Evidence Rules

Feature 076 must include regression evidence for:

- 068R
- 069
- 070
- 071
- 072
- 073
- 074
- 075

Validation must fail if:

- any regression entry is missing
- any regression entry has `passed=False`
- the report claims readiness while any upstream gate is not green

## Claim Boundary Rules

Validation must fail if the report omits any of these boundaries:

- no training claim
- no superiority claim
- no final evaluation claim
- no statistical significance claim
- no full paper reproduction claim

## Scope Validation Rules

Allowed paths:

- `specs/076-combined-baseline-proposed-comparative-readiness/**`
- `src/analysis/combined_baseline_proposed_comparative_readiness/**`
- `tests/unit/test_combined_baseline_proposed_comparative_readiness_*.py`
- `tests/integration/test_combined_baseline_proposed_comparative_readiness_*.py`

Forbidden paths:

- `src/environment/**`
- `src/policies/**`
- `src/training/**`
- `src/agents/**`
- `artifacts/**`
- `resources/**`
- dependency files
- lock files
- Feature 077+ paths

## Readiness Pass Rule

Feature 076 may set `passed=True` only if all validation rules above are satisfied.
