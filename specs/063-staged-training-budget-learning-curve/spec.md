# Feature Specification: Feature 063 - Staged Training Budget Learning Curve and Comparison Analysis

**Feature Branch**: `[063-staged-training-budget-learning-curve]`
**Created**: 2026-06-19
**Status**: Draft
**Input**: User description: "Feature 063 Staged Training Budget Learning Curve and Comparison Analysis"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cumulative staged training sweep (Priority: P1)

As an analyst, I can continue one real training run across staged episode budgets of 100, 150, 200, and 500 so I can see whether the learning curve changes with more budget before any expensive long campaign.

**Why this priority**: This is the only part that creates new evidence. If staged training does not work cumulatively, the feature is dead on arrival.

**Independent Test**: Run the feature and verify the checkpoint artifacts contain four cumulative checkpoints with budgets `[100, 150, 200, 500]`, evaluation episodes `100` per checkpoint, and no restart from zero between checkpoints.

**Acceptance Scenarios**:

1. **Given** a valid Feature 062 prerequisite report and reusable baseline reference, **When** the staged sweep runs, **Then** the checkpoints are produced in cumulative order without training 5000 episodes.
2. **Given** the first checkpoint at 100 episodes, **When** the second checkpoint is reached, **Then** the second checkpoint reflects 150 cumulative training episodes, not a fresh 150-episode restart.

### User Story 2 - Comparison analysis and reporting (Priority: P2)

As an analyst, I can compare each staged checkpoint against the same fixed baseline/reference summary and generate figures, tables, and a claim-safety report so I can judge readiness without making superiority claims.

**Why this priority**: The learning curve is useless without the comparison artifacts and claim boundary checks that keep the report honest.

**Independent Test**: Run the feature and verify the JSON, Markdown, checkpoint metrics, comparison readiness, figure manifest, and staged comparison table are generated and internally consistent.

**Acceptance Scenarios**:

1. **Given** checkpoint metrics exist, **When** the comparison artifacts are generated, **Then** the report states comparison readiness only and does not claim paper reproduction or superiority.
2. **Given** the baseline reference is reused, **When** the comparison table is generated, **Then** the same baseline summary is used across all staged checkpoints.

### Edge Cases

- What happens when cumulative staging cannot be continued from the same trainer instance? The feature must stop and report a staged-training blocker instead of pretending the checkpoints were cumulative.
- What happens when the baseline reference summary is missing or invalid? Comparison readiness must be false and the report must not claim pass.
- What happens when a metric is unavailable from real execution? The report must set it to `null` and mark it as not claimed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST run staged cumulative training budgets in the exact order `[100, 150, 200, 500]`.
- **FR-002**: The feature MUST continue training on the same trainer instance across checkpoints unless the existing repo APIs make cumulative staging impossible.
- **FR-003**: The feature MUST evaluate each checkpoint with `100` evaluation episodes and `episode_length = 110`.
- **FR-004**: The feature MUST record checkpoint metrics for training budget, cumulative training episode count, optimizer steps, replay size, action distribution, loss summary, reward summary, evaluation reward summary, and claim safety.
- **FR-005**: The feature MUST reuse one baseline/reference summary across checkpoints when that summary is fixed for the same trace bank.
- **FR-006**: The feature MUST generate the required JSON, Markdown, and figure artifacts under `artifacts/analysis/staged-training-budget-learning-curve/`.
- **FR-007**: The feature MUST not modify the environment, DAL, policies, reward semantics, replay semantics, or existing Feature 060/062 logic.
- **FR-008**: The feature MUST not run 5000 episodes.
- **FR-009**: The feature MUST not claim paper reproduction, performance superiority, or baseline superiority.

### Key Entities

- **Checkpoint Metric**: A cumulative snapshot for one training budget, including training, evaluation, loss, reward, and claim-safety fields.
- **Baseline Reference Summary**: The reused fixed baseline/reference evidence used for comparison analysis.
- **Comparison Readiness Summary**: A readiness record showing whether each checkpoint is fit for descriptive comparison.
- **Figure Manifest**: The list of generated matplotlib figures for the staged learning curve.
- **Claim Safety Status**: The claim boundary record that keeps the report inside descriptive analysis only.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The output contains exactly four checkpoints with budgets `100`, `150`, `200`, and `500`.
- **SC-002**: The output shows `training_rerun_from_scratch = false` and a cumulative progression across checkpoints.
- **SC-003**: The output includes `100` evaluation episodes for every checkpoint and `episode_length = 110`.
- **SC-004**: All required artifacts and figures exist under the required output directory.
- **SC-005**: The report stays inside comparison readiness and descriptive trend analysis only, with no unsupported superiority claim.

## Assumptions

- The existing `DDQNTrainer` can be reused in one process and stepped forward cumulatively across checkpoints.
- The Feature 060 baseline reference artifact is available and reusable as a fixed comparison summary.
- Matplotlib is the only plotting library needed for the required figures.
- The staged run is allowed to use the existing trainer internals when there is no public helper for cumulative checkpoint continuation.
