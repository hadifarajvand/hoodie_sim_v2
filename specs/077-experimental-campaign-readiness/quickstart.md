# Feature 077 Quickstart

## Purpose

This feature is a readiness layer only. It defines the future experimental campaign configuration and the guardrails that must hold before any execution.

## Later Verification Flow

1. Verify the Feature 076 base is present.
2. Build the campaign readiness report later.
3. Inspect the campaign dimensions.
4. Validate the grid formula:

```text
policy_count * scenario_count * seed_count * workload_count * deadline_pressure_count
```

5. Validate the metric schema.
6. Validate that no execution output is produced.
7. Run future tests.
8. Run regressions.
9. Verify that no claims are made.

## Command Skeletons

```bash
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_experimental_campaign_readiness_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_experimental_campaign_readiness_*.py'
src/.venvmac/bin/python -c "from src.analysis.experimental_campaign_readiness.config import validate_scope; print(validate_scope())"
```

## What Success Looks Like

- Feature 076 is the dependency anchor.
- Campaign dimensions are fixed.
- Grid completeness can be checked mechanically.
- Seed reproducibility is explicit.
- No execution occurs.
- No artifacts are created.
- No superiority, statistical significance, final evaluation, or full reproduction claims are made.
