# Implementation Plan: Feature 061

## Feature

061 — Campaign Integrity, Evaluation Execution, and Comparison Batch

## Batch coverage

This feature replaces five separate micro-features:

1. Campaign Result Integrity and Comparison Readiness Audit
2. Baseline Evaluation Execution
3. Trained Policy Evaluation Execution
4. Baseline vs Trained Policy Comparison Readiness Audit
5. Baseline vs Trained Policy Comparison Report

## Goal

Validate repaired Feature 060 outputs, execute baseline and trained-policy evaluation on the same evaluation trace bank, verify comparison readiness, and generate comparison artifacts.

## Inputs

- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json`
- `artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.json`
- `artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json`
- Feature 060 training/evaluation/checkpoint/manifest artifacts

## Outputs

- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/campaign-integrity-evaluation-comparison-batch-report.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/campaign-integrity-evaluation-comparison-batch-report.md`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-evaluation-results.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/trained-policy-evaluation-results.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/comparison-readiness-audit.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-vs-trained-policy-comparison.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-vs-trained-policy-comparison.md`

## Architecture

Create package:

```text
src/analysis/campaign_integrity_evaluation_comparison_batch/
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

## Validation layers

1. Feature 060 and 060B prerequisite gate.
2. Campaign artifact integrity audit.
3. Baseline evaluation execution.
4. Trained-policy evaluation execution.
5. Comparison readiness audit.
6. Comparison report generation.
7. Artifact manifest validation.
8. Safety/no-claim/no-drift validation.

## Validation Handoff Packet

Required local test command:

```bash
python3 -m unittest \
  tests.unit.test_campaign_integrity_evaluation_comparison_batch_schema \
  tests.unit.test_campaign_integrity_evaluation_comparison_batch_metrics \
  tests.unit.test_campaign_integrity_evaluation_comparison_batch_behavior_equivalence \
  tests.integration.test_campaign_integrity_evaluation_comparison_batch \
  tests.integration.test_campaign_integrity_evaluation_comparison_batch_report \
  tests.integration.test_campaign_integrity_evaluation_comparison_batch_scope_guard
```

Required report-generation command:

```bash
python3 -m src.analysis.campaign_integrity_evaluation_comparison_batch
```

Expected passing final verdict:

```text
campaign_integrity_evaluation_comparison_batch_passed
```

Expected next feature:

```text
Feature 062 — Multi-Seed Campaign and Ablation Batch
```

Approved paths:

```text
specs/061-campaign-integrity-evaluation-comparison-batch/
src/analysis/campaign_integrity_evaluation_comparison_batch/
tests/unit/test_campaign_integrity_evaluation_comparison_batch_*.py
tests/integration/test_campaign_integrity_evaluation_comparison_batch*.py
artifacts/analysis/campaign-integrity-evaluation-comparison-batch/
```

Forbidden paths:

```text
.specify/feature.json
AGENTS.md
.gitignore
dependency files
src/environment/
src/policies/
prior Feature 037-060B artifacts
model checkpoint binaries
paper reproduction outputs
uncontrolled campaign outputs
```

Auto-commit/push authorization:

Guarded auto-commit/push is allowed after tests pass, report verdict is internally consistent, blockers are empty, dirty paths are approved, and forbidden paths are absent.
