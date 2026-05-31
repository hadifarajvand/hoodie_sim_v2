# Feature 080 - Evaluation Ranking

## Goal

Build an evaluation layer over Feature 079 summaries.

Feature 080 ranks all policies together using declared metrics and directions.

## Input

Feature 079 aggregation report.

## Required Metrics

Higher is better:
- completion_rate
- average_reward
- total_reward

Lower is better:
- timeout_drop_rate
- unavailable_drop_rate
- deadline_violation_rate
- average_delay

## Required Output

- all-policy ranking table
- per-metric ranking table
- composite score table
- evaluation notes

## Rules

- consume Feature 079 only
- do not execute campaign cells
- do not recompute raw rows
- include all policies
- include all required metrics
- record metric direction
- record score formula
- keep claim boundary explicit

## Boundary

Feature 080 may report ranking evidence from current summaries.

Feature 080 must not claim final paper proof.
