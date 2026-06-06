# Research: User-Approved Assumption Patch Registry

## Decision 1: Governance reconciliation is PATCH-only

- Decision: Keep the governance/docs reconciliation scoped to the approved interpreter/runtime guidance correction and matching wording cleanup.
- Rationale: The spec explicitly prefers PATCH unless broad new principles are intentionally retained, and runtime adoption remains out of scope.
- Alternatives considered: MINOR governance expansion with new principles; rejected because it is not intentionally approved in the Feature 031 scope.

## Decision 2: Constitution versioning stays at 1.3.1

- Decision: Update the constitution footer/sync report alignment to `1.3.1`.
- Rationale: The repository already records the interpreter baseline rebase as `1.3.1`, so the plan must align documentation rather than invent a new version.
- Alternatives considered: Reverting to `1.3.0`; rejected because it would reintroduce the mismatch the feature is intended to fix.

## Decision 3: Approved interpreter path is the `.venvmac` binary

- Decision: Use `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python` as the approved interpreter path in governance docs.
- Rationale: This path is already the constitution-approved interpreter boundary and is the source of the guidance correction.
- Alternatives considered: Reverting to `.venv/bin/python`; rejected because that path is no longer the approved runtime anchor.

## Decision 4: Feature 031 registry/report stays unchanged

- Decision: Preserve the finalized Feature 031 registry/report behavior and treat governance/docs edits as separate intentional documentation changes.
- Rationale: The registry feature is already complete and should not be re-opened for behavior changes.
- Alternatives considered: Folding runtime adoption into Feature 031; rejected because runtime adoption is explicitly out of scope.

