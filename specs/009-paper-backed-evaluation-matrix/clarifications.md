# Clarifications: Paper-Backed Evaluation Matrix

## Scope Locks

- No training, hyperparameter search, or optimization behavior is part of this feature.
- No paper plots are reproduced; the output is limited to auditable JSON/CSV artifacts.
- No special policy-specific environment path is allowed.
- Unsupported policy and scenario names must fail fast rather than acting as aliases.
- Parallel execution is out of scope; the minimum complete version is serial.
- No external experiment trackers or plotting libraries are required.
