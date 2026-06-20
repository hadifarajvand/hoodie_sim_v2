# EULS Phase 29 - Calibration Metric Consistency Reconciliation Fix

This phase defines the 070 analysis repair that makes the calibration metrics internally consistent.

## Key points

- Reward events and terminal events are reconciled on the unique-task universe.
- Feasibility counts are explicitly labeled by universe.
- Action feasibility diversity is computed from the repaired task set, not inferred from the compacted summary.
- The feature remains analysis-only and does not change environment, reward, policy, or state semantics.
