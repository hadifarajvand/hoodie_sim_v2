# Research: Dynamic Traffic Generation & Simulation Adaptability

## Decision 1: Add a dedicated traffic configuration module

- **Decision**: Introduce `src/environment/traffic_config.py` with a `TrafficConfig` dataclass and static preset factories for `paper_default`, `moderate`, `heavy`, and `extreme`.
- **Rationale**: The paper-backed traffic settings are scenario data, not environment lifecycle logic. A dedicated config module keeps the presets testable and avoids hardcoding traffic constants inside the generator or the environment boundary.
- **Alternatives considered**:
  - Hardcoding the traffic values in the generator. Rejected because it makes scenario validation brittle.
  - Encoding presets only in docs. Rejected because the feature needs executable, seedable presets.

## Decision 2: Generate Bernoulli traffic deterministically with seeded standard-library RNG

- **Decision**: Implement `src/environment/traffic_generator.py` around a seeded `random.Random(seed)` instance and a nested slot-by-agent loop that creates exactly one task when `rand < P`.
- **Rationale**: The paper’s Algorithm 1 is Bernoulli arrival logic, not a richer traffic process. A seeded standard-library RNG gives reproducibility without new dependencies or lifecycle side effects.
- **Alternatives considered**:
  - Using a global RNG. Rejected because it would not be reproducible across tests and callers.
  - Introducing Poisson, Markov, burst, or anomaly logic. Rejected because the feature spec explicitly forbids unsupported models.

## Decision 3: Preserve the paper’s traffic units directly in the trace path

- **Decision**: Carry paper traffic values directly through the generator and trace blueprint path, instead of hiding them behind a synthetic scale factor.
- **Rationale**: The feature needs to reproduce the paper’s `0.1` Mbit step size and `0.297` gigacycles/Mbit density exactly. A hidden unit conversion would invent behavior that is not paper-backed.
- **Alternatives considered**:
  - Converting everything into tenths or hundredths of a unit behind the scenes. Rejected because that creates an undocumented internal convention.
  - Converting sizes into a separate integer-only representation without recording the mapping. Rejected for the same reason.

## Decision 4: Use a deterministic mapping over the paper-backed discrete task-size set

- **Decision**: Assign each generated task a size by deterministically indexing into the paper-backed discrete size set, using the seed and task identifier, rather than introducing a stochastic size distribution.
- **Rationale**: The OCR confirms the discrete set of valid task sizes but does not recover a paper-backed distribution for sampling from that set. A deterministic mapping preserves the allowed values, avoids inventing a distribution, and keeps same-seed replay reproducible.
- **Alternatives considered**:
  - Uniformly sampling from the size set. Rejected because it invents an unsupported distribution.
  - Always selecting the minimum or maximum size. Rejected because it is less informative than deterministic indexing and still not paper-backed.

## Decision 5: Keep compatibility with the existing `EvaluationTrace` / `TraceTaskBlueprint` path

- **Decision**: Generate traffic into the existing evaluation-trace surface so `HoodieGymEnvironment.reset(seed)` can consume the workload without a new lifecycle wrapper.
- **Rationale**: The completed environment boundary from feature 004 already owns the lifecycle contract. Traffic generation should feed that path, not replace it.
- **Alternatives considered**:
  - Adding a new environment controller or a second episode runner. Rejected because it would bypass the stable adapter boundary.
  - Reworking `HoodieGymEnvironment` to own traffic generation directly. Rejected because it mixes workload generation with lifecycle orchestration.

## Decision 6: Expose a traffic observer for full-trace and rolling-window summaries

- **Decision**: Implement `src/environment/traffic_observer.py` to compute traffic summaries over the full trace by default and over a caller-provided rolling window when requested.
- **Rationale**: The adaptability requirement is observability, not model switching. Summary metrics need to tell later features how loaded the traffic is without changing simulator semantics.
- **Alternatives considered**:
  - Building LSTM or anomaly-detection logic now. Rejected because it is explicitly out of scope.
  - Recording only raw arrivals with no summary helper. Rejected because the feature goal includes observed arrival probability and load metrics.

## Decision 7: Keep same-slot ordering delegated to the existing environment contract

- **Decision**: Traffic generation will preserve deterministic per-slot, per-agent ordering in the generated records, while `HoodieGymEnvironment` continues to serialize same-slot arrivals using its existing one-active-task contract.
- **Rationale**: The environment boundary already defines how same-slot arrivals are presented. The traffic layer should not introduce a second ordering policy.
- **Alternatives considered**:
  - Introducing action dictionaries or multi-action batching for same-slot arrivals. Rejected because it would change the adapter contract.

## Resulting implementation shape

- `TrafficConfig` owns traffic parameters and preset factories.
- `TrafficTrace` owns generated records, the trace seed, and summary metadata.
- `TrafficObserver` computes configured and observed arrival probabilities plus arrival counts.
- `EvaluationTrace` remains the compatibility carrier into `HoodieGymEnvironment`.
- No new dependency, no lifecycle ownership change, and no training-layer work are required.
