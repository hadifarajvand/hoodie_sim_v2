# Implementation Plan: User-Approved Assumption Patch Registry

**Branch**: `031-user-approved-assumption-patch-registry` | **Date**: 2026-05-12 | **Spec**: [`specs/031-user-approved-assumption-patch-registry/spec.md`](spec.md)
**Input**: Feature specification from `/specs/031-user-approved-assumption-patch-registry/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build an analysis-only registry pipeline that converts Feature 030 unrecoverable or partially recovered paper gaps into explicit user-approved assumption records. The registry preserves paper status separately from assumption status, blocks runtime use until an assumption is explicitly approved, and produces deterministic JSON and Markdown audit artifacts without claiming any paper recovery.

## Technical Context

**Language/Version**: Python 3.x using the repo-approved interpreter  
**Primary Dependencies**: Standard library plus existing local analysis modules and Feature 030 closure artifacts  
**Storage**: Files under `resources/papers/hoodie/recovered/` and `artifacts/analysis/`  
**Testing**: `unittest` plus JSON parse and diff-scope validation  
**Target Platform**: Local repository analysis on the approved development environment  
**Project Type**: Analysis/reporting pipeline  
**Performance Goals**: Deterministic registry generation from unchanged inputs; no expensive runtime execution  
**Constraints**: Analysis-only; no simulator runtime changes unless a later approved feature consumes an approved assumption; no new dependencies; no training or network work  
**Scale/Scope**: Limited to the Feature 030 closure report and the in-scope unresolved paper-gap items named in the spec  

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

User approval is required before any later implementation step that would apply an approved assumption to runtime config or behavior.

## Project Structure

### Documentation (this feature)

```text
specs/031-user-approved-assumption-patch-registry/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
resources/papers/hoodie/recovered/
└── user-approved-assumption-registry.json

artifacts/analysis/user-approved-assumption-patch-registry/
├── assumption-patch-report.json
└── assumption-patch-report.md

src/analysis/user_approved_assumption_patch_registry/
├── __init__.py
├── registry.py
├── report.py
└── runner.py

tests/unit/
└── test_user_approved_assumption_patch_registry_*.py

tests/integration/
└── test_user_approved_assumption_patch_registry_*.py
```

**Structure Decision**: Single analysis-focused Python package under `src/analysis/user_approved_assumption_patch_registry/` with registry artifacts in `resources/papers/hoodie/recovered/` and audit reports in `artifacts/analysis/user-approved-assumption-patch-registry/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
