# Implementation Plan: Feature 060A

## Feature

060A — Real Torch Trainer Binding Audit

## Goal

Audit whether Feature 060 actually executed through the real Torch/TorchRL trainer path or only generated deterministic scalar campaign artifacts.

## Inputs

- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json`
- `src/analysis/full_paper_default_training_campaign_execution/runner.py`
- `src/analysis/full_paper_default_training_campaign_execution/config.py`
- `src/agents/torchrl_hoodie_learner.py`
- `src/analysis/full_training_reproduction_campaign/`
- `src/analysis/paper_hoodie_network_implementation/`

## Outputs

- `artifacts/analysis/real-torch-trainer-binding-audit/real-torch-trainer-binding-audit-report.json`
- `artifacts/analysis/real-torch-trainer-binding-audit/real-torch-trainer-binding-audit-report.md`

## Architecture

Create package:

```text
src/analysis/real_torch_trainer_binding_audit/
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

## Core audit layers

1. Feature 060 prerequisite/report presence.
2. Python interpreter/environment proof.
3. Torch availability proof.
4. TorchRL availability proof.
5. Feature 060 source binding scan.
6. Real trainer candidate scan.
7. Scalar fallback detection.
8. Verdict routing.

## Validation Handoff Packet

Required local test command:

```bash
python3 -m unittest \
  tests.unit.test_real_torch_trainer_binding_audit_schema \
  tests.unit.test_real_torch_trainer_binding_audit_metrics \
  tests.unit.test_real_torch_trainer_binding_audit_behavior_equivalence \
  tests.integration.test_real_torch_trainer_binding_audit \
  tests.integration.test_real_torch_trainer_binding_audit_report \
  tests.integration.test_real_torch_trainer_binding_audit_scope_guard
```

Required report-generation command:

```bash
python3 -m src.analysis.real_torch_trainer_binding_audit
```

Expected likely final verdict for current Feature 060 implementation:

```text
real_torch_trainer_binding_missing_repair_required
```

Expected recommended next feature when binding is missing:

```text
Feature 060B — Bind Full Campaign Execution to Real Torch Trainer
```

Required JSON proof fields:

```text
python_environment_summary
torch_availability_summary
feature_060_claim_summary
feature_060_code_binding_summary
real_trainer_candidate_summary
simulation_fallback_summary
binding_audit_summary
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
specs/060a-real-torch-trainer-binding-audit/
src/analysis/real_torch_trainer_binding_audit/
tests/unit/test_real_torch_trainer_binding_audit_*.py
tests/integration/test_real_torch_trainer_binding_audit*.py
artifacts/analysis/real-torch-trainer-binding-audit/
```

Forbidden paths:

```text
.specify/feature.json
AGENTS.md
.gitignore
dependency files
src/environment/
src/policies/
Feature 060 execution source unless the feature explicitly scopes only read-only audit tests
prior Feature 037-060 artifacts
model checkpoint binaries
```

Auto-commit/push authorization:

Guarded auto-commit/push is allowed after tests pass, the report has an internally consistent verdict, blockers match verdict, dirty paths are approved, and forbidden paths are absent.
