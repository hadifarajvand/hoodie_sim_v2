# Feature 078 Plan

## Objective

Create the future implementation path for the campaign execution engine.

## Current Scope

This Spec Kit defines the execution contract. Implementation will be done later by Codex/local agent.

## Future Package Path

- `src/analysis/campaign_execution_engine/`

## Future Test Paths

- `tests/unit/test_campaign_execution_engine_*`
- `tests/integration/test_campaign_execution_engine_*`

## Required Later Steps

1. Read Feature 077 campaign schema.
2. Read Feature 076 combined readiness report.
3. Define deterministic seed plan.
4. Build campaign grid.
5. Execute every grid cell once per configured seed.
6. Produce raw action-bound result rows.
7. Validate row count.
8. Validate metrics.
9. Validate topology mode.
10. Validate runtime mode.
11. Validate compatibility mode is false.
12. Keep generated outputs out of git unless explicitly approved.
13. Run targeted regressions from Features 068R through 077.

## Future Validation Commands

Use only:

```bash
src/.venvmac/bin/python
```

No system `python3`.

## Regression Target

- Feature 068R baseline fidelity tests
- Feature 069 report tests
- Feature 070 topology/timeout/reward tests
- Feature 071 paper runtime tests
- Feature 072 golden trace tests
- Feature 073 controlled batch readiness tests
- Feature 074 baseline comparison tests
- Feature 075 proposed integration tests
- Feature 076 combined comparison tests
- Feature 077 campaign readiness checks
- Feature 078 execution engine tests
