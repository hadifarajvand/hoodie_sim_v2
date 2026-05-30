# Research: Feature 068

## Decision 1: Keep Feature 068 in the policy layer

Decision: Baseline fidelity is repaired only in policy modules, policy registry, and tests.

Rationale: Changing simulator lifecycle, traffic, or reward behavior while repairing baselines would mix concerns and make later comparison evidence impossible to audit.

Alternatives considered:

- Modify environment observations broadly: rejected for this feature. Observation expansion belongs to an environment fidelity feature.
- Regenerate campaign artifacts: rejected because this feature prepares policy fidelity, not campaign reporting.

## Decision 2: Registry coverage is mandatory

Decision: RO, FLC, VO, HO, BCO, and MLEO must resolve from the shared policy registry.

Rationale: Evaluation and campaign code should not instantiate baseline classes through hidden special cases.

Alternatives considered:

- Direct class construction in tests: rejected because it hides registry drift.
- Partial registry coverage: rejected because the paper-facing baseline set must be complete.

## Decision 3: Action mask is authoritative

Decision: Every baseline must select only from the supplied action mask or report a documented no-choice path.

Rationale: The mask reflects current availability, topology, or action-space constraints. Bypassing it corrupts fairness.

Alternatives considered:

- Select preferred action and let the environment reject it: rejected because it creates noisy comparison traces.
- Silent fallback: rejected unless fallback is documented and tested.

## Decision 4: MLEO ranks total-delay candidates

Decision: MLEO should build candidate estimates and rank by total estimated delay when comparable data is present.

Rationale: MLEO is a minimum-latency baseline. Static priorities are not enough.

Alternatives considered:

- First available action: rejected except as a documented fallback.
- Static local-horizontal-vertical priority: rejected because it is not latency-based.

## Decision 5: Missing data produces visible fallback

Decision: Incomplete MLEO candidate fields must produce explicit fallback behavior.

Rationale: Current observation exposure may be incomplete. A visible fallback is honest; a hidden fallback creates fake fidelity.

Alternatives considered:

- Raise on every missing field: rejected because it can block smoke validation.
- Ignore missing fields silently: rejected because it hides drift.

## Decision 6: Feature 068 does not claim paper reproduction

Decision: Feature 068 may only claim baseline-policy fidelity readiness after tests pass.

Rationale: Full paper reproduction also depends on environment, training, workload, topology, and evaluation campaign features.

Alternatives considered:

- Use Feature 068 as a paper reproduction milestone: rejected because that would overclaim.
