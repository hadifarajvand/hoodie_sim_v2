# Contract: Feature 070 Fidelity Report Schema

## Required Fields

- `feature_name`: must be `Feature 070 - Topology, Timeout/Drop, and Reward Fidelity`.
- `status`: implementation status.
- `passed`: boolean pass/fail result for targeted validation.
- `changed_files`: list of files changed by the implementation.
- `topology_evidence`: structured topology evidence or explicit blocker state.
- `neighbor_legality_evidence`: neighbor legality evidence.
- `timeout_drop_accounting_evidence`: timeout/drop terminal accounting evidence.
- `reward_equation_evidence`: reward equation source and recovery status.
- `terminal_reward_evidence`: terminal reward timing and equation linkage.
- `blockers`: unresolved blocker list.
- `feature_068r_regression_status`: prior baseline placement regression status.
- `feature_069_regression_status`: prior mechanism report regression status.
- `paper_claim_boundary`: explicit claim boundary.
- `recommended_next_feature`: next recommended project step.

## Topology Evidence Rule

Topology evidence is valid only if adjacency or neighbor legality is structured and source-backed. Missing adjacency must remain a blocker.

## Timeout/Drop Rule

Timeout/drop evidence is valid only if terminal task state is explicit and tied to deadline or timeout semantics.

## Reward Rule

Reward fidelity requires both equation evidence and terminal reward timing. If the exact equation is not recovered, the report must keep reward fidelity assumption-backed or blocked.

## Claim Boundary Rule

The report must not claim complete paper reproduction unless topology, timeout/drop, and reward fidelity are all resolved with structured evidence and targeted tests.
