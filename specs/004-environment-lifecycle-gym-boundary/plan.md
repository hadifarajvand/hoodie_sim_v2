# Implementation Plan: 004-environment-lifecycle-gym-boundary

**Branch**: `004-environment-lifecycle-gym-boundary` | **Date**: 2026-04-30 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from [`specs/004-environment-lifecycle-gym-boundary/spec.md`](./spec.md)

## Summary

Complete the existing slot-based HOODIE environment lifecycle and keep the simulator boundary clean:
`reset(seed)` must build a deterministic trace and initialize queues/topology/metrics; `step(action)` must advance exactly one slot, apply one legal decision for one active task, emit delayed terminal reward only after completion/drop, and return a Gymnasium-style tuple without adding a Gymnasium dependency.

The plan deliberately keeps policy execution outside the adapter. It also chooses a documented single-active-task contract for same-slot arrivals: if multiple tasks arrive for the same slot, the adapter presents them in deterministic order and only exposes one active task to `step()` at a time.

## Technical Context

**Language/Version**: Python 3.14.3 in the workspace; repository code is Python and uses modern dataclass/typing features  
**Primary Dependencies**: Standard library only for this feature; no new dependencies, no Gymnasium requirement  
**Storage**: File-backed traces and specs only; no database  
**Testing**: Existing unittest-based unit and integration tests, plus new lifecycle tests in `tests/unit` and `tests/integration`  
**Target Platform**: Local development and evaluation on the approved workstation / Linux-compatible Python runtime  
**Project Type**: Research reproduction simulator / library-style package with evaluation and baseline runners  
**Performance Goals**: Deterministic one-slot step latency; no new asymptotic bottlenecks beyond the existing slot loop  
**Constraints**: No dependency changes, no virtual-environment changes, no neural-network code, no ns-3-gym, no reward/metric formula changes, no source-wide refactors  
**Scale/Scope**: Single repository, single environment adapter, shared baseline evaluation path

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

No constitution violations are required for this plan. The only design risk that needed explicit resolution was the same-slot multi-arrival case, and this plan resolves it with a documented single-active-task contract plus deterministic presentation order.

## Project Structure

### Documentation (this feature)

```text
specs/004-environment-lifecycle-gym-boundary/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── environment-boundary.md
```

### Source Code (repository root)

```text
src/
├── environment/
│   ├── environment.py
│   ├── gym_adapter.py
│   ├── slot_engine.py
│   ├── private_queue.py
│   ├── public_queue.py
│   ├── offloading_queue.py
│   ├── topology.py
│   ├── trace_source.py
│   ├── runtime_model.py
│   ├── reward_timing.py
│   ├── deadline_rules.py
│   └── task.py
├── policies/
│   ├── action_masking.py
│   ├── policy_interface.py
│   ├── flc.py
│   ├── ho.py
│   ├── vo.py
│   ├── ro.py
│   ├── bco.py
│   └── mleo.py
└── evaluation/
    ├── metrics.py
    ├── evaluation_module.py
    ├── runner.py
    └── validation_runner.py

tests/
├── unit/
└── integration/
```

**Structure Decision**: Keep the adapter and lifecycle logic in `src/environment/`, keep action legality in `src/policies/`, and keep shared metrics/evaluation in `src/evaluation/`. The feature does not introduce any new source tree or dependency layer.

## Current-State Audit

### Already implemented

