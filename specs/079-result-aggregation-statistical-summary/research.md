# Feature 079 Research

## Decision 1: Aggregate all policies together
- Rationale: single-policy or pairwise comparison is insufficient.
- Consequence: mean, std, min, max, count, CI95 are computed across all policies.

## Decision 2: Consume Feature 078 rows only
- Rationale: Feature 079 must not execute any campaign cells.
- Consequence: aggregation is fully separated from runtime execution.

## Decision 3: No ranking or winner declaration
- Rationale: feature is only aggregation layer.
- Consequence: later Feature 080 handles comparative ranking.

## Decision 4: Preserve metric integrity
- Rationale: each policy/scenario/workload/deadline combination must be represented.
- Consequence: validation ensures coverage.
