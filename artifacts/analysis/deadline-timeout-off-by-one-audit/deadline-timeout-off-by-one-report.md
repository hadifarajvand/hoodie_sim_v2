# Deadline/Timeout Off-by-One Audit Report

- feature_id: `036-deadline-timeout-off-by-one-audit`
- timeout_slots: `20`
- slot_duration_seconds: `0.1`
- timeout_seconds: `2.0`
- contradiction_detected: `True`
- final_verdict: `deadline_timeout_boundary_repaired`
- no_paper_recovery_claims: `True`
- no_dependency_drift: `True`
- no_training_or_policy_drift: `True`
- no_reward_timing_change: `True`
- no_execution_time_contract_drift: `True`
- no_transmission_delay_contract_drift: `True`
- no_capacity_sharing_contract_drift: `True`
- no_campaign_rerun: `True`

## Deadline Contract
absolute_deadline_slot = arrival_slot + timeout_slots; completion_slot <= absolute_deadline_slot is completed; completion_slot > absolute_deadline_slot is dropped; exact-boundary completion is accepted.

## Old Runtime Behavior
deadline_rules.has_expired previously returned True for current_slot >= absolute_deadline_slot, which incorrectly treated exact-boundary current_slot == absolute_deadline_slot as expired.

## Repaired Runtime Components
- `src/environment/deadline_rules.py`

## Validated Runtime Components
- `src/environment/runtime_model.py`
- `src/environment/environment.py`
- `src/environment/gym_adapter.py`
- `src/environment/traffic_config.py`

## Boundary Cases Validated
- `current_slot < absolute_deadline_slot -> not expired`
- `current_slot == absolute_deadline_slot -> not expired`
- `current_slot > absolute_deadline_slot -> expired`
- `completion_slot == absolute_deadline_slot -> completed`
- `completion_slot == absolute_deadline_slot + 1 -> dropped`
- `arrival_slot = 5, timeout_slots = 20, absolute_deadline_slot = 25, completion_slot = 25 -> completed`

## Tests Added
- `test_task_not_expired_before_deadline`
- `test_task_not_expired_at_deadline`
- `test_task_expires_after_deadline`
- `test_completion_at_deadline_is_completed`
- `test_completion_after_deadline_is_dropped`
- `test_nonzero_arrival_exact_deadline_boundary`
- `test_environment_exact_deadline_completion_not_dropped`
- `test_reward_emitted_only_after_terminal_completion_drop`
- `test_drop_penalty_only_after_deadline_drop`
- `test_feature_033_execution_contract_not_changed`
- `test_feature_034_transmission_delay_contract_not_changed`
- `test_feature_035_capacity_sharing_contract_not_changed`
- `test_scope_guard_no_training_policy_dependency_campaign_drift`

## Tests Run
- `tests.unit.test_deadline_rules`
- `tests.unit.test_timeout_boundary_contract`
- `tests.integration.test_deadline_timeout_off_by_one_audit`
- `tests.integration.test_deadline_timeout_off_by_one_report`
- `tests.integration.test_deadline_timeout_off_by_one_scope_guard`
- `tests.integration.test_execution_time_flow`
- `tests.integration.test_transmission_delay_runtime_wiring`
- `tests.integration.test_public_cloud_capacity_sharing_flow`
- `tests.integration.test_mechanism_repair_timeout_drop`
