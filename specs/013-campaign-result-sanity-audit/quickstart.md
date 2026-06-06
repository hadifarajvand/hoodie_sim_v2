# Campaign Result Sanity Audit Quickstart

## Goal

Inspect completed campaign artifacts and review a deterministic anomaly report.

## Inputs

Provide a completed campaign artifact directory containing campaign, matrix, bundle, and trace outputs.

## Expected Output

- A human-readable audit summary
- A structured audit summary
- Explicit notes for:
  - high drop ratio
  - weak scenario differentiation
  - weak policy differentiation
  - accounting inconsistencies

## Usage Notes

- The audit does not modify artifacts.
- The audit does not rerun simulation work.
- The audit treats existing campaign artifacts as the source of truth.
- Missing files must be reported, not ignored.

