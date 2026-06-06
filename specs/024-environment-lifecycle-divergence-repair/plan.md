# Implementation Plan: Environment Lifecycle Divergence Repair

**Branch**: `[024-environment-lifecycle-divergence-repair]` | **Date**: 2026-05-10 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/024-environment-lifecycle-divergence-repair/spec.md`

## Summary

Repair remaining `HoodieGymEnvironment` lifecycle divergences only where the reference lifecycle kernel and existing audit evidence support the change. The repair is surgical: local compute and deterministic ordering may be corrected; delayed reward timing may be tightened only when OCR-backed and lifecycle-backed; unresolved instrumentation gaps stay deferred unless strictly required for lifecycle correctness.

## Technical Context

**Language/Version**: Python 3.x in the approved project interpreter  
**Primary Dependencies**: Existing project modules only; standard library preferred  
**Storage**: Files under `artifacts/analysis/differential-environment-audit/` and `artifacts/analysis/environment-lifecycle-divergence-repair/`  
**Testing**: `unittest`-based unit and integration tests  
**Target Platform**: Local project workspace / developer machine  
**Project Type**: Internal diagnostic repair feature  
**Performance Goals**: Keep the repair path small and deterministic; validation should remain fast enough for interactive review  
**Constraints**: No training implementation, no new dependencies, no baseline redesign, no policy redesign, no simulator campaign reruns, no metric formula changes, no paper-validity claim, no TorchRL, no Gymnasium, no ns-3, no ns-3-gym  
**Scale/Scope**: Two lifecycle divergences, one paper-grounded reward assumption, and one regenerated differential audit

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

No constitution gate violations are introduced by this plan. Any repair that would require policy, metric, baseline, or campaign changes is treated as blocked.

## Project Structure

### Documentation (this feature)

```text
specs/024-environment-lifecycle-divergence-repair/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
└── quickstart.md
```

### Source Code (repository root)

```text
src/environment/
├── environment.py
├── deadline_rules.py
└── ...

src/reference_model/
├── __init__.py
├── ledger.py
├── lifecycle.py
└── models.py

tests/unit/
├── test_environment_lifecycle_repair.py
└── test_environment_lifecycle_scope_guard.py

tests/integration/
├── test_environment_lifecycle_repair_flow.py
├── test_environment_lifecycle_reference_alignment.py
├── test_environment_lifecycle_scope_guard.py
└── test_environment_lifecycle_final_diff.py

artifacts/analysis/differential-environment-audit/
├── differential-audit.json
└── differential-audit.md

artifacts/analysis/environment-lifecycle-divergence-repair/
├── repair-summary.json
└── repair-summary.md
```

**Structure Decision**: Keep the repair inside `src/environment/` only where directly required for local-compute or deterministic-ordering correctness. Record the repair outcome under `artifacts/analysis/environment-lifecycle-divergence-repair/` and regenerate the differential audit only if the repaired lifecycle actually changes the divergence classification.

## Phase 0: Outline & Research

1. Confirm the current Feature 018 differential audit still reports `case-local-compute` and `case-deterministic-ordering` as `divergence / likely_environment_bug`.
2. Map the reference lifecycle kernel events for local compute and deterministic ordering to the current environment behavior.
3. Decide whether delayed reward timing needs an update or remains an assumption gap because evidence is insufficient.
4. Document blocked repair conditions for any change that would require policy, metric, baseline, training, or campaign scope expansion.

## Phase 1: Design & Contracts

1. Define the repair boundary and lifecycle entities in `data-model.md`.
2. Define exact regression tests for local compute, deterministic ordering, and scope guards.
3. Define the repair summary shape and the differential audit regeneration contract in `quickstart.md`.
4. Update `AGENTS.md` to point at this plan file for Feature 024.
5. Re-check constitution alignment after the design artifacts are written.

## Implementation Approach

1. Read the reference lifecycle kernel and current differential audit first.
2. Repair local compute and deterministic ordering only if the evidence supports lifecycle-only changes.
3. Keep delayed reward timing strict and paper-backed; if evidence is insufficient, classify it as an assumption gap rather than inventing a fix.
4. Regenerate the differential audit only if the lifecycle repair changes the classification.
5. Stop and report a blocker if the repair would require policy, metric, baseline, training, or campaign changes.

## Validation Strategy

1. Unit tests verify local-compute completion timing, deterministic ordering, and scope restrictions.
2. Integration tests compare `HoodieGymEnvironment` lifecycle outcomes against the reference lifecycle kernel.
3. Final diff tests verify no forbidden paths, dependency files, campaign artifacts, or unrelated simulator areas changed.
4. Repair summary tests verify the diagnostic output and regenerated audit artifact paths.

## Risks and Constraints

- If the environment behavior is not repairable without policy, metric, baseline, or campaign changes, the correct outcome is blocked repair.
- Delayed reward timing must not be changed unless both the OCR and lifecycle evidence support it.
- Horizontal and vertical instrumentation gaps remain out of scope unless they are strictly necessary for lifecycle correctness.

## Deliverables

- `specs/024-environment-lifecycle-divergence-repair/research.md`
- `specs/024-environment-lifecycle-divergence-repair/data-model.md`
- `specs/024-environment-lifecycle-divergence-repair/quickstart.md`
- `artifacts/analysis/environment-lifecycle-divergence-repair/repair-summary.json`
- `artifacts/analysis/environment-lifecycle-divergence-repair/repair-summary.md`
- `artifacts/analysis/differential-environment-audit/differential-audit.json`
- `artifacts/analysis/differential-environment-audit/differential-audit.md`
