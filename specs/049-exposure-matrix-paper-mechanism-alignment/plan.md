# Implementation Plan: Exposure Matrix Rerun and Paper Mechanism Alignment

**Branch**: `049-exposure-matrix-paper-mechanism-alignment` | **Date**: `2026-05-23` | **Spec**: `specs/049-exposure-matrix-paper-mechanism-alignment/spec.md`
**Input**: Feature specification from `specs/049-exposure-matrix-paper-mechanism-alignment/spec.md`

## Summary

Feature 049 is diagnostic/alignment only. It uses Feature 048 legality evidence to rerun the exposure matrix, compares legal availability with selected actions, audits the paper HOODIE observation vector, checks timing/unit formulas against the paper contract, and issues a readiness decision for the next training-contract bundle. It does not train, optimize, replay, or update targets.

## Technical Context

**Language/Version**: Python 3.x using the approved interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Project-local analysis and environment modules only; standard library and existing repository code  
**Storage**: File-based analysis artifacts under `artifacts/analysis/exposure-matrix-paper-mechanism-alignment/`  
**Testing**: `unittest` with Feature 049 tests and committed-artifact checks for Features 043-048  
**Target Platform**: Local development and CI on POSIX-like environments  
**Project Type**: Passive analysis, exposure diagnostics, and paper-mechanism alignment reporting  
**Performance Goals**: Deterministic rerun and audit over the paper-default grid without changing runtime outcomes  
**Constraints**: Diagnostic/alignment only; no training; no optimizer; no replay training; no target update; no full campaign; no figure reproduction; no dependency change; no policy change; no runtime semantic change unless separately approved in a future feature; no curve fitting; no simulator-output tuning; no paper reproduction claim  
**Scale/Scope**: One legality-evidence rerun plus observation/formula audits and a training-readiness decision

## Constitution Check

- [x] Scope is limited to diagnostic/alignment only.
- [x] No training, optimizer, replay, or target-update work is proposed.
- [x] No policy, dependency, or runtime-semantic changes are introduced.
- [x] No full campaign or figure reproduction claim is made.
- [x] Behavior is evaluated through committed artifacts and analysis, not by changing the simulator contract.
- [x] The next training-contract bundle is gated, not executed here.
- [x] Validation avoids dirty-worktree-sensitive older report tests.

No constitution violations require justification.

## Project Structure

### Documentation Artifacts

