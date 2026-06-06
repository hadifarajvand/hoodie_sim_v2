# Research: Transmission Delay Runtime Wiring

## Decision 1: Keep transmission-delay ownership in `HoodieGymEnvironment`

- **Decision**: Compute transmission metadata when a task is admitted to offloading, record it on the task metadata, and let `SlotEngine` only decide whether the head of the queue may move on.
- **Rationale**: The environment already owns orchestration, queue selection, and trace emission. Moving delay calculation into `SlotEngine` would collapse the helper-only boundary and blur runtime ownership.
- **Alternatives considered**:
  - Put delay logic in `SlotEngine`: rejected because the helper is intentionally admission-only.
  - Put delay logic on `Task`: rejected because it would turn `Task` into a policy object instead of a data record.

## Decision 2: Reuse the existing delay helper exactly

- **Decision**: Use `src/environment/link_rate_config.py::compute_transmission_delay()` as the single source of `delay_slots` and delay seconds.
- **Rationale**: The helper already validates payload bits, link rate, slot duration, and rounding policy. Reusing it avoids a second timing model and keeps slot rounding consistent.
- **Alternatives considered**:
  - Reimplement delay math in the environment: rejected because it duplicates logic and risks boundary drift.
  - Introduce a new helper: rejected because the repo already has the approved helper.

## Decision 3: Store transmission state on task metadata

- **Decision**: Record `transmission_started_at`, `transmission_completed_at`, `transmission_delay_slots`, `transmission_delay_seconds`, `transmission_payload_bits`, `transmission_data_rate_bps`, and `transmission_rate_source` on the task metadata, and use those fields for deterministic admission.
- **Rationale**: The task object already carries lifecycle metadata and trace linkage. Metadata fields are the lightest way to preserve traceability without changing the task schema.
- **Alternatives considered**:
  - Add a new transmission state object: rejected because it adds a parallel state model for one runtime concern.
  - Encode timing only in queue timestamps: rejected because queue entry time alone is insufficient to explain the boundary.

## Decision 4: Keep the admission boundary explicit and deterministic

- **Decision**: Admit a task to downstream execution only when `current_slot >= transmission_started_at + transmission_delay_slots`.
- **Rationale**: This matches the clarified contract and avoids off-by-one ambiguity. A zero-delay transfer remains deterministic and can be admitted on the same step once the boundary condition is true.
- **Alternatives considered**:
  - `current_slot > boundary`: rejected because it inserts an unnecessary one-slot lag.
  - Special-case zero delay with separate logic: rejected because it creates a second boundary rule.

## Decision 5: Preserve existing link-rate values and rounding policy

- **Decision**: Horizontal uses `30 Mbps`, vertical uses `10 Mbps`, and `compute_transmission_delay()` keeps the default `ceil` slot rounding unless explicitly configured otherwise.
- **Rationale**: These values are already approved by Feature 032 and documented in the link-rate contract.
- **Alternatives considered**:
  - Add a cloud-specific transmission rate: rejected because Feature 034 explicitly forbids it.
  - Tune delay to fit curves: rejected because the feature is runtime wiring, not curve fitting.

## Decision 6: Keep timeout and reward timing unchanged

- **Decision**: Transmission delay counts toward runtime delay for timeout evaluation, but reward is still emitted only at the terminal completion or drop event.
- **Rationale**: Reward timing is a Feature 033 contract and must not be changed by transmission wiring.
- **Alternatives considered**:
  - Emit reward during transmission: rejected because it violates the terminal-only reward contract.
  - Rewrite timeout semantics: rejected because the feature does not own deadline policy.

## Decision 7: Validate with targeted regression tests only

- **Decision**: Add unit and integration tests around helper delay computation, queue admission boundaries, metadata recording, timeout/drop behavior, and delayed reward emission.
- **Rationale**: The feature is narrow. Targeted tests prove the wiring without dragging in training or campaign infrastructure.
- **Alternatives considered**:
  - Add new campaign runs: rejected by scope.
  - Add neural-network or policy tests: rejected because no policy behavior changes are in scope.
