# Validation Rules: Feature 086

## Active Policy Rule

Active paper-fidelity policies must be exactly:

```text
HOODIE
RO
FLC
VO
HO
BCO
MLEO
```

The active runtime, generated artifacts, report rows, and rankings must not include:

```text
MQO
Minimum Queue Offloader
ORIGINAL_HOODIE_BASELINE
HOODIE_PROPOSED
```

Historical mentions are allowed only inside Spec Kit historical-defect documentation.

## System-Model Mechanism Rule

Every required HOODIE system-model mechanism must be listed in the matrix and generated artifacts.

Allowed statuses:

```text
exact
approximate_documented
missing
wrong
not_exercised
```

Feature 086 fails if any required mechanism is `missing`, `wrong`, or `not_exercised`.

`approximate_documented` is acceptable only if:

1. the approximation is explicit;
2. the claim boundary is conservative;
3. at least one scenario/test/artifact exercises the represented behavior.

## MLEO Numeric Evidence Rule

MLEO must select the legal candidate with minimum estimated `total_delay`.

The test suite must include a controlled case where:

- local, horizontal, and vertical candidates exist;
- the minimum queue-length candidate is not the minimum total-delay candidate;
- MLEO selects the minimum total-delay candidate;
- candidate delays are asserted directly.

A queue-length-only implementation must fail this test.

## Scenario Coverage Rule

At least one test/scenario/artifact must exercise:

- local execution;
- horizontal offloading;
- vertical/cloud offloading;
- illegal horizontal destination rejection;
- timeout/drop;
- private/local queue behavior;
- offloading/public/cloud queue behavior where represented;
- MLEO minimum-latency selection.

## Metric Readiness Rule

Every output metric must be classified as one of:

```text
paper_primary_metric
paper_secondary_or_derived_metric
paper_secondary_or_repository_metric
repository_diagnostic_metric
not_for_paper_comparison
```

Repository diagnostics must not be used as paper-comparison headline metrics.

At minimum classify:

- `task_completion_delay`
- `task_drop_ratio`
- `completion_rate`
- `timeout_drop_rate`
- `unavailable_drop_rate`
- `deadline_violation_rate`
- `average_reward`
- `total_reward`
- `throughput`
- `queue_stability_score`
- `illegal_action_rejection_count`

## Final Readiness Rule

The final Feature 086 report must declare exactly one of:

```text
system_model_fidelity_ready_for_output_comparison
system_model_fidelity_blocked
```

A ready verdict is allowed only when no blocking mechanism remains and all approximations are documented.
