# Requirements Checklist: Feature 071

## Spec Kit Scope

- [X] Feature 071 starts from Feature 070 accepted evidence branch.
- [X] Feature 071 is not based on stale `main` alone.
- [X] Spec Kit files are created under `specs/071-runtime-paper-faithful-semantics-alignment/`.
- [X] No PR is opened by this workflow.
- [X] No merge is performed by this workflow.

## Dependency Recording

- [X] Feature 068R regression dependency is recorded.
- [X] Feature 069 regression dependency is recorded.
- [X] Feature 070 evidence dependency is recorded.
- [X] Runtime divergence from Feature 070 is explicitly recorded as the reason for Feature 071.

## Runtime Coverage

- [X] Paper-mode deadline strictness is specified.
- [X] Compatibility mode is specified separately.
- [X] Terminal-state accounting is specified.
- [X] Reward Eq. (20)-(23) implementation is specified.
- [X] Runtime report evidence is specified.

## Claim Safety

- [X] Full paper reproduction is not claimed.
- [X] Feature 072 is reserved for end-to-end golden trace validation.
- [X] Feature 071 claim boundary is limited to runtime helper semantics alignment.

## Proceed Gate

- [X] Implementation must use targeted tests before runtime helper changes.
- [X] Scope validator must protect against artifacts, training, agents, dependencies, lock files, and Feature 072+ paths.
