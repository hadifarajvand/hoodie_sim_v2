# Feature 080 - Base Paper Evaluation Ranking

## Goal

Evaluate the base paper method against its baseline policies using the base paper metric family.

Feature 080 must not evaluate the user's thesis method.

## Target Method

The target method is the proposed method from the base HOODIE paper.

Do not use the user's DCQ or deadline-aware thesis method here.

## Input

Feature 079 aggregation report.

## Metric Family

Use the metrics already available from Feature 078 and Feature 079 that match the base paper evaluation layer:

Higher is better:
- average_reward
- total_reward
- completion_rate

Lower is better:
- average_delay
- timeout_drop_rate
- unavailable_drop_rate

Deadline violation can be reported as an auxiliary metric only if it exists in the current report. It must not be treated as the main thesis metric here.

## Required Output

- all-policy evaluation table
- base-paper proposed method row
- baseline rows
- per-metric ordering
- compact evaluation notes

## Rules

- consume Feature 079 only
- do not execute campaign cells
- do not recompute raw rows
- include all policies
- use base-paper metric direction
- keep claim boundary explicit

## Boundary

Feature 080 may report current simulation evidence for the base paper method versus baselines.

Feature 080 must not claim thesis-method superiority.
