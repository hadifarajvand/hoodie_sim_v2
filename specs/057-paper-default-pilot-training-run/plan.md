# Implementation Plan: Feature 057

## Feature

057 — Paper-Default Pilot Training Run

## Goal

Run a controlled paper-default pilot training run that is larger than Feature 055 smoke training but still explicitly smaller than a full campaign.

## Inputs

- `artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.json`
- `artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.json`
- `artifacts/analysis/training-readiness-contract/training-readiness-contract-report.json`
- Existing trainer/replay/checkpoint metadata components under `src/analysis/full_training_reproduction_campaign/`

## Outputs

- `artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.json`
- `artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.md`

## Architecture

Create package:

```text
src/analysis/paper_default_pilot_training_run/
```

Required files:

```text
__init__.py
__main__.py
config.py
model.py
runner.py
report.py
```

## Core validation layers

1. Feature 056 prerequisite gate.
2. Pilot scope validation.
3. Live environment training validation.
4. Replay growth validation.
5. Optimizer progress validation.
6. Finite loss validation.
7. Reward/delayed reward contract validation.
8. Legal-action validation.
9. Target-update/checkpoint metadata validation.
10. Train/eval trace-bank separation validation.
11. Safety/no-drift validation.

## Pilot scope

The pilot must use more than the Feature 055 smoke episode count and must stay below full-campaign scale. Suggested default:

```text
pilot_episodes = 3
pilot_episode_length = 110
full_campaign = false
baseline_comparison = false
paper_reproduction_claim = false
```

## Validation Handoff Packet

Required local test command:

```bash
python3 -m unittest \
  tests.unit.test_paper_default_pilot_training_run_schema \
  tests.unit.test_paper_default_pilot_training_run_metrics \
  tests.unit.test_paper_default_pilot_training_run_behavior_equivalence \
  tests.integration.test_paper_default_pilot_training_run \
  tests.integration.test_paper_default_pilot_training_run_report \
  tests.integration.test_paper_default_pilot_training_run_scope_guard
```

Required report-generation command:

```bash
python3 -m src.analysis.paper_default_pilot_training_run
```

Expected passing final verdict:

```text
paper_default_pilot_training_passed
```

Expected recommended next feature:

```text
Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness
```

Required JSON proof fields:

```text
feature_056_validation_verified
live_environment_training_used
fixture_training_used
episode_summary
replay_summary
optimizer_summary
loss_summary
reward_summary
legal_action_summary
checkpoint_summary
train_eval_contract_verified
remaining_blockers
final_verdict
recommended_next_feature
```

Required git-state commands:

```bash
git status --short
git diff --name-only main...HEAD
git diff --stat main...HEAD
git diff --cached --name-only
```

Approved paths:

```text
specs/057-paper-default-pilot-training-run/
src/analysis/paper_default_pilot_training_run/
tests/unit/test_paper_default_pilot_training_run_*.py
tests/integration/test_paper_default_pilot_training_run*.py
artifacts/analysis/paper-default-pilot-training-run/
```

Forbidden paths:

```text
.specify/feature.json
AGENTS.md
.gitignore
dependency files
src/environment/
src/policies/
prior Feature 037-056 artifacts
full-campaign outputs
baseline-comparison outputs
paper-reproduction outputs
model checkpoint binaries unless explicitly metadata-only
```

Auto-commit/push authorization:

Guarded auto-commit/push is allowed only after all tests pass, the report has the expected passing verdict, blockers are empty, dirty paths are approved, and forbidden paths are absent.
