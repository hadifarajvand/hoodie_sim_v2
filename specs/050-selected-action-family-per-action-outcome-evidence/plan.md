# Implementation Plan: Selected-Action Family and Per-Action Outcome Evidence Expansion

**Branch**: `050-selected-action-family-per-action-outcome-evidence` | **Date**: 2026-05-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/050-selected-action-family-per-action-outcome-evidence/spec.md`

**Note**: This plan is generated from the Feature 050 specification and is limited to passive evidence expansion only.

## Summary

Feature 050 expands passive evidence so Feature 049 can be rerun without inventing selected-action family counts or per-action outcome rates. The implementation will capture selected action family identity, join selected actions to task and terminal outcome keys, compute per-action completion/drop/pending evidence only when trace-backed, and report whether Feature 049 remains blocked or can be rerun safely.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Standard library only for the analysis package; existing project runtime modules for passive trace access  
**Storage**: File-based JSON and Markdown artifacts under `artifacts/analysis/selected-action-family-per-action-outcome-evidence/`  
**Testing**: `unittest` via the approved interpreter; Feature 050 validation uses Feature 050 tests plus safe prior schema/config/runtime checks, and validates prior Features 044, 048, and 049 through committed-artifact-only assertions inside Feature 050 tests
**Target Platform**: Local Linux/macOS development and CI  
**Project Type**: CLI-driven analysis package inside a simulator repository  
**Performance Goals**: Generate the passive evidence report quickly enough for routine planning/validation use; no training or campaign execution  
**Constraints**: Passive evidence only; no training, optimizer, replay training, target updates, full campaign, or policy/runtime semantic changes  
**Scale/Scope**: Single-feature diagnostic expansion over committed Feature 044, 048, and 049 artifacts

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

The feature stays within passive evidence expansion and does not alter scheduling, action legality, reward timing, timeout behavior, queue behavior, execution behavior, transmission behavior, or capacity semantics.

## Project Structure

### Documentation (this feature)

```text
specs/050-selected-action-family-per-action-outcome-evidence/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/analysis/selected_action_family_per_action_outcome_evidence/
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
│   ├── test_selected_action_outcome_evidence.py
│   ├── test_selected_action_outcome_report.py
│   └── test_selected_action_outcome_scope_guard.py
└── unit/
    ├── test_selected_action_outcome_evidence_schema.py
    ├── test_selected_action_outcome_evidence_metrics.py
    └── test_selected_action_outcome_behavior_equivalence.py

artifacts/analysis/selected-action-family-per-action-outcome-evidence/
```

**Structure Decision**: A single passive-analysis package under `src/analysis/selected_action_family_per_action_outcome_evidence/` with report generation and validation artifacts only. The environment layer may only receive passive trace-schema and emission extensions through `src/environment/lifecycle_trace.py` and `src/environment/gym_adapter.py`.

## Phase 0: Outline & Research

Research is limited to the passive evidence model already defined by committed Feature 044, 048, and 049 artifacts.

### Decisions

1. Capture selected action family at each decision opportunity using passive trace fields only.
2. Join selected actions to task identity and terminal outcome using deterministic join keys.
3. Treat missing selected-family or outcome evidence as unavailable, not zero-valued.
4. Use the Feature 049 readiness decision as the downstream gating target.
5. Preserve behavior equivalence checks as a separate passive audit, with unique check names.

### Research Deliverable

`research.md` will record the evidence model, join-key strategy, failure modes, and reasons alternative placeholder-driven designs were rejected.

## Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. Extract entities and relationships into `data-model.md`.
2. Define the report contract in `contracts/`.
3. Write `quickstart.md` for report generation and validation.
4. Re-evaluate the constitution check after the design artifacts are in place.

### Design Focus

- Selected-action family evidence status and counts
- Selected-action-to-task join keys
- Per-action terminal outcome join keys and counts/rates
- Legal-but-unselected consistency
- Exposure matrix internal consistency
- Feature 049 unblock assessment
- Behavior equivalence audit with deduplicated checks

### Report Contract

The Feature 050 report MUST expose these top-level fields:

- `selected_action_family_evidence_status`
- `selected_action_to_task_join_status`
- `per_action_outcome_evidence_status`
- `behavior_equivalence_passed`
- `feature_049_can_be_rerun`
- `feature_049_remaining_blockers`
- `feature_049_unblock_assessment`

`feature_049_unblock_assessment` is the canonical umbrella object. It MUST contain:

- `feature_049_can_be_rerun`
- `feature_049_remaining_blockers`
- `selected_action_family_evidence_status`
- `selected_action_to_task_join_status`
- `per_action_outcome_evidence_status`
- `exposure_matrix_internal_consistency_verified`
- `behavior_equivalence_passed`
- `recommended_next_feature`

Top-level values and nested `feature_049_unblock_assessment` values MUST match exactly for:

- `selected_action_family_evidence_status`
- `selected_action_to_task_join_status`
- `per_action_outcome_evidence_status`
- `behavior_equivalence_passed`
- `feature_049_can_be_rerun`
- `feature_049_remaining_blockers`

Readiness rule:

- `behavior_equivalence_passed` MUST equal `behavior_equivalence_summary.passed`.
- `feature_049_can_be_rerun` may be `true` only when `selected_action_family_evidence_status = available`, `selected_action_to_task_join_status = available`, `per_action_outcome_evidence_status = available`, `exposure_matrix_internal_consistency_verified = true`, `behavior_equivalence_passed = true`, `no_action_selection_drift = true`, and `no_action_legality_drift = true`.
- If any readiness condition fails, `feature_049_can_be_rerun` MUST be `false`, `feature_049_remaining_blockers` MUST be non-empty, `recommended_next_feature` MUST NOT point to a Feature 049 rerun, and `final_verdict` MUST NOT be `selected_action_outcome_evidence_ready_for_feature_049_rerun`.

Validation language:

- Validation MUST fail if any top-level status field is missing.
- Validation MUST fail if `feature_049_unblock_assessment` is missing.
- Validation MUST fail if `behavior_equivalence_passed` is missing.
- Validation MUST fail if `feature_049_can_be_rerun` is missing.
- Validation MUST fail if `feature_049_remaining_blockers` is missing.
- Validation MUST fail if top-level and nested readiness/status values contradict each other.
- Validation MUST fail if `behavior_equivalence_passed` contradicts `behavior_equivalence_summary.passed`.
- Validation MUST fail if a Feature 049 rerun is recommended while any required evidence status is `unavailable` or `partial`.
- Validation MUST fail if a Feature 049 rerun is recommended while `exposure_matrix_internal_consistency_verified = false`.
- Validation MUST fail if a Feature 049 rerun is recommended while `behavior_equivalence_passed = false`.
- Validation MUST fail if `final_verdict` claims readiness while `feature_049_can_be_rerun = false`.
- Validation MUST fail if `feature_049_remaining_blockers` omits `behavior_equivalence_failed` when `behavior_equivalence_passed = false`.

Validation scope discipline:

- Feature 050 validation MUST use Feature 050 tests for current feature behavior.
- Feature 050 validation MUST use committed-artifact-only checks for prior Features 044, 048, and 049.
- Feature 050 validation MUST avoid any prior-feature test that inspects active worktree dirtiness, active `.specify/feature.json` state, current dirty paths, current branch local-only files, or report regeneration cleanliness from the active worktree.
- Feature 050 validation MUST keep current Feature 050 hygiene rules limited to commit-scope rules such as not staging or committing `.specify/feature.json`, `AGENTS.md`, or unrelated files.

## Complexity Tracking

No constitution violations require justification. The feature remains passive and scoped to evidence expansion only.
