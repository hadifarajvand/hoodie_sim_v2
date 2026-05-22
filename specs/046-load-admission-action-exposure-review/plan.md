# Implementation Plan: Load, Admission, and Action-Exposure Review

**Branch**: `046-load-admission-action-exposure-review` | **Date**: `2026-05-22` | **Spec**: `specs/046-load-admission-action-exposure-review/spec.md`
**Input**: Feature specification from `specs/046-load-admission-action-exposure-review/spec.md`

## Summary

Feature 046 performs a diagnostic review to determine whether completion weakness under paper-default runtime is explained by load pressure, admission serialization, action exposure, queue pressure, offload path pressure, mixed load/action pressure, or insufficient full-population exposure evidence.

This feature is diagnostic only. It must not repair runtime behavior, redesign policy, run training, or claim paper reproduction. Existing passive trace analysis paths may be reused only if they preserve full-population evidence discipline. Sample-only trace evidence is restricted to representative examples and must not drive aggregate metrics or the final verdict.

## Technical Context

**Language/Version**: Python 3.x using the approved interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Project-local analysis modules only; standard library and existing repository analysis code  
**Storage**: File-based analysis artifacts under `artifacts/analysis/load-admission-action-exposure-review/`  
**Testing**: `unittest` with the approved Feature 046 validation bundle  
**Target Platform**: Local development and CI on POSIX-like environments  
**Project Type**: CLI-driven simulator analysis and report generation  
**Performance Goals**: Deterministic passive review, clear evidence-population accounting, and no change to simulator behavior  
**Constraints**: Diagnostic only; no runtime repair; no `src/environment/`; no `src/policies/`; no dependency changes; no training; no optimizer; no replay training; no target update; no reward-timing change; no timeout-contract change; no capacity-contract change; no transmission-contract change; no action-legality drift; no fake trace evidence; no curve fitting; no simulator-output tuning; no paper reproduction claim  
**Scale/Scope**: Single-feature review over a fixed paper-default horizon using committed Feature 044/045 trace and report artifacts

## Constitution Check

- [x] Scope is limited to diagnostic review only.
- [x] No runtime repair is proposed or required.
- [x] No policy, environment, dependency, or training changes are introduced.
- [x] No paper reproduction claim is made.
- [x] Evidence-population discipline is explicit for aggregate metrics and verdicts.
- [x] Canonical terminology is limited to the approved follow-up feature names.

No constitution violations require justification.

## Project Structure

### Documentation Artifacts

