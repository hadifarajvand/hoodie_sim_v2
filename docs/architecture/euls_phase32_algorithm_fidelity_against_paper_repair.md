# Algorithm Fidelity Against Paper Repair

This feature audits the HOODIE DRL implementation against the paper's
Algorithm 1 and network/training details recovered from OCR.

The repair run applies two paper-aligned adjustments for validation:

1. Episode-based epsilon-greedy exploration schedule.
2. Episode-based target-network copy cadence for the bounded repair smoke.

The feature does not alter environment dynamics, reward semantics, topology, or
the policy class itself. It exists to determine whether the current training
pipeline is paper-faithful enough to learn the mixed/load-spreading behavior
observed in the oracle validation.
