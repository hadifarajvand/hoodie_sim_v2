# Research: Smoke Training

## Decision 1: Smoke Data Source

- **Decision**: Use tiny deterministic fixture transitions as the primary smoke source. If an environment rollout is used, it is only for interface validation and not as the main smoke proof.
- **Rationale**: Fixture transitions keep the smoke run bounded and reproducible while avoiding reliance on sparse terminal outcomes.
- **Alternatives considered**: Environment-only rollout was rejected because it adds variance and can blur the line between interface validation and smoke validation.

## Decision 2: Optimizer Step Budget

- **Decision**: Allow exactly one optimizer step.
- **Rationale**: One step is sufficient to prove wiring, finite loss, and parameter update behavior without drifting into training.
- **Alternatives considered**: Two steps were acceptable as an upper bound, but one step is the cleanest bounded check and reduces run time.

## Decision 3: Target Network Handling

- **Decision**: Instantiate the target network but do not sync or update it.
- **Rationale**: Feature 038 still leaves the target-update meaning unresolved, and this smoke feature must not resolve that ambiguity.
- **Alternatives considered**: Syncing the target network was rejected because it would cross into training behavior.

## Decision 4: Smoke Loss

- **Decision**: Use a minimal MSE smoke loss against deterministic fixture targets.
- **Rationale**: MSE is enough to validate finite-loss behavior and parameter updates without pretending to reproduce the paper’s loss exactly.
- **Alternatives considered**: A paper-equation loss was rejected because this feature is explicitly not paper reproduction.

## Decision 5: Replay Buffer Scope

- **Decision**: Do not implement a production replay buffer; use only a tiny smoke fixture schema.
- **Rationale**: A production replay buffer would expand scope and risk turning the feature into a full training pipeline.
- **Alternatives considered**: Full replay support was rejected as out of scope for a bounded smoke run.

## Decision 6: Readiness Gate Interpretation

- **Decision**: Feature 040 is a smoke-only technical exception and does not override the Feature 038 training readiness block.
- **Rationale**: The feature verifies engineering wiring, not readiness for full training or scientific claims.
- **Alternatives considered**: Treating the smoke run as a readiness override was rejected because it would misrepresent the project state.

## Decision 7: Report Content

- **Decision**: Report only engineering smoke metrics: finite loss, parameter change, deterministic repeatability, and no target update. Do not include performance metrics.
- **Rationale**: Performance metrics would encourage interpretation as an experiment rather than a bounded smoke check.
- **Alternatives considered**: Adding throughput or quality metrics was rejected to avoid paper-reproduction framing.
