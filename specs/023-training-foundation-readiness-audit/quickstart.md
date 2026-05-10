# Quickstart: HOODIE Training Foundation Readiness Audit

## Purpose

Run the Feature 023 readiness audit to determine whether the current project is blocked or ready for future DRL training work.

## Required Inputs

- HOODIE paper OCR artifact
- Mechanism registry artifact
- Differential audit artifact
- Mechanism repair summary artifact
- Controlled sweeps artifact
- Baseline fairness rebuild artifact
- Baseline rebuild sensitivity audit artifact

## Expected Outputs

- `artifacts/analysis/hoodie-training-foundation-readiness-audit/hoodie-training-foundation-readiness-audit.json`
- `artifacts/analysis/hoodie-training-foundation-readiness-audit/hoodie-training-foundation-readiness-audit.md`
- Optional deterministic CSV summary if already conventional in the repository

## Validation Guidance

- Use the approved project interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`
- Run the unit and integration tests associated with the readiness audit
- Confirm the report explicitly classifies the result as blocked readiness unless every required readiness dimension is supported by the source artifacts

## Scope Reminder

- No training loop is written
- No policy redesign is introduced
- No metric formula changes are introduced
- No simulator/environment behavior changes are introduced
- No paper-validity claim is made

