# Implementation Plan: Feature 062

## Feature

062 — Multi-Seed Campaign and Ablation Batch

## Batch coverage

This feature replaces five separate micro-features:

1. Multi-Seed Campaign Gate
2. Multi-Seed Campaign Execution
3. Multi-Seed Result Aggregation
4. Mechanism Ablation Gate
5. Mechanism Ablation Execution

## Goal

Extend the single-run Feature 061 evidence into controlled multi-seed and ablation evidence without claiming paper reproduction or unsupported superiority.

## Inputs

- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/campaign-integrity-evaluation-comparison-batch-report.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-evaluation-results.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/trained-policy-evaluation-results.json`
- `artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-vs-trained-policy-comparison.json`
- `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json`
- `artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.json`

## Outputs

- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.md`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-gate.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-aggregation.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/ablation-gate.json`
- `artifacts/analysis/multi-seed-campaign-ablation-batch/ablation-results.json`

## Architecture

Create package:

```text
src/analysis/multi_seed_campaign_ablation_batch/
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

1. Feature 061 prerequisite gate.
2. Multi-seed campaign gate.
3. Multi-seed campaign execution or controlled materialization.
4. Multi-seed result aggregation.
5. Ablation gate.
6. Ablation execution or controlled materialization.
7. Artifact manifest validation.
8. Safety/no-claim/no-drift validation.

## Validation Handoff Packet

Required local test command:

```bash
python3 -m unittest \
  tests.unit.test_multi_seed_campaign_ablation_batch_schema \
  tests.unit.test_multi_seed_campaign_ablation_batch_metrics \
  tests.unit.test_multi_seed_campaign_ablation_batch_behavior_equivalence \
  tests.integration.test_multi_seed_campaign_ablation_batch \
  tests.integration.test_multi_seed_campaign_ablation_batch_report \
  tests.integration.test_multi_seed_campaign_ablation_batch_scope_guard
```

Required report-generation command:

```bash
python3 -m src.analysis.multi_seed_campaign_ablation_batch
```

Expected passing final verdict:

```text
multi_seed_campaign_ablation_batch_passed
```

Expected next feature:

```text
Feature 063 — Results Export, Reproducibility, and Final Documentation Batch
```

Approved paths:

```text
specs/062-multi-seed-campaign-ablation-batch/
src/analysis/multi_seed_campaign_ablation_batch/
tests/unit/test_multi_seed_campaign_ablation_batch_*.py
tests/integration/test_multi_seed_campaign_ablation_batch*.py
artifacts/analysis/multi-seed-campaign-ablation-batch/
```

Forbidden paths:

```text
.specify/feature.json
AGENTS.md
.gitignore
dependency files
src/environment/
src/policies/
prior Feature 037-061 artifacts
model checkpoint binaries
paper reproduction outputs
uncontrolled campaign outputs
```

Auto-commit/push authorization:

Guarded auto-commit/push is allowed after tests pass, report verdict is internally consistent, blockers are empty, dirty paths are approved, and forbidden paths are absent.
