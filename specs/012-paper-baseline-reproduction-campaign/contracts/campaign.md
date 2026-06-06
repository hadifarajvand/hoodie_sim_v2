# Contract: Campaign Reproduction Workflow

## Purpose

Define the campaign-level reproduction workflow that orchestrates existing evaluation matrix and reproducibility bundle outputs.

## Required Inputs

- Campaign name
- Policy names
- Scenario names
- Seeds
- Output directory
- Optional episode-length override
- Optional deterministic timestamp override
- Dependency-change note

## Required Outputs

- `campaign/campaign-manifest.json`
- `campaign/campaign-summary.json`
- `campaign/policy-summary.json`
- `campaign/scenario-summary.json`
- `campaign/determinism-check.json`
- `campaign/README.md`

## Workflow Rules

- The campaign must call `EvaluationMatrixRunner`.
- The campaign must not duplicate environment stepping.
- The campaign must reference the reproducibility bundle output after the matrix run.
- The campaign must keep metric formulas unchanged.
- The campaign must reject unsupported policy and scenario names using existing registries.

## Reporting Rules

- Campaign summaries must be grouped by policy and by scenario.
- Determinism checks must report whether repeated runs match.
- Missing or failed runs must be explicitly reported.
