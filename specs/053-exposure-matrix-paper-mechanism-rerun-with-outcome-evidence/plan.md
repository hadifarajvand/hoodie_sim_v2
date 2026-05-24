# Implementation Plan: Exposure Matrix Paper Mechanism Rerun with Outcome Evidence

**Branch**: `053-exposure-matrix-paper-mechanism-rerun-with-outcome-evidence` | **Date**: 2026-05-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/053-exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/spec.md`

## Summary

Rerun the Feature 049 exposure-matrix paper-mechanism alignment using the committed evidence stack from Features 048 through 052. The feature is diagnostic and evidence-only: it consumes committed reports, verifies that Feature 052 is rerun-ready, recomputes the alignment statuses needed to judge paper-mechanism readiness, and produces a verdict that decides whether the project can move into the next paper-mechanism repair or training-readiness phase.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Standard library analysis package plus committed prior-feature artifact JSON reports  
**Storage**: File-based JSON and Markdown artifacts under `artifacts/analysis/exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/`  
**Testing**: `unittest` via the approved interpreter; Feature 053 validation uses Feature 053 tests and committed-artifact-only checks for Features 048, 049, 050, 051, and 052  
**Target Platform**: Local Linux/macOS development and CI  
**Project Type**: CLI-driven analysis package inside a simulator repository  
**Performance Goals**: Produce the rerun report quickly enough for routine evidence review  
**Constraints**: Evidence rerun only; no training, optimizer, replay, target update, campaign, or policy/runtime semantic changes  
**Scale/Scope**: Single-feature rerun over committed Feature 048 through 052 artifacts

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
specs/053-exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
```

### Source Code (repository root)

```text
src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/
├── __init__.py
├── __main__.py
├── config.py
├── model.py
├── runner.py
└── report.py

tests/
├── integration/
│   ├── test_exposure_matrix_paper_mechanism_rerun.py
│   ├── test_exposure_matrix_paper_mechanism_rerun_report.py
│   └── test_exposure_matrix_paper_mechanism_rerun_scope_guard.py
└── unit/
    ├── test_exposure_matrix_paper_mechanism_rerun_schema.py
    ├── test_exposure_matrix_paper_mechanism_rerun_metrics.py
    └── test_exposure_matrix_paper_mechanism_rerun_behavior_equivalence.py

artifacts/analysis/exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/
```

**Structure Decision**: A single passive analysis package under `src/analysis/exposure_matrix_paper_mechanism_rerun_with_outcome_evidence/` that consumes committed Feature 048 through 052 evidence and emits rerun reports only.

## Phase 0: Outline & Research

Research is limited to the committed prior evidence reports and the already-populated Feature 052 rerun-ready report.

### Decisions

1. Use Feature 052 readiness as a hard prerequisite gate.
2. Recompute exposure-matrix paper-mechanism alignment from committed Feature 048 through 052 evidence only.
3. Separate observation-vector alignment, formula/unit alignment, exposure-matrix alignment, and selected-action-outcome alignment into independent report fields.
4. Preserve training-readiness contract evaluation as a report-level decision, not a runtime repair target.
5. Keep behavior-equivalence checks unique and passive so rerun analysis cannot silently alter simulator semantics.

### Research Deliverable

`research.md` will record the evidence contract, blocker routing, and the reasons placeholder-driven alternatives were rejected.

## Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. Extract entities and relationships into `data-model.md`.
2. Define the report contract in `contracts/`.
3. Write `quickstart.md` for report generation and validation.

### Design Focus

- Feature 052 readiness gate validation
- Observation-vector alignment
- Formula/unit alignment
- Exposure-matrix alignment
- Selected-action-outcome alignment
- Training-readiness contract assessment
- Behavior-equivalence audit with unique check names

### Report Contract

The Feature 053 report MUST expose these top-level fields:

- `feature_052_trace_readiness_verified`
- `observation_vector_alignment_status`
- `formula_unit_alignment_status`
- `exposure_matrix_alignment_status`
- `selected_action_outcome_alignment_status`
- `training_readiness_contract_status`
- `paper_mechanism_alignment_ready`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`
- `behavior_equivalence_passed`
- `behavior_equivalence_summary`

Validation scope:

- Feature 053 validation MUST use Feature 053 tests for current behavior.
- Feature 053 validation MUST use committed-artifact-only checks for prior Features 048, 049, 050, 051, and 052.
- Feature 053 validation MUST avoid any prior-feature test that inspects active worktree dirtiness, active `.specify/feature.json` state, current dirty paths, or prior report regeneration cleanliness from the active worktree.
- Feature 053 validation MUST keep current hygiene rules limited to commit-scope rules such as not staging or committing `.specify/feature.json`, `AGENTS.md`, or unrelated files.

Readiness rule:

- `feature_052_trace_readiness_verified` must be true only when Feature 052 reports `feature_049_can_be_rerun = true`, `feature_049_remaining_blockers = []`, `per_action_outcome_evidence_status = available`, `exposure_matrix_internal_consistency_verified = true`, and `final_verdict = selected_action_outcome_evidence_ready_for_feature_049_rerun`.
- If the Feature 052 readiness gate fails, the rerun analysis MUST be blocked, `paper_mechanism_alignment_ready` MUST be false, and `remaining_blockers` MUST be non-empty.
- `behavior_equivalence_passed` MUST equal `behavior_equivalence_summary.passed`.
- Each alignment status field MUST be one of `available`, `partial`, or `unavailable`.

Validation failure conditions:

- The plan MUST fail if the Feature 052 readiness gate is false.
- The plan MUST fail if any required alignment status field is missing.
- The plan MUST fail if rerun verdicts, blocker lists, or readiness states are fabricated rather than derived from committed evidence.
- The plan MUST fail if `paper_mechanism_alignment_ready` is true while any required alignment status is partial or unavailable.
- The plan MUST fail if `remaining_blockers` is empty while readiness is false.
- The plan MUST fail if `behavior_equivalence_passed` contradicts `behavior_equivalence_summary.passed`.
- The plan MUST fail if `final_verdict` claims readiness while `paper_mechanism_alignment_ready` is false.
- The plan MUST fail if `recommended_next_feature` routes to Feature 054 while required alignment evidence is unavailable.
