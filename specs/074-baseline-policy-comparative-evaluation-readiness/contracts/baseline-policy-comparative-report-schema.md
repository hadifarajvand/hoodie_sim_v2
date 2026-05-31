# Contract: Feature 074 Baseline Policy Comparative Report Schema

## Required Fields

- `feature_name`: must be `Feature 074 - Baseline Policy Comparative Evaluation Readiness`.
- `status`: comparative readiness status.
- `passed`: final pass/fail value.
- `changed_files`: changed file list.
- `policy_descriptors`: required policy registry coverage.
- `scenario_comparisons`: per-policy, per-scenario comparison rows.
- `policy_aggregate_metrics`: per-policy aggregate metrics.
- `feature_068r_regression_status`: Feature 068R targeted gate.
- `feature_069_regression_status`: Feature 069 targeted gate.
- `feature_070_regression_status`: Feature 070 targeted gate.
- `feature_071_regression_status`: Feature 071 targeted gate.
- `feature_072_regression_status`: Feature 072 targeted gate.
- `feature_073_regression_status`: Feature 073 targeted gate.
- `paper_claim_boundary`: explicit claim boundary.
- `recommended_next_feature`: expected next feature.

## Policy Coverage Rule

Required policies:

- FLC
- VO
- HO
- RO
- BCO
- MLEO

All required policies must be available. Missing policies block readiness.

## Comparison Rule

Every required policy must have a scenario comparison for every Feature 073 controlled scenario.

## Metric Rule

Per-policy scenario and aggregate metrics must expose completion, drop, violation, illegal-action, delay, reward, paper-mode success, compatibility-mode usage, action family, and decision-trace evidence.

## Pass Rule

The report may have `passed=True` only if:

- all required policies are available
- all required scenario comparisons exist
- all comparisons pass
- all policy aggregates match their scenario rows
- compatibility mode is not used by default
- Feature 068R through Feature 073 regressions pass
- no final evaluation claim is made
- no policy superiority claim is made
- no full paper reproduction claim is made

## Claim Boundary Rule

The report may claim baseline policy comparative evaluation readiness only. It must not claim final evaluation, statistical significance, policy superiority, training correctness, or full paper reproduction.
