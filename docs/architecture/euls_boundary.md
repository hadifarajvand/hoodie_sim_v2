# EULS Boundary

EULS means Execution and Queue Lifecycle Simulator. In Phase 1, EULS is an
explicit boundary around the existing `environment.Environment` runtime.

This phase exists to make the simulator architecture honest and testable before
any semantic refactor. The wrapper exposes the current execution kernel through
a named API, but it does not alter runtime behavior.

Current runtime behavior that remains unchanged:

- queue timing and admission behavior
- deadline and drop handling
- offloading and transmission lifecycle behavior
- action representation and policy behavior
- training, baselines, and figure generation

EULS owns the long-term execution boundary for:

- task arrival
- queue admission
- queue mutation
- queue service
- transmission lifecycle
- public queue handoff
- deadline/drop handling
- completion lifecycle
- reward availability events
- replay/determinism evidence

EULS does not own:

- policy optimization
- DRL training
- baseline comparison logic
- figure plotting
- paper result claims
- DAL mutation

Future phases will move queue, timing, and deadline ownership into EULS.
They will also introduce DAL as an advisory layer only after the EULS boundary
is stable. Figures 8-11 are not claimed ready in this phase because this work
is architecture-boundary work only, not fidelity completion.
