# Research: Reward Equation and Terminal Reward Contract

## Decision 1: Recover Eq. (20) in normalized form
- **Decision**: Store Eq. (20) as a normalized structured contract with explicit branches for no-task `NaN`, successful completion `-Phi_n(t)`, and thrown/dropped task `-C`.
- **Rationale**: OCR directly exposes the reward branches and the paper text explains the negative-cost convention.
- **Alternatives considered**: Leaving Eq. (20) as prose only, or collapsing all branches into a single sign label. Both would hide the semantics that matter for DRL correctness.

## Decision 2: Recover Eq. (21)-(23) as structured delay-cost definitions
- **Decision**: Store `Phi_n(t)` as a selector between private and public delay cost, `Phi_n^priv(t) = psi_n^priv(t) - t + 1`, and `Phi_n^pub(t)` as a normalized destination/time aggregation with OCR-noise caveat.
- **Rationale**: OCR provides enough structure to recover the functional meaning without inventing unsupported algebraic formatting.
- **Alternatives considered**: Reconstructing the full LaTeX exactly. Rejected because the OCR is noisy and exact punctuation would be guesswork.

## Decision 3: Treat Eq. (24) as a per-agent discounted objective
- **Decision**: Record Eq. (24) as the agent objective that maximizes expected discounted cumulative reward over time slots, with aggregation/reporting noted separately.
- **Rationale**: The OCR is explicit about the discounted sum and the per-agent policy formulation.
- **Alternatives considered**: Conflating the training curve aggregation with the policy objective. Rejected because the paper distinguishes the objective from reported reward curves.

## Decision 4: Classify C = 40 as paper-backed and artifact-backed
- **Decision**: Treat the drop penalty as `C = 40`, recovered from Table 4 / parameter registry.
- **Rationale**: The OCR and recovered registry both support the value.
- **Alternatives considered**: Leaving `C` symbolic only. Rejected because the recovery is strong enough to pin the paper-backed value.

## Decision 5: Keep no-task reward omitted rather than numeric zero
- **Decision**: Represent no-task reward as omitted / NaN-classified, not as a numeric reward.
- **Rationale**: The OCR says no-task arrival yields `NaN` / omitted reward.
- **Alternatives considered**: Mapping no-task slots to zero. Rejected because it would corrupt reward aggregation semantics.

## Decision 6: Validate reward timing through runtime traces
- **Decision**: Treat the paper’s `r_n(t+1)` notation as next-slot terminal-reward notation and validate that runtime emission occurs only at completion/drop terminal events linked to the originating task.
- **Rationale**: Runtime already emits reward through terminal lifecycle events, and the paper notation is compatible with delayed terminal accounting.
- **Alternatives considered**: Forcing immediate action-time reward emission. Rejected because it would contradict both the runtime trace model and the paper’s delayed notation.

## Decision 7: Classify aggregation as partially assumption-backed
- **Decision**: Record per-agent cumulative reward and average across distributed agents as artifact-backed, but keep the exact reduction order assumption-backed.
- **Rationale**: The paper supports the cumulative and averaged reporting language, but not every reduction detail is explicit enough to treat as fully recovered.
- **Alternatives considered**: Declaring the whole aggregation operator fully paper-backed. Rejected because the exact reduction order is not fully evidenced.

## Decision 8: Scope the implementation to analysis and runtime auditing
- **Decision**: Keep training code read-only and refuse any reward repair that requires training-side rewrites.
- **Rationale**: The feature is a contract validation gate, not a training feature.
- **Alternatives considered**: Editing `src/training/delayed_reward_training.py`. Rejected unless a later audit proves a minimal runtime bug repair is impossible without it, in which case the feature should block.
