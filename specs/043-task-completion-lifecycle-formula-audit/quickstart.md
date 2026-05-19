# Quickstart: Task Completion Lifecycle and Formula Audit

## Purpose

Generate a diagnostic report that explains why paper-default `T = 110` probes produce reward-bearing terminal drops but zero completions.

## Run the audit

Use the approved interpreter and the Feature 043 analysis entrypoint:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m src.analysis.task_completion_lifecycle_formula_audit
```

## Expected outputs

- `artifacts/analysis/task-completion-lifecycle-formula-audit/completion-lifecycle-audit-report.json`
- `artifacts/analysis/task-completion-lifecycle-formula-audit/completion-lifecycle-audit-report.md`

## Validation

Run the Feature 043 test bundle after the implementation is complete:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_task_completion_formula_audit \
  tests.unit.test_task_completion_lifecycle_schema \
  tests.integration.test_task_completion_lifecycle_audit \
  tests.integration.test_task_completion_lifecycle_report \
  tests.integration.test_task_completion_lifecycle_scope_guard \
  tests.unit.test_paper_default_terminal_exposure_config \
  tests.unit.test_smoke_training_contract \
  tests.integration.test_smoke_training_report \
  tests.unit.test_paper_hoodie_network_config \
  tests.unit.test_paper_hoodie_network_shapes \
  tests.integration.test_paper_hoodie_network_report \
  tests.unit.test_training_foundation_contract \
  tests.integration.test_training_foundation_contract_report \
  tests.integration.test_deadline_timeout_off_by_one_audit \
  tests.integration.test_transmission_delay_runtime_wiring \
  tests.integration.test_public_cloud_capacity_sharing_flow \
  tests.integration.test_execution_time_flow
```

Feature 042 prerequisite artifact referenced by this validation scope:

- `artifacts/analysis/paper-default-terminal-exposure-probe/terminal-exposure-report.json`

## Interpretation

- If the audit finds a lifecycle or runtime bug, the next feature should be a dedicated runtime repair feature.
- If the audit only shows queue pressure or insufficient observation, the next feature should focus on better observation or exploration, not runtime repair.
