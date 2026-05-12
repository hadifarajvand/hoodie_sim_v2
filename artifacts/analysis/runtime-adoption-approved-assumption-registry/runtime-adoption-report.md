# Runtime Adoption Report

- feature_id: `032-runtime-adoption-approved-assumption-registry`
- final_verdict: `runtime_adoption_completed_with_user_approved_assumptions`
- no_paper_recovery_claims: `True`
- no_dependency_drift: `True`
- no_training_or_policy_drift: `True`
- no_reward_timing_change: `True`
- no_campaign_rerun: `True`

## Consumed Assumptions
- `Figure_7_adjacency`
- `legal_horizontal_destinations`
- `EA_private_cpu_capacity`
- `EA_public_cpu_capacity`
- `cloud_cpu_capacity`
- `cloud_data_rate`
- `timeout_value`
- `multi_agent_aggregation_reduction_order`

## Runtime Components Changed
- `src/environment/compute_config.py`
- `src/environment/topology.py`
- `src/environment/gym_adapter.py`
- `src/environment/link_rate_config.py`
- `src/environment/traffic_config.py`
- `src/evaluation/aggregate_metrics.py`
- `src/evaluation/runner.py`

## Runtime Components Validated
- `Figure_7_adjacency`
- `legal_horizontal_destinations`
- `approved_figure7_topology_keeps_vertical_cloud_offload_legal`
- `EA_private_cpu_capacity`
- `EA_public_cpu_capacity`
- `cloud_cpu_capacity`
- `cloud_data_rate`
- `timeout_value`
- `multi_agent_aggregation_reduction_order`

## Tests Added
- `test_compute_config_uses_approved_assumption_capacities`
- `test_topology_figure7_adjacency_invariants`
- `test_horizontal_legality_neighbor_only_no_self_no_non_neighbor`
- `test_action_mask_rejects_non_neighbor_horizontal_destinations`
- `test_approved_figure7_topology_keeps_vertical_cloud_offload_legal`
- `test_cloud_vertical_rate_uses_RV_10mbps_no_fake_cloud_rate`
- `test_timeout_contract_20_slots_2_seconds`
- `test_timeout_drop_behavior_consumes_runtime_contract`
- `test_aggregation_per_agent_episode_sum_then_mean`
- `test_aggregation_excludes_nan_no_task_omitted_slots`
- `test_feature_032_scope_guard_no_training_policy_dependency_drift`

## Tests Run
- `python -m unittest tests.unit.test_compute_config`
- `python -m unittest tests.unit.test_runtime_adoption_approved_assumption_registry`
- `python -m unittest tests.integration.test_runtime_adoption_report`

## Old Stale Values Replaced
- `ComputeConfig defaults 32.0/64.0/128.0 replaced with 0.5/0.5/3.0`
- `EvaluationRunner compute defaults 128.0/256.0/512.0 replaced with 0.5/0.5/3.0`
