# Quickstart: Feature 064 - Final Review and Release Gate Batch

## Run the feature

```bash
PY=/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venvmac/bin/python
$PY -m src.analysis.final_review_release_gate_batch.runner --json
```

## Run the focused tests

```bash
$PY -m pytest tests/unit -vv -k "final_review_release_gate_batch"
$PY -m pytest tests/integration -vv -k "final_review_release_gate_batch"
```

## Expected artifacts

- `artifacts/analysis/final-review-release-gate-batch/final-review-release-gate-report.json`
- `artifacts/analysis/final-review-release-gate-batch/final-review-release-gate-report.md`
- `artifacts/analysis/final-review-release-gate-batch/diagnostic-findings.json`
- `artifacts/analysis/final-review-release-gate-batch/reward-stability-review.json`
- `artifacts/analysis/final-review-release-gate-batch/action-collapse-review.json`
- `artifacts/analysis/final-review-release-gate-batch/replay-buffer-review.json`
- `artifacts/analysis/final-review-release-gate-batch/evaluation-signal-review.json`
- `artifacts/analysis/final-review-release-gate-batch/next-action-decision.json`
- `artifacts/analysis/final-review-release-gate-batch/final-review-summary.md`
- `artifacts/analysis/final-review-release-gate-batch/figures/figure_01_reward_stability_gate.png`
- `artifacts/analysis/final-review-release-gate-batch/figures/figure_02_vertical_action_collapse_gate.png`
- `artifacts/analysis/final-review-release-gate-batch/figures/figure_03_replay_cap_gate.png`
