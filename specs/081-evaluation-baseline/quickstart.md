# Feature 081 Quickstart — HOODIE Evaluation & Baseline Benchmarking

## Pull Branch

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2
git fetch origin
git checkout 081-hoodie-evaluation-baseline-benchmarking
git pull --ff-only origin 081-hoodie-evaluation-baseline-benchmarking
git status --short
git rev-parse HEAD
```

## Validation Commands

Use only:

```bash
src/.venvmac/bin/python
```

Run:

```bash
git diff --check
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_evaluation_runner_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_evaluation_runner_*.py'
src/.venvmac/bin/python -m analysis.hoodie_evaluation_runner
```

## Expected Implementation Package

```text
src/analysis/hoodie_evaluation_runner/
  __init__.py
  __main__.py
  config.py
  model.py
  policies.py
  scenarios.py
  metrics.py
  runner.py
  aggregation.py
  ranking.py
  report.py
```

## Claim Boundary
This feature benchmarks implemented methods using deterministic scenarios. It does not claim full empirical reproduction of the HOODIE paper or statistical superiority.
