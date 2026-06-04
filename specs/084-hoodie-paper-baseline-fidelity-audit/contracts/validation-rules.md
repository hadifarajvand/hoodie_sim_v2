# Validation Rules: Feature 084

## Active Policy Rules

The active paper-fidelity policy set must be exactly:

```text
HOODIE
RO
FLC
VO
HO
BCO
MLEO
```

The following identifiers must fail validation if they appear in active policy registries, generated active artifact rows, aggregate tables, rankings, or final paper-fidelity reports:

```text
MQO
Minimum Queue Offloader
ORIGINAL_HOODIE_BASELINE
HOODIE_PROPOSED
```

`MQO` may appear only in Feature 084 documentation as a historical defect note.

## MLEO Rules

- `MLEO` means Minimum Latency Estimation Offloader.
- MLEO must choose the valid action/destination with minimum estimated end-to-end completion latency.
- MLEO must not be implemented as a pure minimum-queue-length policy.
- If latency estimation cannot include all paper components because runtime state lacks a component, the approximation must be documented in `formula-mapping-matrix.md`.

## HOODIE Method Identity Rules

- `HOODIE` is the only active proposed paper method.
- `ORIGINAL_HOODIE_BASELINE` is conceptually invalid and must not be active.
- `HOODIE_PROPOSED` is not the canonical active ID and must not appear in final active artifacts.

## Formula Mapping Rules

Every formula mapping row must include:

- Paper item
- Meaning
- Expected simulation logic
- Current code location or `missing`
- Status
- Required fix
- Evidence

Allowed statuses:

```text
exact
approximate
missing
wrong
out_of_scope
```

Rows with status `approximate`, `missing`, or `wrong` must have non-empty `required_fix`.

## Report Claim Rules

- Do not claim full empirical paper reproduction unless trained DRL, LSTM behavior, topology, traffic, and paper figure reproduction are validated.
- Deterministic benchmark approximations must be labeled as deterministic benchmark approximations.
- Repository-specific metrics must be labeled as repository-specific and not as paper metrics unless directly supported by the paper.
