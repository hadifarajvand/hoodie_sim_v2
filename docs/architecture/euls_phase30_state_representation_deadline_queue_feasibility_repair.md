# EULS Phase 30: State Representation Repair for Deadline / Queue Feasibility

This feature adds a profile-aware state vector for the training and evaluation stack.

Key points:
- `legacy_minimal` remains available for backward compatibility.
- `deadline_queue_feasibility_v1` exposes deadline slack, queue pressure, legal-action availability, and path-feasibility estimates.
- The calibration profile from Feature 069 remains active.
- Reward, terminal accounting, and policy semantics are unchanged.

This document is a repair note, not a performance claim.

