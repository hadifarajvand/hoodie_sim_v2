# Research: Baseline Rebuild Sensitivity Audit

## Decisions

### 1. Gate Order
- **Decision**: Validate Feature 018, 019, 020, and 021 artifacts before any sensitivity audit is accepted.
- **Rationale**: The audit only has meaning if it is anchored to the prior baseline fairness rebuild and its credibility gates.
- **Alternatives considered**: Running the audit without gate validation was rejected because it would invite false confidence.

### 2. Sensitivity Scope
- **Decision**: Use a tiny fixed seed set, a supported scenario set, and supported tiny episode lengths only.
- **Rationale**: The feature is a diagnostic robustness check, not a campaign-scale reproduction effort.
- **Alternatives considered**: Broad sweeps were rejected because they would blur the line between sensitivity audit and optimization.

### 3. Reference Point
- **Decision**: Compare directly against the Feature 021 baseline fairness rebuild result.
- **Rationale**: Feature 022 exists to test whether the Feature 021 anti-collapse signal is stable under small perturbations.
- **Alternatives considered**: Recomputing a fresh baseline without reference to Feature 021 was rejected because it would weaken the sensitivity claim.

### 4. Classification
- **Decision**: Classify outcomes as `robust_collapse_reduced`, `fragile_collapse_reduced`, `collapse_unchanged`, `collapse_worsened`, or `inconclusive`.
- **Rationale**: The audit must distinguish stable improvement from fragile improvement and preserve conservative outcomes.
- **Alternatives considered**: A single pass/fail label was rejected because it hides instability.

### 5. Report Shape
- **Decision**: Emit JSON and Markdown as required artifacts, with CSV only if already conventional and deterministic in the repository.
- **Rationale**: JSON is machine-checkable and Markdown is human-readable; CSV is optional and should not expand scope.
- **Alternatives considered**: Plots were rejected because they are unnecessary for the diagnostic question.

## Assumptions

- Feature 021 artifacts are available in the repository and can be used as the reference point for sensitivity checks.
- Supported scenarios and episode lengths are limited to what the current public interfaces already expose.
- If a dimension cannot be controlled through current interfaces, that dimension is reported as inconclusive instead of being patched.
- The audit is diagnostic only and does not claim paper-validity or baseline superiority.
- The audit does not redesign policies, add training, change metric formulas, or expand into campaign-scale reproduction.
