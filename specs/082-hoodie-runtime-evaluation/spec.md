# Feature 082 — HOODIE Runtime Evaluation Policy-Divergence Repair

## Spec Kit Reference

This feature follows the GitHub Spec Kit workflow as the governing implementation process reference:

https://github.com/github/spec-kit

Implementation must be driven by this specification, the plan, and the tasks. Do not bypass the Spec Kit by repeatedly running implementation prompts without first updating the spec artifacts.

## Current Problem

Feature 082 already repaired two proxy failures:

- `HOODIE_PROPOSED != LOCAL_ONLY`
- `ORIGINAL_HOODIE_BASELINE != CLOUD_ONLY`

However, the current artifact bundle still has a critical policy identity failure:

- `HOODIE_PROPOSED == ORIGINAL_HOODIE_BASELINE` across the core aggregate metrics.

The current aggregate values for `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE` are numerically identical for:

- `completion_rate`
- `timeout_drop_rate`
- `unavailable_drop_rate`
- `deadline_violation_rate`
- `average_delay`
- `average_reward`
- `total_reward`
- `throughput`
- `queue_stability_score`
- `illegal_action_rejection_count`

Distinct adapter names are not enough. If the generated aggregate behavior is identical across all core metrics, the comparison is not research-valid.

## Goal

Repair Feature 082 so that `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE` become behaviorally distinct in generated artifacts.

The final artifact bundle must prove all three identities:

- `HOODIE_PROPOSED != LOCAL_ONLY`
- `ORIGINAL_HOODIE_BASELINE != CLOUD_ONLY`
- `HOODIE_PROPOSED != ORIGINAL_HOODIE_BASELINE`

## Hard Failure Gate

If `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE` remain identical across all core aggregate metrics after regeneration, the feature is still failed.

The implementation must not report success, readiness, or final state when this equality remains.

## Policy Requirements

### HOODIE_PROPOSED

Must:

- use Feature 080 base-paper proposed-method components
- expose proposed-method-specific decision trace labels
- use a proposed-method scoring path that is not reused by `ORIGINAL_HOODIE_BASELINE`
- select different actions than `ORIGINAL_HOODIE_BASELINE` in at least one mixed local/horizontal/vertical candidate scenario
- remain base-paper HOODIE only

Must not:

- use DCQ
- use the thesis method
- mutate Feature 080 internals
- share the same runtime decision path as `ORIGINAL_HOODIE_BASELINE`

### ORIGINAL_HOODIE_BASELINE

Must:

- use a distinct paper-aligned baseline policy path
- expose baseline-specific decision trace labels
- avoid calling the same proposed-method scoring function
- differ from `HOODIE_PROPOSED` in at least one core aggregate metric after artifact regeneration

If full original-HOODIE runtime is unavailable, this must be documented as a limitation, but the adapter must still be behaviorally distinct from `HOODIE_PROPOSED`.

## Core Metrics for Divergence Gate

The divergence check must evaluate:

- `completion_rate`
- `timeout_drop_rate`
- `unavailable_drop_rate`
- `deadline_violation_rate`
- `average_delay`
- `average_reward`
- `total_reward`
- `throughput`
- `queue_stability_score`
- `illegal_action_rejection_count`

At least one of these metrics must differ between `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE`.

## Required Tests

Add tests that fail when:

- `HOODIE_PROPOSED` and `ORIGINAL_HOODIE_BASELINE` use the same decision trace under mixed candidates
- both policies always choose the same action in mixed local/horizontal/vertical candidate scenarios
- generated aggregate artifacts show equality across all core metrics
- artifact validation accepts equality between the two core policies

## Required Artifacts

Regenerate:

```text
artifacts/feature_082_full_runtime_eval/raw_rows.json
artifacts/feature_082_full_runtime_eval/raw_rows.csv
artifacts/feature_082_full_runtime_eval/aggregate_by_policy.json
artifacts/feature_082_full_runtime_eval/aggregate_by_policy.csv
artifacts/feature_082_full_runtime_eval/ranking_by_metric.json
artifacts/feature_082_full_runtime_eval/ranking_by_metric.csv
artifacts/feature_082_full_runtime_eval/feature_082_runtime_evaluation_report.json
artifacts/feature_082_full_runtime_eval/feature_082_runtime_evaluation_report.md
artifacts/feature_082_full_runtime_eval/execution_manifest.json
```

## Readiness Rules

- `blocked`: `HOODIE_PROPOSED == ORIGINAL_HOODIE_BASELINE` across all core aggregate metrics
- `partial`: policy divergence exists but tests or artifact proof are incomplete
- `mostly_implemented`: divergence exists, tests pass, artifacts regenerate, limitations are documented
- `fully_implemented`: all required divergence and identity gates pass with no active compatibility limitation

## Claim Boundary

The repaired feature may claim:

- deterministic runtime evaluation artifacts exist
- policy identity gates pass
- metric-by-metric ranking artifacts were generated

The repaired feature must not claim:

- statistical superiority
- full empirical paper reproduction
- thesis/DCQ method comparison
- trained DRL reproduction beyond implemented components
