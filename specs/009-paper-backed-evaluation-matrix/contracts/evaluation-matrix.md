# Contract: Paper-Backed Evaluation Matrix

## Evaluation Matrix Configuration

### `EvaluationMatrixConfig`

Defines the serial, reproducible matrix scope.

Required inputs:
- policy names
- scenario names
- seeds
- output directory

Optional inputs:
- episode-length override
- runtime configuration reference
- compute configuration reference

Requirements:
- Must validate unsupported names before execution.
- Must not mutate global configuration.
- Must preserve deterministic ordering of policies, scenarios, and seeds.

## Policy Registry

### `resolve_policy(name)`

Returns an implemented policy instance for an approved policy name.

Requirements:
- Must reject unsupported names.
- Must not create aliases for unapproved names.

## Scenario Registry

### `resolve_scenario(name)`

Returns a paper-backed traffic configuration for an approved scenario name.

Requirements:
- Must reject unsupported names.
- Must only return the recovered traffic scenarios.

## Matrix Runner

### `run_matrix(config)`

Executes every approved policy × scenario × seed combination in serial order.

Requirements:
- Must generate traffic through the existing traffic generation feature.
- Must execute through the shared `HoodieGymEnvironment` reset/step loop.
- Must collect existing evaluation metrics without changing formulas.
- Must emit machine-readable per-run artifacts and an aggregate summary.
- Must remain deterministic for identical configs and seed sets.

## Artifact Contract

Per-run record must include:
- policy
- scenario
- seed
- trace identifier
- config snapshot
- dependency-change note

Aggregate output must summarize:
- total runs
- completed runs
- failed runs
- policies
- scenarios
- seeds

## Compatibility

- No special policy-specific environment paths.
- No new traffic models.
- No parallel execution requirement.
- No external trackers required.
