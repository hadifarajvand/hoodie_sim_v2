# Implementation Plan: Mechanism Repair

**Branch**: `[019-mechanism-repair]` | **Date**: 2026-05-10 | **Spec**: [`specs/019-mechanism-repair/spec.md`](spec.md)
**Input**: Feature specification from `/specs/019-mechanism-repair/spec.md`

## Summary

Apply a surgical repair to the timeout/drop terminal accounting path only, using the committed Feature 018 audit as the gate. The repair must be proven by regression tests first, preserve the public environment interface, and regenerate the Feature 018 differential audit after the fix so the repaired divergence is no longer reported as a divergence if behavior now matches.

## Technical Context

**Language/Version**: Python 3.11 in the approved project interpreter `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Standard library plus existing project code only; no new dependencies  
**Storage**: File-based artifacts under `artifacts/analysis/` and repository-tracked source/tests  
**Testing**: `unittest` via the approved interpreter  
**Target Platform**: Local development environment on the repository’s current Linux/macOS-compatible project setup  
**Project Type**: Simulator reproduction project with internal audit/repair workflow  
**Performance Goals**: No new performance target; preserve existing step semantics and delayed reward timing  
**Constraints**: No dependency drift, no policy/baseline/campaign changes, no metric formula changes, no topology repair, no offload instrumentation repair, no paper-curve fitting  
**Scale/Scope**: One confirmed divergence fix, one regression test path, one audit regeneration pass

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
specs/019-mechanism-repair/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── environment/
│   └── gym_adapter.py   # public environment boundary for timeout/drop accounting
├── reference_model/     # Feature 017 comparison source only
└── audits/              # Feature 018 audit source only

tests/
├── integration/
└── unit/
```

**Structure Decision**: Keep the repair inside the smallest environment path that owns public `step`-level terminal accounting. Add regression tests in `tests/unit/` and `tests/integration/`, and regenerate only the Feature 018 audit artifacts after the fix. No new contracts directory is required because this is an internal repair feature.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
