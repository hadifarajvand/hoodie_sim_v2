# Validation Rules: Feature 086

## MLEO Numeric Evidence Rule

A valid `MLEO` implementation must select the candidate with the minimum estimated `total_delay` among legal candidates.

The test suite must include a controlled scenario where:

- at least three candidates exist;
- candidate queue lengths differ;
- the minimum queue-length candidate is not the minimum total-delay candidate;
- `MLEO` selects the minimum total-delay candidate;
- candidate delay values are asserted directly.

A queue-length-only implementation must fail this test.

## Candidate Evidence Rule

The selected candidate and all considered candidate delay values must be available through at least one of:

- `MinimumLatencyEstimateOffloadingPolicy.last_candidates`
- runtime adapter trace details
- generated evidence artifact

## HOODIE/MLEO Tie Evidence Rule

If `HOODIE` and `MLEO` have equal aggregate metrics in the deterministic benchmark, the report or evidence artifact must state why.

Allowed explanations:

- identical selected actions across all benchmark rows;
- different actions but equivalent modeled delay/drop/reward outcomes;
- deterministic benchmark structure collapses both policies to the same choices;
- insufficient trace granularity, in which case readiness must not claim the tie is explained.

## Claim Boundary

Feature 086 proves a numeric baseline-policy evidence gate only. It does not prove full empirical reproduction of the HOODIE paper.
