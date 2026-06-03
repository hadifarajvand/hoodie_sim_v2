# Feature 083 Baseline Mapping Matrix

## Source
Baselines are extracted from the HOODIE paper comparative analysis section.

## Required Method Set

| Paper Method | Role | Repository Policy Name | Required Behavior | Current Gap |
|---|---|---|---|---|
| HOODIE | Proposed method | HOODIE | Use Feature 080 proposed-method runtime path | Existing HOODIE_PROPOSED must be normalized to HOODIE |
| Random Offloader | Baseline | RO | Randomly choose local, vertical, or horizontal offload; horizontal destination chosen uniformly among other edge agents | Existing RANDOM_POLICY must be renamed and checked for paper behavior |
| Full Local Computing | Baseline | FLC | Execute all tasks locally | Existing LOCAL_ONLY must be renamed and checked |
| Vertical Offloader | Baseline | VO | Offload all tasks vertically to cloud | Existing CLOUD_ONLY must be renamed and checked |
| Horizontal Offloader | Baseline | HO | Offload all tasks horizontally to another edge agent selected uniformly | Missing adapter |
| Balanced Cyclic Offloader | Baseline | BCO | Cycle through local, vertical, and horizontal actions in a balanced repeating order | Missing adapter |
| Minimum Queue Offloader | Baseline | MQO | Select the destination with minimum queue length among legal candidates | Missing adapter |

## Primary Paper Metrics
- task completion delay
- task drop ratio

## Secondary Repository Metrics
- completion_rate
- timeout_drop_rate
- unavailable_drop_rate
- deadline_violation_rate
- average_reward
- total_reward
- throughput
- queue_stability_score

## Invalid Policies
- ORIGINAL_HOODIE_BASELINE is invalid unless the paper explicitly defines it. It must be removed from Feature 083.
