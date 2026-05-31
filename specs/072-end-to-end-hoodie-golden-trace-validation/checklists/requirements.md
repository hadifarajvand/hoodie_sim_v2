# Requirements Checklist: Feature 072

## Scope

- [X] Feature 072 starts from Feature 071 runtime-semantics branch.
- [X] Spec Kit files are under `specs/072-end-to-end-hoodie-golden-trace-validation/`.
- [X] No PR is opened by this workflow.
- [X] No merge is performed by this workflow.

## Dependencies

- [X] Feature 068R regression dependency is recorded.
- [X] Feature 069 regression dependency is recorded.
- [X] Feature 070 topology dependency is recorded.
- [X] Feature 071 runtime-semantics dependency is recorded.

## Trace Coverage

- [X] Local success trace is specified.
- [X] Local timeout trace is specified.
- [X] Horizontal legal-neighbor trace is specified.
- [X] Horizontal non-neighbor trace is specified.
- [X] Horizontal self-destination rejection is specified.
- [X] Cloud vertical success trace is specified.
- [X] Success, drop, inactive, and pending reward traces are specified.
- [X] Compatibility boundary trace is specified.

## Claim Safety

- [X] Full paper reproduction is not claimed.
- [X] Training correctness is not claimed.
- [X] Campaign evaluation readiness is not claimed.
- [X] Feature 073+ scope is excluded.

## Proceed Gate

- [X] Implementation must use Feature 071 helpers rather than duplicate formulas.
- [X] Implementation must use Feature 070 Figure 7 topology.
- [X] Scope validator must protect against artifacts, training, agents, dependencies, and Feature 073+ paths.
