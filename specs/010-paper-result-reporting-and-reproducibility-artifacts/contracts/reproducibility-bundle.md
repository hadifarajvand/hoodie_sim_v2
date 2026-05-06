# Contract: Reproducibility Bundle

## Purpose

Define the artifact bundle produced from an evaluation matrix output directory.

## Required Outputs

- `manifest.json`
- `run-config.json`
- `artifact-index.json`
- `validation-summary.json`
- `README.md`

## Bundle Rules

- The bundle must be derived from an existing matrix output directory.
- The bundle must preserve relative artifact paths.
- The bundle must record checksums for discovered artifacts.
- The bundle must record missing expected artifacts in validation output.
- The bundle must remain independent of evaluation metrics and policy behavior.

## Input Contract

- Source directory contains matrix artifacts produced by feature 009.
- Destination directory is separate from the source directory.
- Deterministic timestamp override is optional and used for reproducible test runs.

## Output Contract

- Bundle files are valid JSON or Markdown as appropriate.
- Bundle content is deterministic when input ordering and timestamp override are fixed.
- Missing artifacts are reflected in `validation-summary.json` rather than hidden.
