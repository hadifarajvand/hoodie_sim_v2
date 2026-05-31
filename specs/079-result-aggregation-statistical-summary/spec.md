# Feature 079 - Result Aggregation and Statistical Summary

## Goal

Aggregate raw Feature 078 execution rows into policy-level, scenario-level, workload-level, and deadline-pressure-level statistical summaries.

Feature 079 consumes Feature 078. It must not execute campaign cells again.

## Dependencies

- Feature 078: `078-campaign-execution-engine`
- Feature 077: `077-experimental-campaign-readiness`

## Required Input

- Feature 078 report status: `campaign_execution_engine_ready`
- Feature 078 `passed=True`
- raw execution rows covering the full grid
- row count equals `441 * seed_count`

## Required Summaries

For each metric and grouping, compute:

- `mean`
- `std`
- `min`
- `max`
- `count`
- `ci95_low`
- `ci95_high`

## Required Metrics

- `completion_rate`
- `timeout_drop_rate`
- `unavailable_drop_rate`
- `deadline_violation_rate`
- `average_delay`
- `average_reward`
- `total_reward`

## Required Groupings

- by policy
- by policy and scenario
- by policy and workload level
- by policy and deadline pressure level
- by policy, workload level, and deadline pressure level

## Acceptance Criteria

- Feature 078 rows are consumed.
- No campaign cells are executed by Feature 079.
- All required policies are represented.
- All required scenarios are represented.
- All required metrics are summarized.
- CI95 bounds are computed using deterministic formulas.
- No ranking is produced.
- No winner is declared.
- No superiority claim is made.
- No final evaluation claim is made.

## Out of Scope

- executing campaign cells
- changing Feature 078 execution logic
- method ranking
- declaring winners
- final evaluation report
- ablation study
- sensitivity analysis
- model training
- dependency or lock-file edits
