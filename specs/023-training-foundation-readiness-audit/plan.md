# Implementation Plan: HOODIE Training Foundation Readiness Audit

**Branch**: `[023-training-foundation-readiness-audit]` | **Date**: 2026-05-10 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/023-training-foundation-readiness-audit/spec.md`

## Summary

Create a read-only diagnostic audit that determines whether the current HOODIE reproduction project is ready to begin future DRL training work. The audit does not implement training. It validates required source artifacts, checks readiness dimensions, and reports blocked readiness unless every required dimension is supported.

## Technical Context

**Language/Version**: Python 3.x in the approved project interpreter  
**Primary Dependencies**: Existing project modules only; standard library preferred  
**Storage**: Files under `artifacts/analysis/hoodie-training-foundation-readiness-audit/`  
**Testing**: `unittest`-based unit and integration tests  
**Target Platform**: Local project workspace / developer machine  
**Project Type**: Internal analysis/audit feature  
**Performance Goals**: The audit should complete quickly enough for a maintainer to review interactively, ideally under 1 minute on a standard local run  
**Constraints**: No training implementation, no new dependencies, no policy redesign, no simulator/environment behavior changes, no metric changes, no paper-validity claim, no campaign-scale reproduction, no plotting  
**Scale/Scope**: Tiny deterministic diagnostic audit over the current paper OCR and prior audit artifacts

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

No constitution gate violations are introduced by this plan. The feature is diagnostic only and does not modify training, simulator, policy, or metric behavior.

## Project Structure

### Documentation (this feature)

```text
specs/023-training-foundation-readiness-audit/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
└── quickstart.md
```

### Source Code (repository root)

```text
src/analysis/hoodie_training_foundation_readiness_audit/
├── __init__.py
├── gates.py
├── readiness.py
├── report.py
└── runner.py

tests/unit/
└── test_hoodie_training_foundation_readiness_audit.py

tests/integration/
├── test_hoodie_training_foundation_readiness_audit_flow.py
├── test_hoodie_training_foundation_readiness_audit_scope_guard.py
└── test_hoodie_training_foundation_readiness_audit_final_diff.py

artifacts/analysis/hoodie-training-foundation-readiness-audit/
├── hoodie-training-foundation-readiness-audit.json
└── hoodie-training-foundation-readiness-audit.md
```

**Structure Decision**: Add an isolated internal analysis package under `src/analysis/hoodie_training_foundation_readiness_audit/` and keep the report artifacts namespaced under `artifacts/analysis/hoodie-training-foundation-readiness-audit/`. No contracts directory is required because this feature is an internal diagnostic audit with no external interface surface.

## Phase 0: Outline & Research

1. Confirm what each required source artifact contributes to the readiness gate.
2. Determine the readiness dimensions and blocker taxonomy for the audit.
3. Define how blocked readiness, inconclusive evidence, and readiness approval are represented in the report.
4. Document assumptions and limitations in `research.md`.

## Phase 1: Design & Contracts

1. Define source gates, readiness dimensions, blocker entities, and report schema in `data-model.md`.
2. Define the JSON/Markdown summary shape in `quickstart.md`.
3. Update `AGENTS.md` to point at this plan file for Feature 023.
4. Re-check constitution alignment after the design artifacts are written.

## Implementation Approach

1. Read the gate artifacts first and fail closed if the audit evidence is not credible.
2. Treat any missing readiness dimension as a blocker rather than a partial pass.
3. Compare the audit inputs against the paper OCR and prior audits without changing simulator, policy, metric, or training behavior.
4. Produce deterministic JSON and Markdown reports; CSV only if already conventional and deterministic.
5. Keep the audit framing diagnostic only and preserve blocked readiness as the default when evidence is incomplete.

## Validation Strategy

1. Unit tests verify gate validation, readiness-dimension evaluation, verdict taxonomy, and disclaimer framing.
2. Integration tests execute the tiny deterministic audit and write the JSON/Markdown artifacts to a temporary path.
3. Scope-guard tests verify no forbidden source paths, dependency files, campaign artifacts, plots, or simulator changes are introduced.

## Risks and Constraints

- The paper OCR or prior audit artifacts may be incomplete, which should produce blocked readiness rather than optimistic inference.
- The report must not imply that training should begin just because some dimensions are supported.
- Any attempt to broaden the feature into implementation guidance, policy redesign, or training work is out of scope.

## Deliverables

- `specs/023-training-foundation-readiness-audit/research.md`
- `specs/023-training-foundation-readiness-audit/data-model.md`
- `specs/023-training-foundation-readiness-audit/quickstart.md`
- `src/analysis/hoodie_training_foundation_readiness_audit/`
- `artifacts/analysis/hoodie-training-foundation-readiness-audit/hoodie-training-foundation-readiness-audit.json`
- `artifacts/analysis/hoodie-training-foundation-readiness-audit/hoodie-training-foundation-readiness-audit.md`
