# Feature 083 Data Model

## Purpose
Defines the data model required to evaluate HOODIE against the six baselines extracted from the HOODIE paper.

## Policies
- HOODIE: Feature 080 proposed method.
- RO: Random Offloader.
- FLC: Full Local Computing.
- VO: Vertical Offloader.
- HO: Horizontal Offloader.
- BCO: Balanced Cyclic Offloader.
- MQO: Minimum Queue Offloader.

## Evaluation Row
Each raw row must include:
- policy
- scenario
- workload
- deadline_pressure
- seed
- task_count
- completed_count
- timeout_drop_count
- unavailable_drop_count
- deadline_violation_count
- average_delay
- drop_ratio
- completion_rate
- throughput
- average_reward
- total_reward
- queue_stability_score
- decision_trace_summary

## Aggregate Row
Each aggregate row must include:
- policy
- average_delay
- drop_ratio
- completion_rate
- throughput
- average_reward
- total_reward
- queue_stability_score

## Report Model
The report must include:
- paper baseline coverage
- adapter mapping status
- primary paper metrics
- secondary repository metrics
- ranking by metric
- gaps and limitations
- scope proof
- claim boundary
