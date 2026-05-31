# Contract: Feature 071 Runtime Paper-Faithful Semantics Report Schema

## Required Fields

- `feature_name`: must be `Feature 071 - Runtime Paper-Faithful Semantics Alignment`.
- `status`: runtime alignment status.
- `passed`: targeted validation pass/fail.
- `changed_files`: changed file list.
- `deadline_evidence`: paper and compatibility deadline evidence.
- `terminal_state_evidence`: terminal state consistency evidence.
- `reward_runtime_evidence`: Eq. (20)-(23) runtime evidence.
- `compatibility_evidence`: explicit compatibility-mode evidence.
- `feature_068r_regression_status`: Feature 068R targeted gate.
- `feature_069_regression_status`: Feature 069 targeted gate.
- `feature_070_regression_status`: Feature 070 targeted gate.
- `paper_claim_boundary`: explicit claim boundary.
- `recommended_next_feature`: expected next feature.

## Deadline Evidence Rule

Deadline evidence must include paper mode and compatibility mode. Paper mode must use strict completion-before-deadline semantics. Compatibility mode may preserve equality-at-deadline behavior only when explicitly requested.

## Terminal State Rule

Terminal state evidence must reject contradictory records:

- completed with drop reason
- dropped without terminal slot
- pending with reward emission

## Reward Evidence Rule

Reward evidence must prove:

- Eq. (20) inactive/success/drop branches.
- Eq. (21) private/public Phi selection.
- Eq. (22) private Phi calculation.
- Eq. (23) public Phi aggregation.

## Claim Boundary Rule

Feature 071 may claim runtime helper semantics alignment only. It must not claim full HOODIE reproduction or end-to-end golden trace correctness.
