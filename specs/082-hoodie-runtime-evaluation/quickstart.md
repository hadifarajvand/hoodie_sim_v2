# Quickstart

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2
git checkout 082-hoodie-runtime-evaluation
src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --write-artifacts artifacts/feature_082_full_runtime_eval
src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts --artifact-dir artifacts/feature_082_full_runtime_eval
```

Validation:

```bash
git diff --check
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_runtime_evaluation_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_runtime_evaluation_*.py'
src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts --artifact-dir artifacts/feature_082_full_runtime_eval
```

