# Quickstart: Paper Baseline Reproduction Campaign

## What this feature does

This feature runs a reproducible campaign across the implemented policies and paper-backed scenarios, then records campaign-level artifacts and a reproducibility bundle reference.

## Expected inputs

- A valid campaign configuration
- Approved policy names
- Approved scenario names
- Fixed seeds
- Optional deterministic timestamp override

## Expected outputs

- Matrix outputs under `matrix/`
- Reproducibility bundle under `bundle/`
- Campaign artifacts under `campaign/`

## Notes

- No dependency files should change for this feature.
- No training or plotting should be introduced by this feature.
- No policy behavior or metric formulas should change.
- Campaign outputs should be deterministic when the same override is supplied.
