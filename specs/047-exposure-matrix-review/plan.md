# Implementation Plan: Exposure-Matrix Review

**Branch**: `047-exposure-matrix-review` | **Date**: `2026-05-22` | **Spec**: `specs/047-exposure-matrix-review/spec.md`
**Input**: Feature specification from `specs/047-exposure-matrix-review/spec.md`

## Summary

Feature 047 is a diagnostic exposure-matrix review that closes the legal-vs-selected exposure gap left by Feature 046. It evaluates the full paper-default strategy/seed grid using existing runtime behavior and passive evidence only, then determines whether action exposure, load dominance, or offload underexposure best explains the observed weakness. It does not repair runtime behavior, redesign policy, or run training.

## Technical Context

**Language/Version**: Python 3.x using the approved interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Project-local analysis modules only; standard library and existing repository analysis code  
**Storage**: File-based analysis artifacts under `artifacts/analysis/exposure-matrix-review/`  
**Testing**: `unittest` with approved Feature 047 and safe prior regression checks  
**Target Platform**: Local development and CI on POSIX-like environments  
**Project Type**: CLI-driven passive analysis and report generation  
**Performance Goals**: Deterministic matrix reconstruction over the full strategy/seed grid with honest evidence-population accounting  
**Constraints**: Diagnostic-only scope; no runtime repair; no environment semantic change; no policy redesign; no dependency change; no reward timing change; no timeout/deadline change; no execution/capacity change; no transmission delay change; no action legality change; no training; no optimizer; no replay training; no target update; no curve fitting; no simulator-output tuning; no paper reproduction claim  
**Scale/Scope**: One feature review over the paper-default grid with full-population decision-opportunity accounting when evidence exists

## Constitution Check

- [x] Scope is limited to diagnostic exposure review only.
- [x] No runtime repair is proposed or required.
- [x] No policy, environment, dependency, or training changes are introduced.
- [x] No paper reproduction claim is made.
- [x] Evidence-population discipline is explicit for aggregate metrics and verdicts.
- [x] Canonical routing terminology is limited to the approved next-feature names.

No constitution violations require justification.

## Project Structure

### Documentation Artifacts

```text
specs/047-exposure-matrix-review/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code

```text
src/analysis/exposure_matrix_review/
```

### Tests

```text
tests/unit/test_exposure_matrix_schema.py
tests/unit/test_exposure_matrix_metrics.py
tests/integration/test_exposure_matrix_review.py
tests/integration/test_exposure_matrix_report.py
tests/integration/test_exposure_matrix_scope_guard.py
```

### Artifacts

```text
artifacts/analysis/exposure-matrix-review/
```

## Structure Decision

Add a passive analysis package under `src/analysis/exposure_matrix_review/` that reads committed Feature 044/045/046 artifacts, reconstructs the exposure matrix, emits JSON and Markdown reports, and preserves the passive runtime boundary.

## Technical Decisions

1. Use paper-default `T = 110`, seeds `[0, 1, 2]`, and the five approved probe strategies from Features 042-046.
2. Collect full-population decision-opportunity counts for each strategy/seed run when the committed evidence supports them.
3. Distinguish legal action exposure from selected action counts explicitly; legal counts must come from trace legality snapshots, environment action masks, or an approved public legality helper.
4. Never derive aggregate exposure metrics from representative samples.
5. Report unavailable legal evidence as unavailable or null, not zero.
6. Validate prior Feature 037-046 committed artifacts through artifact checks only; do not rerun dirty-worktree-sensitive older report tests.
7. The routing rule is strict:
   - complete exposure evidence routes to `Feature 048 — Paper HOODIE Observation Vector`
   - incomplete legality evidence routes to legality evidence expansion before Feature 048
8. Runtime repair is out of scope unless a verified contradiction against Features 045 or 046 is found.
9. The report must stay diagnostic-only and must not imply training or policy redesign.

## Evidence Discipline

- Full-population decision opportunities are required for aggregate matrix metrics.
- `lifecycle_trace_sample` may only be used for representative examples.
- Legal action counts must be trace-backed.
- If legal evidence is unavailable or partial, the report must expose the coverage ratio and mark the matrix incomplete.
- Sample-only aggregate metrics are forbidden.

## Required Metric Groups

The implementation and report must include:

1. Exposure matrix by strategy/seed
2. Legal-vs-selected action matrix
3. Per-action outcome matrix
4. Per-queue matrix
5. Offload exposure matrix
6. Exposure bias summary
7. Load-vs-exposure summary
8. Matrix completeness summary
9. Dominant exposure findings
10. Next-feature recommendation

## Required Report Fields

The report must include, at minimum:

- `feature_id`
- `prerequisite_tags_verified`
- `prior_feature_gates_verified`
- `paper_default_runtime_verified`
- `exposure_matrix_input_sources`
- `exposure_matrix_population`
- `legal_action_evidence_source`
- `legal_action_evidence_coverage_ratio`
- `per_strategy_seed_matrix`
- `aggregate_exposure_matrix`
- `per_action_outcome_matrix`
- `per_queue_matrix`
- `offload_exposure_matrix`
- `illegal_action_summary`
- `exposure_bias_summary`
- `load_vs_exposure_summary`
- `matrix_completeness_summary`
- `dominant_exposure_findings`
- `diagnosis`
- `recommended_next_feature`
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
- `final_verdict`

`prior_feature_gates_verified` must include Features 037 through 046.

## Verdict Discipline

- `exposure_matrix_complete_ready_for_observation_vector` only when the full-population matrix is complete and legal exposure is measurable.
- `exposure_matrix_identifies_action_exposure_bias` only when legal-vs-selected differences are trace-backed.
- `exposure_matrix_identifies_load_dominance` only when load dominates independently of action exposure.
- `exposure_matrix_identifies_offload_underexposure` only when legal offload actions exist but are rarely selected and that underexposure is trace-backed.
- `exposure_matrix_incomplete_requires_legality_evidence` when legal evidence is unavailable.
- `exposure_matrix_incomplete_requires_full_trace_collection` when the strategy/seed grid cannot be fully covered by committed passive traces.

## Validation Strategy

The validation workflow must use Feature 047 tests and safe prior artifact checks only.

- Validate Feature 046 through committed artifact checks only.
- Do not run dirty-worktree-sensitive older report-generation tests.
- Use the approved interpreter and the Feature 047 passive analysis entrypoint.
- Confirm that the report fields, evidence-population discipline, and verdict routing behavior are all present before implementation starts.

### Corrected Validation Command

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

## Risks and Mitigations

- Risk: Confusing sample examples with aggregate matrix evidence.  
  Mitigation: Treat representative slices as examples only and require full-population aggregates for verdicts.
- Risk: Faking legal exposure zeros when evidence is missing.  
  Mitigation: Require null/unavailable legal fields plus explicit coverage status.
- Risk: Routing to Feature 048 too early.  
  Mitigation: Gate routing on matrix completeness and trace-backed legal-vs-selected evidence.

## Open Questions

None. The clarified decisions remove the blocking ambiguity around runtime mutation, trace source priority, horizon, seeds/strategies, legal evidence handling, and routing.
