# Implementation Plan: Reward Equation and Terminal Reward Contract

**Branch**: `[029-reward-equation-terminal-reward-contract]` | **Date**: 2026-05-11 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/029-reward-equation-terminal-reward-contract/spec.md`

## Summary

Recover the HOODIE reward equation contract from OCR and artifact evidence, then validate the runtime terminal-reward bridge without starting DRL training. The plan is to encode and audit the reward sign, no-task behavior, drop penalty, delayed terminal emission, and aggregation classification while preserving the existing environment lifecycle and trace contract.

## Technical Context

**Language/Version**: Python 3.x with the session-approved interpreter `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Standard library, project-local modules only; no new third-party dependencies  
**Storage**: File-based artifacts under `artifacts/analysis/reward-equation-terminal-reward-contract/`  
**Testing**: Existing project test runner via the approved Python interpreter; targeted unit and integration tests  
**Target Platform**: Local Linux/macOS development environment for the repository workspace  
**Project Type**: Simulation / research reproduction codebase  
**Performance Goals**: Deterministic validation runs; no training workload introduced  
**Constraints**: No DRL training, no neural-network changes, no TorchRL, no Gymnasium, no ns-3, no dependency changes, no topology fabrication, no policy redesign, no reward shaping, no curve fitting  
**Scale/Scope**: Single-feature audit and contract bridge across paper OCR, runtime traces, and environment reward emission

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

No constitution principle is violated by the planned scope. Any training code mutation, dependency change, or hidden reward shaping would be a direct constitution breach and is excluded.

## Project Structure

### Documentation (this feature)

```text
specs/029-reward-equation-terminal-reward-contract/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── analysis/
│   └── reward_equation_terminal_reward_contract/
├── environment/
│   ├── gym_adapter.py
│   ├── offload_trace_ledger.py
│   ├── offload_trace_schema.py
│   ├── reward_timing.py
│   └── task.py
├── evaluation/
└── training/
    └── delayed_reward_training.py

tests/
├── unit/
└── integration/
```

**Structure Decision**: Keep the reward contract bridge in `src/analysis/reward_equation_terminal_reward_contract/` with runtime validation anchored in `src/environment/gym_adapter.py`, `src/environment/reward_timing.py`, `src/environment/offload_trace_ledger.py`, and read-only inspection of `src/training/delayed_reward_training.py`. The runtime environment remains the orchestration owner; any reward contract repair must stay event-driven and trace-linked.

## Phase 0: Research Plan

Evidence sources already identified:
- `resources/papers/hoodie/ocr/merged.tex`
- `resources/papers/hoodie/recovered/paper-parameter-registry.json`
- `artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json`
- `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json`
- `artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.json`

Research tasks:
- Normalize Eq. (20)-(24) into structured reward-evidence records.
- Classify completion reward, drop penalty, no-task omission, and delayed terminal timing.
- Classify aggregation as paper-backed per-agent reward, artifact-backed episode averaging, and assumption-backed reduction order.
- Audit the runtime reward path and trace linkage without modifying training code.

## Phase 1: Design Plan

- Define a compact reward contract schema for the analysis report.
- Record raw OCR support, normalized equations, confidence, and classification for each recovered term.
- Preserve source wording such as `task thrown` while documenting runtime terminology normalization to `dropped` / `timeout` only as a mapping note.
- Mark any unrecoverable algebraic detail explicitly rather than guessing.
- Keep the report faithful to the runtime observation that reward emission is terminal and trace-linked through lifecycle events.

## Constitution Re-check

The planned design remains aligned with the constitution because:
- Reward emission is handled as a terminal lifecycle event, not a decision-time side effect.
- No new dependency, package, or environment is required.
- Training code is inspect-only and not part of the edit scope.
- Artifact generation is limited to the feature-owned analysis report and markdown companion.
- Paper-to-code mapping remains explicit through the contract report and tests.

## Complexity Tracking

No constitution violations require justification. The design intentionally avoids complexity escalation by not changing training orchestration, not adding a new environment layer, and not broadening the reward semantics beyond the paper-backed contract bridge.
