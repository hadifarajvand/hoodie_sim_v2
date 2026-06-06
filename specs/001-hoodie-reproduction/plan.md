# Implementation Plan: 001-hoodie-reproduction

**Branch**: `001-hoodie-reproduction` | **Date**: 2026-04-21 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/001-hoodie-reproduction/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a shared discrete-time Cloud-Edge Continuum simulator that reproduces the HOODIE paper
through the same environment, workload control, and metric computation used for all baselines and
the HOODIE policy. The plan emphasizes fairness, traceability, and reproducibility over convenience
or simplification.

## Technical Context

**Language/Version**: Python; version must match the approved active environment  
**Primary Dependencies**: Existing project-approved scientific stack already present in the approved
environment; no new dependency assumptions are allowed  
**Storage**: Version-controlled files under `specs/`, `docs/`, `configs/`, `resources/`, `src/`, and
`tests/`  
**Testing**: Unit tests plus integration tests for full-episode simulation and shared evaluation  
**Target Platform**: Local development on the approved user environment; validation on the same
workspace across MacBook Air M3 and GTX 1660 Super targets  
**Project Type**: Simulator / research reproduction project  
**Performance Goals**: Deterministic episode replay, reproducible traces, and bounded per-slot
simulation overhead suitable for experiment sweeps  
**Constraints**: No unapproved dependencies, no undocumented assumptions, no hidden environment
switches, no unfair baseline/HOODIE differences, no silent configuration drift  
**Scale/Scope**: Single-paper reproduction with multiple baselines, shared evaluation traces, and
controlled sweep runs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Dependency Control Rule: pass if no dependency changes are introduced without user approval.
- Environment Rule: pass if all work is tied to the approved virtual environment and no new virtual
  environment is created.
- Assumptions Rule: pass if every paper gap is recorded before implementation depends on it.
- Fidelity Rule: pass if the simulator preserves paper behavior unless approved deviations are
  documented.
- Implementation Order Rule: pass if environment and queue system are prioritized before any neural
  network logic.
- Testing Rule: pass if queue, timing, reward, legality, and integration behaviors are all test
  targets.
- Reproducibility Rule: pass if seeds, configs, environment details, and trace identifiers are all
  treated as required outputs.
- Configuration Rule: pass if every tunable value comes from paper values, config files, or approved
  assumptions.
- Architecture Rule: pass if environment, baselines, learning agents, training loop, configs, tests,
  and analysis remain separated.
- Validation Rule: pass if comparison artifacts are defined up front and deviations are documented.
- Reward Integrity Rule: pass if reward emission is tied to actual completion or drop timing.
- Traceability Rule: pass if debug traces can reconstruct individual task lifecycles.
- Change Scope Rule: pass if the plan stays within the requested reproduction scope.
- Hardware Awareness Rule: pass if the plan respects the declared local development targets.
- Experiment Budget Rule: pass if staged experiments are preserved.
- Paper-to-Code Mapping Rule: pass if paper sections/equations are mapped to simulator modules.
- Configuration Freeze Rule: pass if result-bearing configs are versioned and not edited in place.
- Failure Transparency Rule: pass if missing details stop progress instead of being silently filled.
- Baseline Fairness Rule: pass if baselines and HOODIE share the same environment and evaluation
  protocol.
- Resource Management Rule: pass if paper and reference resources are separated by authority level.

## Project Structure

### Documentation (this feature)

```text
specs/001-hoodie-reproduction/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
```

### Source Code (repository root)

```text
src/
├── environment/
├── policies/
├── evaluation/
├── agents/
├── training/
└── config/

tests/
├── unit/
├── integration/
└── regression/

configs/
analysis/
docs/
└── paper_notes/
```

**Structure Decision**: Use a single shared simulator under `src/environment/`, a shared policy
interface under `src/policies/`, a shared evaluation layer under `src/evaluation/`, and separate
locations for configuration, tests, and analysis artifacts. No baseline receives a different
environment or metric pipeline from HOODIE.

## Environment Execution Order

Each slot must execute in a fixed order so that policy decisions, queue movement, completion timing,
and reward emission remain comparable across baselines and HOODIE:

1. arrival loading or generation
2. task creation
3. observation construction
4. legal action masking
5. policy action selection
6. queue admission
7. offloading progression
8. public-queue admission after offload
9. execution progression
10. completion/drop handling
11. delayed reward emission
12. metric updates

This order is owned by the environment. Policies observe state, choose an action, and do not mutate
task state, queue state, or metric state directly.

## Policy Interface Contract

The shared policy contract must expose the same interaction path for baselines and HOODIE:

- Inputs: the current observation, the legal-action mask, and any policy-visible trace/history state
  allowed by the feature spec.
- Outputs: one action choice for the currently presented task.
- Ownership: the environment owns all state mutation, queue transitions, timing updates, completion
  handling, and reward emission after the action is returned.

The interface must not give any policy an alternate environment path, hidden metric access, or
future-task information that is unavailable to its comparison peers.

## Evaluation Design

Evaluation must use one shared module for all metrics and outputs.

- Comparison runs must use a shared evaluation trace bank or a paired-seed protocol.
- Identical evaluation traces must be replayed across all compared policies when trace-bank replay is
  used.
- The evaluation module must compute per-trace metrics and aggregate metrics from the same shared
  simulator outputs.
- The stored outputs must include both per-trace results and aggregate results so comparisons can be
  audited later.

The evaluation layer must preserve the same environment rules, trace identifiers, and fairness
conditions for baselines and HOODIE.

## Slot Boundary Rules

- Queue admission occurs in the same slot after policy action selection resolves the task's chosen
  action and destination.
- Offload completion admits a task into the destination public queue in the next slot unless the
  paper-defined offload timing for that scenario explicitly states same-slot admission.
- Deadline expiration is checked after execution progression and before reward emission for the slot.
- If completion and drop are both possible in the same slot, terminal completion takes precedence only
  when the task finishes before or at its absolute deadline; otherwise the drop outcome is resolved
  first.
- Delayed rewards are emitted immediately after the terminal outcome is resolved and before metric
  updates for that slot.

## Trace Source Rules

- Evaluation traces may come from pre-generated trace banks or deterministic seed replay.
- The chosen mechanism must be recorded in run metadata.
- Identical evaluation traces must be used across compared policies.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None      | N/A        | N/A                                 |
