# Implementation Plan: TorchRL-backed HOODIE Training

**Branch**: `[003-torchrl-hoodie-training]` | **Date**: 2026-04-26 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/003-torchrl-hoodie-training/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Integrate TorchRL-backed HOODIE training behind the existing HOODIE agent contract while preserving the simulator, evaluation, validation, packaging, and reproducibility contracts. The plan keeps PyTorch/TorchRL isolated to the learning path, reuses the current unified config, and introduces a deterministic versioned checkpoint flow for trained HOODIE state without changing baseline behavior or validation-only defaults.

## Technical Context

**Language/Version**: Python 3.x in the approved active environment  
**Primary Dependencies**: Existing approved scientific stack plus PyTorch/TorchRL in the HOODIE training path only  
**Storage**: Version-controlled files and deterministic JSON/binary checkpoint artifacts under the repository output directories  
**Testing**: Existing unittest-based unit and integration coverage  
**Target Platform**: Local development on the approved user environment, with deterministic validation in the same workspace  
**Project Type**: Research reproduction simulator / CLI workflow  
**Performance Goals**: Deterministic training runs, byte-identical packaged outputs for identical configs, and no measurable regression in validation-only behavior  
**Constraints**: TorchRL/PyTorch limited to HOODIE training, simulator remains source of truth, replay/loss ownership stays in training, no hidden randomness, no unapproved dependencies  
**Scale/Scope**: Single-paper reproduction with one learned policy family, shared evaluation traces, and reproducible training/validation handoff

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Dependency Control Rule: pass if no dependency changes are introduced without explicit approval and TorchRL/PyTorch remain scoped to HOODIE training.
- Environment Rule: pass if all work targets the approved virtual environment and no new venv is created.
- Assumptions Rule: pass if unrecovered HOODIE details are documented and the TorchRL migration preserves assumption-backed items rather than inventing paper facts.
- Fidelity Rule: pass if the simulator, evaluation, validation, packaging, and reward semantics remain unchanged.
- Implementation Order Rule: pass if the environment remains the source of truth and learning code does not move into simulator, baseline, or validation layers.
- Testing Rule: pass if training, checkpoint, reproducibility, and handoff paths are covered by tests without disturbing existing simulator tests.
- Reproducibility Rule: pass if training and replay seeds are explicitly derived and packaging remains byte-identical for identical runs.
- Configuration Rule: pass if the unified config shape is preserved and only explicit training/checkpoint fields are added.
- Architecture Rule: pass if environment, baselines, learning agents, training loop, configs, tests, and analysis remain separated.
- Validation Rule: pass if validation-only behavior still works by default and trained validation requires an explicit trained-state source.
- Reward Integrity Rule: pass if delayed reward semantics remain owned by the environment and are not redefined by the learner.
- Traceability Rule: pass if trained-state provenance can be reconstructed from packaged artifacts.
- Change Scope Rule: pass if the plan stays within the TorchRL-backed HOODIE training scope.
- Resource Management Rule: pass if paper evidence, assumptions, and training implementation are separated by authority level.

## Project Structure

### Documentation (this feature)

```text
specs/003-torchrl-hoodie-training/
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
├── agents/
├── training/
├── config/
├── repro/
├── evaluation/
├── environment/
└── policies/

tests/
├── unit/
└── integration/
```

**Structure Decision**: Keep TorchRL-backed learning entirely inside `src/agents/` and `src/training/`, with config parsing in `src/config/`, deterministic checkpoint packaging in `src/repro/`, and validation left in `src/evaluation/`. The simulator stays in `src/environment/`, baselines stay in `src/policies/`, and tests remain split between unit and integration coverage.

## Complexity Tracking

No constitution violations require a structural exception at this stage. TorchRL is treated as an internal learning dependency bounded to the HOODIE training path, not as a new architecture tier.
