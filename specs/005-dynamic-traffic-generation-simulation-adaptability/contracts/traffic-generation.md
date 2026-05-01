# Contract: Traffic Generation & Observability

## Purpose

Define the seedable traffic-generation boundary that feeds the already-stable `HoodieGymEnvironment` without changing its lifecycle contract.

## Interface

### `TrafficConfig`

- Holds the scenario name, agent count, episode length, arrival probability, slot duration, timeout, size range, and processing density.
- Must validate the approved scenario names: `paper_default`, `moderate`, `heavy`, `extreme`.

### `TrafficScenarioPreset`

- Static factory layer for the approved paper-backed presets.
- Returns validated `TrafficConfig` instances only.

### `TrafficGenerator.generate(config, seed) -> TrafficTrace`

- Samples one Bernoulli arrival trial per agent per slot.
- Creates exactly one task per successful arrival.
- Returns a deterministic workload when called with the same config and seed.
- Orders records deterministically by `arrival_slot`, `source_agent_id`, then `task_id`.
- Selects task sizes deterministically from the paper-backed discrete size set because the OCR recovers the set of valid sizes but not a paper-backed stochastic size distribution.

### `TrafficTrace`

- Owns the generated records, the originating config, the seed, and the compatibility `EvaluationTrace`.
- Exposes helpers to serialize into the same `tasks` payload shape already consumed by `TraceSource.load()` and to rebuild the compatibility `EvaluationTrace`.

### `TrafficObserver.summarize(trace, window_slots: int | None = None) -> TrafficSummary`

- Reports configured arrival probability, observed arrival probability, total arrivals, arrivals per slot, arrivals per agent, scenario name, seed, and task-size range.
- Uses the full trace by default.
- When `window_slots` is provided, reports a clipped rolling-window summary over the same generated records.

## Trace payload contract

- The generated payload must remain compatible with the existing evaluation trace loader.
- Each task record must include `task_id`, `source_agent_id`, `arrival_slot`, `size`, `processing_density`, `timeout_length`, and `absolute_deadline_slot`.
- No hidden scaling, synthetic arrival model, or lifecycle behavior may be introduced by the generator.

## Environment compatibility contract

- The traffic layer feeds `HoodieGymEnvironment` through the existing trace surface.
- `reset(seed)` and `step(action)` remain the only lifecycle entry points.
- Same-slot multi-agent arrivals remain serialized by the environment’s existing one-active-task contract.
- `SlotEngine` remains helper-only and does not own traffic or lifecycle control.

## Non-goals

- No Gymnasium dependency.
- No ns-3 or ns-3-gym integration.
- No model switching, LSTM, anomaly detection, or traffic-policy logic.
- No training, agent, or neural-network changes.
