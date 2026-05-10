# Research: HOODIE Training Foundation Readiness Audit

## Decisions

### 1. Gate Order
- **Decision**: Validate the HOODIE paper OCR, mechanism registry, differential audit, mechanism repair summary, controlled sweeps, baseline fairness rebuild, and baseline rebuild sensitivity audit artifacts before any readiness verdict is accepted.
- **Rationale**: The audit only has meaning if it is anchored to the existing recovery path and prior evidence trail.
- **Alternatives considered**: Running the audit with advisory-only inputs was rejected because it would invite false readiness signals.

### 2. Readiness Verdict
- **Decision**: Use a blocked-readiness default. Any missing required readiness dimension or unsupported evidence source yields blocked readiness rather than partial readiness.
- **Rationale**: A training-foundation audit must be conservative; “mostly ready” is too easy to abuse as a green light.
- **Alternatives considered**: Partial readiness tiers were rejected because they would blur the gate and weaken the audit.

### 3. Readiness Dimensions
- **Decision**: Assess state representation, action-space legality, delayed reward timing, episode protocol, replay/log artifact requirements, DQN mechanism gaps, Double-DQN mechanism gaps, Dueling-DQN mechanism gaps, LSTM mechanism gaps, training/evaluation separation, reproducibility requirements, and pre-training blockers.
- **Rationale**: These are the minimum scientific and architectural prerequisites needed before a future training loop would be credible.
- **Alternatives considered**: A smaller checklist was rejected because it would miss mechanism gaps that are material to DRL readiness.

### 4. Report Shape
- **Decision**: Emit JSON and Markdown as required artifacts, with CSV only if already conventional and deterministic in the repository.
- **Rationale**: JSON is machine-checkable and Markdown is human-readable; CSV is optional and should not expand scope.
- **Alternatives considered**: Plots were rejected because they are unnecessary for a readiness gate.

## Assumptions

- The source artifacts named in the spec are already present and can be used as the source of truth for readiness evaluation.
- If evidence for a readiness dimension is incomplete or unsupported, the audit must classify that dimension as blocked or inconclusive and keep the overall result blocked.
- The audit remains diagnostic only and does not imply paper-level completeness or a recommendation to begin training.
- The audit does not define the future training loop; it only determines whether that future work is premature.

