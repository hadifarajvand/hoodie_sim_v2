# Implementation Plan: Paper Assumption Closure and Evidence Exhaustion Pipeline

**Branch**: `030-paper-assumption-closure-evidence-exhaustion-pipeline` | **Date**: 2026-05-11 | **Spec**: [`specs/030-paper-assumption-closure-evidence-exhaustion-pipeline/spec.md`](spec.md)
**Input**: Feature specification from `/specs/030-paper-assumption-closure-evidence-exhaustion-pipeline/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build an analysis-only evidence-exhaustion pipeline that inventories all remaining paper-related uncovered or assumption-backed items, searches paper and prior-artifact sources, records evidence strength and contradictions, supports manual visual review only where defensible, and emits a deterministic closure report. The pipeline does not change runtime behavior; it produces an auditable classification for each item so later implementation work cannot silently use fabricated topology, capacities, timeout values, or reward semantics.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.x used by the repo-approved interpreter  
**Primary Dependencies**: Standard library plus existing project analysis/runtime modules and local paper artifacts  
**Storage**: Files in `artifacts/analysis/` and optional recovered registries under `resources/papers/hoodie/recovered/`  
**Testing**: `unittest` plus report-generation and JSON validation checks  
**Target Platform**: Local Linux/macOS development environment for repository analysis  
**Project Type**: analysis pipeline / repository tooling  
**Performance Goals**: Deterministic report generation from the same inputs; no expensive runtime work or campaign execution  
**Constraints**: Analysis-only by default; no runtime behavior changes unless a later approved feature explicitly uses recovered evidence  
**Scale/Scope**: Limited to paper evidence, prior feature reports, recovered registries, and closure artifacts

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
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: Single analysis-focused Python project under `src/analysis/` with report artifacts in `artifacts/analysis/` and tests under `tests/unit/` and `tests/integration/`. No application split is needed because the feature is analysis-only and does not expose a UI or external service.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
