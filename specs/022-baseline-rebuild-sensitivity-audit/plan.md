# Implementation Plan: Baseline Rebuild Sensitivity Audit

**Branch**: `[022-baseline-rebuild-sensitivity-audit]` | **Date**: 2026-05-10 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/022-baseline-rebuild-sensitivity-audit/spec.md`

## Summary

Run a diagnostic sensitivity audit over the Feature 021 baseline fairness rebuild result using only tiny deterministic variations in seeds, scenarios, and supported episode lengths. The audit is read-only, compares against Feature 021 as the reference point, and reports whether the rebuild conclusion is robust, fragile, worsened, or inconclusive without changing policies, metrics, or simulator behavior.

## Technical Context

**Language/Version**: Python 3.x in the approved project interpreter  
**Primary Dependencies**: Existing project modules only; standard library preferred  
**Storage**: Files under `artifacts/analysis/baseline-rebuild-sensitivity-audit/`  
**Testing**: `unittest`-based unit and integration tests  
**Target Platform**: Local project workspace / developer machine  
**Project Type**: Internal analysis/audit feature  
**Performance Goals**: Tiny audit completes in under 1 minute under standard local project conditions  
**Constraints**: No policy redesign, no new baselines, no DRL training, no neural networks, no simulator/environment changes, no metric formula changes, no campaign-scale reproduction, no plotting, no dependency changes  
**Scale/Scope**: Tiny deterministic sensitivity matrix using all existing baseline policies, supported tiny scenarios, and supported tiny episode-length variations

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

No constitution gate violations are introduced by this plan. The feature reuses the baseline fairness rebuild result in read-only mode and does not change simulator, policy, metric, or training behavior.

## Project Structure

### Documentation (this feature)

```text
specs/022-baseline-rebuild-sensitivity-audit/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/analysis/baseline_rebuild_sensitivity_audit/
├── __init__.py
├── gates.py
├── settings.py
├── classifier.py
├── runner.py
└── report.py

tests/unit/
└── test_baseline_rebuild_sensitivity_audit.py

tests/integration/
├── test_baseline_rebuild_sensitivity_audit_flow.py
├── test_baseline_rebuild_sensitivity_audit_scope_guard.py
└── test_baseline_rebuild_sensitivity_audit_final_diff.py

artifacts/analysis/baseline-rebuild-sensitivity-audit/
├── baseline-rebuild-sensitivity-audit.json
└── baseline-rebuild-sensitivity-audit.md
```

**Structure Decision**: Add an isolated internal analysis/audit package under `src/analysis/baseline_rebuild_sensitivity_audit/` and keep the report artifacts namespaced under `artifacts/analysis/baseline-rebuild-sensitivity-audit/`. No contracts directory is required because the feature has no external interface surface.

## Phase 0: Outline & Research

1. Confirm how the Feature 018/019/020/021 gate artifacts are validated and reported.
2. Determine how the tiny seed, scenario, and episode-length sensitivity sets are represented when a setting is unsupported.
3. Define the conservative sensitivity classification rule for robust/fragile/reduced/unchanged/worsened/inconclusive outcomes.
4. Document assumptions and limitations in `research.md`.

## Phase 1: Design & Contracts

1. Define source gates, sensitivity dimensions, baseline signature entities, and report schema in `data-model.md`.
2. Define the JSON/Markdown summary shape in `quickstart.md`.
3. Update `AGENTS.md` to point at this plan file for Feature 022.
4. Re-check constitution alignment after the design artifacts are written.

## Implementation Approach

1. Read the gate artifacts first and fail fast if the audit is not credible.
2. Reuse the Feature 021 baseline fairness rebuild as the reference point.
3. Run all baselines against identical environment, workload, topology, deadline, reward, and metric settings within each sensitivity setting.
4. Produce deterministic JSON and Markdown reports; CSV only if already conventional and deterministic.
5. Classify sensitivity using existing baseline signatures and preserve the possibility that instability reflects a real mechanism property.

## Validation Strategy

1. Unit tests verify gate validation, sensitivity-setting definitions, classification, and disclaimer framing.
2. Integration tests execute the tiny deterministic sensitivity audit and write the JSON/Markdown artifacts to a temporary path.
3. A scope guard test verifies no forbidden source paths, dependency files, campaign artifacts, plots, or simulator changes are introduced.

## Risks and Constraints

- Some sensitivity settings may be unsupported by the current public interfaces; that is a valid outcome and must be marked inconclusive rather than patched.
- The report must not imply paper-level validity, baseline superiority, or training-driven improvement.
- Any attempt to broaden the feature into policy redesign or training foundation work is out of scope.

## Deliverables

- `specs/022-baseline-rebuild-sensitivity-audit/research.md`
- `specs/022-baseline-rebuild-sensitivity-audit/data-model.md`
- `specs/022-baseline-rebuild-sensitivity-audit/quickstart.md`
- `src/analysis/baseline_rebuild_sensitivity_audit/`
- `artifacts/analysis/baseline-rebuild-sensitivity-audit/baseline-rebuild-sensitivity-audit.json`
- `artifacts/analysis/baseline-rebuild-sensitivity-audit/baseline-rebuild-sensitivity-audit.md`
