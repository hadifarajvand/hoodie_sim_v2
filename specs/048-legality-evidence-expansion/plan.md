# Implementation Plan: Legality Evidence Expansion

**Branch**: `048-legality-evidence-expansion` | **Date**: `2026-05-22` | **Spec**: `specs/048-legality-evidence-expansion/spec.md`
**Input**: Feature specification from `specs/048-legality-evidence-expansion/spec.md`

## Summary

Feature 048 is passive instrumentation only. It adds trace-backed legality evidence so the exposure matrix can distinguish legal availability from selected action choice without fake zeros or sample-only inference. It does not repair runtime behavior, redesign policy, change action legality, or alter selected actions.

## Technical Context

**Language/Version**: Python 3.x using the approved interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Project-local analysis and environment modules only; standard library and existing repository code  
**Storage**: File-based legality evidence artifacts under `artifacts/analysis/legality-evidence-expansion/`  
**Testing**: `unittest` with approved Feature 048 and safe prior regression checks  
**Target Platform**: Local development and CI on POSIX-like environments  
**Project Type**: Passive environment instrumentation plus report generation  
**Performance Goals**: Deterministic legality capture over the paper-default grid without changing runtime outcomes  
**Constraints**: Passive legality evidence only; no runtime repair; no action legality semantic change; no action selection change; no policy redesign; no dependency change; no reward timing change; no timeout/deadline change; no execution/capacity change; no transmission delay change; no training; no optimizer; no replay training; no target update; no curve fitting; no simulator-output tuning; no paper reproduction claim  
**Scale/Scope**: One passive legality-evidence pass over the paper-default grid, plus a behavior-equivalence baseline comparison

## Constitution Check

- [x] Scope is limited to passive legality evidence capture only.
- [x] No runtime repair is proposed or required.
- [x] No policy, dependency, or training changes are introduced.
- [x] No selected-action semantics are changed.
- [x] No reward, timeout, capacity, or transmission semantics are changed.
- [x] No paper reproduction claim is made.
- [x] Behavior equivalence is explicit and measurable.
- [x] Canonical routing terminology is limited to the approved next-feature names.

No constitution violations require justification.

## Project Structure

### Documentation Artifacts

