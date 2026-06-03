# Feature 083 — HOODIE Paper Baseline Fidelity

## Reference
GitHub Spec Kit: https://github.com/github/spec-kit

## Goal
- HOODIE = proposed method.
- Baselines derived from HOODIE paper: RO, FLC, VO, HO, BCO, MQO
- Remove ORIGINAL_HOODIE_BASELINE as independent policy.
- Generate artifact bundle reflecting paper baselines.

## Non-goals
- No DCQ
- No thesis method
- No queue redesign
- No statistical superiority claim
- No full paper reproduction

## Required Artifacts
- raw_rows.json / csv
- aggregate_by_policy.json / csv
- ranking_by_metric.json / csv
- feature_083_runtime_evaluation_report.json / md
- execution_manifest.json

## Claim Boundary
- HOODIE = Feature 080 proposed method only
- Baselines paper-aligned
- Deterministic evaluation