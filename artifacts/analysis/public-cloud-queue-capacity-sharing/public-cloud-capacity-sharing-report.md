# Public/Cloud Queue Capacity Sharing Report

- feature_id: `035-public-cloud-queue-capacity-sharing-contract`
- sharing_rule: `deterministic_equal_share_at_slot_start`
- redistribution_policy: `no_same_slot_redistribution`
- final_verdict: `public_cloud_capacity_sharing_wired`
- no_paper_recovery_claims: `True`
- no_dependency_drift: `True`
- no_training_or_policy_drift: `True`
- no_reward_timing_change: `True`
- no_execution_time_contract_drift: `True`
- no_transmission_delay_contract_drift: `True`
- no_campaign_rerun: `True`

## Old Invalid Behavior
Each public/cloud queue previously received the full host capacity independently, so multiple active heads could silently multiply the configured per-slot CPU budget.

## New Capacity Sharing Contract
Public EA heads are grouped by destination host_node_id and cloud heads are grouped under host_node_id == "cloud"; each host pool splits its fixed per-slot CPU capacity equally across the active heads present at slot start.

## Wired Runtime Components
- `src/environment/gym_adapter.py`

## Validated Runtime Components
- `src/environment/public_queue.py`
- `src/environment/offloading_queue.py`
- `src/environment/compute_config.py`
- `src/environment/execution_helper.py`
- `src/environment/link_rate_config.py`

## Destination Kinds Validated
- `public`
- `cloud`
- `local`

## Tests Added
- `test_single_public_queue_gets_full_edge_capacity`
- `test_two_public_queues_same_host_share_edge_capacity_equally`
- `test_two_public_queues_different_hosts_do_not_share_capacity`
- `test_two_cloud_queues_share_global_cloud_capacity_equally`
- `test_total_public_host_consumption_does_not_exceed_edge_capacity`
- `test_total_cloud_consumption_does_not_exceed_cloud_capacity`
- `test_capacity_sharing_order_is_deterministic`
- `test_local_private_execution_not_changed`
- `test_feature_033_execution_contract_not_changed`
- `test_feature_034_transmission_delay_contract_not_changed`
- `test_reward_timing_not_changed`
- `test_scope_guard_no_training_policy_dependency_campaign_drift`

## Tests Run
- `tests.unit.test_public_cloud_capacity_sharing`
- `tests.integration.test_public_cloud_capacity_sharing_flow`
- `tests.integration.test_public_cloud_capacity_sharing_report`
- `tests.integration.test_public_cloud_capacity_sharing_scope_guard`
- `tests.integration.test_execution_time_flow`
- `tests.integration.test_transmission_delay_runtime_wiring`
