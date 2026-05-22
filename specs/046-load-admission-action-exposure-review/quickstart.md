# Quickstart: Load, Admission, and Action-Exposure Review

## Purpose

Use Feature 044 passive traces and the Feature 045 report to explain whether paper-default completion weakness is primarily caused by load pressure, admission serialization, action exposure, queue pressure, or offload-path pressure.

## Run the review

Use the approved interpreter and the Feature 046 analysis entrypoint:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m src.analysis.load_admission_action_exposure_review
```

## Expected outputs

- `artifacts/analysis/load-admission-action-exposure-review/load-admission-action-exposure-report.json`
- `artifacts/analysis/load-admission-action-exposure-review/load-admission-action-exposure-report.md`

The review must use:

- Feature 044 passive lifecycle trace report as the primary trace input
- Feature 045 completion root-cause report as the primary verdict input
- paper-default `T = 110`
- seeds `[0, 1, 2]`
- strategies:
  - `environment_default_policy_probe`
  - `force_local_legal_probe`
  - `force_horizontal_legal_probe`
  - `force_vertical_legal_probe`
  - `mixed_legal_round_robin_probe`

## Validation

Run the Feature 046 test bundle after implementation is complete:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_load_admission_action_exposure_schema \
  tests.unit.test_load_admission_action_exposure_metrics \
  tests.integration.test_load_admission_action_exposure_review \
  tests.integration.test_load_admission_action_exposure_report \
  tests.integration.test_load_admission_action_exposure_scope_guard \
  tests.unit.test_lifecycle_trace_schema \
  tests.integration.test_passive_lifecycle_trace_report \
  tests.unit.test_task_completion_formula_audit \
  tests.unit.test_task_completion_lifecycle_schema \
  tests.unit.test_paper_default_terminal_exposure_config \
  tests.unit.test_smoke_training_contract \
  tests.unit.test_paper_hoodie_network_config \
  tests.unit.test_paper_hoodie_network_shapes \
  tests.unit.test_training_foundation_contract \
  tests.integration.test_deadline_timeout_off_by_one_audit \
  tests.integration.test_execution_time_flow \
  tests.integration.test_transmission_delay_runtime_wiring \
  tests.integration.test_public_cloud_capacity_sharing_flow
```

Validation expectations:

- No runtime repair is performed.
- The review uses Feature 044 traces and the Feature 045 report only.
- The report quantifies load, admission, action exposure, queue, and offload-path pressure.
- The report ranks the dominant pressure source or states that evidence is inconclusive.
- The report recommends the next diagnostic feature honestly.
- Older pointer-sensitive report tests remain out of scope.

## Interpretation

- If action exposure is dominant, the next feature should focus on `Feature 047 — Paper HOODIE Observation Vector`.
- If mixed load/action pressure is dominant, the next feature should focus on `exposure-matrix review` before Feature 047.
- If load or admission pressure is dominant, the next feature should focus on load/admission assumptions or `exposure-matrix review`.
- If the evidence remains insufficient, the next feature should deepen passive diagnosis rather than changing runtime semantics.
