# Quickstart: Feature 065 - Evaluation Instrumentation and Reward/State Diagnostic Repair

## Run the feature

```bash
PY=/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venvmac/bin/python
$PY -m src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner --json
```

## Run the focused tests

```bash
$PY -m pytest tests/unit -vv -k "evaluation_instrumentation_reward_state_diagnostic"
$PY -m pytest tests/integration -vv -k "evaluation_instrumentation_reward_state_diagnostic"
```

## Expected artifacts

- `artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/evaluation-instrumentation-diagnostic-report.json`
- `artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/evaluation-instrumentation-diagnostic-report.md`
- `artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/instrumented-checkpoint-metrics.json`
- `artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/evaluation-action-distribution.json`
- `artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/per-action-outcome-summary.json`
- `artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/reward-decomposition.json`
- `artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/replay-window-vs-cumulative-training-actions.json`
- `artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/state-feature-coverage-audit.json`
- `artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/policy-effect-diagnostic.json`
- `artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/diagnostic-decision.json`
- `artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/final-diagnostic-summary.md`
