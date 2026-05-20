# Quickstart: Passive Runtime Lifecycle Trace Instrumentation

## Purpose

Collect passive lifecycle trace evidence for paper-default `T = 110` runs so downstream diagnostics can explain why completions are absent.

Report regeneration must happen from a clean workspace, except for an optional local `.specify/feature.json` pointer file. `AGENTS.md` must be clean before regeneration.

## Run the instrumentation audit

Use the approved interpreter and the Feature 044 analysis entrypoint:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m src.analysis.passive_runtime_lifecycle_trace_instrumentation
```

## Expected outputs

- `artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json`
- `artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.md`

The generated report sample must reflect the approved Feature 044 paper-default probe configuration:

- `T = 110`
- `timeout_slots = 20`
- task sizes in `[2.0, 5.0]`
- `processing_density_gcycles_per_mbit = 0.297`
- private/public/cloud CPU capacities `0.5/0.5/3.0`
- horizontal rate `30 Mbps`
- vertical rate `10 Mbps`

## Validation

Run the Feature 044 test bundle after the implementation is complete:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_lifecycle_trace_schema \
  tests.unit.test_lifecycle_trace_behavior_equivalence \
  tests.integration.test_passive_lifecycle_trace_runtime \
  tests.integration.test_passive_lifecycle_trace_report \
  tests.integration.test_passive_lifecycle_trace_scope_guard \
  tests.unit.test_task_completion_formula_audit \
  tests.unit.test_task_completion_lifecycle_schema \
  tests.integration.test_task_completion_lifecycle_audit \
  tests.integration.test_task_completion_lifecycle_report \
  tests.integration.test_task_completion_lifecycle_scope_guard \
  tests.unit.test_paper_default_terminal_exposure_config \
  tests.unit.test_paper_default_terminal_exposure_schema \
  tests.unit.test_smoke_training_contract \
  tests.integration.test_smoke_training_report \
  tests.unit.test_paper_hoodie_network_config \
  tests.unit.test_paper_hoodie_network_shapes \
  tests.integration.test_paper_hoodie_network_report \
  tests.unit.test_training_foundation_contract \
  tests.integration.test_training_foundation_contract_report \
  tests.integration.test_deadline_timeout_off_by_one_audit \
  tests.integration.test_execution_time_flow \
  tests.integration.test_transmission_delay_runtime_wiring \
  tests.integration.test_public_cloud_capacity_sharing_flow
```

Feature 043 prerequisite artifact referenced by this validation scope:

- `artifacts/analysis/task-completion-lifecycle-formula-audit/completion-lifecycle-audit-report.json`

Validation expectations:

- `no_unrelated_dirty_files` must be `true` when only the optional `.specify/feature.json` pointer is dirty.
- The report must include a paper-default lifecycle sample, not an ad-hoc fixture sample.
- `deadline_expired` must be visible on drop paths whenever `task_dropped` is observed.
- `task_completed_supported` must remain `true` even if no completion is observed in the sample.
- Duplicate behavior-equivalence check names must not appear.
- Older Feature 042 report tests that inspect active pointer state remain out of scope.

## Interpretation

- If tracing changes behavior, the feature is a failure.
- If tracing reveals a runtime bug, the next feature should be a dedicated runtime repair feature.
- If tracing remains insufficient, the next feature should expand passive instrumentation rather than alter runtime behavior.
