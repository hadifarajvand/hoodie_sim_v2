# Quickstart: Completion Root-Cause Diagnosis Using Passive Lifecycle Traces

## Purpose

Use Feature 044 passive lifecycle traces to explain why task completions are weak or absent under the paper-default runtime.

## Run the diagnosis

Use the approved interpreter and the Feature 045 analysis entrypoint:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m src.analysis.completion_root_cause_diagnosis
```

## Expected outputs

- `artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.json`
- `artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.md`

The diagnosis must use:

- Feature 044 passive lifecycle trace report as the primary input
- paper-default `T = 110`
- seeds `[0, 1, 2]`
- strategies:
  - `environment_default_policy_probe`
  - `force_local_legal_probe`
  - `force_horizontal_legal_probe`
  - `force_vertical_legal_probe`
  - `mixed_legal_round_robin_probe`

## Validation

Run the Feature 045 test bundle after implementation is complete:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_completion_root_cause_schema \
  tests.unit.test_completion_root_cause_classifiers \
  tests.integration.test_completion_root_cause_diagnosis \
  tests.integration.test_completion_root_cause_report \
  tests.integration.test_completion_root_cause_scope_guard \
  tests.unit.test_lifecycle_trace_schema \
  tests.unit.test_lifecycle_trace_behavior_equivalence \
  tests.integration.test_passive_lifecycle_trace_report \
  tests.integration.test_passive_lifecycle_trace_scope_guard \
  tests.unit.test_paper_default_terminal_exposure_config \
  tests.unit.test_paper_default_terminal_exposure_schema \
  tests.unit.test_smoke_training_contract \
  tests.integration.test_smoke_training_report \
  tests.unit.test_paper_hoodie_network_config \
  tests.unit.test_paper_hoodie_network_shapes \
  tests.integration.test_paper_hoodie_network_report \
  tests.unit.test_training_foundation_contract \
  tests.integration.test_training_foundation_contract_report
```

Feature 044 prerequisite artifact referenced by this validation scope:

- `artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json`

Validation expectations:

- No runtime repair is performed.
- The diagnosis uses Feature 044 passive traces only.
- The report includes per-task lifecycle reconstruction.
- The report ranks multiple root-cause classes by evidence strength.
- The report identifies the next feature type when diagnosis remains unresolved.
- Older pointer-sensitive report tests remain out of scope.

## Interpretation

- If runtime behavior is proven wrong, the next feature is Feature 046 - Runtime Repair for Completion Lifecycle.
- If runtime behavior is valid but load or action exposure is the issue, follow-up should target observation vectors, exploration, or loss sequences.
- If evidence is insufficient, the next feature should increase passive diagnostic depth rather than change runtime semantics.
