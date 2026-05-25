# Implementation Plan: Feature 058

## Feature

058 — Evaluation Trace Bank and Baseline Evaluation Harness

## Goal

Create a deterministic evaluation trace bank and baseline evaluation harness after Feature 057 confirmed the paper-default pilot training run.

## Inputs

- `artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.json`
- `artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.json`
- `artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.json`

## Outputs

- `artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json`
- `artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.md`

## Architecture

Create package:

```text
src/analysis/evaluation_trace_bank_baseline_harness/
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

1. Feature 057 prerequisite gate.
2. Deterministic evaluation trace-bank construction.
3. Train/eval trace-bank separation.
4. Baseline policy registry.
5. Baseline evaluation harness evidence path.
6. Metric schema coverage.
7. Determinism/repeatability check.
8. Safety/no-training/no-drift validation.

## Validation Handoff Packet

Required local test command:

```bash
python3 -m unittest \
  tests.unit.test_evaluation_trace_bank_baseline_harness_schema \
  tests.unit.test_evaluation_trace_bank_baseline_harness_metrics \
  tests.unit.test_evaluation_trace_bank_baseline_harness_behavior_equivalence \
  tests.integration.test_evaluation_trace_bank_baseline_harness \
  tests.integration.test_evaluation_trace_bank_baseline_harness_report \
  tests.integration.test_evaluation_trace_bank_baseline_harness_scope_guard
```

Required report-generation command:

```bash
python3 -m src.analysis.evaluation_trace_bank_baseline_harness
```

Expected passing final verdict:

```text
evaluation_trace_bank_baseline_harness_ready
```

Expected recommended next feature:

```text
Feature 059 — Full Paper-Default Training Campaign Gate
```

Required JSON proof fields:

```text
feature_057_pilot_verified
evaluation_trace_bank_summary
train_eval_separation_summary
baseline_policy_registry_summary
baseline_evaluation_harness_summary
metric_schema_summary
determinism_summary
behavior_safety_summary
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
specs/058-evaluation-trace-bank-baseline-harness/
src/analysis/evaluation_trace_bank_baseline_harness/
tests/unit/test_evaluation_trace_bank_baseline_harness_*.py
tests/integration/test_evaluation_trace_bank_baseline_harness*.py
artifacts/analysis/evaluation-trace-bank-baseline-harness/
```

Auto-commit/push authorization:

Guarded auto-commit/push is allowed after tests pass, the report has the expected passing verdict, blockers are empty, dirty paths are approved, and forbidden paths are absent.
