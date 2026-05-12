# Transmission Delay Runtime Wiring Report

- feature_id: `034-transmission-delay-runtime-wiring`
- horizontal_rate_mbps: `30.0`
- vertical_rate_mbps: `10.0`
- slot_duration_seconds: `0.1`
- rounding_policy: `ceil`
- final_verdict: `transmission_delay_runtime_wired`
- no_dependency_drift: `True`
- no_training_or_policy_drift: `True`
- no_reward_timing_change: `True`
- no_execution_time_contract_drift: `True`
- no_capacity_sharing_scope_creep: `True`
- no_campaign_rerun: `True`

## Old Invalid Behavior
Offload admission previously occurred after a fixed one-slot queue hop, ignoring payload size, link rate, and the computed transmission boundary.

## New Transmission Contract
Horizontal and vertical offloads compute transmission delay from payload bits, the configured link rate, slot duration, and the active rounding policy; admission occurs only when current_slot >= transmission_started_at + transmission_delay_slots.

## Admission Boundary Contract
If transmission starts at slot s and delay_slots is d, the task is admitted when current_slot >= s + d. The stored metadata records both the start and completion slots, and local tasks do not carry transmission metadata.

## Transmission Metadata Fields
- `transmission_started_at`
- `transmission_completed_at`
- `transmission_delay_slots`
- `transmission_delay_seconds`
- `transmission_payload_bits`
- `transmission_data_rate_bps`
- `transmission_rate_source`
- `transmission_rounding_policy`

## Wired Runtime Components
- `src/environment/gym_adapter.py`
- `src/environment/slot_engine.py`

## Validated Runtime Components
- `src/environment/offloading_queue.py`
- `src/environment/link_rate_config.py`
- `src/environment/runtime_model.py`

## Tests Added
- `test_horizontal_transmission_delay_uses_task_size_and_RH`
- `test_vertical_transmission_delay_uses_task_size_and_RV`
- `test_vertical_delay_exceeds_horizontal_delay_for_same_payload`
- `test_offload_not_admitted_before_delay_boundary`
- `test_offload_admitted_at_documented_boundary`
- `test_horizontal_metadata_recorded`
- `test_vertical_metadata_recorded`
- `test_local_path_has_no_transmission_metadata`
- `test_reward_not_emitted_during_transmission`
- `test_timeout_drop_includes_transmission_delay`
- `test_no_feature_033_execution_contract_drift`
- `test_no_dependency_training_policy_campaign_drift`

## Tests Run
- `tests.unit.test_link_rate_config`
- `tests.integration.test_transmission_delay_runtime_wiring`
- `tests.integration.test_execution_time_flow`
- `tests.integration.test_mechanism_repair_timeout_drop`
- `tests.integration.test_transmission_delay_runtime_report`
- `tests.integration.test_transmission_delay_runtime_scope_guard`
