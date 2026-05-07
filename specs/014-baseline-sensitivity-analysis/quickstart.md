# Baseline Sensitivity Analysis Quickstart

## Goal

Inspect committed baseline campaign artifacts and generate a deterministic sensitivity report.

## Inputs

Provide the committed campaign artifact root and, optionally, a separate output directory for sensitivity reports.

## Expected Output

- A machine-readable sensitivity report
- A human-readable sensitivity summary
- Explicit diagnostics for:
  - trace collapse
  - policy behavior collapse
  - scenario output collapse
  - saturation-dominant signals
  - accounting status

## Usage Notes

- The analysis does not mutate existing artifacts.
- The analysis does not rerun simulations.
- The analysis uses the committed campaign artifacts as the source of truth.
- Missing files must be reported, not ignored.

