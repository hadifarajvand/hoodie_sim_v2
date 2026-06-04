# HOODIE System-Model Approximation Backlog

This file records the system-model mechanisms that are not missing or wrong, but are still not exact reproductions of the HOODIE paper implementation model.

These items were accepted by Feature 086 only as `approximate_documented`. They should not be used to claim exact full HOODIE reproduction.

## Summary

| Category | Count |
|---|---:|
| Exact mechanisms from Feature 086 | 7 |
| Approximate documented mechanisms | 15 |
| Blocking missing/wrong/not_exercised mechanisms | 0 |

## Exact Mechanisms Already Acceptable

| Mechanism | Status |
|---|---|
| `horizontal_transmission_delay` | exact |
| `vertical_transmission_delay` | exact |
| `hybrid_action_model` | exact |
| `hoodie_claim_boundary` | exact |
| `official_paper_baselines` | exact |
| `mleo_min_total_latency` | exact |
| `output_metrics_readiness` | exact |

## Approximation Repair Candidates

| Mechanism | Current Status | Why It Matters | Future Repair Direction |
|---|---|---|---|
| `three_tier_topology` | approximate_documented | Paper uses a cloud-edge-IoT continuum; simulator currently uses deterministic abstraction/evidence-layer topology. | Introduce explicit topology model with task-source layer, EA layer, and cloud layer. |
| `edge_agent_set_cloud_node` | approximate_documented | EA/cloud are represented through scenario/context rather than a full distributed runtime. | Add explicit EdgeAgent and CloudNode runtime entities if output divergence requires it. |
| `horizontal_connectivity_legality` | approximate_documented | Legality exists, but full paper-like adjacency/topology matrix is not guaranteed. | Add explicit EA-to-EA adjacency matrix and validate legal/illegal offload paths against it. |
| `vertical_ea_cloud_path` | approximate_documented | Cloud path is traced, but cloud service/queue abstraction may be simplified. | Add explicit vertical link and cloud service path decomposition. |
| `task_model` | approximate_documented | Task attributes exist, but generator may not match paper exactly. | Align task ID, size, CPU density, timeout, and arrival semantics with paper definitions. |
| `workload_arrival_representation` | approximate_documented | Paper workload/stochastic arrivals may differ from deterministic benchmark scenarios. | Implement paper-compatible workload/stochastic arrival generator if needed. |
| `private_queue_behavior` | approximate_documented | Queue behavior is evidence-layer; full event-level queue semantics may be simplified. | Implement explicit private FIFO/local execution queue lifecycle. |
| `offloading_queue_behavior` | approximate_documented | Offload queue is represented through candidate/timing abstraction. | Implement explicit offloading queue state transitions if output mismatch suggests queue dynamics matter. |
| `public_cloud_queue_behavior` | approximate_documented | Cloud/public queue may not be a full independent queue simulator. | Add explicit public/cloud queue capacity, service discipline, and waiting-time lifecycle. |
| `local_execution_delay` | approximate_documented | Local delay is present in outputs, but not necessarily full event-level simulation. | Tie local execution delay to explicit queue service and task CPU demand lifecycle. |
| `remote_cloud_execution_delay` | approximate_documented | Remote/cloud execution term exists, but remote service lifecycle may be simplified. | Separate remote edge execution from cloud execution with explicit service models. |
| `waiting_time_completion_time` | approximate_documented | Waiting/completion are computed for audit/output, but full lifecycle reconstruction may be simplified. | Implement event-level arrival/start/finish timestamps for each queue path. |
| `timeout_drop_unavailability_behavior` | approximate_documented | Drop outcomes are tracked, but timeout/drop semantics may be approximated. | Align timeout and deadline violation semantics exactly with paper equations. |
| `two_stage_decision_boundary` | approximate_documented | Paper has two-stage decision logic; runtime may collapse to a single action. | Implement explicit DM1 local-vs-offload decision and DM2 destination-selection decision traces. |
| `reward_cost_boundary` | approximate_documented | Reward/cost is mapped conservatively, not proven exact against paper coefficients/sign conventions. | Audit reward equations and implement exact coefficients/terminal penalties if needed. |

## Recommended Future Repair Order

1. `workload_arrival_representation`
2. `horizontal_connectivity_legality`
3. `private_queue_behavior`
4. `offloading_queue_behavior`
5. `public_cloud_queue_behavior`
6. `waiting_time_completion_time`
7. `timeout_drop_unavailability_behavior`
8. `two_stage_decision_boundary`
9. `reward_cost_boundary`
10. topology/entity refinements if output divergence persists

## Decision For Now

Do not implement these repairs now.

Proceed with output analysis from Feature 087 first. Use this backlog if output comparison shows divergence that plausibly comes from these approximations.
