# Quickstart: Feature 063 - Staged Training Budget Learning Curve and Comparison Analysis

## Run the feature

```bash
PY=/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venvmac/bin/python
$PY -m src.analysis.staged_training_budget_learning_curve.runner --json
```

## Run the focused tests

```bash
$PY -m pytest tests/unit -vv -k "staged_training_budget_learning_curve"
$PY -m pytest tests/integration -vv -k "staged_training_budget_learning_curve"
```

## Expected artifacts

- `artifacts/analysis/staged-training-budget-learning-curve/staged-training-budget-learning-curve-report.json`
- `artifacts/analysis/staged-training-budget-learning-curve/staged-training-budget-learning-curve-report.md`
- `artifacts/analysis/staged-training-budget-learning-curve/checkpoint-metrics.json`
- `artifacts/analysis/staged-training-budget-learning-curve/comparison-readiness.json`
- `artifacts/analysis/staged-training-budget-learning-curve/staged-comparative-table.json`
- `artifacts/analysis/staged-training-budget-learning-curve/staged-findings.md`
- `artifacts/analysis/staged-training-budget-learning-curve/figure-manifest.json`
- `artifacts/analysis/staged-training-budget-learning-curve/figures/figure_01_eval_reward_by_training_budget.png`
- `artifacts/analysis/staged-training-budget-learning-curve/figures/figure_02_replay_size_and_optimizer_steps_by_budget.png`
- `artifacts/analysis/staged-training-budget-learning-curve/figures/figure_03_action_distribution_by_training_budget.png`
- `artifacts/analysis/staged-training-budget-learning-curve/figures/figure_04_loss_by_training_budget.png`
- `artifacts/analysis/staged-training-budget-learning-curve/figures/figure_05_comparison_readiness_by_budget.png`
