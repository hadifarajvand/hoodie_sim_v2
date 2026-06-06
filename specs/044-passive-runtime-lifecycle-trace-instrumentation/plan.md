# Implementation Plan: Passive Runtime Lifecycle Trace Instrumentation

**Branch**: `044-passive-runtime-lifecycle-trace-instrumentation` | **Date**: 2026-05-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/044-passive-runtime-lifecycle-trace-instrumentation/spec.md`

## Summary

Add passive lifecycle trace instrumentation that exposes task-level runtime evidence for paper-default `T = 110` runs without changing simulator decisions, rewards, timing, legality, or queue behavior. The implementation must generate report artifacts only from a clean workspace, except for an optional local `.specify/feature.json` pointer, and it must distinguish trace support from trace observation so the report can explain absent completions without overclaiming.

## Technical Context

**Language/Version**: Python 3.x using the approved interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Project-local runtime modules only; no new dependencies  
**Storage**: File-based artifacts under `artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/`  
**Testing**: `unittest`  
**Target Platform**: Local development and CI on Linux/macOS-style POSIX environment  
**Project Type**: CLI-driven simulator analysis feature inside a larger repository  
**Performance Goals**: Deterministic passive trace collection for paper-default runs; trace overhead must not change observable simulator outcomes  
**Constraints**: No runtime semantics changes; no reward timing changes; no timeout/deadline changes; no capacity or transmission changes; no action legality changes; no policy changes; no training or optimizer execution; no paper reproduction claim  
**Scale/Scope**: Single-feature passive instrumentation across a fixed paper-default diagnostic horizon and a small set of validated seeds

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

No constitution violations require justification. This feature is passive instrumentation only and does not alter simulator behavior.

## Project Structure

### Documentation (this feature)

```text
specs/044-passive-runtime-lifecycle-trace-instrumentation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/environment/lifecycle_trace.py
src/environment/gym_adapter.py
src/analysis/passive_runtime_lifecycle_trace_instrumentation/
tests/unit/test_lifecycle_trace_schema.py
tests/unit/test_lifecycle_trace_behavior_equivalence.py
tests/integration/test_passive_lifecycle_trace_runtime.py
tests/integration/test_passive_lifecycle_trace_report.py
tests/integration/test_passive_lifecycle_trace_scope_guard.py
artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/
```

**Structure Decision**: Add a passive lifecycle trace module in `src/environment/` for event creation and recording, then add a dedicated analysis package under `src/analysis/passive_runtime_lifecycle_trace_instrumentation/` with unit and integration tests plus report artifacts under `artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/`.

## Technical Decisions

- Reports must be generated only when the workspace is clean except for an optional local `.specify/feature.json` pointer file.
- `AGENTS.md` is treated as a disallowed dirty path for report regeneration.
- The paper-default report sample must come from the approved Feature 044 probe configuration, not from ad-hoc fixtures.
- Trace reporting must distinguish `event_type_supported`, `event_type_observed`, and `event_type_missing_from_instrumentation`.
- `task_completed` must remain supported even if not observed in the sample.
- For timeout/drop paths, `deadline_expired` must be emitted before or alongside `task_dropped`, and `reward_emitted` must follow the terminal event.
- Behavior-equivalence checks must be aggregated so each unique name appears once.

## Constitution Notes

This feature stays within the constitution because it only adds passive observability, preserves runtime behavior, and uses the approved interpreter. The plan does not justify any deviation from the reward, timeout, capacity, transmission, or policy contracts.

## Validation Strategy

The validation command must include the new Feature 044 tests plus safe prior regression tests only. It must exclude pointer-sensitive older report tests and must verify:

- report cleanliness rules
- paper-default sample bounds and metadata
- `deadline_expired` ordering for drop paths
- `task_completed` support even when not observed
- deduplicated behavior-equivalence checks
- no false audit flags
- no simulator semantic drift

## Complexity Tracking

No constitution violations require justification.

