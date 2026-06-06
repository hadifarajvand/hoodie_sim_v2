# Quickstart: 001-hoodie-reproduction

## Goal

Validate the shared HOODIE reproduction workflow from configuration through evaluation without
breaking fairness or reproducibility rules.

## Minimum Checks

1. Confirm the approved environment is active.
2. Confirm the feature directory is `specs/001-hoodie-reproduction/`.
3. Confirm configuration files are present for the run.
4. Confirm the selected evaluation trace bank or saved seed set is recorded.
5. Confirm the shared evaluation module is used for all policies.
6. Confirm outputs include average delay, drop ratio, and convergence traces.

## Minimal Validation Workflow

1. Run one environment sanity check and confirm one local-processing path, one horizontal offload
   path, one timeout/drop path, and one delayed-reward emission path are all observable.
2. Run one baseline smoke comparison against HOODIE using the shared evaluation path.
3. Run one trace replay reproducibility check using the same saved trace bank or paired seed set and
   confirm the outputs match the recorded reference run.

## Validation Expectations

- Baselines and HOODIE must run through the same environment.
- Trace-based replay or paired workload control must be identifiable in the run metadata.
- Result-bearing configuration files must remain unchanged after use.
- Unknown paper details must be logged as gaps before they affect a run.
