# Implementation Plan: Load, Admission, and Action-Exposure Review

**Branch**: `046-load-admission-action-exposure-review` | **Date**: 2026-05-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/046-load-admission-action-exposure-review/spec.md`

## Summary

Build a passive diagnostic review that explains paper-default completion weakness using Feature 044 trace evidence and the Feature 045 verdict report. The feature quantifies load pressure, admission serialization, action exposure, queue pressure, offload-path pressure, and representative budget comparisons, then recommends the next feature type without changing runtime behavior.

## Technical Context

**Language/Version**: Python 3.x using the approved interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Project-local analysis modules only; no new dependencies  
**Storage**: File-based analysis artifacts under `artifacts/analysis/load-admission-action-exposure-review/`  
**Testing**: `unittest`  
**Target Platform**: Local development and CI on POSIX environments  
**Project Type**: CLI-driven simulator analysis feature inside a larger repository  
**Performance Goals**: Deterministic passive review over paper-default runs; report generation must not alter simulator outcomes  
**Constraints**: Diagnostic analysis only; no runtime repair; no environment semantics changes; no reward timing changes; no timeout/deadline changes; no execution/capacity changes; no transmission delay changes; no action legality changes; no policy changes; no training; no optimizer/replay/target update; no curve fitting; no paper reproduction claim  
**Scale/Scope**: Single-feature review over a fixed paper-default horizon and the approved Feature 044/045 trace/report inputs

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
specs/046-load-admission-action-exposure-review/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/analysis/load_admission_action_exposure_review/
tests/unit/test_load_admission_action_exposure_schema.py
tests/unit/test_load_admission_action_exposure_metrics.py
tests/integration/test_load_admission_action_exposure_review.py
tests/integration/test_load_admission_action_exposure_report.py
tests/integration/test_load_admission_action_exposure_scope_guard.py
artifacts/analysis/load-admission-action-exposure-review/
```

**Structure Decision**: Add a dedicated passive analysis package under `src/analysis/load_admission_action_exposure_review/` with unit and integration tests plus report artifacts under `artifacts/analysis/load-admission-action-exposure-review/`.

## Technical Decisions

- The feature consumes Feature 044 passive traces and the Feature 045 report as the primary inputs, and may reuse the existing passive trace analysis path if needed.
- Diagnosis uses paper-default `T = 110` runs with seeds `[0, 1, 2]` and the approved Feature 044 strategy set.
- The report must quantify overall load pressure, same-slot admission serialization, legal action exposure versus selected action distribution, queue family pressure, offload-path pressure, and representative task budget comparisons.
- The review must support multiple pressure sources per run, ranked by evidence strength and confidence where applicable.
- If the evidence is insufficient to separate load from action exposure, the report must state that explicitly rather than forcing a conclusion.
- Runtime repair is out of scope unless traces uncover a verified runtime-fault contradiction; if that happens, the feature should document the contradiction and route to the next diagnostic or repair feature without changing runtime behavior here.
- Canonical follow-up terminology is limited to `Feature 047 — Paper HOODIE Observation Vector`, `Feature 048 — Delayed-Reward DDQN Loss Contract`, `Feature 049 — Exploration Schedule Contract`, and `exposure-matrix review`.
- Loose synonyms such as observation-vector, observation vector, pilot-policy review, and exposure matrix/pilot policy review are prohibited.

## Constitution Notes

This feature stays within the constitution because it only adds passive diagnosis, preserves runtime behavior, and uses the approved interpreter. The plan does not justify any deviation from reward, timeout, capacity, transmission, action legality, or policy contracts.

## Validation Strategy

The validation command must include the new Feature 046 tests plus safe prior regression tests only. It must exclude pointer-sensitive older report tests and must verify:

- passive trace consumption from Feature 044
- use of the Feature 045 report as a prior-feature input
- load/admission/action exposure quantification
- same-slot admission serialization and lag
- queue pressure and offload-path pressure summaries
- per-action distribution and per-action outcomes
- paper-default runtime usage
- no runtime behavior modification
- no training
- no repair approval
- future-feature routing when needed

## Complexity Tracking

No constitution violations require justification.
