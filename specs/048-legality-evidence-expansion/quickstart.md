# Quickstart: Legality Evidence Expansion

## Purpose

Capture passive legality evidence for the paper-default strategy/seed grid without changing runtime behavior, then report whether Feature 049 can rerun the exposure matrix with legality evidence.

## Run the feature

Use the approved interpreter and the Feature 048 passive instrumentation entrypoint:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m src.analysis.legality_evidence_expansion
```

## Expected outputs

- `artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json`
- `artifacts/analysis/legality-evidence-expansion/legality-evidence-report.md`

The feature must preserve:

- the paper-default `T = 110`
- seeds `[0, 1, 2]`
- the five approved probe strategies
- the selected action sequence
- the reward sequence
- terminal outcomes
- queue progression
- timeout/deadline behavior
- capacity/execution behavior
- transmission behavior

## Validation

Run the Feature 048 test bundle after implementation is complete:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_legality_evidence_schema \
  tests.unit.test_legality_evidence_metrics \
  tests.unit.test_legality_evidence_behavior_equivalence \
  tests.integration.test_legality_evidence_expansion \
  tests.integration.test_legality_evidence_report \
  tests.integration.test_legality_evidence_scope_guard \
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
- No policy, reward, timeout, capacity, or transmission semantics change.
- The report distinguishes legality coverage from selected action behavior.
- Missing legality evidence is reported as null/unavailable, not zero.
- Behavior equivalence against a no-legality-capture baseline is explicit.
- Older dirty-worktree-sensitive report tests remain out of scope.
- Feature 047 and earlier are validated through committed artifact checks inside the Feature 048 tests, not rerun worktree-sensitive report-generation tests.

## Feature 047 prerequisite check

Feature 048 tests must validate the committed Feature 047 report artifact at `artifacts/analysis/exposure-matrix-review/exposure-matrix-report.json` and assert:

- `feature_id = 047-exposure-matrix-review`
- `final_verdict = exposure_matrix_incomplete_requires_legality_evidence`
- `recommended_next_feature = legality evidence expansion before Feature 048`
- `legal_action_evidence_source = unavailable_in_committed_artifacts`
- `legal_action_evidence_coverage_ratio = 0.0`
- `selected_illegal_action_count = null`
- `prior_feature_gates_verified` includes Features 037 through 046
- `no_runtime_repair_performed = true`
- `no_training_started = true`
- `no_paper_reproduction_claim = true`

## Interpretation

- If legality evidence covers the full strategy/seed decision population and behavior equivalence passes, the next feature should be `Feature 049 — Exposure-Matrix Rerun with Legality Evidence`.
- If legality evidence is partial, the next feature should expand trace depth before the exposure-matrix rerun.
- If legality evidence cannot be extracted without semantic runtime change, the next feature should be a public legality helper before the exposure-matrix rerun.
