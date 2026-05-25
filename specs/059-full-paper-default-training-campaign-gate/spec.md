# Feature 059 — Full Paper-Default Training Campaign Gate

## Purpose

Create the controlled gate that decides whether the project is ready to run the full paper-default training campaign after Feature 058 established a deterministic evaluation trace bank and baseline evaluation harness.

## Problem

The project has validated smoke training, replay and target-update mechanics, pilot training, and evaluation-harness readiness. It still must not jump directly into a full campaign without a machine-readable gate that verifies all prerequisites, campaign scope, resource controls, artifact outputs, and safety rules.

## Required prior inputs

- `artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json`
- `artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.json`
- `artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.json`
- `artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.json`

## Required output artifacts

- `artifacts/analysis/full-paper-default-training-campaign-gate/full-paper-default-training-campaign-gate-report.json`
- `artifacts/analysis/full-paper-default-training-campaign-gate/full-paper-default-training-campaign-gate-report.md`

## Required report decisions

The report must decide whether a full paper-default training campaign may be executed in the next feature.

Required top-level fields:

- `feature_id`
- `prerequisite_tags_verified`
- `feature_058_harness_verified`
- `campaign_scope_summary`
- `training_execution_gate_summary`
- `evaluation_harness_gate_summary`
- `artifact_output_contract_summary`
- `resource_control_summary`
- `checkpoint_contract_summary`
- `metric_collection_contract_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Required passing behavior

Passing verdict requires:

- Feature 058 final verdict is `evaluation_trace_bank_baseline_harness_ready`
- evaluation trace bank exists and is deterministic
- train/eval trace banks are disjoint
- baseline policy registry and baseline harness are ready
- metric schema is complete
- campaign scope is explicitly defined
- full campaign execution is gated to the next feature, not this feature
- training execution is not performed in this feature
- optimizer execution is not performed in this feature
- replay mutation is not performed in this feature
- checkpoint binaries are not written in this feature
- output artifact contract for next campaign is defined
- resource controls are defined
- no paper reproduction/performance claim is made

## Allowed final verdicts

- `full_paper_default_training_campaign_gate_ready`
- `feature_058_prerequisite_blocked`
- `campaign_scope_blocked`
- `training_execution_gate_blocked`
- `evaluation_harness_gate_blocked`
- `artifact_output_contract_blocked`
- `resource_control_blocked`
- `checkpoint_contract_blocked`
- `metric_collection_contract_blocked`
- `behavior_drift_detected`

## Routing

If all gates pass:

- `final_verdict = full_paper_default_training_campaign_gate_ready`
- `recommended_next_feature = Feature 060 — Full Paper-Default Training Campaign Execution`
- `remaining_blockers = []`

If any gate fails, `remaining_blockers` must name the exact failed gate and `recommended_next_feature` must route to repair, not Feature 060.

## Hard scope

Allowed:

- full-campaign readiness gate
- campaign scope contract
- resource-control contract
- next-feature artifact contract
- checkpoint and metric collection contract
- report artifacts and tests

Forbidden:

- actual full campaign execution
- training execution
- optimizer execution
- replay mutation
- checkpoint binary writing
- paper reproduction claim
- performance claim
- baseline superiority claim
- policy drift
- dependency drift
- environment semantic changes
- reward timing changes
- prior Feature 037–058 artifact rewrites
- `.specify/feature.json` committed diff
- `AGENTS.md` rewrite
