# Quickstart: Deadline/Timeout Off-by-One Audit

## Approved Interpreter

Use the approved environment only:

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python
```

## Implementation Target

This feature is scoped to timeout/deadline boundary semantics only. Expected touchpoints are:

- `src/environment/deadline_rules.py`
- `src/environment/runtime_model.py`
- `src/environment/environment.py`
- `src/environment/gym_adapter.py`
- `src/environment/traffic_config.py`
- `src/analysis/deadline_timeout_off_by_one_audit/`

## Validation Command

Run the targeted tests with the approved interpreter:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_deadline_rules \
  tests.unit.test_timeout_boundary_contract \
  tests.integration.test_deadline_timeout_off_by_one_audit \
  tests.integration.test_deadline_timeout_off_by_one_report \
  tests.integration.test_deadline_timeout_off_by_one_scope_guard \
  tests.integration.test_execution_time_flow \
  tests.integration.test_transmission_delay_runtime_wiring \
  tests.integration.test_public_cloud_capacity_sharing_flow \
  tests.integration.test_mechanism_repair_timeout_drop
```

## Expected Outcomes

- `timeout_slots = 20` and `slot_duration_seconds = 0.1` yield `timeout_seconds = 2.0`.
- Completion at the exact deadline is accepted.
- Completion after the deadline is dropped.
- Runtime helpers agree on the same boundary rule.
- Reward remains terminal-only and drop penalties apply only to dropped tasks.

## Report Artifacts

Generate:

- `artifacts/analysis/deadline-timeout-off-by-one-audit/deadline-timeout-off-by-one-report.json`
- `artifacts/analysis/deadline-timeout-off-by-one-audit/deadline-timeout-off-by-one-report.md`

The report must distinguish:
- old boundary behavior
- contradiction detected or not
- repaired runtime components, if any
- validated runtime components
- boundary cases validated
- tests added
- tests run
