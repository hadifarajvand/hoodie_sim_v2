# Feature 060B — Bind Full Campaign Execution to Real Torch Trainer

## Purpose

Repair Feature 060 by replacing scalar fallback campaign execution with a real Torch/TorchRL-backed trainer binding while preserving the existing Feature 060 artifact contract.

## Problem

Feature 060A proved that the Feature 060 campaign execution claim is not supported by real Torch trainer binding. The environment supports real binding through the repo venv, but Feature 060 did not import or execute the real trainer path.

## Required prior inputs

- `artifacts/analysis/real-torch-trainer-binding-audit/real-torch-trainer-binding-audit-report.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json`
- `src/analysis/full_paper_default_training_campaign_execution/runner.py`
- `src/analysis/full_training_reproduction_campaign/`
- `src/agents/torchrl_hoodie_learner.py`
- `src/analysis/paper_hoodie_network_implementation/`

## Required output artifacts

Feature 060B must regenerate the Feature 060 execution artifacts after real binding is used:

- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.md`
- `artifacts/analysis/full-paper-default-training-campaign-execution/training-metrics.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/evaluation-metrics.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/checkpoint-metadata.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/run-manifest.json`

It must also generate:

- `artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.json`
- `artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.md`

## Required report decisions

Required top-level fields:

- `feature_id`
- `prerequisite_tags_verified`
- `feature_060a_audit_verified`
- `torch_environment_summary`
- `real_trainer_binding_summary`
- `feature_060_repair_summary`
- `campaign_execution_summary`
- `training_metrics_summary`
- `evaluation_metrics_summary`
- `artifact_regeneration_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Required passing behavior

Passing requires:

- Feature 060A final verdict is `real_torch_trainer_binding_missing_repair_required`
- repo venv has `torch` and `torchrl`
- Feature 060 runner imports the real trainer/learner path
- Feature 060 runner executes the real trainer update/train path
- scalar fallback no longer drives the campaign claim
- regenerated Feature 060 report no longer claims unsupported scalar execution
- metrics and checkpoint metadata are produced from the real trainer-bound execution path
- no paper reproduction claim
- no performance superiority claim
- no baseline superiority claim

## Allowed final verdicts

- `real_torch_trainer_binding_repair_passed`
- `feature_060a_prerequisite_blocked`
- `torch_environment_blocked`
- `real_trainer_binding_blocked`
- `feature_060_repair_blocked`
- `artifact_regeneration_blocked`
- `behavior_drift_detected`

## Routing

If all gates pass:

- `final_verdict = real_torch_trainer_binding_repair_passed`
- `recommended_next_feature = Feature 061 — Campaign Result Integrity and Comparison Readiness Audit`
- `remaining_blockers = []`

If any gate fails, route to exact repair, not Feature 061.

## Hard scope

Allowed:

- modify Feature 060 execution package to bind to the real trainer
- regenerate Feature 060 execution artifacts
- create Feature 060B repair report artifacts and tests

Forbidden:

- dependency installation or dependency-file changes
- policy drift
- environment semantic drift
- reward timing drift
- paper reproduction claim
- performance superiority claim
- baseline superiority claim
- uncontrolled campaign loop
- model checkpoint binaries unless explicitly metadata-only or already contract-controlled
- `.specify/feature.json` committed diff
- `AGENTS.md` rewrite
