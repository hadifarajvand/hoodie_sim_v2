# Contract: Full HOODIE Mechanism Fidelity Batch Report Schema

## Required Fields

- `feature_name`: must be `Feature 069 - Full HOODIE Mechanism Fidelity Batch`.
- `status`: implementation status.
- `passed`: boolean pass/fail result for targeted validation.
- `changed_files`: list of files changed by the implementation.
- `mechanism_contracts`: list of mechanism contract results.
- `blocker_list`: unresolved blockers with severity and next action.
- `validation_commands`: exact commands executed.
- `feature_068r_regression_status`: status of the prior baseline placement repair regression gate.
- `paper_claim_boundary`: explicit claim boundary.
- `recommended_next_feature`: next recommended project step.

## Mechanism Contract Entry

Each `mechanism_contracts` entry must include:

- `name`
- `category`
- `status`
- `verified_behavior`
- `compatibility_fallback`
- `assumption_backed_behavior`
- `blockers`
- `evidence_files`

## Blocker Entry

Each `blocker_list` entry must include:

- `category`
- `severity`
- `description`
- `evidence_source`
- `next_action`

## Validation Rule

A report is valid only if it separates verified behavior from compatibility fallback, assumption-backed behavior, and unresolved blockers.

## Claim Boundary Rule

The report may claim mechanism-fidelity readiness for targeted contracts only. It must not claim complete paper reproduction.
