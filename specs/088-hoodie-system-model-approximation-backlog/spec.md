# Feature 088: HOODIE System-Model Approximation Backlog

## Purpose

Feature 088 records the remaining HOODIE system-model mechanisms that are currently accepted as `approximate_documented` by Feature 086, but are not yet exact implementations.

This feature is a backlog and repair-plan feature only. It must not be implemented now unless explicitly activated later.

The project may continue with output analysis from Feature 087. If simulator outputs diverge from the paper or if higher-fidelity HOODIE reproduction is required, this backlog defines the mechanisms to repair first.

## Current Decision

Do not apply these repairs now.

Proceed with output analysis first. Return to this feature if:

- Feature 087 output comparison shows unacceptable divergence;
- thesis baseline fidelity requires stricter HOODIE reproduction;
- the user decides documented approximations are no longer acceptable.

## Approximation Inventory

The following mechanisms were reported as `approximate_documented` in Feature 086 and should be treated as future repair candidates:

1. `three_tier_topology`
2. `edge_agent_set_cloud_node`
3. `horizontal_connectivity_legality`
4. `vertical_ea_cloud_path`
5. `task_model`
6. `workload_arrival_representation`
7. `private_queue_behavior`
8. `offloading_queue_behavior`
9. `public_cloud_queue_behavior`
10. `local_execution_delay`
11. `remote_cloud_execution_delay`
12. `waiting_time_completion_time`
13. `timeout_drop_unavailability_behavior`
14. `two_stage_decision_boundary`
15. `reward_cost_boundary`

## Claim Boundary

Feature 086 allows output comparison under documented approximations. It does not prove exact one-to-one reproduction of the HOODIE paper system model.

Feature 088 exists so these approximations are not forgotten or silently treated as exact implementation.

## Out of Scope For Now

- No code repair now.
- No simulator rewrite now.
- No thesis method.
- No DCQ.
- No custom queue redesign.
- No new proposed method.
- No empirical figure reproduction claim.

## Future Acceptance Criteria

If this feature is activated later, it should convert approximation candidates into exact implementations where feasible and produce evidence artifacts proving which approximations were removed.
