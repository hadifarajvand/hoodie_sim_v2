# Feature 086: HOODIE System-Model Mechanism Fidelity Gate

## Purpose

Feature 086 is the blocking gate before moving from HOODIE system-model implementation to output comparison against the paper.

Feature 085 repaired the active baseline set to `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, and `MLEO`. Feature 086 must now prove that the simulator implements the HOODIE paper system model, not only the baseline labels.

## Required Verdict

The final report must declare one of:

- `system_model_fidelity_ready_for_output_comparison`
- `system_model_fidelity_blocked`

If blocked, the report must list exact blocking gaps. If ready, it must list remaining approximations honestly.

## Required Mechanisms

Feature 086 must audit, repair where needed, test, and produce evidence for:

1. three-tier topology: IoT/task source, Edge Agents, Cloud;
2. Edge Agent set and Cloud node representation;
3. horizontal EA-to-EA connectivity and legality constraints;
4. vertical EA-to-Cloud path;
5. task ID, task size/data, CPU demand or processing density, timeout/deadline;
6. workload/task arrival representation;
7. private/local queue behavior;
8. offloading queue behavior;
9. public/cloud queue behavior;
10. local execution delay;
11. horizontal transmission delay;
12. vertical transmission delay;
13. remote/cloud execution delay;
14. waiting time and completion time;
15. timeout/drop/unavailability behavior;
16. hybrid action model: local, horizontal, vertical;
17. two-stage decision boundary where represented or a documented single-stage approximation;
18. HOODIE proposed-method claim boundary;
19. official paper baselines only: RO, FLC, VO, HO, BCO, MLEO;
20. MLEO as minimum estimated total latency, not queue-length-only;
21. reward/cost formula boundary;
22. output metrics readiness for paper comparison.

## Status Labels

Every mechanism must be classified as:

- `exact`
- `approximate_documented`
- `missing`
- `wrong`
- `not_exercised`

`missing`, `wrong`, and `not_exercised` are blocking unless explicitly out of paper scope.

## Out of Scope

- No thesis method.
- No DCQ.
- No custom queue redesign.
- No new proposed method.
- No full empirical paper reproduction claim unless separately validated.

## Acceptance Criteria

- Mechanism coverage artifact exists.
- System-model gap matrix artifact exists.
- Metric readiness artifact exists.
- Scenario mechanism coverage artifact exists.
- MLEO numeric non-queue-only test exists.
- Tests fail if active policies are not exactly `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`.
- Tests fail if legacy labels appear in active outputs: `MQO`, `Minimum Queue Offloader`, `ORIGINAL_HOODIE_BASELINE`, `HOODIE_PROPOSED`.
- Final report states whether we may proceed to output comparison.
