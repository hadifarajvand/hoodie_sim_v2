# Quickstart: Selected-Action Family and Per-Action Outcome Evidence Expansion

## Environment

Use the approved interpreter:

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python
```

## Generate the passive evidence report

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 \
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m src.analysis.selected_action_family_per_action_outcome_evidence
```

This writes:

- `artifacts/analysis/selected-action-family-per-action-outcome-evidence/selected-action-family-outcome-evidence-report.json`
- `artifacts/analysis/selected-action-family-per-action-outcome-evidence/selected-action-family-outcome-evidence-report.md`

## Validate the passive evidence contract

Run the Feature 050 unit and integration tests only after the passive evidence package and report artifacts exist.

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 \
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_selected_action_outcome_evidence_schema \
  tests.unit.test_selected_action_outcome_evidence_metrics \
  tests.unit.test_selected_action_outcome_behavior_equivalence \
  tests.integration.test_selected_action_outcome_evidence \
  tests.integration.test_selected_action_outcome_report \
  tests.integration.test_selected_action_outcome_scope_guard \
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

- The report distinguishes available from unavailable selected-action family evidence.
- Selected-action counts are trace-backed when present and not faked when absent.
- Selected actions join to task and terminal outcome evidence when the keys exist.
- Feature 049 rerun readiness is blocked until the evidence gates are complete.
