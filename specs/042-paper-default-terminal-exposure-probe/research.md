# Research: Paper-default Terminal Exposure Probe

## Decision 1: Probe horizon

- **Decision**: Use the paper-default horizon `T = 110` for the diagnostic probe.
- **Rationale**: Feature 042 exists specifically to determine whether terminal exposure appears under the paper-default episode horizon, not the short readiness horizon.
- **Alternatives considered**:
  - `T = 20`: rejected because it reproduces the readiness gate rather than the paper-default diagnostic.
  - Mixed horizons: rejected because they blur the diagnostic signal.

## Decision 2: Probe strategies

- **Decision**: Include deterministic strategies for default behavior, forced local, forced horizontal, forced vertical/cloud, and optional mixed legal action selection.
- **Rationale**: The probe must separate environment exposure from action-selection behavior without changing policy design.
- **Alternatives considered**:
  - Default policy only: rejected because it cannot isolate whether other legal actions unlock terminal exposure.
  - Learned-policy probe: rejected because this feature is diagnostic only and not training.

## Decision 3: Reward timing and pending-at-horizon

- **Decision**: Preserve delayed rewards only on completion or drop; keep pending-at-horizon non-terminal.
- **Rationale**: The diagnostic must observe the existing simulator contract rather than create terminal evidence.
- **Alternatives considered**:
  - Treat pending-at-horizon as terminal: rejected because it would fabricate terminal exposure.
  - Alter reward timing: rejected because it would invalidate the diagnosis.

## Decision 4: Reporting policy

- **Decision**: Emit JSON and Markdown reports that explicitly record per-strategy counters, aggregate terminal exposure, lifecycle integrity, and the next recommended diagnostic feature.
- **Rationale**: The output must support an honest go/no-go decision without suggesting reproduction.
- **Alternatives considered**:
  - Single summary number only: rejected because it hides strategy-level behavior.
  - Reproduction-style reporting: rejected because Feature 042 is not a reproduction claim.

## Decision 5: Training boundary

- **Decision**: Do not train, optimize, or update targets in Feature 042.
- **Rationale**: The feature answers a diagnostic question; training remains Feature 041-gated behavior.
- **Alternatives considered**:
  - Run pilot training if exposure appears: rejected because this feature is not a training gate.
  - Modify runtime to force exposure: rejected because it would be fake reproduction.
