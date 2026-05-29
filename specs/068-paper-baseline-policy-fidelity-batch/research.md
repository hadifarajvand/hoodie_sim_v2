# Research: Feature 068

## Decision: Keep baseline fidelity isolated to policy layer

Rationale: Baselines must be comparable through the shared policy interface. Changing simulator lifecycle behavior here would mix baseline repair with environment repair and make comparison claims impossible to audit.

Alternatives considered:

- Modify environment observations broadly: rejected for this feature unless only policy-facing metadata is already available or narrowly exposed without semantic changes.
- Rebuild evaluation matrix: rejected for this feature; matrix execution belongs to later reproduction batches.

## Decision: MLEO ranks legal delay candidates

Rationale: Minimum-latency edge offloading cannot be a placeholder hint. The policy must build candidate estimates for legal local, horizontal, and vertical actions and choose the minimum total delay.

Alternatives considered:

- First legal action fallback: rejected except as documented missing-input fallback.
- Static action preference: rejected because it is not a latency estimate.

## Decision: Fallbacks must be explicit

Rationale: Missing observation fields are expected while environment state exposure is still evolving. Silent fallback would hide paper-to-code drift.

Alternatives considered:

- Raise on all missing fields: rejected because it would break partial evaluation smoke runs.
- Silent fallback: rejected because it creates fake fidelity.
