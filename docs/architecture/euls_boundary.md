# EULS Boundary

EULS means Execution and Queue Lifecycle Simulator. In Phase 1, EULS is an
explicit wrapper boundary around the existing `HoodieGymEnvironment`.

Why this phase exists:
- to make the runtime boundary explicit before any semantic refactor
- to document ownership without changing simulator behavior
- to create a stable target for later queue/timing/deadline work

What remains unchanged:
- queue semantics
- timing semantics
- deadline/drop logic
- policies
- training
- figure generation

What EULS owns now and will own later:
- task arrival
- queue admission
- queue mutation
- queue service
- transmission lifecycle
- public queue handoff
- deadline/drop handling
- completion lifecycle
- reward availability event
- replay/determinism evidence

What EULS does not own:
- policy optimization
- DRL training
- baseline comparison logic
- figure plotting
- paper result claims
- DAL mutation

DAL must remain advisory in later phases because Phase 1 only establishes a
boundary. It does not move decision logic or queue ownership.

Figures 8-11 are not claimed ready by this phase because this is architecture
boundary work only, not HOODIE fidelity completion.
