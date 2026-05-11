# Implementation Plan: Computation Delay / CPU Unit Validation

**Branch**: `[028-computation-delay-cpu-unit-validation]` | **Date**: 2026-05-11 | **Spec**: [`specs/028-computation-delay-unit-validation/spec.md`](./spec.md)
**Input**: Feature specification from `/specs/028-computation-delay-unit-validation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Audit and validate computation-delay semantics, CPU-capacity semantics, and seconds-to-slots conversion with deterministic evidence-backed reports. The feature will expose the paper-backed unit meanings, classify missing CPU capacities honestly, and either repair or explicitly block the slot-duration mismatch between the recovered paper default `Δ = 0.1 s` and the current runtime/report behavior if evidence supports a narrow correction.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11  
**Primary Dependencies**: Standard library plus existing HOODIE project modules  
**Storage**: Files under `artifacts/analysis/` and `specs/`  
**Testing**: `unittest` via the approved virtual environment  
**Target Platform**: Local reproduction workspace on Linux/macOS-compatible Python runtime  
**Project Type**: Simulation/reproduction repository with analysis helpers  
**Performance Goals**: Deterministic validation with no campaign reruns; tests should remain fast enough for local CI  
**Constraints**: No training, no policy redesign, no metric redesign beyond explicit unit contract correction, no dependency or lockfile changes, no topology fabrication  
**Scale/Scope**: Narrow unit-contract validation over a fixed reproduction codebase

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

User approval is required before edits, refactors, or other repository actions when the constitution
or current session guidance requires it.

## Project Structure

### Documentation (this feature)

```text
specs/028-computation-delay-unit-validation/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── analysis/
│   └── computation_delay_cpu_unit_validation/
├── environment/
└── ...

tests/
├── unit/
└── integration/

artifacts/
└── analysis/
    └── computation-delay-cpu-unit-validation/
```

**Structure Decision**: Use the existing HOODIE simulator layout, with a narrow analysis package in `src/analysis/computation_delay_cpu_unit_validation/` and validation tests under `tests/unit/` and `tests/integration/`. Environment config files may be touched only if tests prove a minimal, evidence-backed unit bug.

## Complexity Tracking

No constitution violations are currently justified. If the Δ mismatch requires a narrow runtime correction, it must be documented as a minimal evidence-backed repair and not a broad simulator rewrite.
