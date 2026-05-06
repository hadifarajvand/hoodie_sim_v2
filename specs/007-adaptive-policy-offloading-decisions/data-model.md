# Data Model: Adaptive Policy and Offloading Decisions

## Entities

### PolicyContext

Existing policy wrapper used by baselines and the adaptive policy.

- `observation: dict[str, object]`
- `legal_action_mask: dict[str, bool]`
- `trace_history: tuple[object, ...]`

### AdaptiveDecisionContext

Read-only decision bundle built from `PolicyContext` plus optional summaries.

Fields:
- `agent_id: str | int | None`
- `current_slot: int | None`
- `task_id: int | str | None`
- `task_size: float | None`
- `processing_density: float | None`
- `cycles_required: float | None`
- `cycles_remaining: float | None`
- `timeout_slots: int | None`
- `absolute_deadline_slot: int | None`
- `legal_action_mask: dict[str, bool]`
- `queue_load: float | int | None`
- `observed_arrival_probability: float | None`
- `arrivals_per_slot: tuple[int, ...] | None`
- `arrivals_per_agent: tuple[int, ...] | None`
- `latency_estimates: dict[str, float] | None`
- `balance_hint: dict[str, float] | None`
- `topology_metadata: dict[str, object] | None`
- `traffic_summary: dict[str, object] | None`
- `execution_summary: dict[str, object] | None`

Validation rules:
- `legal_action_mask` must remain the source of legality.
- Missing optional fields must be tolerated.
- The structure is immutable from the caller perspective.

### AdaptiveOffloadingPolicy

Deterministic policy that chooses one legal action for the active task only.

Behavioral rules:
- Uses only current context inputs.
- Never silently remaps illegal choices.
- Uses fallback order `local` / `compute_local`, then `horizontal` / `offload_horizontal`, then `vertical` / `offload_vertical` when adaptive fields are absent or tied.
- Does not mutate the environment.

## Relationships

- `PolicyContext` is the input source.
- `AdaptiveDecisionContext` is derived from `PolicyContext` and optional summaries.
- `AdaptiveOffloadingPolicy` consumes `AdaptiveDecisionContext` or equivalent enriched inputs.

## State / Lifecycle

- Context objects are transient and per-decision.
- No persistence layer is introduced.
- No environment lifecycle state is owned here.
