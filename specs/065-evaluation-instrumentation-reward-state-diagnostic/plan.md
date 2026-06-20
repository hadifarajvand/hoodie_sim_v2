# Implementation Plan: Feature 065 - Evaluation Instrumentation and Reward/State Diagnostic Repair

**Branch**: `[065-evaluation-instrumentation-reward-state-diagnostic]` | **Date**: 2026-06-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/065-evaluation-instrumentation-reward-state-diagnostic/spec.md`

## Summary

Add a read-only diagnostic package that reruns the staged 100/150/200/500 campaign with instrumentation for evaluation actions, replay-window vs cumulative action histories, per-action outcomes, reward decomposition, state-feature coverage, and policy-effect analysis.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: Existing trainer/environment code, `torch`, `matplotlib`, standard library
**Storage**: JSON/Markdown/PNG files under `artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/`
**Testing**: Focused `pytest` unit and integration tests
**Target Platform**: Local repo execution on Linux/macOS developer workstation
**Project Type**: Analysis/reporting package
**Performance Goals**: Complete the staged diagnostic without running 5000 episodes
**Constraints**: No environment, DAL, policy, reward, or replay semantic changes; no unsupported claims
**Scale/Scope**: One diagnostic rerun with instrumented checkpoints and policy comparison

## Constitution Check

*GATE: Must pass before implementation.*

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
- [x] Claim-safety impact checked
- [x] Prior artifact impact checked

## Project Structure

### Documentation

```text
specs/065-evaluation-instrumentation-reward-state-diagnostic/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
src/analysis/evaluation_instrumentation_reward_state_diagnostic/
├── __init__.py
├── config.py
├── model.py
├── instrumented_evaluator.py
├── diagnostics.py
├── runner.py
├── report.py
└── figures.py

tests/unit/
└── test_evaluation_instrumentation_reward_state_diagnostic_*.py

tests/integration/
└── test_evaluation_instrumentation_reward_state_diagnostic_*.py

docs/architecture/euls_phase24_evaluation_instrumentation_reward_state_diagnostic.md
```

**Structure Decision**: Keep the diagnostic self-contained and read-only. If any existing trainer helper must be used, use it without changing default behavior.
