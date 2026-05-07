# Campaign Result Sanity Audit Contract

## Input Contract

The audit consumes a completed campaign artifact directory containing, at minimum:

- campaign-level summary artifacts
- matrix-level per-run results and matrix summary files
- bundle artifacts when present
- trace artifacts when present

## Output Contract

The audit produces:

- a human-readable audit report
- a machine-readable audit summary
- explicit anomaly findings for:
  - unusually high drop ratio
  - weak policy differentiation
  - weak scenario differentiation
  - missing finalization or accounting inconsistencies

## Behavioral Contract

- The audit is read-only.
- The audit is deterministic for the same input artifact set.
- The audit does not rerun simulations.
- The audit does not rewrite existing artifacts.
- The audit reports missing artifacts explicitly instead of inferring success.

