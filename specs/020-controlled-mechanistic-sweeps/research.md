# Research: Controlled Mechanistic Sweeps

## Decisions

### 1. Sweep Scope
- **Decision**: Keep the feature to tiny deterministic sweeps over arrival probability, timeout, CPU capacity, link rate, and topology density.
- **Rationale**: This is enough to check qualitative monotonic behavior without drifting into campaign-scale experiments or paper reproduction claims.
- **Alternatives considered**: Larger sweeps and broader parameter grids were rejected because they would blur the feature into optimization or campaign reruns.

### 2. Control Surface
- **Decision**: Only use dimensions already exposed through public configuration or the current environment interface.
- **Rationale**: The feature must remain diagnostic-only and must not introduce new simulator hooks just to make every sweep dimension appear supported.
- **Alternatives considered**: Patching the environment to expose hidden controls was rejected because it would violate the no-simulator-change constraint.

### 3. Status Classification
- **Decision**: Use pass, warn, inconclusive, and instrumentation_gap to describe each sweep family.
- **Rationale**: The status values distinguish real monotonic support from weak evidence and from missing control/evidence.
- **Alternatives considered**: A numeric score or confidence interval was rejected because it would add unnecessary complexity and imply statistical rigor the feature does not claim.

### 4. Output Shape
- **Decision**: Emit deterministic JSON and Markdown summaries under `artifacts/analysis/controlled-mechanistic-sweeps/`.
- **Rationale**: The feature needs a machine-readable summary for tests and a human-readable summary for review.
- **Alternatives considered**: Plot outputs were rejected because the feature explicitly forbids plotting and visual curve fitting.

### 5. No Reproduction Claim
- **Decision**: The report must explicitly say the sweeps are not proof of paper-level completeness or baseline superiority.
- **Rationale**: The goal is mechanistic validation only.
- **Alternatives considered**: Framing the sweeps as validation for the full paper claim was rejected because it would overstate the evidence.

## Assumptions

- Existing public environment and configuration hooks are sufficient for at least some sweep dimensions.
- Any unsupported dimension will be documented as inconclusive or instrumentation_gap rather than repaired.
- Fixed seeds and tiny run counts are enough for deterministic qualitative summaries in this feature.
