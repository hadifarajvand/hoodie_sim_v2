# Contract: Feature 073 Controlled Evaluation Batch Report Schema

## Required Fields

- `feature_name`: must be `Feature 073 - Controlled Evaluation Batch Readiness`.
- `status`: controlled evaluation readiness status.
- `passed`: final pass/fail value.
- `changed_files`: changed file list.
- `scenarios`: controlled evaluation scenarios.
- `aggregate_metrics`: batch-level metrics.
- `feature_068r_regression_status`: Feature 068R targeted gate.
- `feature_069_regression_status`: Feature 069 targeted gate.
- `feature_070_regression_status`: Feature 070 targeted gate.
- `feature_071_regression_status`: Feature 071 targeted gate.
- `feature_072_regression_status`: Feature 072 targeted gate.
- `paper_claim_boundary`: explicit claim boundary.
- `recommended_next_feature`: expected next feature.

## Scenario Rule

Each controlled scenario must include:

- scenario id
- scenario name
- deterministic task records
- expected metrics
- actual metrics
- paper mode only flag
- passed flag

## Metric Rule

Each scenario and aggregate batch must expose:

- completed count
- timeout drop count
- unavailable drop count
- deadline violation count
- illegal action rejection count
- average delay
- average reward
- paper-mode success count
- compatibility mode usage flag

## Pass Rule

The report may have `passed=True` only if:

- all controlled scenarios pass
- aggregate metrics match scenario metrics
- compatibility mode is not used in the default batch
- Feature 068R regression passes
- Feature 069 regression passes
- Feature 070 regression passes
- Feature 071 regression passes
- Feature 072 regression passes
- no full paper reproduction claim is made

## Claim Boundary Rule

The report may claim controlled evaluation batch readiness only. It must not claim final evaluation, performance superiority, training correctness, or full paper reproduction.