```text
specs/048-legality-evidence-expansion/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code

```text
src/analysis/legality_evidence_expansion/
src/environment/lifecycle_trace.py
src/environment/gym_adapter.py
```

### Tests

```text
tests/unit/test_legality_evidence_schema.py
tests/unit/test_legality_evidence_metrics.py
tests/unit/test_legality_evidence_behavior_equivalence.py
tests/integration/test_legality_evidence_expansion.py
tests/integration/test_legality_evidence_report.py
tests/integration/test_legality_evidence_scope_guard.py
```

### Artifacts

```text
artifacts/analysis/legality-evidence-expansion/
```

## Structure Decision

Add a passive legality-evidence package under `src/analysis/legality_evidence_expansion/` that reads the same paper-default strategy/seed grid used by Features 047 and earlier, captures legality snapshots without changing runtime behavior, compares the capture run against a no-legality-capture baseline, and emits JSON/Markdown reports.

The implementation may touch `src/environment/lifecycle_trace.py` and `src/environment/gym_adapter.py` only if the changes are strictly passive, behavior-equivalent, and limited to exposing legality snapshots that already exist or can be surfaced without semantic drift.

## Technical Decisions

1. Use paper-default `T = 110`, seeds `[0, 1, 2]`, and the five approved probe strategies from Features 042-047.
2. Prefer existing runtime info action masks when already emitted.
3. Prefer the existing public legality helper if it already exists.
4. Fall back to passive legality snapshots added to lifecycle trace if they can be exposed without semantic change.
5. Report unavailable legal evidence as null/unavailable rather than zero.
6. Compare every legality-capture run against a no-legality-capture baseline using the same seeds, the same strategy, and the same paper-default config.
7. Validate prior Feature 044-047 committed artifacts through artifact checks only; do not rerun dirty-worktree-sensitive older report tests.
8. The routing rule is strict:
   - sufficient legality evidence + behavior equivalence passes routes to `Feature 049 — Exposure-Matrix Rerun with Legality Evidence`
   - partial legality coverage routes to trace-depth expansion before Feature 049
   - legality evidence that requires semantic runtime change routes to a public legality helper feature before Feature 049
9. Runtime repair is out of scope.
10. The report must explicitly state whether Feature 049 can rerun the exposure matrix.

## Evidence Discipline

- Passive legality evidence only.
- `lifecycle_trace_sample` may be used as representative examples only.
- Legal action evidence must be trace-backed or honestly marked unavailable.
- The new instrumentation must not change selected actions, rewards, queue progression, terminal outcomes, or timing behavior.
- Behavior-equivalence results are required before the legality evidence can unblock Feature 049.

## Required Metric Groups

The implementation and report must include:

1. Legality snapshot coverage by strategy/seed
2. Selected-was-legal derivation
3. Selected-illegal-action derivation
4. Action-mask summary
5. Behavior-equivalence summary
6. Exposure-matrix unblock decision
7. Next-feature recommendation

## Required Report Fields

The report must include, at minimum:

- `feature_id`
- `prerequisite_tags_verified`
- `prior_feature_gates_verified`
- `paper_default_runtime_verified`
- `legality_evidence_source`
- `legality_snapshot_schema`
- `legality_evidence_coverage_summary`
- `per_strategy_seed_legality_coverage`
- `action_mask_summary`
- `selected_illegal_action_summary`
- `behavior_equivalence_summary`
- `exposure_matrix_unblocked`
- `recommended_next_feature`
- `no_runtime_repair_performed = true`
- `no_training_started = true`
- `no_optimizer_step = true`
- `no_replay_training = true`
- `no_target_update_execution = true`
- `no_dependency_drift = true`
- `no_policy_drift = true`
- `no_reward_timing_change = true`
- `no_timeout_contract_drift = true`
- `no_capacity_contract_drift = true`
- `no_transmission_contract_drift = true`
- `no_action_legality_drift = true`
- `no_action_selection_drift = true`
- `no_curve_fitting = true`
- `no_simulator_output_tuning = true`
- `no_paper_reproduction_claim = true`
- `final_verdict`

`prior_feature_gates_verified` must include Features 044 through 047.

## Verdict Discipline

- `legality_evidence_ready_for_exposure_matrix_rerun` only when full legality evidence coverage exists and behavior equivalence passes.
- `legality_evidence_partial_requires_trace_depth_expansion` only when legality coverage is partial.
- `legality_evidence_unavailable_requires_runtime_public_helper` only when legality evidence cannot be extracted without semantic runtime change.
- `behavior_drift_detected` when legality capture changes selected actions, rewards, queue progression, terminal outcomes, or timing behavior.

## Validation Strategy

The validation workflow must use Feature 048 tests and safe prior artifact checks only.

- Validate Feature 047 through committed artifact checks only.
- Do not run dirty-worktree-sensitive older report-generation tests.
- Use the approved interpreter and the Feature 048 passive instrumentation entrypoint.
- Confirm that legality coverage, behavior equivalence, and routing behavior are all present before implementation starts.

### Corrected Validation Command

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

Feature 047 prerequisite validation must be done inside Feature 048 tests by checking the committed artifact at `artifacts/analysis/exposure-matrix-review/exposure-matrix-report.json`, not by rerunning dirty-worktree-sensitive Feature 047 schema or report tests.

## Risks and Mitigations

- Risk: Accidentally changing action selection or queue/reward behavior while adding instrumentation.  
  Mitigation: Compare capture runs against a no-legality-capture baseline using the same seeds and strategies.
- Risk: Reporting zero legal evidence when evidence is actually unavailable.  
  Mitigation: Require null/unavailable values and explicit coverage summaries.
- Risk: Treating passive samples as complete legality evidence.  
  Mitigation: Separate representative examples from aggregate legality coverage.

## Open Questions

None. The clarified decisions remove the blocking ambiguity around runtime mutation, evidence-source priority, behavior equivalence, strategy/seed grid, null handling, routing, dirty-worktree-sensitive older tests, and AGENTS.md cleanliness.
