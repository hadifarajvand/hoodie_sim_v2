# Execution-Time Contract Repair Report

- feature_id: `033-execution-time-contract-repair`
- final_verdict: `execution_time_contract_repaired`
- no_dependency_drift: `True`
- no_training_or_policy_drift: `True`
- no_reward_timing_change: `True`
- no_transmission_delay_scope_creep: `True`
- no_capacity_sharing_scope_creep: `True`

## Old Invalid Behavior
Local/private execution previously short-circuited when timeout_length > 1 and cycles_before exceeded capacity, consuming all remaining cycles in one slot.

## New Execution Contract
Every supported destination consumes at most its configured per-slot capacity using cycles_consumed = min(cycles_before, compute_capacity) and cycles_after = max(0, cycles_before - compute_capacity).

## Completion Slot Contract
Completion is recorded at the end of the slot in which remaining cycles reach zero.

## Destination Kinds Validated
- `local/private/self`
- `public/edge/horizontal`
- `cloud/vertical`

## Repaired Runtime Components
- `src/environment/execution_helper.py`
- `src/environment/gym_adapter.py`
- `src/environment/runtime_model.py`

## Tests Added
- `test_local_execution_no_single_slot_shortcut_when_cycles_exceed_capacity`
- `test_local_execution_consumes_at_most_agent_capacity_per_slot`
- `test_public_execution_consumes_at_most_edge_capacity_per_slot`
- `test_cloud_execution_consumes_at_most_cloud_capacity_per_slot`
- `test_execution_exact_capacity_boundary_completion_contract`
- `test_cycles_remaining_decreases_monotonically`
- `test_environment_local_execution_requires_multiple_slots_when_cycles_exceed_capacity`
- `test_timeout_drop_still_uses_multislot_execution_contract`
- `test_reward_emitted_only_after_terminal_completion_or_drop`
- `test_feature_033_scope_guard_no_training_policy_dependency_drift`

## Tests Run
- `python -m unittest tests.unit.test_execution_helper`
- `python -m unittest tests.unit.test_execution_model`
- `python -m unittest tests.integration.test_execution_time_flow`
- `python -m unittest tests.integration.test_mechanism_repair_timeout_drop`