- `src/environment/slot_engine.py`: lifecycle skeleton with named phases, runtime progression hooks, delayed reward hook, and offload-to-public-queue helper.
- `src/environment/environment.py`: environment state snapshots, policy action application helper, and terminal-state finalization helper.
- `src/environment/gym_adapter.py`: reset/step boundary, deterministic trace loading/generation, queue admission, offload/public-queue progression, delayed reward collection, and info assembly.
- `src/environment/reward_timing.py`: terminal-only reward emission and terminal reward calculation.
- `src/environment/runtime_model.py`: shared runtime progression and terminal-state resolution.
- `src/environment/private_queue.py`, `public_queue.py`, `offloading_queue.py`: queue admission/dequeue/waiting-time behavior.
- `src/environment/topology.py`: topology graph and legality lookup.
- `src/environment/trace_source.py` and `src/evaluation/trace_protocol.py`: deterministic trace source and trace construction.
- `src/policies/action_masking.py` and `src/policies/policy_interface.py`: central legality enforcement and policy contract.
- `src/evaluation/metrics.py` and `src/evaluation/evaluation_module.py`: shared metric formulas and evaluation aggregation.
- Existing tests already cover key slices of deterministic replay, policy interface flow, delayed reward, topology legality, offload next-slot behavior, and evaluation pipeline behavior.

### Gaps / stubs

- `src/environment/slot_engine.py`: most phase methods are stubs and need real lifecycle orchestration or explicit delegation into the adapter.
- `src/environment/gym_adapter.py`: already functional, but its same-slot multi-arrival behavior needs to be made explicit in the plan and future implementation.
- `src/environment/environment.py`: helper layer exists, but it does not yet own a full episode boundary or batch lifecycle.
- Trace/debug info is present but needs final contract alignment so lifecycle reconstruction is stable and testable.

## Research

`research.md` documents the decisions needed to remove ambiguity before implementation tasks are written.

### Key decisions recorded there

- Use the existing adapter rather than adding a new boundary module.
- Keep `step()` policy-agnostic; baselines call `reset()` / `step()` externally.
- Keep one action per slot and one active task per `step()`.
- Resolve same-slot multi-arrival cases with deterministic presentation order and a single-active-task constraint.
- Reuse existing deterministic trace generation and trace-bank loading.
- Keep delayed reward terminal-only and shared through the evaluation path.

## Architecture Decision

- **Adapter location**: `src/environment/gym_adapter.py`.
- **Episode state owner**: `HoodieGymEnvironment` owns episode state; `SlotEngine` is the lifecycle orchestrator used by the adapter.
- **Reset initialization**: `reset(seed)` clears queues, metrics, current slot, and history; seeds deterministic trace generation or trace-bank replay; initializes pending arrivals from trace blueprints; loads the first active task if one exists.
- **Step advancement**: `step(action)` advances exactly one slot, applies at most one policy decision to the current active task, progresses queues, emits delayed reward for terminalized tasks, updates metrics, then returns the next observation and control flags.

### Same-slot multi-arrival contract

- The plan uses a **documented single-active-task constraint**.
- If multiple tasks arrive in the same slot, the adapter presents them in **deterministic order**: sort by `arrival_slot`, then `source_agent_id`, then `task_id`.
- Only the first unresolved task is active for `step()`; remaining arrivals stay pending until later slots or later turns in the deterministic presentation order.
- This preserves the one-action-per-step contract and avoids introducing an action dictionary that the current policies do not support.

## Lifecycle Plan

1. **Task arrival/loading**
   - Build deterministic traces from `trace_source` or load from a trace bank.
   - Populate pending arrivals by slot.
   - Load only the next active task into the environment boundary.
2. **Observation construction**
   - Return a slot-level observation mapping keyed by edge-agent ID.
   - Include task features, legal-action mask, queue/load hints, and trace/debug metadata.
3. **Legal action masking**
   - Use the central policy masking helper plus topology adjacency.
   - Reject illegal actions rather than silently remapping them.
4. **Policy/action handoff**
   - Keep policy selection outside the adapter.
   - The adapter accepts a single action for the current active task only.
5. **Private queue admission**
   - Local actions enqueue into the private queue for the source node.
6. **Offload queue admission/progression**
   - Horizontal and vertical actions enqueue into the offloading queue.
   - Offloading progression advances queue state and resolves the next hop.
