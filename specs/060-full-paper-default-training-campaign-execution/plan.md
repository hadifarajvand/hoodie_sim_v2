# Implementation Plan: Feature 060

## Feature

060 — Full Paper-Default Training Campaign Execution

## Goal

Execute the controlled full paper-default training campaign authorized by Feature 059 and produce auditable campaign artifacts.

## Inputs

- `artifacts/analysis/full-paper-default-training-campaign-gate/full-paper-default-training-campaign-gate-report.json`
- `artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json`
- `artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.json`

## Outputs

- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.md`
- `artifacts/analysis/full-paper-default-training-campaign-execution/training-metrics.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/evaluation-metrics.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/checkpoint-metadata.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/run-manifest.json`

## Architecture

Create package:

```text
src/analysis/full_paper_default_training_campaign_execution/
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

1. Feature 059 prerequisite gate.
2. Controlled campaign execution.
3. Training metrics artifact.
4. Evaluation metrics artifact.
5. Baseline evaluation metrics artifact.
6. Checkpoint metadata artifact.
7. Run manifest artifact.
8. Resource-control compliance.
9. Safety/no-claim/no-drift validation.

## Campaign execution scope

Use Feature 059 campaign scope and resource controls. If the full requested budget is too expensive for local validation, implement a controlled execution path that honors the configured budget contract and reports exact actual executed counts. Do not fabricate completed episode counts.

## Validation Handoff Packet

Required local test command:

```bash
python3 -m unittest \
  tests.unit.test_full_paper_default_training_campaign_execution_schema \
  tests.unit.test_full_paper_default_training_campaign_execution_metrics \
  tests.unit.test_full_paper_default_training_campaign_execution_behavior_equivalence \
  tests.integration.test_full_paper_default_training_campaign_execution \
  tests.integration.test_full_paper_default_training_campaign_execution_report \
  tests.integration.test_full_paper_default_training_campaign_execution_scope_guard
```

Required report-generation command:

```bash
python3 -m src.analysis.full_paper_default_training_campaign_execution
```

Expected passing final verdict:

```text
full_paper_default_training_campaign_execution_passed
```

Expected recommended next feature:

```text
Feature 061 — Campaign Result Integrity and Comparison Readiness Audit
```

Required JSON proof fields:

```text
feature_059_gate_verified
campaign_execution_summary
training_metrics_summary
evaluation_metrics_summary
baseline_evaluation_summary
checkpoint_metadata_summary
artifact_manifest_summary
resource_control_summary
safety_summary
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
specs/060-full-paper-default-training-campaign-execution/
src/analysis/full_paper_default_training_campaign_execution/
tests/unit/test_full_paper_default_training_campaign_execution_*.py
tests/integration/test_full_paper_default_training_campaign_execution*.py
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
prior Feature 037-059 artifacts
paper-reproduction outputs
uncontrolled campaign outputs
```

Auto-commit/push authorization:

Guarded auto-commit/push is allowed after tests pass, the report has the expected passing verdict, blockers are empty, dirty paths are approved, and forbidden paths are absent.
