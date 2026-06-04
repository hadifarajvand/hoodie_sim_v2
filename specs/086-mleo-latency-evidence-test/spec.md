# Feature 086: MLEO Latency Evidence Test

## Purpose

Feature 086 adds a narrow validation layer on top of Feature 085. Feature 085 repaired the active paper baseline identity from the invalid `MQO` label to the paper-correct `MLEO` baseline. However, the Feature 085 aggregate results show `HOODIE` and `MLEO` tied exactly across all reported benchmark metrics. That tie may be valid for the deterministic benchmark, but it must be backed by numeric evidence rather than accepted from aggregate equality alone.

This feature must add tests and artifact/report evidence proving that `MLEO` is implemented as a minimum estimated latency policy and not merely a renamed minimum-queue policy.

## Scope

In scope:

- Add numeric unit/integration tests for `MinimumLatencyEstimateOffloadingPolicy`.
- Verify `MLEO` selects the candidate with the smallest estimated total delay.
- Verify queue length alone cannot dominate candidate selection when total latency says otherwise.
- Add a deterministic tie-evidence test or report field explaining why `HOODIE` and `MLEO` tie in Feature 085 artifacts.
- Update Feature 086 Spec Kit files with completion evidence after implementation.

Out of scope:

- No thesis method.
- No DCQ.
- No custom deadline-aware queue redesign.
- No change to HOODIE algorithm semantics unless a verified bug is found.
- No full empirical paper reproduction claim.

## Required Evidence

The implementation must prove all of the following:

1. `MLEO` builds or receives candidate latency estimates.
2. Each candidate has an auditable `total_delay` value.
3. `MLEO` chooses the legal candidate with the minimum `total_delay`.
4. A candidate with the smallest queue length must lose if its total estimated latency is larger.
5. If `HOODIE` and `MLEO` remain tied in aggregate artifacts, the report must state whether the tie is due to deterministic scenario structure, identical selected actions, or another measured reason.

## Acceptance Criteria

- Tests fail if `MLEO` is implemented as queue-length-only behavior.
- Tests expose candidate latency numbers, either through assertions against `last_candidates` or equivalent policy trace detail.
- Tests verify selected action equals the candidate with minimum `total_delay`.
- Tie with `HOODIE` is documented as evidence-based, not inferred from final aggregate equality.
- `python -m unittest discover tests/unit -p 'test_hoodie_runtime_evaluation_*.py'` passes.
- Runtime artifact validation still passes after the evidence/report update.
