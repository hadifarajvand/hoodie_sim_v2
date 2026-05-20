# Implementation Plan: Completion Root-Cause Diagnosis Using Passive Lifecycle Traces

**Branch**: `045-completion-root-cause-diagnosis` | **Date**: 2026-05-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/045-completion-root-cause-diagnosis/spec.md`

## Summary

Analyze passive lifecycle traces produced by Feature 044 to determine why task completions are weak or absent under paper-default `T = 110` runs. The plan is diagnostic only: it must consume existing trace evidence, reconstruct per-task lifecycle paths, classify the dominant root cause class, and recommend the next feature type without changing runtime behavior.

## Technical Context

**Language/Version**: Python 3.x using the approved interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Project-local analysis/runtime modules only; no new dependencies  
**Storage**: File-based analysis artifacts under `artifacts/analysis/completion-root-cause-diagnosis/`  
**Testing**: `unittest`  
**Target Platform**: Local development and CI on Linux/macOS-style POSIX environment  
**Project Type**: CLI-driven simulator analysis feature inside a larger repository  
**Performance Goals**: Deterministic passive diagnosis over paper-default runs; report generation must not change simulator outcomes  
**Constraints**: Diagnostic analysis only; no runtime repair; no environment semantics changes; no reward timing changes; no timeout/deadline changes; no execution/capacity changes; no transmission delay changes; no action legality changes; no policy changes; no training; no optimizer/replay/target update; no curve fitting; no paper reproduction claim  
**Scale/Scope**: Single-feature diagnosis over a fixed paper-default horizon and the approved Feature 044 trace inputs

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

No constitution violations require justification. This feature is passive analysis only and does not alter simulator behavior.

## Project Structure

### Documentation (this feature)

```text
specs/045-completion-root-cause-diagnosis/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/analysis/completion_root_cause_diagnosis/
tests/unit/test_completion_root_cause_schema.py
tests/unit/test_completion_root_cause_classifiers.py
tests/integration/test_completion_root_cause_diagnosis.py
tests/integration/test_completion_root_cause_report.py
tests/integration/test_completion_root_cause_scope_guard.py
artifacts/analysis/completion-root-cause-diagnosis/
```

**Structure Decision**: Add a dedicated passive analysis package under `src/analysis/completion_root_cause_diagnosis/` with unit and integration tests plus report artifacts under `artifacts/analysis/completion-root-cause-diagnosis/`.

## Technical Decisions

- The feature consumes Feature 044 passive traces only and may rerun the Feature 044 trace runner if needed, but it must not add new instrumentation.
- Diagnosis uses paper-default `T = 110` runs with seeds `[0, 1, 2]` and the approved Feature 044 strategy set.
- The report must support multiple root-cause classes per run, ranked by evidence strength, and each class must carry low/medium/high confidence.
- If runtime behavior is proven wrong, the output must route to Feature 046 - Runtime Repair for Completion Lifecycle.
- If runtime behavior is valid but load or action exposure is the issue, the output must route toward observation vector, exploration, or loss-sequence follow-up.
- Older pointer-sensitive report tests remain out of scope; prior features must be validated through committed artifacts and safe tests only.

## Constitution Notes

This feature stays within the constitution because it only adds passive diagnosis, preserves runtime behavior, and uses the approved interpreter. The plan does not justify any deviation from reward, timeout, capacity, transmission, or policy contracts.

## Validation Strategy

The validation command must include the new Feature 045 tests plus safe prior regression tests only. It must exclude pointer-sensitive older report tests and must verify:

- passive trace consumption from Feature 044
- per-task lifecycle reconstruction
- root-cause class evaluation
- completion/drop/pending/reward/counter path separation
- paper-default runtime usage
- no runtime behavior modification
- no training
- no repair approval
- future-feature routing when needed

## Complexity Tracking

No constitution violations require justification.
