# Research: 004-environment-lifecycle-gym-boundary

## Current mismatch audit

- The adapter boundary, helper-only `SlotEngine` boundary, same-slot serialization, delayed reward timing, and external baseline loop are now aligned in the docs and implementation.
- The remaining work in this feature is test closure, traceability updates, and the no-dependency cleanup note.

## Decision 1: Adapter boundary

- **Decision**: Use the existing `src/environment/gym_adapter.py` boundary as the official `reset(seed)` / `step(action)` entry point.
- **Rationale**: The adapter already wraps the slot-based simulator core and already exposes the Gymnasium-style tuple shape without requiring a new dependency.
- **Alternatives considered**: Introduce a new wrapper module or a new Gymnasium dependency. Both would fragment the boundary and violate the dependency constraint.

## Decision 2: Episode state ownership

- **Decision**: `HoodieGymEnvironment` owns all episode and slot lifecycle orchestration; `SlotEngine` is helper-only.
- **Rationale**: This keeps ownership fixed at the environment boundary and avoids a risky controller refactor.
- **Alternatives considered**: Move lifecycle ownership into `SlotEngine` or make `SlotEngine` the controller. Both would blur architecture boundaries and create unnecessary churn.
- **Implementation guardrail**: `SlotEngine.run_slot()`, `SlotEngine.slot_flow`, and `SlotEngine.slot_flow_names()` are architectural drift and must be removed or hard-disabled so they cannot advance a slot, sequence lifecycle phases, or imply orchestration ownership.

## Decision 3: Same-slot multi-arrival handling

- **Decision**: Document a single-active-task contract with deterministic presentation order for same-slot arrivals.
- **Rationale**: The current policy interface is single-action, the recovered paper model is slot-based and per-agent, and an action-dict boundary would require larger interface changes.
- **Alternatives considered**: Action dictionary support or a global batched action surface. Those options would ripple through policies, tests, and evaluation and are not required to preserve the simulator semantics.

## Decision 4: Deterministic replay

- **Decision**: Use the existing deterministic trace generation and trace-bank loading mechanisms, seeded from `reset(seed)`.
- **Rationale**: This is already aligned with the reproducibility rule and the current trace protocol.
- **Alternatives considered**: Introduce a new RNG system or new trace loader. Both would create unnecessary risk.

## Decision 5: Reward timing

- **Decision**: Keep delayed reward terminal-only and return it as a scalar sum per slot.
- **Rationale**: The paper-backed semantics and the existing reward helper already define reward at completion/drop, not decision time.
- **Alternatives considered**: Per-task reward dict or per-agent reward dict. Those would complicate the adapter contract without improving fidelity.

## Decision 6: Baseline execution

- **Decision**: Baselines drive the adapter externally through `reset()` / `step()`; any episode runner must be a thin wrapper.
- **Rationale**: This keeps the environment boundary clean and preserves baseline fairness.
- **Alternatives considered**: Internal policy execution inside the adapter. That would mix environment and policy responsibilities.

## Decision 7: No new dependency boundary

- **Decision**: Keep the environment boundary dependency-free beyond the repository's existing approved Python stack; do not add Gymnasium, ns-3, or ns-3-gym.
- **Rationale**: The feature is an interface cleanup around the existing simulator, not a simulator replacement or dependency expansion.
- **Alternatives considered**: Introducing Gymnasium or a new simulator package. Both would expand the boundary and violate the feature constraints.
