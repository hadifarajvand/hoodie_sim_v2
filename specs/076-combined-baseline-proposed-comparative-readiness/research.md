# Feature 076 Research

## Decision 1: Combine Feature 074 and Feature 075 outputs, do not recompute their internals

Decision: Feature 076 must consume Feature 074 baseline comparison rows and Feature 075 proposed-method rows as upstream source reports.

Rationale: Feature 074 already binds baseline selected actions to controlled metrics. Feature 075 already binds the proposed method to the same action-bound contract. Recomputing their internal decision logic in Feature 076 would duplicate logic and create drift.

Rejected alternative: Rebuild baseline and proposed decisions directly inside Feature 076.

Reason rejected: It would bypass the validated upstream contracts and make the combined layer harder to audit.

## Decision 2: Normalize into one common row schema

Decision: Feature 076 must convert upstream rows into `CombinedPolicyRow` records with a shared contract for policy id, scenario id, selected action, action legality, terminal status, reward, compatibility mode, decision trace, and metrics.

Rationale: Baseline and proposed outputs are not identical objects, but they must become comparable at the readiness layer.

Rejected alternative: Render two separate tables in one markdown report.

Reason rejected: A visual table merge is not enough. The code must validate one structured matrix.

## Decision 3: Exact 7 by 7 matrix

Decision: The combined matrix must contain 7 policies/methods and 7 scenarios, for exactly 49 rows.

Required policy/method IDs:

- FLC
- VO
- HO
- RO
- BCO
- MLEO
- PROPOSED_DCQ

Required scenario IDs:

- light_load_no_deadline_pressure
- tight_deadline_pressure
- legal_horizontal_offload
- illegal_horizontal_destination_attempt
- cloud_vertical_fallback
- timeout_drop_case
- mixed_local_horizontal_cloud_candidates

Rationale: Feature 076 is a coverage-readiness gate. Missing or duplicated rows destroy the comparison contract.

## Decision 4: Readiness only, no ranking

Decision: Feature 076 computes aggregate metrics but does not rank methods, choose winners, or claim superiority.

Rationale: The controlled scenarios are deterministic and narrow. They verify integration readiness, not statistical performance.

Rejected alternative: Sort policies by mean reward or mean delay.

Reason rejected: That would create an unsupported performance claim.

## Decision 5: Compatibility mode is forbidden by default

Decision: Any combined row with `compatibility_mode_used=True` blocks readiness.

Rationale: Features 071 through 075 established paper-mode semantics as the default. Compatibility mode is only for legacy regression protection, not for comparative readiness.

## Decision 6: Action-bound evidence remains mandatory

Decision: Every combined row must preserve `action_bound_metrics_derived=True` from its source feature.

Rationale: Feature 074 was repaired specifically because copied metrics without selected-action binding were scientifically weak. Feature 076 must not regress that.

## Decision 7: Scope remains analysis-only

Decision: Feature 076 only adds a read-only analysis package, tests, and Spec Kit files.

Forbidden:

- policy rewrites
- runtime helper rewrites
- training code
- generated artifacts
- dependency changes
- Feature 077+ files

Rationale: Feature 076 is an aggregation/readiness layer, not a modeling or training feature.

## Decision 8: Upstream regression evidence is required

Decision: Feature 076 must include targeted regression evidence for Features 068R through 075.

Rationale: The combined report depends on every upstream layer. A green Feature 076 report is meaningless if an upstream contract regressed.

## Open Questions

None. Feature 076 has enough upstream artifacts to implement without asking the user for more information.

## Risk Notes

- If Feature 074 or Feature 075 changes their row shape later, Feature 076 must be revalidated.
- If scenario IDs change upstream, Feature 076 must fail loudly rather than silently adapting.
- If the proposed method changes from deterministic readiness policy to trained DRL later, that belongs in a later feature and must not be smuggled into Feature 076.
