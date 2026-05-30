# Research: Feature 070

## Decision 1: Combine the three blockers in one feature, but keep separate contracts

Decision: Structured topology, timeout/drop accounting, and reward equation fidelity are implemented under one Feature 070 umbrella with independent contracts and tests.

Rationale: Feature 069 recorded these blockers together as the next hard fidelity risks. They interact at terminal task outcome and reporting time.

Rejected alternative: Split into three separate features immediately. Rejected for now because the final claim boundary needs one integrated blocker-resolution report.

## Decision 2: Topology evidence must be structured or explicitly blocked

Decision: Neighbor graph fidelity requires a structured topology contract. If the repository cannot provide paper-backed adjacency, implementation must report a blocker instead of inventing edges.

Rationale: Horizontal offloading claims depend on destination legality.

Rejected alternative: Use arbitrary complete graph assumptions. Rejected because it would make HO fidelity fake.

## Decision 3: Timeout/drop accounting must be terminal-state based

Decision: Timeout/drop fidelity must be tied to task arrival, deadline or timeout, completion slot, terminal slot, and drop status.

Rationale: Drop metrics are meaningless unless terminal accounting is explicit.

Rejected alternative: Count drops only from aggregate counters. Rejected because it hides per-task state transitions.

## Decision 4: Reward fidelity must distinguish equation recovery from emission timing

Decision: Reward equation fidelity and reward emission timing are separate checks. The equation can remain blocked while timing is verified, but the report must not conflate them.

Rationale: Feature 069 showed that reward timing can be evidenced while the exact equation remains assumption-backed.

Rejected alternative: Treat terminal reward timing as full reward fidelity. Rejected as overclaiming.

## Decision 5: No campaign regeneration

Decision: Feature 070 must not regenerate campaign outputs.

Rationale: The feature is about blocker resolution and targeted evidence, not evaluation campaign production.

Rejected alternative: Run a new campaign to infer behavior. Rejected because inference from outputs is weaker than contract-level evidence.

## Decision 6: Regressions from Feature 068R and Feature 069 remain gates

Decision: Feature 070 cannot pass unless the targeted Feature 068R and Feature 069 validation slices remain green.

Rationale: Resolving blockers must not damage the mechanism readiness already merged.

Rejected alternative: Validate Feature 070 only. Rejected because it can silently break earlier fidelity layers.
