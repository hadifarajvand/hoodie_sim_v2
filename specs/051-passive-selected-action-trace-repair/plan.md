# Implementation Plan: Passive Selected-Action Trace Repair

**Branch**: `051-passive-selected-action-trace-repair` | **Date**: 2026-05-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/051-passive-selected-action-trace-repair/spec.md`

## Summary

Repair passive runtime trace emission so future evidence analysis can recover selected-action family identity, selected-action-to-task joins, and terminal-outcome join readiness from actual runtime trace population without changing action selection, legality, rewards, timing, queueing, execution, transmission, or capacity behavior.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11  
**Primary Dependencies**: Standard library analysis package plus existing runtime modules for passive trace emission  
**Storage**: File-based JSON and Markdown artifacts under `artifacts/analysis/passive-selected-action-trace-repair/`  
**Testing**: `unittest` via the approved interpreter; Feature 051 validation uses Feature 051 tests plus safe prior schema/config/runtime tests, with prior Features 044, 048, 049, and 050 validated only through committed-artifact checks inside Feature 051 tests  
**Target Platform**: Local Linux/macOS development and CI  
**Project Type**: CLI-driven analysis package inside a simulator repository  
**Performance Goals**: Generate the passive trace repair report quickly enough for routine planning and validation use  
**Constraints**: Passive trace emission only; no training, optimizer, replay, target update, campaign, or policy/runtime semantic changes  
**Scale/Scope**: Single-feature diagnostic repair over committed Feature 044, 048, 049, and 050 artifacts

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitution Gate

- [x] Dependency impact checked
- [x] Environment impact checked
- [x] Assumption impact checked
- [x] Fidelity impact checked
- [x] Test impact checked
- [x] Reproducibility impact checked
- [x] Config/schema impact checked
- [x] Public interface impact checked
- [x] Artifact impact checked
- [x] Security/secret impact checked
- [x] Performance budget impact checked
- [x] Baseline fairness impact checked
- [x] Paper-to-code mapping impact checked
- [x] Definition-of-done impact checked

## Project Structure

### Documentation (this feature)

```text
specs/051-passive-selected-action-trace-repair/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/analysis/passive_selected_action_trace_repair/
├── __init__.py
├── __main__.py
├── config.py
├── model.py
├── runner.py
└── report.py

src/environment/
├── lifecycle_trace.py
└── gym_adapter.py

tests/
├── integration/
│   ├── test_passive_selected_action_trace_repair.py
│   ├── test_passive_selected_action_trace_report.py
│   └── test_passive_selected_action_trace_scope_guard.py
└── unit/
    ├── test_passive_selected_action_trace_schema.py
    ├── test_passive_selected_action_trace_metrics.py
    └── test_passive_selected_action_trace_behavior_equivalence.py

