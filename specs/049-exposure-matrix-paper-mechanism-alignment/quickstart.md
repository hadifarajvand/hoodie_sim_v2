# Quickstart: Exposure Matrix Rerun and Paper Mechanism Alignment

## Purpose

Use Feature 048 legality evidence to rerun the exposure matrix, audit the paper HOODIE observation and timing contract, and decide whether the next training-contract bundle is ready.

## Run the feature

Use the approved interpreter and the Feature 049 passive analysis entrypoint:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m src.analysis.exposure_matrix_paper_mechanism_alignment
```

## Expected outputs

- `artifacts/analysis/exposure-matrix-paper-mechanism-alignment/exposure-matrix-paper-mechanism-report.json`
- `artifacts/analysis/exposure-matrix-paper-mechanism-alignment/exposure-matrix-paper-mechanism-report.md`

## Validation

Run the Feature 049 test bundle after implementation is complete:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_exposure_matrix_paper_mechanism_schema \
  tests.unit.test_exposure_matrix_paper_mechanism_metrics \
  tests.integration.test_exposure_matrix_paper_mechanism_alignment \
  tests.integration.test_exposure_matrix_paper_mechanism_report \
  tests.integration.test_exposure_matrix_paper_mechanism_scope_guard \
  tests.unit.test_legality_evidence_schema \
  tests.unit.test_legality_evidence_metrics \
  tests.unit.test_legality_evidence_behavior_equivalence \
  tests.integration.test_legality_evidence_expansion \
  tests.integration.test_legality_evidence_report \
  tests.integration.test_legality_evidence_scope_guard \
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

- No training, optimizer, replay, or target updates are started.
- No dirty-worktree-sensitive older report tests are rerun.
- Features 043 through 048 are validated through committed artifact checks inside the Feature 049 tests.
- The report states whether the exposure matrix is complete enough for readiness and whether the observation/formula audits pass.
- If the exposure matrix is complete and the audits pass, the report recommends `Feature 050 — DDQN Training Contract Bundle`.

## Interpretation

- If the exposure matrix is incomplete or biased, the next feature must repair or expand the relevant alignment gap.
- If the observation vector is incomplete, the next feature must repair observation-vector coverage before training.
- If a formula or unit mismatch is detected, the next feature must repair the formula/unit contract before training.
- If the simulator contract contradicts the paper mechanism, the next feature must route that contradiction to a future repair feature.
