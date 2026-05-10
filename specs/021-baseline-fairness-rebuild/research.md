# Research: Baseline Fairness Rebuild

## Decisions

### 1. Gate Order
- **Decision**: Validate the source gates before running any baseline rebuild.
- **Rationale**: The feature is explicitly conditioned on prior credibility artifacts; running a rebuild before validating those gates would be misleading.
- **Alternatives considered**: Running the matrix regardless and annotating it later was rejected because it weakens the gate and invites false confidence.

### 2. Baseline Set
- **Decision**: Use all existing baseline policies already supported by the baseline evaluation framework.
- **Rationale**: This avoids cherry-picking and preserves the meaning of a fairness rebuild.
- **Alternatives considered**: A smaller hand-picked subset was rejected because it could distort the collapse conclusion.

### 3. Rebuild Scope
- **Decision**: Reuse the smallest existing baseline-evaluation scenarios/traces that already exercise collapse signatures.
- **Rationale**: This keeps the rebuild small and directly comparable while avoiding campaign-scale reproduction.
- **Alternatives considered**: Using the full reproduction matrix was rejected because it is unnecessary for the fairness question and too expensive for a diagnostic rebuild.

### 4. Execution Surface
- **Decision**: Reuse the existing baseline evaluation framework’s runner directly in read-only mode.
- **Rationale**: Reusing the established runner minimizes new machinery and keeps the report comparable to prior baseline outputs.
- **Alternatives considered**: A custom wrapper was considered but rejected because it adds extra orchestration without improving the fairness signal.

### 5. Collapse Classification
- **Decision**: Classify results as `collapse_reduced`, `collapse_unchanged`, `collapse_worsened`, or `inconclusive` using the existing collapse indicators and a qualitative comparison to prior baseline state.
- **Rationale**: The feature needs a stable, reviewer-friendly label without changing metric formulas or inventing new numeric thresholds.
- **Alternatives considered**: Numeric thresholds and policy-specific scoring were rejected because they would be brittle and would blur into metric redesign.

### 6. Report Shape
- **Decision**: Emit JSON and Markdown as required artifacts, with CSV only if already conventional and deterministic in the repository.
- **Rationale**: JSON is machine-checkable, Markdown is human-readable, and CSV is not necessary unless the repository already uses it.
- **Alternatives considered**: Plots were rejected because the feature is diagnostic and must not become a new visualization workflow.

## Assumptions

- Existing baseline evaluation utilities expose enough information to summarize collapse indicators without formula changes.
- The prior credibility artifacts are available in the repository and can be read directly.
- If the rebuild still shows collapse, that is evidence for more mechanism investigation or policy-definition audit rather than an automatic bug.
- The report is diagnostic only and does not claim paper-validity or baseline superiority.

## Report Framing

- The rebuild report must stay conservative: persistent collapse is reported as a valid outcome, not as proof that the rebuild failed.
- The report must not imply that policy redesign or training is required unless a separate analysis explicitly proves that case.
- The report must not present the rebuild as paper-level completeness or baseline superiority evidence.
