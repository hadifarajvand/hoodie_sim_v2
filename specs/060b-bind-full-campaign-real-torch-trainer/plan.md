# Implementation Plan: Feature 060B

## Feature

060B — Bind Full Campaign Execution to Real Torch Trainer

## Goal

Repair Feature 060 so the campaign execution path is bound to real Torch/TorchRL trainer code instead of scalar fallback logic.

## Inputs

- `artifacts/analysis/real-torch-trainer-binding-audit/real-torch-trainer-binding-audit-report.json`
- `src/analysis/full_paper_default_training_campaign_execution/runner.py`
- `src/analysis/full_paper_default_training_campaign_execution/config.py`
- `src/analysis/full_training_reproduction_campaign/`
- `src/agents/torchrl_hoodie_learner.py`
- `src/analysis/paper_hoodie_network_implementation/`

## Outputs

Regenerate Feature 060 artifacts:

- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.md`
- `artifacts/analysis/full-paper-default-training-campaign-execution/training-metrics.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/evaluation-metrics.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/checkpoint-metadata.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/run-manifest.json`

Create Feature 060B artifacts:

- `artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.json`
- `artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.md`

## Architecture

Create package:

```text
src/analysis/bind_full_campaign_real_torch_trainer/
```

Allowed repair target:

```text
src/analysis/full_paper_default_training_campaign_execution/
```

## Real binding rule

Feature 060 must import and call real trainer, learner, or network code from the existing repository. Acceptable candidates include the full training reproduction campaign trainer/runner, the TorchRL hoodie learner, and paper hoodie network implementation.

## Validation Handoff Packet

Run Feature 060B tests:

```bash
python3 -m unittest \
  tests.unit.test_bind_full_campaign_real_torch_trainer_schema \
  tests.unit.test_bind_full_campaign_real_torch_trainer_metrics \
  tests.unit.test_bind_full_campaign_real_torch_trainer_behavior_equivalence \
  tests.integration.test_bind_full_campaign_real_torch_trainer \
  tests.integration.test_bind_full_campaign_real_torch_trainer_report \
  tests.integration.test_bind_full_campaign_real_torch_trainer_scope_guard
```

Run Feature 060 regression tests:

```bash
python3 -m unittest \
  tests.unit.test_full_paper_default_training_campaign_execution_schema \
  tests.unit.test_full_paper_default_training_campaign_execution_metrics \
  tests.unit.test_full_paper_default_training_campaign_execution_behavior_equivalence \
  tests.integration.test_full_paper_default_training_campaign_execution \
  tests.integration.test_full_paper_default_training_campaign_execution_report \
  tests.integration.test_full_paper_default_training_campaign_execution_scope_guard
```

Generate reports:

```bash
python3 -m src.analysis.full_paper_default_training_campaign_execution
python3 -m src.analysis.bind_full_campaign_real_torch_trainer
```

Expected final verdict:

```text
real_torch_trainer_binding_repair_passed
```

Expected next feature:

```text
Feature 061 — Campaign Result Integrity and Comparison Readiness Audit
```

Approved paths:

```text
specs/060b-bind-full-campaign-real-torch-trainer/
src/analysis/bind_full_campaign_real_torch_trainer/
src/analysis/full_paper_default_training_campaign_execution/
tests/unit/test_bind_full_campaign_real_torch_trainer_*.py
tests/integration/test_bind_full_campaign_real_torch_trainer*.py
artifacts/analysis/bind-full-campaign-real-torch-trainer/
artifacts/analysis/full-paper-default-training-campaign-execution/
```

Forbidden paths:

```text
.specify/feature.json
AGENTS.md
.gitignore
dependency files
src/environment/
src/policies/
model checkpoint binaries
```
