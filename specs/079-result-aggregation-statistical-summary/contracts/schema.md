# Schema

Input: Feature 078 execution rows.

Metrics:
- completion_rate
- timeout_drop_rate
- unavailable_drop_rate
- deadline_violation_rate
- average_delay
- average_reward
- total_reward

Summary fields:
- mean
- std
- min
- max
- count
- ci95_low
- ci95_high

Groupings:
- policy
- policy + scenario
- policy + workload
- policy + deadline pressure
