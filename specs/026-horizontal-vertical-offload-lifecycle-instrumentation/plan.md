# Implementation Plan: Horizontal and Vertical Offload Lifecycle Instrumentation

**Branch**: `[026-horizontal-vertical-offload-lifecycle-instrumentation]` | **Date**: 2026-05-10 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/026-horizontal-vertical-offload-lifecycle-instrumentation/spec.md`

## Summary

Add trace and ledger observability for horizontal and vertical offload lifecycle paths so differential audits can distinguish missing visibility from topology or legality blockers. The feature is observability-only by default: it must not change rewards, metrics, policy decisions, task arrivals, or topology legality. If tests prove a simulator bug, any behavior change must be narrowly scoped to that bug.

## Technical Context

**Language/Version**: Python 3.x in the approved project interpreter  
**Primary Dependencies**: Existing project modules, standard library, differential audit code, environment trace structures  
**Storage**: Files under `artifacts/analysis/differential-environment-audit/` and `artifacts/analysis/offload-lifecycle-instrumentation/`  
**Testing**: `unittest`-based trace schema, ordering, regression, no-behavior-change, and scope-guard tests  
**Target Platform**: Local project workspace / developer machine  
**Project Type**: Internal instrumentation and analysis feature  
**Performance Goals**: Preserve current simulation behavior and keep trace emission deterministic and lightweight  
**Constraints**: No topology fabrication, no policy redesign, no metric changes, no training, no neural-network code, no TorchRL, no Gymnasium, no ns-3, no ns-3-gym, no dependency or lockfile changes, no campaign reruns, no paper-validity claim  
**Scale/Scope**: One offload-observability pass across HoodieGymEnvironment traces and the differential environment audit

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

This plan is valid only if instrumentation stays observational by default. If a bug is proven by tests, the fix may alter behavior only as narrowly as necessary to correct trace correctness. Figure 7 topology conclusions from Feature 025 remain authoritative and may not be rewritten.

## Project Structure

### Documentation (this feature)

```text
specs/026-horizontal-vertical-offload-lifecycle-instrumentation/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md
```

### Source / Artifacts (repository root)

```text
src/environment/
├── [trace-event exposure changes only where needed]

src/audits/differential_environment/
├── [audit consumer updates for richer lifecycle traces]

tests/unit/
├── test_offload_lifecycle_trace_schema.py
├── test_offload_lifecycle_trace_ordering.py
├── test_environment_regressions_feature_019_024.py
└── test_offload_instrumentation_no_behavior_change.py

tests/integration/
├── test_offload_lifecycle_trace_visibility_horizontal.py
├── test_offload_lifecycle_trace_visibility_vertical.py
├── test_differential_environment_audit_offload_observability.py
└── test_offload_instrumentation_scope_guard.py

artifacts/analysis/differential-environment-audit/
├── differential-audit.json
└── differential-audit.md

artifacts/analysis/offload-lifecycle-instrumentation/
├── instrumentation-summary.json
└── instrumentation-summary.md
```

**Structure Decision**: Keep the implementation isolated to trace exposure in `src/environment`, audit consumption in `src/audits/differential_environment`, and the test/report surfaces listed above. No baseline, policy, metric, training, or topology modules are part of this feature.

## Phase 0: Outline & Research

1. Confirm the current differential audit still classifies horizontal and vertical offload cases as unsupported due to missing trace visibility.
2. Confirm the trace event contract and ordering needed to represent the horizontal and vertical lifecycle paths without inventing topology or changing behavior.
3. Define the no-behavior-change boundary and the regression checks that prove Feature 019 and Feature 024 remain intact.
4. Record the explicit topology and paper-evidence boundaries inherited from Feature 025.

## Phase 1: Design & Contracts

1. Define the trace event schema and stable ordering for offload lifecycle events.
2. Define the instrumentation summary and audit-output data model.
3. Define the validation and regression checks that prove rewards, metrics, policy decisions, and arrivals remain unchanged.
4. Update `AGENTS.md` to point at this plan file for Feature 026.
5. Re-check constitution alignment after the design artifacts are written.

## Implementation Approach

1. Start with source gates and pre-instrumentation confirmation so the current failure mode is explicit.
2. Add trace event exposure only where needed to make the offload lifecycle visible.
3. Update the differential audit consumer only if richer traces require it.
4. Regenerate the differential audit and instrumentation summary after instrumentation.
5. Preserve all earlier repairs and topology conclusions; do not broaden scope into policy, metrics, training, or topology fabrication.

## Validation Strategy

1. Unit tests validate trace event schema, deterministic ordering, and no-behavior-change boundaries.
2. Integration tests validate horizontal and vertical lifecycle trace visibility.
3. Regression tests confirm Feature 019 and Feature 024 remain stable.
4. Differential audit regeneration proves the cases are no longer blocked solely by missing trace visibility.
5. Scope-guard tests reject forbidden changes to policy, metric, training, dependency, campaign, and topology-fabrication areas.

## Risks and Constraints

- Trace instrumentation can accidentally mutate behavior if it is implemented too close to decision logic; the feature must avoid that and only fix proven bugs.
- The audit may still need to report explicit topology or legality blockers after observability improves; that is expected and must remain honest.
- Feature 025 topology conclusions remain unrecoverable for Figure 7 adjacency and legal horizontal destinations, and this feature must not claim otherwise.

## Deliverables

- `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json`
- `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.md`
- `artifacts/analysis/differential-environment-audit/differential-audit.json`
- `artifacts/analysis/differential-environment-audit/differential-audit.md`