artifacts/analysis/passive-selected-action-trace-repair/
```

**Structure Decision**: A single passive-analysis package under `src/analysis/passive_selected_action_trace_repair/` with report generation and validation artifacts only. The environment layer may only receive passive trace-schema and emission extensions through `src/environment/lifecycle_trace.py` and `src/environment/gym_adapter.py`.

## Phase 0: Outline & Research

Research is limited to the passive evidence model already defined by committed Feature 044, 048, 049, and 050 artifacts.

### Decisions

1. Extend passive trace schema to carry selected action, action index, selected action family, trace source, and deterministic join keys.
2. Run a small deterministic paper-default trace sample with passive tracing enabled and collect actual selected-action trace records.
3. Derive selected-action family from the selected action actually used by the environment, not from legality masks or downstream outcomes.
4. Preserve deterministic trace paths from selected action to task identity to terminal outcome readiness.
5. Treat missing evidence as incomplete or unavailable, not as zero-valued placeholders.
6. Keep behavior-equivalence checks unique and passive so trace repair cannot silently change simulation semantics.

### Research Deliverable

`research.md` will record the selected-action trace model, join-key strategy, failure modes, and reasons placeholder-driven alternatives were rejected.

## Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. Extract entities and relationships into `data-model.md`.
2. Define the report contract in `contracts/`.
3. Write `quickstart.md` for report generation and validation.

### Design Focus

- Selected-action trace schema extension
- Runtime trace population and count-based coverage
- Selected-action family derivation
- Selected-action-to-task join readiness
- Terminal outcome join readiness
- Behavior-equivalence audit with unique check names
- Feature 050 rerun readiness gating from passive trace repair

### Report Contract

The Feature 051 report MUST expose these top-level fields:

- `selected_action_trace_schema`
- `selected_action_trace_emission_summary`
- `decision_opportunity_count`
- `selected_action_trace_record_count`
- `selected_action_family_trace_record_count`
- `selected_action_to_task_join_key_count`
- `terminal_outcome_join_key_count`
- `selected_action_trace_coverage_ratio`
- `selected_action_family_coverage_ratio`
- `selected_action_to_task_join_coverage_ratio`
- `terminal_outcome_join_key_coverage_ratio`
- `missing_selected_action_trace_count`
- `missing_selected_action_family_count`
- `missing_selected_action_to_task_join_key_count`
- `missing_terminal_outcome_join_key_count`
- `selected_action_family_trace_summary`
- `selected_action_family_evidence_status`
- `selected_action_to_task_join_summary`
- `selected_action_to_task_join_status`
- `terminal_outcome_join_key_summary`
- `terminal_outcome_join_status`
- `per_action_outcome_join_readiness`
- `behavior_equivalence_passed`
- `behavior_equivalence_summary`
- `evidence_readiness_for_feature_050_rerun`
- `remaining_blockers`
- `recommended_next_feature`

Validation scope:

- Feature 051 validation MUST use Feature 051 tests for current behavior.
- Feature 051 validation MUST use committed-artifact-only checks for prior Features 044, 048, 049, and 050.
- Feature 051 validation MUST avoid any prior-feature test that inspects active worktree dirtiness, active `.specify/feature.json` state, current dirty paths, current branch local-only files, or report regeneration cleanliness from the active worktree.
- Feature 051 validation MUST keep current Feature 051 hygiene rules limited to commit-scope rules such as not staging or committing `.specify/feature.json`, `AGENTS.md`, or unrelated files.
- Feature 051 validation MUST require actual runtime trace payload inspection before any schema field is counted as emitted.
- Feature 051 validation MUST fail if schema fields are declared but no runtime trace record contains them.
- Feature 051 validation MUST require count-based coverage evidence for decision opportunities, emitted records, join keys, and missing counts.

Readiness rule:

- `evidence_readiness_for_feature_050_rerun` may be `true` only when `decision_opportunity_count > 0`, `selected_action_trace_record_count = decision_opportunity_count`, `selected_action_family_trace_record_count = decision_opportunity_count`, `selected_action_to_task_join_key_count = decision_opportunity_count`, `terminal_outcome_join_key_count = decision_opportunity_count`, all coverage ratios are complete for the emitted sample, `selected_action_family_evidence_status = available`, `selected_action_to_task_join_status = available`, `terminal_outcome_join_status = available`, `per_action_outcome_join_readiness = ready`, `behavior_equivalence_summary.passed = true`, `no_action_selection_drift = true`, and `no_action_legality_drift = true`.
- `behavior_equivalence_passed` MUST equal `behavior_equivalence_summary.passed`.
- If any readiness condition fails, `evidence_readiness_for_feature_050_rerun` MUST be `false`, `remaining_blockers` MUST be non-empty, and `final_verdict` MUST NOT be `passive_selected_action_trace_ready_for_feature_050_rerun`.

Validation failure conditions:

- The plan MUST fail if `decision_opportunity_count` is missing.
- The plan MUST fail if `selected_action_trace_record_count` is missing.
- The plan MUST fail if `selected_action_family_trace_record_count` is missing.
- The plan MUST fail if `selected_action_to_task_join_key_count` is missing.
- The plan MUST fail if `terminal_outcome_join_key_count` is missing.
- The plan MUST fail if any coverage ratio is missing.
- The plan MUST fail if the emission summary says a field is emitted but the corresponding runtime count is zero.
- The plan MUST fail if `selected_action_family_trace_record_count = 0` while emission says selected_action_family is emitted.
- The plan MUST fail if `selected_action_to_task_join_key_count = 0` while emission says join key is emitted.
- The plan MUST fail if `terminal_outcome_join_key_count = 0` while emission says terminal key is emitted.
- The plan MUST fail if readiness remains false without exact count-based blockers.
- The plan MUST fail if `final_verdict` remains `selected_action_family_trace_incomplete` after the repair while all required fields are present in actual trace records.
- The plan MUST fail if any of the four top-level readiness/status fields is missing.
- The plan MUST fail if any top-level readiness/status field contradicts its summary copy.
- The plan MUST fail if `behavior_equivalence_passed` contradicts `behavior_equivalence_summary.passed`.
- The plan MUST fail if readiness is `true` while any status is `partial` or `unavailable`.
- The plan MUST fail if readiness is `true` while `per_action_outcome_join_readiness != ready`.
- The plan MUST fail if readiness is `true` while behavior equivalence fails.
- The plan MUST fail if `final_verdict` claims readiness while readiness is `false`.
- The plan MUST fail if `remaining_blockers` is empty while readiness is `false`.
