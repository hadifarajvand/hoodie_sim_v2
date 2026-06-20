# Feature 070 - Calibration Metric Consistency and Reconciliation Fix

## Objective

Repair the 069 calibration metric universe so that feasibility counts, terminal counts, and reward counts are computed over explicit, compatible universes.

## Scope

- Load the 069 calibration payload as evidence.
- Reconcile reward and terminal counts on the unique-task universe.
- Make the feasibility universe explicit.
- Recompute action diversity truthfully.
- Keep the lightweight 50 / 100 comparison.

## Non-goals

- No environment changes.
- No policy changes.
- No reward redesign.
- No state representation redesign.
- No large training.
