# Implementation Plan: Selected-Action Outcome Evidence Rerun

**Branch**: `052-selected-action-outcome-evidence-rerun` | **Date**: 2026-05-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/052-selected-action-outcome-evidence-rerun/spec.md`

## Summary

Rerun the selected-action family and per-action outcome evidence analysis using the populated Feature 051 trace evidence so the project can determine whether Feature 050 blockers are resolved and whether Feature 049 can now be rerun. This feature is evidence-only: it consumes committed artifacts and previously populated trace evidence, recomputes evidence summaries, and does not alter runtime semantics.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Standard library analysis package plus committed prior-feature artifact JSON reports  
**Storage**: File-based JSON and Markdown artifacts under `artifacts/analysis/selected-action-outcome-evidence-rerun/`  
**Testing**: `unittest` via the approved interpreter; Feature 052 validation uses Feature 052 tests and committed-artifact-only checks for Features 048, 049, 050, and 051  
**Target Platform**: Local Linux/macOS development and CI  
**Project Type**: CLI-driven analysis package inside a simulator repository  
**Performance Goals**: Produce the rerun report quickly enough for routine evidence review  
**Constraints**: Evidence rerun only; no training, optimizer, replay, target update, campaign, or policy/runtime semantic changes  
**Scale/Scope**: Single-feature rerun over committed Feature 048, 049, 050, and 051 artifacts

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
specs/052-selected-action-outcome-evidence-rerun/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
```

### Source Code (repository root)

```text
src/analysis/selected_action_outcome_evidence_rerun/
├── __init__.py
├── __main__.py
├── config.py
├── model.py
├── runner.py
└── report.py

tests/
├── integration/
│   ├── test_selected_action_outcome_rerun.py
│   ├── test_selected_action_outcome_rerun_report.py
│   └── test_selected_action_outcome_rerun_scope_guard.py
└── unit/
    ├── test_selected_action_outcome_rerun_schema.py
    ├── test_selected_action_outcome_rerun_metrics.py
    └── test_selected_action_outcome_rerun_behavior_equivalence.py

artifacts/analysis/selected-action-outcome-evidence-rerun/
```

**Structure Decision**: A single passive analysis package under `src/analysis/selected_action_outcome_evidence_rerun/` that consumes committed Feature 051 evidence and emits rerun reports only.

## Phase 0: Outline & Research

Research is limited to the committed prior evidence reports and the already-populated Feature 051 rerun-ready report.

### Decisions

1. Use Feature 051 readiness as a hard prerequisite gate.
2. Recompute selected-action family and selected-action-to-task evidence from committed Feature 051 trace evidence only.
3. Recompute per-action outcome evidence and legal-but-unselected consistency from the rerun evidence path only.
4. Preserve exposure-matrix internal consistency as a validation gate, not a runtime repair target.
5. Keep behavior-equivalence checks unique and passive so rerun analysis cannot silently alter simulator semantics.

### Research Deliverable

`research.md` will record the rerun evidence model, blocker routing, and the reasons placeholder-driven alternatives were rejected.

## Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. Extract entities and relationships into `data-model.md`.
2. Define the report contract in `contracts/`.
3. Write `quickstart.md` for report generation and validation.

### Design Focus

- Feature 051 readiness gate validation
- Selected-action family evidence rerun
- Selected-action-to-task join rerun
- Per-action outcome rerun
- Legal-but-unselected consistency
- Exposure matrix internal consistency
- Feature 049 unblock assessment
- Behavior-equivalence audit with unique check names

### Report Contract

The Feature 052 report MUST expose these top-level fields:

- `feature_051_trace_readiness_verified`
- `selected_action_family_evidence_summary`
- `selected_action_family_evidence_status`
- `selected_action_to_task_join_summary`
- `selected_action_to_task_join_status`
- `per_action_outcome_join_summary`
- `per_action_outcome_evidence_status`
- `per_action_outcome_matrix`
- `legal_but_unselected_consistency_summary`
- `exposure_matrix_internal_consistency_summary`
- `feature_049_unblock_assessment`
- `behavior_equivalence_passed`
- `behavior_equivalence_summary`
- `feature_049_can_be_rerun`
- `feature_049_remaining_blockers`
- `recommended_next_feature`

Validation scope:

- Feature 052 validation MUST use Feature 052 tests for current behavior.
- Feature 052 validation MUST use committed-artifact-only checks for prior Features 048, 049, 050, and 051.
- Feature 052 validation MUST avoid any prior-feature test that inspects active worktree dirtiness, active `.specify/feature.json` state, current dirty paths, or prior report regeneration cleanliness from the active worktree.
- Feature 052 validation MUST keep current hygiene rules limited to commit-scope rules such as not staging or committing `.specify/feature.json`, `AGENTS.md`, or unrelated files.

Readiness rule:

- `feature_051_trace_readiness_verified` must be true only when Feature 051 reports `evidence_readiness_for_feature_050_rerun = true`, `selected_action_family_evidence_status = available`, `selected_action_to_task_join_status = available`, `terminal_outcome_join_status = available`, `per_action_outcome_join_readiness = ready`, and `behavior_equivalence_summary.passed = true`.
- If the Feature 051 readiness gate fails, the rerun analysis MUST be blocked, `feature_049_can_be_rerun` MUST be false, and `feature_049_remaining_blockers` MUST be non-empty.
- `behavior_equivalence_passed` MUST equal `behavior_equivalence_summary.passed`.
- `per_action_outcome_evidence_status` MUST be one of `available`, `partial`, or `unavailable` and MUST align with `per_action_outcome_join_summary.per_action_outcome_evidence_status` when present.

Validation failure conditions:

- The plan MUST fail if the Feature 051 readiness gate is false.
- The plan MUST fail if any required summary field is missing.
- The plan MUST fail if rerun counts, rates, or blockers are fabricated rather than derived from committed evidence.
- The plan MUST fail if `feature_049_can_be_rerun` is true while any required consistency check fails.
- The plan MUST fail if `feature_049_remaining_blockers` is empty while rerun readiness is false.
- The plan MUST fail if `behavior_equivalence_passed` contradicts `behavior_equivalence_summary.passed`.
- The plan MUST fail if `per_action_outcome_evidence_status` is missing.
- The plan MUST fail if `per_action_outcome_evidence_status` contradicts its summary copy.
- The plan MUST fail if `feature_049_can_be_rerun = true` while `per_action_outcome_evidence_status != available`.
- The plan MUST fail if `final_verdict` claims readiness while `per_action_outcome_evidence_status` is partial or unavailable.
- The plan MUST fail if `recommended_next_feature` routes to Feature 053 while `per_action_outcome_evidence_status` is not available.
- The plan MUST fail if `recommended_next_feature` claims readiness while rerun readiness is false.