```text
specs/046-load-admission-action-exposure-review/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code

```text
src/analysis/load_admission_action_exposure_review/
```

### Tests

```text
tests/unit/test_load_admission_action_exposure_schema.py
tests/unit/test_load_admission_action_exposure_metrics.py
tests/integration/test_load_admission_action_exposure_review.py
tests/integration/test_load_admission_action_exposure_report.py
tests/integration/test_load_admission_action_exposure_scope_guard.py
```

### Artifacts

```text
artifacts/analysis/load-admission-action-exposure-review/
```

## Structure Decision

Add a passive analysis package under `src/analysis/load_admission_action_exposure_review/` that ingests committed Feature 044 and Feature 045 artifacts, computes the permitted diagnostic metrics, and emits JSON and Markdown reports under `artifacts/analysis/load-admission-action-exposure-review/`.

## Technical Decisions

1. Consume the committed passive trace and report artifacts as the only feature inputs:
   - `artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json`
   - `artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.json`
2. Existing passive trace analysis paths may be reused only if they preserve full-population evidence discipline.
3. The diagnostic review uses the paper-default runtime context as a fixed analysis baseline, including the approved feature 044 trace/input grid and the committed Feature 045 reconstruction summary.
4. The report must quantify load pressure, admission serialization, legal action exposure versus selected actions, queue-family pressure, offload-path pressure, representative budget comparisons, and per-strategy/per-action/per-queue summaries when full-population evidence exists.
5. If evidence is insufficient to separate load from action exposure, the report must state that explicitly instead of forcing a conclusion.
6. Runtime repair remains out of scope unless a verified runtime-fault contradiction against Feature 045 is demonstrated by committed evidence.
7. Any follow-up routing must use the canonical terms only:
   - `Feature 047 — Paper HOODIE Observation Vector`
   - `Feature 048 — Delayed-Reward DDQN Loss Contract`
   - `Feature 049 — Exploration Schedule Contract`
   - `exposure-matrix review`
8. Loose synonyms are prohibited because they blur the diagnostic boundary this feature is supposed to establish.

## Evidence-Population Discipline

- Existing passive trace analysis paths may be reused only if they preserve full-population evidence discipline.
- `lifecycle_trace_sample` must not be used for aggregate action exposure, queue pressure, offload path pressure, per-strategy, per-action, or final verdict metrics.
- `lifecycle_trace_sample` may be used only for representative examples.
- If only sample-level evidence is available for exposure, queue, offload, per-strategy, or per-action metrics, Feature 046 must classify the result as `diagnosis_inconclusive_requires_deeper_exposure_matrix`.
- Metric denominator populations must be consistent across compared metric groups, or the report must mark them incomparable.
- Do not mix full aggregate Feature 045 counts with sample-only action, queue, or offload metrics.
- Legal action exposure must be trace-backed. If legal-mask evidence is unavailable, report `action_exposure_data_status = insufficient_data_for_legal_action_exposure` and do not report fake zero values for legal horizontal or vertical counts.

## Required Metric Groups

The implementation and report must include:

1. Load pressure metrics
2. Admission serialization metrics
3. Legal-vs-selected action exposure metrics
4. Queue pressure metrics
5. Offload path pressure metrics
6. Budget comparison metrics
7. Per-strategy summary
8. Per-action summary
9. Per-queue summary
10. Dominant pressure source ranking
11. Next-feature recommendation

## Required Report Fields

The report must include, at minimum:

- `evidence_population_by_metric_group`
- `sample_usage_policy`
- `action_exposure_data_status`
- `legal_action_exposure_evidence_source`
- `metric_population_consistency_verified`
- `aggregate_metrics_not_sample_derived`
- `prerequisite_tags_verified`
- `prior_feature_gates_verified`
- `no_runtime_repair_performed = true`
- `no_training_started = true`
- `no_optimizer_step = true`
- `no_replay_training = true`
- `no_target_update_execution = true`
- `no_dependency_drift = true`
- `no_environment_contract_drift = true`
- `no_policy_drift = true`
- `no_reward_timing_change = true`
- `no_timeout_contract_drift = true`
- `no_capacity_contract_drift = true`
- `no_transmission_contract_drift = true`
- `no_action_legality_drift = true`
- `no_curve_fitting = true`
- `no_simulator_output_tuning = true`
- `no_paper_reproduction_claim = true`

`prior_feature_gates_verified` must include Features 037 through 045, not only 044 and 045.

## Verdict Discipline

- Feature 046 must not recommend runtime repair from load, admission, action exposure, queue pressure, or offload pressure alone.
- Runtime repair may be mentioned only if a verified runtime-fault contradiction against Feature 045 is found in committed evidence.
- If no full-population exposure, queue, or offload evidence exists, `final_verdict` must be `diagnosis_inconclusive_requires_deeper_exposure_matrix`.
- If action exposure dominates with trace-backed legal-vs-selected evidence, route to `Feature 047 — Paper HOODIE Observation Vector`.
- If evidence is insufficient, route to `exposure-matrix review`.

## Validation Strategy

The validation workflow must use the approved Feature 046 tests and safe prior schema/config/runtime checks only.

- Use Feature 046 unit and integration tests.
- Validate Feature 045 through committed artifact checks only.
- Do not run dirty-worktree-sensitive Feature 045 report-generation tests.
- Keep the validation bundle limited to the approved passive analysis and runtime-contract checks.
- Confirm the final report fields, evidence-population discipline, and verdict routing behavior before treating the feature as complete.

### Corrected Validation Command

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_load_admission_action_exposure_schema \
  tests.unit.test_load_admission_action_exposure_metrics \
  tests.integration.test_load_admission_action_exposure_review \
  tests.integration.test_load_admission_action_exposure_report \
  tests.integration.test_load_admission_action_exposure_scope_guard \
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

## Risks and Mitigations

- Risk: Mixing sample-only trace evidence with full Feature 045 aggregates.  
  Mitigation: Enforce evidence-population fields and reject incomparable metric groups.
- Risk: Overclaiming a diagnosis when legal-mask evidence is missing.  
  Mitigation: Require explicit unavailable status and avoid fake zeros.
- Risk: Reintroducing runtime repair logic through the analysis path.  
  Mitigation: Keep the implementation passive and test the no-repair contract explicitly.

## Open Questions

None. The feature scope is fully diagnostic and the evidence discipline is explicit.
