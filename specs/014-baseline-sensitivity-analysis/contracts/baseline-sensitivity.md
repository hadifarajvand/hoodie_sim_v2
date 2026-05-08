# Baseline Sensitivity Analysis Contract

## Input Contract

The analyzer consumes a committed artifact root containing:

- campaign summary artifacts
- matrix per-run JSON files
- matrix-summary.csv
- trace JSON files
- optional audit-report.json input

## Output Contract

The analyzer produces:

- a machine-readable sensitivity report
- a human-readable sensitivity summary
- diagnostic labels for:
  - trace_input_collapsed
  - policy_behavior_collapsed
  - scenario_output_collapsed
  - saturation_dominant
  - accounting_clean
  - insufficient_evidence

## Behavioral Contract

- The analyzer is read-only.
- The analyzer is deterministic for the same input artifacts.
- The analyzer does not rerun simulations.
- The analyzer does not mutate committed artifacts.
- The analyzer does not claim paper reproduction validity.

