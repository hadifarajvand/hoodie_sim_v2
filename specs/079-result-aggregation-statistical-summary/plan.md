# Feature 079 Plan

## Objective

Build a statistical aggregation layer over Feature 078 raw execution rows.

Feature 079 must compare all policies together in a shared summary structure. It must not perform only pairwise comparisons.

## Current Boundary

Feature 079 consumes raw rows from Feature 078. It does not execute campaign cells.

## Future Package Path

- `src/analysis/result_aggregation_statistical_summary/`

## Future Test Paths

- `tests/unit/test_result_aggregation_statistical_summary_*`
- `tests/integration/test_result_aggregation_statistical_summary_*`

## Required Later Steps

1. Read Feature 078 report.
2. Validate Feature 078 passed.
3. Extract raw result rows.
4. Group all policies together.
5. Compute metric summaries for each group.
6. Compute CI95 bounds.
7. Build all-policy comparative tables.
8. Preserve no-winner and no-superiority boundaries.
9. Validate all policies are represented.
10. Validate all metrics are summarized.
11. Run Feature 079 tests.
12. Run Feature 078 regression tests.

## Required Groupings

- policy
- policy plus scenario
- policy plus workload level
- policy plus deadline pressure level
- policy plus workload level plus deadline pressure level

## Required Metrics

- completion_rate
- timeout_drop_rate
- unavailable_drop_rate
- deadline_violation_rate
- average_delay
- average_reward
- total_reward

## Required Summary Fields

- mean
- std
- min
- max
- count
- ci95_low
- ci95_high

## Non-Goals

- execute campaign cells
- pairwise-only comparison
- winner declaration
- superiority claim
- final evaluation claim
- model training
