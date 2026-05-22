# Quickstart: Exposure-Matrix Review

## Purpose

Use the committed Feature 044/045/046 artifacts plus the paper-default passive evidence to determine whether the exposure matrix is complete and whether action exposure, load dominance, or offload underexposure best explains the observed weakness.

## Run the review

Use the approved interpreter and the Feature 047 analysis entrypoint:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m src.analysis.exposure_matrix_review
```

## Expected outputs

- `artifacts/analysis/exposure-matrix-review/exposure-matrix-report.json`
- `artifacts/analysis/exposure-matrix-review/exposure-matrix-report.md`

The review must use:

- the paper-default `T = 110`
- seeds `[0, 1, 2]`
- strategies:
  - `environment_default_policy_probe`
  - `force_local_legal_probe`
  - `force_horizontal_legal_probe`
  - `force_vertical_legal_probe`
  - `mixed_legal_round_robin_probe`
- committed prior-feature artifacts from Features 044, 045, and 046

## Validation

Run the Feature 047 test bundle after implementation is complete:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_exposure_matrix_schema \
  tests.unit.test_exposure_matrix_metrics \
  tests.integration.test_exposure_matrix_review \
  tests.integration.test_exposure_matrix_report \
  tests.integration.test_exposure_matrix_scope_guard \
  tests.unit.test_lifecycle_trace_schema \
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
- The review uses passive evidence only.
- The report distinguishes legal exposure from selected actions.
- The report marks incomplete legality evidence explicitly instead of inventing zero counts.
- Older dirty-worktree-sensitive report tests remain out of scope.
- Feature 046 and earlier are validated through committed artifact checks, not rerun worktree-sensitive report-generation tests.

## Interpretation

- If the matrix is complete and legal-vs-selected exposure is measurable, the next feature should be `Feature 048 — Paper HOODIE Observation Vector`.
- If legality evidence is incomplete, the next feature should expand legality evidence before Feature 048.
- If load dominates independently of action exposure, the matrix should route toward load/admission assumption review before training.