```text
specs/049-exposure-matrix-paper-mechanism-alignment/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code

```text
src/analysis/exposure_matrix_paper_mechanism_alignment/
```

### Tests

```text
tests/unit/test_exposure_matrix_paper_mechanism_schema.py
tests/unit/test_exposure_matrix_paper_mechanism_metrics.py
tests/integration/test_exposure_matrix_paper_mechanism_alignment.py
tests/integration/test_exposure_matrix_paper_mechanism_report.py
tests/integration/test_exposure_matrix_paper_mechanism_scope_guard.py
```

### Artifacts

```text
artifacts/analysis/exposure-matrix-paper-mechanism-alignment/
```

## Structure Decision

Add a passive analysis package under `src/analysis/exposure_matrix_paper_mechanism_alignment/` that consumes Feature 048 legality evidence and Feature 047 exposure-matrix outputs, reruns the exposure matrix as an analysis-only step, and audits whether the current simulator/network interface still matches the paper HOODIE mechanism before any training contract is attempted.

The implementation must remain passive. If the audits reveal a runtime semantic contradiction, the feature must report it and route to a future repair feature rather than changing runtime semantics here.

## Technical Decisions

1. Use the Feature 048 legality evidence as the evidence source for the exposure-matrix rerun.
2. Treat the committed Feature 047 exposure-matrix report as the prior baseline artifact, not a live rerun target.
3. Summarize exposure by strategy, seed, and action so exposure bias can be reviewed before training.
4. Audit the paper HOODIE observation vector against the current simulator/network interface as a read-only alignment check.
5. Audit local execution time, horizontal/vertical transmission delay, queue wait, task age, deadline/timeout, reward timing, and terminal-state handling against paper assumptions as read-only checks.
6. Use committed artifacts from Features 043 through 048 as prerequisite evidence only.
7. Do not add any training loop, optimizer step, replay buffer update, or target-network cadence.
8. Do not recommend the full campaign in this feature.
9. The readiness decision must be one of the approved diagnostic/alignment verdicts in the spec.
10. If a runtime semantic contradiction is detected, route it to a future repair feature and stop recommending training readiness.

## Evidence Discipline

- Passive diagnostics only.
- Legal-vs-selected action exposure must be trace-backed from Feature 048 evidence.
- Representative examples are examples only; they are not aggregate proof.
- Observation and formula audits must be evidence-based and must not silently invent missing values.
- The analysis must not alter selected actions, rewards, queue progression, terminal outcomes, or timing behavior.
- The readiness decision is a gate, not an implementation of training.

## Required Metric Groups

The implementation and report must include:

1. Exposure-matrix rerun summary
2. Legal-vs-selected action matrix
3. Per-strategy/per-seed/per-action exposure and outcome summaries
4. Observation vector audit
5. Paper formula/unit audit
6. Runtime semantic drift check
7. Training readiness decision

## Required Report Fields

The report must include, at minimum:

- `feature_id`
- `prerequisite_tags_verified`
- `prior_feature_gates_verified`
- `legality_evidence_verified`
- `exposure_matrix_rerun_summary`
- `legal_vs_selected_action_matrix`
- `per_strategy_seed_matrix`
- `per_action_outcome_matrix`
- `selected_illegal_action_summary`
- `observation_vector_audit`
- `paper_formula_unit_audit`
- `runtime_semantic_drift_check`
- `training_readiness_decision`
- `recommended_next_feature`
- `no_runtime_repair_performed`
- `no_training_started`
- `no_optimizer_step`
- `no_replay_training`
- `no_target_update_execution`
- `no_dependency_drift`
- `no_policy_drift`
- `no_reward_timing_change`
- `no_timeout_contract_drift`
- `no_capacity_contract_drift`
- `no_transmission_contract_drift`
- `no_action_legality_drift`
- `no_action_selection_drift`
- `no_curve_fitting`
- `no_simulator_output_tuning`
- `no_paper_reproduction_claim`
- `final_verdict`

`prior_feature_gates_verified` must include Features 043 through 048.

## Verdict Discipline

- `paper_mechanism_alignment_ready_for_training_contract` only when the exposure matrix is complete and the observation/formula audits pass.
- `observation_vector_gap_blocks_training` when the observation vector is incomplete.
- `formula_unit_gap_blocks_training` when a formula or unit mismatch is detected.
- `exposure_bias_blocks_training` when legal-vs-selected exposure remains too biased for readiness.
- `runtime_semantic_contradiction_requires_repair` when the simulator contract contradicts the paper mechanism.
- `insufficient_legality_or_trace_evidence` when the rerun or audit cannot be supported by the available evidence.
- `prerequisite_blocked` when a required prior artifact is missing.

## Validation Strategy

The validation workflow must use Feature 049 tests and safe prior artifact checks only.

- Confirm `.specify/feature.json` is non-commit-capable before any implementation step.
- Validate Features 043 through 048 through committed artifact checks only.
- Do not run dirty-worktree-sensitive older report-generation tests.
- Use the approved interpreter and the Feature 049 passive analysis entrypoint.
- Confirm that legality coverage, exposure bias, observation alignment, formula/unit alignment, and readiness routing are all present before planning implementation tasks.

### Corrected Validation Command

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

Feature 047, 048, and prior prerequisite validation must be done inside Feature 049 tests by checking committed artifacts, not by rerunning dirty-worktree-sensitive older report tests.

## Risks and Mitigations

- Risk: Confusing analysis-only rerun logic with a training campaign.  
  Mitigation: Keep the feature scoped to diagnostics, reporting, and readiness gating only.
- Risk: Treating evidence gaps as proof of readiness.  
  Mitigation: Require explicit unavailable/insufficient verdicts and route to repair or readiness blockers.
- Risk: Accidentally mutating simulator semantics while auditing.  
  Mitigation: Keep the feature read-only and rely on committed artifacts plus passive metrics.

## Open Questions

None. The feature scope is intentionally bundled but bounded: exposure rerun, paper-mechanism audit, and readiness decision only.
