# Implementation Plan: User-Approved Assumption Patch Registry

**Branch**: `031-user-approved-assumption-patch-registry` | **Date**: 2026-05-12 | **Spec**: [`spec.md`](spec.md)
**Input**: Feature specification from `/specs/031-user-approved-assumption-patch-registry/spec.md`

## Summary

Build an analysis-only registry pipeline for Feature 030 paper gaps and intentionally fold in a governance/runtime-guidance reconciliation so the approved interpreter path and constitution versioning remain internally consistent. The governance portion is a MINOR constitution expansion: it synchronizes the visible constitution footer, sync impact report, and runtime guidance wording around the approved interpreter path at `1.4.0` while intentionally retaining principles 21 through 30.

## Technical Context

**Language/Version**: Python 3.x via the approved interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Standard library plus existing local analysis modules and governance documentation files  
**Storage**: Repository files under `.specify/`, `docs/`, `resources/papers/hoodie/recovered/`, `artifacts/analysis/`, `src/analysis/`, and `tests/`  
**Testing**: `unittest`, JSON parsing, and diff-scope validation  
**Target Platform**: Local repository execution on the approved development environment  
**Project Type**: Analysis/reporting pipeline with governance documentation reconciliation  
**Performance Goals**: Deterministic generation of registry and report artifacts; no expensive runtime execution  
**Constraints**: Governance-only changes for the reconciliation portion; no runtime behavior changes; no new dependencies; no training or network work  
**Scale/Scope**: Limited to Feature 030 closure artifacts, Feature 031 registry/report artifacts, and the approved governance/runtime guidance files referenced in the spec

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

### Governance Decision

This feature follows **Option B, MINOR governance expansion**.

- Constitution version: `1.4.0`
- Sync Impact Report version: `1.4.0`
- Constitution footer version: `1.4.0`
- Approved interpreter path: `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`
- New governance principles: retained intentionally, principles 21 through 30

The governance portion is intentionally expanded to keep the constitution, sync report, footer, and runtime guidance aligned at `1.4.0`. Runtime adoption of assumptions remains out of scope for Feature 031.

## Project Structure

### Documentation (this feature)

```text
specs/031-user-approved-assumption-patch-registry/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output only if needed
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Repository Files Affected by This Feature

```text
.specify/memory/constitution.md
docs/reproducibility.md
AGENTS.md
.specify/feature.json

resources/papers/hoodie/recovered/user-approved-assumption-registry.json
artifacts/analysis/user-approved-assumption-patch-registry/assumption-patch-report.json
artifacts/analysis/user-approved-assumption-patch-registry/assumption-patch-report.md

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

**Structure Decision**: Single analysis-focused Python package for registry/report generation plus a narrow governance/docs reconciliation in the existing feature branch. No new runtime package structure is introduced.

## Phase Plan

### Phase 0: Research

- Confirm the governance change is MINOR-level and intentionally retains principles 21 through 30.
- Validate the constitution sync impact report against the visible footer and identify the exact wording needed to keep them aligned at `1.4.0`.
- Confirm the approved interpreter path is consistently referenced across constitution and reproducibility guidance.
- Confirm the Feature 031 registry/report artifact set remains unchanged by the governance/docs reconciliation.

### Phase 1: Design & Validation

- Define the document-level update boundaries for `.specify/memory/constitution.md`, `docs/reproducibility.md`, and `AGENTS.md` if needed.
- Define the repository-level validation checks that will prove:
  - sync impact report version equals footer version
  - semver level matches the change scope
  - approved interpreter path is consistent
  - no runtime, analysis, registry, or dependency files are touched
- Define the merge order guardrail: Feature 032 does not exist as a separate merge target; Feature 031 remains the branch that will carry the governance cleanup intentionally.

### Phase 2: Implementation Readiness

- Prepare the task graph for the governance/docs cleanup as part of Feature 031 if the feature owner requests execution.
- Keep the Feature 031 assumption registry/report logic frozen unless a later task explicitly touches the governance/docs files referenced above.

## Dependencies & Execution Order

- Governance reconciliation depends on the current Feature 031 registry/report state being stable.
- Any document updates must happen before any future merge/tag of Feature 031.
- Runtime adoption of assumptions is explicitly excluded from this feature and must be handled by a later feature, if ever approved.

## Validation Strategy

- Confirm constitution footer and sync impact report both show version `1.4.0`.
- Confirm the approved interpreter path is exactly `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`.
- Confirm principles 21 through 30 are intentionally retained and documented as the MINOR expansion path.
- Confirm the diff does not touch runtime code, training code, dependency files, topology files, or Feature 031 registry/report artifacts.
- Confirm `.specify/feature.json` is treated only as active Spec Kit metadata while planning and is not left as accidental merge pollution.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