7. **Public queue admission after offload**
   - After offload completion, move the task into the correct public queue.
8. **Execution progression**
   - Progress the currently executing task through the shared runtime model.
9. **Completion/drop resolution**
   - Finalize task terminal state using the shared runtime/deadline logic.
10. **Delayed reward emission**
    - Emit reward only on completion/drop, never at decision time.
11. **Metric updates**
    - Update shared metrics through `src/evaluation/metrics.py` and the evaluation runner path.
12. **Debug trace emission**
    - Record per-task lifecycle details sufficient to reconstruct arrival, queueing, offload, execution, terminal outcome, and reward timing.

## Interface Contract

- **Observation structure**: `dict[str, Any]`, slot-scoped, keyed by edge-agent ID, with the current task fields and legal-action mask for the active agent.
- **Action structure**: one string action for the current active task; no action dict in the core contract.
- **Reward return structure**: scalar reward equal to the sum of terminal rewards emitted in that slot.
- **terminated / truncated**:
  - `terminated=True` when all generated tasks are fully resolved before the configured horizon.
  - `truncated=True` when the configured slot horizon ends the episode.
- **Info/debug trace structure**: include slot index, queue load, finalized task records, trace metadata, and metrics snapshot.
- **Illegal action behavior**: reject illegal actions via the existing legality check rather than silently correcting them.
- **Empty slot behavior**: when no task is active for the current step, advance the slot and return a no-op update with empty task fields and continued queue progression.

## Constitution Gate

- **Dependency impact**: No dependency additions or version churn.
- **Environment impact**: Keep the approved environment boundary; no new venv or simulator backend.
- **Assumptions impact**: Record any missing paper detail before implementation; the only active assumption is the documented single-active-task contract for same-slot arrivals.
- **Fidelity impact**: Preserve queue, timing, reward, and topology behavior from the paper and existing recovered semantics.
- **Testing impact**: Add lifecycle tests for deterministic replay, legality, queue admission, offload paths, delayed reward, and metric consistency.
- **Reproducibility impact**: Seed all relevant RNG sources and make the trace source deterministic.
- **Config/schema impact**: Avoid new config fields unless a later task proves they are unavoidable; if added, they must be validated and documented.
- **Public interface impact**: Keep the adapter contract stable and document callers/migration if anything changes.
- **Artifact impact**: Do not add generated artifacts to git; keep docs, specs, and tests only.
- **Security impact**: No secret or remote-code concerns are introduced by this feature.
- **Performance budget impact**: Keep the slot loop linear in active tasks; do not add expensive lookahead or batch conversion.
- **Baseline fairness impact**: Baselines and HOODIE use the same adapter and evaluation path.
- **Paper-to-code mapping impact**: Update paper notes for the adapter contract and lifecycle boundary if implementation changes introduce new mappings.
- **Definition-of-done impact**: Feature is done only when artifacts, tests, assumptions, and documentation are all updated and the adapter behaves deterministically.

## Test Plan

- `reset(seed)` determinism.
- Same seed + same baseline policy = same trace.
- One-slot `step()` behavior.
- Full episode with at least one baseline policy.
- Local queue admission.
- Horizontal offload path.
- Vertical cloud offload path.
- Public queue admission after offload.
- Illegal action behavior.
- No-task-slot behavior.
- Delayed reward timing.
- Metric consistency.
- No dependency changes.

## Migration Plan

- Existing baselines continue to call `reset()` / `step()` externally through the adapter.
- The baseline policies in `src/policies/` remain unchanged unless a future task proves an interface mismatch.
- Training specs in `specs/002-torchrl-hoodie-training/` and `specs/003-torchrl-hoodie-training/` remain deferred until environment stability is verified.
- Update existing tests where contract assumptions changed; add new tests for same-slot handling, empty-slot behavior, and adapter boundary semantics.

## Complexity Tracking

No constitution violations are required for this plan, so there is no complexity exception table.
