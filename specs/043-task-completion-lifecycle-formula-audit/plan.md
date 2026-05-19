# Implementation Plan: Task Completion Lifecycle and Formula Audit

**Branch**: `043-task-completion-lifecycle-formula-audit` | **Date**: 2026-05-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/043-task-completion-lifecycle-formula-audit/spec.md`

## Summary

Build a diagnostic-only audit package that explains why paper-default `T = 110` probes produce reward-bearing terminal drops but zero task completions. The implementation will not change runtime semantics, reward timing, timeout behavior, capacities, or policies. It will calculate expected compute/transmission slot counts from the paper-default formulas, extract lifecycle evidence from existing runtime outputs, classify the breakpoint honestly, and write reproducible audit reports.

## Technical Context

**Language/Version**: Python 3.x using the approved interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Project-local runtime modules only; no new dependencies  
**Storage**: File-based artifacts under `artifacts/analysis/task-completion-lifecycle-formula-audit/`  
**Testing**: `unittest`  
**Target Platform**: Local development and CI on Linux/macOS-style POSIX environment  
**Project Type**: CLI-driven analysis package inside a larger simulator repository  
**Performance Goals**: Deterministic audit output for a small set of seeded trace analyses; no expensive sweeps  
**Constraints**: No runtime/environment semantic changes; no reward timing changes; no timeout, topology, CPU, transmission, or policy changes; no training or optimizer execution  
**Scale/Scope**: Single-feature diagnostic audit across a small fixed seed set and a fixed set of probe strategies

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

No constitution violations require justification. The feature is analysis-only and does not alter simulator behavior.

## Project Structure

### Documentation (this feature)

```text
specs/043-task-completion-lifecycle-formula-audit/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/analysis/task_completion_lifecycle_formula_audit/
tests/unit/test_task_completion_formula_audit.py
tests/unit/test_task_completion_lifecycle_schema.py
tests/integration/test_task_completion_lifecycle_audit.py
tests/integration/test_task_completion_lifecycle_report.py
tests/integration/test_task_completion_lifecycle_scope_guard.py
artifacts/analysis/task-completion-lifecycle-formula-audit/
```

**Structure Decision**: Add a standalone analysis package under `src/analysis/task_completion_lifecycle_formula_audit/` with unit and integration tests under the existing `tests/` layout and report artifacts under `artifacts/analysis/task-completion-lifecycle-formula-audit/`.

## Complexity Tracking

No constitution violations require justification.
