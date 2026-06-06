# Research: Adaptive Policy and Offloading Decisions

## Decision 1: Adaptive context is policy-side metadata, not environment-side control

- **Decision**: Build `AdaptiveDecisionContext` from existing `PolicyContext` data plus optional traffic and compute summaries.
- **Rationale**: The environment must stay policy-agnostic. Context enrichment belongs in the policy layer, where it can consume already-exposed observation data without mutating lifecycle state.
- **Alternatives considered**:
  - Adding a special adaptive mode to `HoodieGymEnvironment`
  - Embedding policy selection inside the environment
  - Both were rejected because they violate the architecture boundary and create special-case control flow.

## Decision 2: Deterministic conservative heuristic, not learned adaptation

- **Decision**: Implement `AdaptiveOffloadingPolicy` as a deterministic heuristic over legal actions and available hints.
- **Rationale**: The clarified scope explicitly excludes DRL training, model switching, LSTM forecasting, and any learned controller changes.
- **Alternatives considered**:
  - Reusing a trained checkpoint selector
  - Adding an LSTM predictor
  - Introducing stochastic tie-breaking
  - All were rejected because they are unsupported or would destroy reproducibility.

## Decision 3: Canonical fallback order is local, then horizontal, then vertical

- **Decision**: When adaptive inputs are missing or tied, fall back deterministically to `local` / `compute_local`, then `horizontal` / `offload_horizontal`, then `vertical` / `offload_vertical`.
- **Rationale**: The user explicitly clarified this fallback order, and it preserves a safe, paper-compatible default without inventing hidden policy behavior.
- **Alternatives considered**:
  - Random fallback
  - Cost-based global search
  - Environment-driven remapping
  - Rejected because they would introduce non-determinism or hidden policy logic.

## Decision 4: Use only exposed signals, never future trace knowledge

- **Decision**: Limit the adaptive policy to the current observation, legal mask, optional traffic summary, optional compute summary, and topology metadata.
- **Rationale**: The clarified scope forbids inspecting the full trace or hidden future load. The policy must remain an autonomous local decision-maker.
- **Alternatives considered**:
  - Looking at future arrivals
  - Reading the entire evaluation trace
  - Using offline trace statistics as a hidden advantage
  - Rejected because they violate local decision semantics and baseline fairness.

## Decision 5: Evaluation metrics stay unchanged

- **Decision**: Do not alter metric formulas; only add labels or metadata identifying the adaptive policy when needed.
- **Rationale**: The user explicitly prohibited formula changes. Metrics must remain comparable with existing baselines.
- **Alternatives considered**:
  - Adding a new adaptive score
  - Modifying delay or reward formulas
  - Rejected because they would change the experiment contract.

## Decision 6: Paper gap handling remains explicit

- **Decision**: If a paper-backed ranking equation cannot be recovered, document the heuristic as assumption-backed rather than paper-backed.
- **Rationale**: The constitution requires failures of recovery to be transparent.
- **Alternatives considered**:
  - Inventing a paper claim for the heuristic
  - Hiding the heuristic in policy code only
  - Rejected because it would undermine traceability.
