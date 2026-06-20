# EULS Phase 24 - Evaluation Instrumentation and Reward/State Diagnostic Repair

Feature 065 is a read-only diagnostic pass. It does not change reward semantics, environment semantics, policy behavior, DAL behavior, or replay semantics.

Scope:
- rerun the staged 100/150/200/500 diagnostic campaign with evaluation instrumentation
- separate evaluation actions from replay-window action counts
- decompose reward by action and terminal outcome
- audit policy-visible state coverage
- compare candidate and fixed policies on the same evaluation trace bank

Out of scope:
- 5000-episode training
- reward redesign
- environment redesign
- policy redesign
- replay-buffer redesign

Release gate:
- The feature is complete only if it emits the required artifacts and stays inside the approved paths.
- If cumulative staging or instrumented evaluation cannot be executed without semantic changes, the feature must report a blocked verdict instead of inventing data.
