# Quickstart: Runtime Adoption of Approved Assumption Registry

## Purpose

This feature applies the approved Feature 031 assumptions to runtime configuration and validation boundaries without changing training or dependency behavior.

## Expected Workflow

1. Verify the Feature 031 registry and report artifacts are available and unchanged.
2. Load the approved compute capacities, topology adjacency, link-rate, timeout, and aggregation contracts from the approved assumptions.
3. Run the targeted runtime adoption tests.
4. Generate the runtime adoption report with provenance and validation evidence.

## Validation Commands

- Run the targeted runtime-adoption unit and integration tests with the approved interpreter:
  - `PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest tests.unit.test_compute_config tests.unit.test_runtime_adoption_approved_assumption_registry tests.integration.test_runtime_adoption_report tests.integration.test_runtime_adoption_scope_guard`
  - `PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest tests.unit.test_gym_environment tests.unit.test_action_masking tests.unit.test_traffic_config tests.integration.test_execution_time_flow tests.integration.test_evaluation_runner tests.integration.test_policy_interface_flow`
- Run the approved-topology vertical/cloud legality check using `TopologyGraph.from_approved_assumption_registry()` to ensure cloud offload remains legal even when the Figure 7 adjacency contains only horizontal EA neighbors.
- Inspect the adoption report for the consumed assumption IDs and runtime component changes.
- Verify the final diff only includes the approved runtime-adoption files.

## Success Checks

- Compute capacities match the approved assumption values.
- Topology legality forbids self-offload and non-neighbor horizontal offload.
- Approved topology still allows vertical/cloud offload without requiring `cloud` inside the Figure 7 adjacency map.
- Cloud-facing vertical rate is `10 Mbps` and no extra cloud-specific rate exists.
- Timeout validation uses `20` slots and `0.1` second slot duration.
- Aggregation uses per-agent sum then arithmetic mean and excludes no-task/NaN/omitted slots.
- No training, dependency, or campaign drift occurs.
