# Implementation Plan: Baseline Fairness Rebuild

**Branch**: `[021-baseline-fairness-rebuild]` | **Date**: 2026-05-10 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/021-baseline-fairness-rebuild/spec.md`

## Summary

Rebuild baseline fairness using the existing baseline evaluation framework, existing baseline policies, and the smallest existing fairness-relevant scenarios/traces after the mechanism credibility gates have passed. The feature is diagnostic only: it reassesses collapse signatures, does not redesign policies, and does not introduce training or simulator changes.

## Technical Context

**Language/Version**: Python 3.x in the approved project interpreter  
**Primary Dependencies**: Existing project modules only; standard library preferred  
**Storage**: Files under `artifacts/analysis/baseline-fairness-rebuild/`  
**Testing**: `unittest`-based unit and integration tests  
**Target Platform**: Local project workspace / developer machine  
**Project Type**: Internal analysis/rebuild feature  
**Performance Goals**: Tiny fairness matrix completes in under 1 minute under standard local project conditions  
**Constraints**: No policy redesign, no new baselines, no DRL training, no neural networks, no simulator/environment changes, no metric formula changes, no campaign-scale reproduction, no plotting, no dependency changes  
**Scale/Scope**: Small deterministic baseline matrix using all existing baseline policies and the smallest existing collapse-relevant scenarios/traces

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

No constitution gate violations are introduced by this plan. The feature reuses the baseline evaluation framework in read-only mode and does not change simulator, policy, metric, or training behavior.

## Project Structure

### Documentation (this feature)

```text
specs/021-baseline-fairness-rebuild/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md
```

### Source Code (repository root)

```text
src/analysis/baseline_fairness_rebuild/
├── __init__.py
├── gates.py
├── runner.py
├── report.py
└── classify.py

tests/unit/
└── test_baseline_fairness_rebuild.py

tests/integration/
└── test_baseline_fairness_rebuild_flow.py

artifacts/analysis/baseline-fairness-rebuild/
├── baseline-fairness-rebuild.json
└── baseline-fairness-rebuild.md
```

**Structure Decision**: Add an isolated internal analysis/rebuild package under `src/analysis/baseline_fairness_rebuild/` and keep the report artifacts namespaced under `artifacts/analysis/baseline-fairness-rebuild/`. No contracts directory is required because the feature has no external interface surface.

## Phase 0: Outline & Research

1. Confirm which source-gate artifacts are required and how their presence/status should be reported.
2. Determine which baseline policies and scenarios/traces are the smallest existing fairness-relevant set.
3. Define the qualitative collapse classification rule for reduced/unchanged/worsened/inconclusive using existing collapse indicators only.
4. Document assumptions and limitations in `research.md`.

## Phase 1: Design & Contracts

1. Define source gates, baseline matrix entities, collapse indicators, and report schema in `data-model.md`.
2. Define the JSON/Markdown summary shape in `quickstart.md`.
3. Update `AGENTS.md` to point at this plan file for Feature 021.
4. Re-check constitution alignment after the design artifacts are written.

## Implementation Approach

1. Read the gate artifacts first and fail fast if the rebuild is not credible.
2. Reuse the existing baseline evaluation framework directly in read-only mode.
3. Run all baselines against identical environment, workload, topology, deadline, reward, and metric settings.
4. Produce deterministic JSON and Markdown reports; CSV only if already conventional and deterministic.
5. Classify collapse using existing evaluation indicators and preserve the possibility that persistent collapse is a mechanism property.

## Validation Strategy

1. Unit tests verify gate validation, collapse classification, and disclaimer framing.
2. Integration tests execute the tiny deterministic rebuild and write the JSON/Markdown artifacts to a temporary path.
3. A scope guard test verifies no forbidden source paths, dependency files, campaign artifacts, plots, or simulator changes are introduced.

## Risks and Constraints

- Some baseline collapse signatures may remain unchanged or worsened even after the mechanism repairs; that is a valid outcome and must not be normalized away.
- The report must not imply paper-level validity, baseline superiority, or training-driven improvement.
- Any attempt to broaden the feature into policy redesign or training foundation work is out of scope.

## Deliverables

- `specs/021-baseline-fairness-rebuild/research.md`
- `specs/021-baseline-fairness-rebuild/data-model.md`
- `specs/021-baseline-fairness-rebuild/quickstart.md`
- `src/analysis/baseline_fairness_rebuild/`
- `artifacts/analysis/baseline-fairness-rebuild/baseline-fairness-rebuild.json`
- `artifacts/analysis/baseline-fairness-rebuild/baseline-fairness-rebuild.md`
