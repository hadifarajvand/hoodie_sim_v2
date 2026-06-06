# Contract: Feature 072 Golden Trace Report Schema

## Required Fields

- `feature_name`: must be `Feature 072 - End-to-End HOODIE Golden Trace Validation`.
- `status`: golden trace validation status.
- `passed`: final pass/fail value.
- `changed_files`: changed file list.
- `scenarios`: list of golden trace scenarios.
- `feature_068r_regression_status`: Feature 068R targeted gate.
- `feature_069_regression_status`: Feature 069 targeted gate.
- `feature_070_regression_status`: Feature 070 targeted gate.
- `feature_071_regression_status`: Feature 071 targeted gate.
- `paper_claim_boundary`: explicit claim boundary.
- `recommended_next_feature`: expected next feature.

## Scenario Rule

Each scenario must include:

- scenario id
- scenario name
- inputs
- expected outputs
- actual outputs
- steps
- passed flag

## Step Rule

Each step must include:

- step name
- input snapshot
- expected output
- actual output
- passed flag
- evidence source

## Pass Rule

The report may have `passed=True` only if:

- all golden trace scenarios pass
- Feature 068R regression passes
- Feature 069 regression passes
- Feature 070 regression passes
- Feature 071 regression passes
- no full paper reproduction claim is made

## Claim Boundary Rule

The report may claim deterministic end-to-end semantic trace validation only. It must not claim full paper reproduction, training correctness, performance reproduction, or evaluation readiness.
