# Implementation Plan: Controlled Mechanistic Sweeps

**Branch**: `[020-controlled-mechanistic-sweeps]` | **Date**: 2026-05-10 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/020-controlled-mechanistic-sweeps/spec.md`

## Summary

Build a diagnostic-only analysis workflow that runs tiny deterministic sweeps over a small set of mechanism parameters and summarizes only qualitative monotonic behavior. The feature must remain read-only with respect to simulator behavior, metric formulas, policies, campaigns, training, and plotting.

## Technical Context

**Language/Version**: Python 3.x in the approved project interpreter  
**Primary Dependencies**: Existing project modules only; standard library preferred  
**Storage**: Files under `artifacts/analysis/controlled-mechanistic-sweeps/`  
**Testing**: `unittest`-based unit and integration tests  
**Target Platform**: Local project workspace / developer machine  
**Project Type**: Internal analysis/audit feature  
**Performance Goals**: Tiny sweep set completes in under 1 minute under standard local project conditions  
**Constraints**: No simulator/environment changes, no policy changes, no metric formula changes, no campaign reruns, no plotting, no dependency changes, no paper-curve fitting  
**Scale/Scope**: Five tiny deterministic sweep families with fixed seeds and small run counts

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

No constitution gate violations are introduced by this plan. The feature is diagnostic only and does not alter simulator behavior or campaign outputs.

## Project Structure

### Documentation (this feature)

```text
specs/020-controlled-mechanistic-sweeps/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/   # not required; no external interface surface is introduced
└── tasks.md
```

### Source Code (repository root)

```text
src/analysis/controlled_mechanistic_sweeps/
├── __init__.py
├── sweeps.py
├── runner.py
├── report.py
└── classify.py

tests/unit/
└── test_controlled_mechanistic_sweeps.py

tests/integration/
└── test_controlled_mechanistic_sweeps_flow.py

artifacts/analysis/controlled-mechanistic-sweeps/
├── controlled-mechanistic-sweeps.json
└── controlled-mechanistic-sweeps.md
```

**Structure Decision**: Add an isolated internal analysis package under `src/analysis/controlled_mechanistic_sweeps/` and keep the report artifacts namespaced under `artifacts/analysis/controlled-mechanistic-sweeps/`. No contracts directory is required because the feature has no external interface surface.

## Phase 0: Outline & Research

1. Confirm controlled sweep dimensions and fixed value sets from the feature spec and current public interfaces.
2. Determine which sweep dimensions are directly controllable through existing public configuration or environment hooks and which must be classified as inconclusive or instrumentation_gap.
3. Define the qualitative monotonic rule for pass/warn/inconclusive/instrumentation_gap without introducing numeric optimization or reproduction claims.
4. Document assumptions and limitations in `research.md`.

## Phase 1: Design & Contracts

1. Define sweep entities and report schema in `data-model.md`.
2. Define the JSON/Markdown summary shape in `quickstart.md`.
3. Update `AGENTS.md` to point at this plan file for Feature 020.
4. Re-check constitution alignment after the design artifacts are written.

## Implementation Approach

1. Use the current public environment/config interface only.
2. Use tiny deterministic seed sets and tiny run counts.
3. Keep the analysis read-only: no campaign orchestration, no plotting, no metric formula changes, no simulator patches.
4. Produce two deterministic artifacts: JSON and Markdown summaries.
5. Classify unsupported or unobservable sweep dimensions explicitly as inconclusive or instrumentation_gap.

## Validation Strategy

1. Unit tests verify sweep definition schema, monotonic classification logic, and report disclaimers.
2. Integration tests execute the tiny sweeps deterministically and write the JSON/Markdown artifacts to a temporary path.
3. A scope guard test verifies no forbidden source paths, dependency files, campaign artifacts, plots, or simulator changes are introduced.

## Risks and Constraints

- Some sweep dimensions may not be fully controllable through current public hooks; these must remain explicitly classified rather than patched.
- The report must not imply paper-level validity, baseline superiority, or reproduction completeness.
- Any attempt to broaden the feature into campaign reruns or plotting is out of scope.

## Deliverables

- `specs/020-controlled-mechanistic-sweeps/research.md`
- `specs/020-controlled-mechanistic-sweeps/data-model.md`
- `specs/020-controlled-mechanistic-sweeps/quickstart.md`
- `src/analysis/controlled_mechanistic_sweeps/`
- `artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.json`
- `artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.md`
