# Research: Feature 063 - Staged Training Budget Learning Curve and Comparison Analysis

## Decision 1: Cumulative staging uses one trainer instance

- **Decision**: Continue training on a single `DDQNTrainer` instance across checkpoint budgets.
- **Rationale**: The feature explicitly requires cumulative staging and forbids fake from-scratch checkpointing when continuation is possible.
- **Alternatives considered**: Restarting at each budget was rejected because it destroys the learning curve signal and violates the prompt.

## Decision 2: Use trainer internals only where the repo has no public continuation helper

- **Decision**: Call the existing trainer rollout/evaluation methods directly, and use the existing checkpoint metadata helpers already present in the repo.
- **Rationale**: The repo has a real trainer but no public staged checkpoint API.
- **Alternatives considered**: Adding new trainer APIs was rejected because the user forbade modifying the existing training logic.

## Decision 3: Reuse one fixed baseline/reference summary

- **Decision**: Load the prior baseline reference artifact once and reuse it across all staged checkpoints.
- **Rationale**: The prompt says the baseline does not need to be rerun four times if it is the same fixed baseline/reference over the same trace bank.
- **Alternatives considered**: Rerunning the baseline at every checkpoint was rejected as redundant and more expensive.

## Decision 4: Matplotlib-only figures

- **Decision**: Generate all required figures with matplotlib only.
- **Rationale**: The user explicitly required matplotlib and forbade seaborn.
- **Alternatives considered**: Seaborn and paper-style composite figures were rejected.

## Decision 5: Claim safety stays descriptive only

- **Decision**: The report can describe trends and readiness, but it must never claim paper reproduction, performance superiority, or baseline superiority.
- **Rationale**: The prompt forbids those claims unless complete real metrics support them.
- **Alternatives considered**: Performance-oriented claims were rejected because they would exceed the available evidence.
