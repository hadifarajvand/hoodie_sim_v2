# Feature 071 — State Representation Repair for Deadline/Queue/Action Feasibility Awareness

## Goal
Expose deadline, queue-pressure, legal-action, and action-feasibility signals in the policy state vector without changing reward, environment stepping, or policy semantics.

## Scope
- Add a backward-compatible `state_representation_profile` switch.
- Preserve `legacy_minimal`.
- Add `deadline_queue_feasibility_v1` as a larger profiled state vector.
- Run only 50/100 cumulative training budgets.
- Keep calibration profile `paper_aligned_feasible_v1` active.

## Required outputs
- `artifacts/analysis/state-representation-deadline-queue-feasibility-repair/`
- state coverage, normalization, profile comparison, action-collapse, feasibility, policy-effect, reconciliation, diagnostic-decision, and figure artifacts

## Claim safety
- No paper reproduction claim.
- No performance superiority claim.
- No reward or policy redesign.

