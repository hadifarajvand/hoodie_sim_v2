# Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness

## Purpose

Create the evaluation trace bank and baseline evaluation harness required after Feature 057 proved a controlled paper-default pilot training run can execute safely.

## Problem

The project now has smoke, target-update/replay validation, and pilot training evidence. It still lacks a dedicated evaluation harness that separates evaluation traces from training traces and can evaluate baseline decision policies without running a full campaign or making a paper reproduction claim.

## Required prior inputs

- `artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.json`
- `artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.json`
- `artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.json`

## Required output artifacts

- `artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json`
- `artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.md`

## Required report decisions

The report must decide whether a deterministic evaluation trace bank and baseline harness are ready for later full campaign/evaluation work.

Required top-level fields:

- `feature_id`
- `prerequisite_tags_verified`
- `feature_057_pilot_verified`
- `evaluation_trace_bank_summary`
- `train_eval_separation_summary`
- `baseline_policy_registry_summary`
- `baseline_evaluation_harness_summary`
- `metric_schema_summary`
- `determinism_summary`
- `behavior_safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Required passing behavior

Passing verdict requires:

- Feature 057 final verdict is `paper_default_pilot_training_passed`
- evaluation trace bank exists and is deterministic
- evaluation trace bank is disjoint from training trace bank
- baseline policy registry exists
- baseline harness can evaluate baseline policies against evaluation traces
- metric schema includes delay, drop, timeout, reward, action distribution, local/horizontal/vertical action counts, and per-episode summaries
- no training occurs
- no optimizer step occurs
- no replay mutation occurs
- no model checkpoint is written
- no full campaign is run
- no paper reproduction/performance claim is made

## Allowed final verdicts

- `evaluation_trace_bank_baseline_harness_ready`
- `feature_057_prerequisite_blocked`
- `evaluation_trace_bank_blocked`
- `train_eval_separation_blocked`
- `baseline_registry_blocked`
- `baseline_harness_blocked`
- `metric_schema_blocked`
- `determinism_blocked`
- `behavior_drift_detected`

## Routing

If all gates pass:

- `final_verdict = evaluation_trace_bank_baseline_harness_ready`
- `recommended_next_feature = Feature 059 — Full Paper-Default Training Campaign Gate`
- `remaining_blockers = []`

If any gate fails, `remaining_blockers` must name the exact failed gate and `recommended_next_feature` must route to the exact repair, not Feature 059.

## Hard scope

Allowed:

- deterministic evaluation trace-bank definition
- baseline policy registry definition
- baseline evaluation harness validation
- metric schema validation
- report artifacts and tests

Forbidden:

- training execution
- optimizer execution
- replay mutation
- model checkpoint writing
- full campaign execution
- paper reproduction claim
- performance claim
- policy drift
- dependency drift
- environment semantic changes
- reward timing changes
- prior Feature 037–057 artifact rewrites
- `.specify/feature.json` committed diff
- `AGENTS.md` rewrite
