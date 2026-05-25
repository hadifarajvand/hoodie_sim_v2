# Quickstart: Feature 055

## Validation

Run the Feature 055 tests and smoke analysis from the approved interpreter:

```bash
PATH="$(pwd)/src/.venvmac/bin:$PATH" python3 -m unittest \
  tests.unit.test_paper_default_training_smoke_run_schema \
  tests.unit.test_paper_default_training_smoke_run_metrics \
  tests.unit.test_paper_default_training_smoke_run_behavior_equivalence \
  tests.integration.test_paper_default_training_smoke_run \
  tests.integration.test_paper_default_training_smoke_run_report \
  tests.integration.test_paper_default_training_smoke_run_scope_guard

PATH="$(pwd)/src/.venvmac/bin:$PATH" python3 -m src.analysis.paper_default_training_smoke_run
```

## Output Artifacts

- `artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.json`
- `artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.md`

## Expected Pass Path

- Feature 054 readiness is verified from the committed report artifact.
- Live environment training is used.
- Replay is populated.
- At least one optimizer step executes.
- Loss is finite.
- Legal actions are preserved.
- Delayed reward handling is preserved.
- Checkpoint metadata is valid.
- The report routes to Feature 056 only on the pass path.
