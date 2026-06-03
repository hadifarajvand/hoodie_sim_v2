# Feature 081 Plan — HOODIE Evaluation & Baseline Benchmarking

## Goal
Build an evaluation and benchmarking layer that compares Feature 080 `HOODIE_PROPOSED` against explicit baseline policies using deterministic scenarios, explicit metrics, and metric-by-metric ranking tables.

## Current Dependency
Feature 080 has been completed and merged. Feature 081 must treat `src/analysis/hoodie_proposed_method/` as an input dependency, not as code to modify.

## Architecture

Feature 081 implementation package:

```text
src/analysis/hoodie_evaluation_runner/
  __init__.py
  __main__.py
  config.py
  model.py
  policies.py
  scenarios.py
  metrics.py
  runner.py
  aggregation.py
  ranking.py
  report.py
```

## Implementation Phases

### Phase 1 — Contracts and Models
- Define policy names.
- Define scenario context model.
- Define task/outcome/metric row model.
- Define report model.

### Phase 2 — Baseline Policy Adapters
- Implement `LOCAL_ONLY`.
- Implement `CLOUD_ONLY`.
- Implement `RANDOM_POLICY` with seed control.
- Implement `ORIGINAL_HOODIE_BASELINE` adapter using available repository baseline/runtime components where possible.
- Implement `HOODIE_PROPOSED` adapter calling Feature 080 package.

### Phase 3 — Scenario Generator
Implement deterministic scenarios:
- light_load_no_deadline_pressure
- tight_deadline_pressure
- legal_horizontal_offload
- illegal_horizontal_destination_attempt
- cloud_vertical_fallback
- timeout_drop_case
- mixed_local_horizontal_cloud_candidates

Each scenario must support workload levels:
- low
- medium
- high

Each scenario must support deadline pressure:
- relaxed
- moderate
- tight

### Phase 4 — Metrics
Implement metrics:
- completion_rate
- timeout_drop_rate
- unavailable_drop_rate
- deadline_violation_rate
- average_delay
- average_reward
- total_reward
- throughput
- queue_stability_score
- illegal_action_rejection_count

### Phase 5 — Aggregation and Ranking
- Aggregate by policy.
- Aggregate by policy + scenario.
- Aggregate by policy + workload.
- Aggregate by policy + deadline pressure.
- Produce metric-by-metric ranking tables.

### Phase 6 — Report and Validation
- Build `build_feature_081_report()`.
- Include policy coverage, scenario coverage, metric coverage, ranking coverage, claim boundary, and scope proof.
- Keep claim boundary explicit.

## Readiness Levels

- `blocked`: required policy/scenario/metric missing
- `partial`: runner exists but coverage incomplete
- `mostly_implemented`: all structures exist, but one or more adapters are compatibility-mode only
- `fully_implemented`: all required policies, scenarios, metrics, aggregation, ranking, report, and tests are implemented

## Required Validation Commands

```bash
git diff --check
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_evaluation_runner_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_evaluation_runner_*.py'
src/.venvmac/bin/python -m analysis.hoodie_evaluation_runner
```

## Claim Boundary
This feature may produce deterministic comparison tables. It must not claim full empirical paper reproduction or statistical superiority unless later features add full experiment execution and statistical testing.
