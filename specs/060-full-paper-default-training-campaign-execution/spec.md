# Feature 060 — Full Paper-Default Training Campaign Execution

## Purpose

Execute the controlled full paper-default training campaign authorized by Feature 059, while preserving the evaluation harness, metric collection contract, checkpoint metadata contract, and safety boundaries.

## Problem

Feature 059 created the gate that allows a full paper-default campaign in the next feature. The repository now needs the first actual campaign execution feature that runs the approved training loop under explicit resource controls and produces campaign artifacts without claiming paper reproduction or baseline superiority.

## Required prior inputs

- `artifacts/analysis/full-paper-default-training-campaign-gate/full-paper-default-training-campaign-gate-report.json`
- `artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json`
- `artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.json`

## Required output artifacts

- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.md`
- `artifacts/analysis/full-paper-default-training-campaign-execution/training-metrics.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/evaluation-metrics.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/checkpoint-metadata.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/run-manifest.json`

## Required report decisions

The report must decide whether the controlled full paper-default training campaign executed successfully and produced auditable artifacts.

Required top-level fields:

- `feature_id`
- `prerequisite_tags_verified`
- `feature_059_gate_verified`
- `campaign_execution_summary`
- `training_metrics_summary`
- `evaluation_metrics_summary`
- `baseline_evaluation_summary`
- `checkpoint_metadata_summary`
- `artifact_manifest_summary`
- `resource_control_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Required passing behavior

Passing verdict requires:

- Feature 059 final verdict is `full_paper_default_training_campaign_gate_ready`
- campaign execution follows the Feature 059 scope and resource controls
- training executes inside the approved controlled output directory
- optimizer steps execute and are reported
- replay is populated and summarized
- checkpoint metadata artifact is written
- evaluation metrics artifact is written using the Feature 058 evaluation trace bank
- baseline evaluation metrics artifact is written using the Feature 058 baseline registry/harness contract
- all required artifacts exist and are listed in the run manifest
- metric schema is complete
- no paper reproduction claim is made
- no performance superiority claim is made
- no policy, dependency, environment, or reward-timing drift occurs

## Allowed final verdicts

- `full_paper_default_training_campaign_execution_passed`
- `feature_059_prerequisite_blocked`
- `campaign_execution_blocked`
- `training_metrics_blocked`
- `evaluation_metrics_blocked`
- `baseline_evaluation_blocked`
- `checkpoint_metadata_blocked`
- `artifact_manifest_blocked`
- `resource_control_blocked`
- `behavior_drift_detected`

## Routing

If all gates pass:

- `final_verdict = full_paper_default_training_campaign_execution_passed`
- `recommended_next_feature = Feature 061 — Campaign Result Integrity and Comparison Readiness Audit`
- `remaining_blockers = []`

If any gate fails, `remaining_blockers` must name the exact failed gate and `recommended_next_feature` must route to repair, not Feature 061.

## Hard scope

Allowed:

- controlled full paper-default training campaign execution
- training metrics artifact generation
- evaluation metrics artifact generation
- baseline evaluation metrics artifact generation
- checkpoint metadata artifact generation
- run manifest generation

Forbidden:

- paper reproduction claim
- performance superiority claim
- uncontrolled campaign loop
- dependency drift
- policy drift
- environment semantic changes
- reward timing changes
- prior Feature 037–059 artifact rewrites
- `.specify/feature.json` committed diff
- `AGENTS.md` rewrite
