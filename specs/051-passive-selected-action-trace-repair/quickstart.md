# Quickstart: Passive Selected-Action Trace Repair

## Environment

Use the approved interpreter:

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python
```

## Generate the passive trace repair report

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 \
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m src.analysis.passive_selected_action_trace_repair
```

This writes:

- `artifacts/analysis/passive-selected-action-trace-repair/passive-selected-action-trace-repair-report.json`
- `artifacts/analysis/passive-selected-action-trace-repair/passive-selected-action-trace-repair-report.md`

## Validate the passive trace repair contract

Run the Feature 051 unit and integration tests only after the passive trace repair package and report artifacts exist.

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 \
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_passive_selected_action_trace_schema \
  tests.unit.test_passive_selected_action_trace_metrics \
  tests.unit.test_passive_selected_action_trace_behavior_equivalence \
  tests.integration.test_passive_selected_action_trace_repair \
  tests.integration.test_passive_selected_action_trace_report \
  tests.integration.test_passive_selected_action_trace_scope_guard \
  tests.unit.test_lifecycle_trace_schema \
  tests.unit.test_task_completion_lifecycle_schema \
  tests.unit.test_paper_default_terminal_exposure_config \
  tests.unit.test_smoke_training_contract \
  tests.unit.test_training_foundation_contract \
  tests.integration.test_execution_time_flow \
  tests.integration.test_transmission_delay_runtime_wiring \
  tests.integration.test_public_cloud_capacity_sharing_flow
```

## What success looks like

- The report exposes selected-action trace schema, emission summary, and selected-action family trace readiness.
- Selected-action-to-task join keys and terminal outcome join keys are trace-backed rather than inferred.
- Behavior equivalence remains stable and unique checks prevent redundant duplication.
- Feature 050 rerun readiness is blocked until the passive trace emits the required join evidence.
