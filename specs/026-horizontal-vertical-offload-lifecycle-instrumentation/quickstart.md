# Quickstart: Horizontal and Vertical Offload Lifecycle Instrumentation

## Goal

Add trace observability for horizontal and vertical offload lifecycle paths without changing simulator behavior unless a bug is proven by tests.

## Validation Checklist

1. Confirm the current differential audit still reports horizontal and vertical offload cases as unsupported due to missing trace visibility.
2. Run unit tests that verify the trace event schema and deterministic ordering.
3. Run integration tests that verify horizontal and vertical offload lifecycle trace visibility.
4. Run regression tests that confirm Feature 019 timeout/drop and Feature 024 local-compute/deterministic-ordering behavior remain unchanged.
5. Run the no-behavior-change test to confirm rewards, metrics, policy decisions, and arrivals are unchanged for equivalent execution.
6. Regenerate the differential environment audit and verify the offload cases are no longer blocked solely by missing selected_action-only visibility.
7. Confirm the instrumentation summary states any remaining blockers honestly as topology or legality issues rather than observability issues.

## Expected Outputs

- `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json`
- `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.md`
- `artifacts/analysis/differential-environment-audit/differential-audit.json`
- `artifacts/analysis/differential-environment-audit/differential-audit.md`

## Notes

- Do not claim legal horizontal destinations are paper-backed.
- Do not introduce topology fabrication or paper-validity claims.
- If a simulator bug is proven by tests, keep the fix narrowly scoped to trace correctness.

