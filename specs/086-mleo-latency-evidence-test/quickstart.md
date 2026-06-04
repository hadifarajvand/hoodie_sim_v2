# Quickstart: Feature 086 Full System-Model Fidelity Gate

## Current State

Feature 086 is implemented and the current report verdict is `system_model_fidelity_ready_for_output_comparison`.

The gate preserves the MLEO numeric evidence and the HOODIE/MLEO tie evidence from Feature 085 while adding a system-model coverage matrix, a metric-readiness matrix, a scenario-coverage artifact, and a Feature 086 report bundle.

## Run

```bash
cd /Users/hadi/Documents/GitHub/hoodie_sim_v2
git fetch origin
git checkout 086-mleo-latency-evidence-test
git pull --ff-only origin 086-mleo-latency-evidence-test

src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts --artifact-dir artifacts/feature_085_full_audit
src/.venvmac/bin/python -m analysis.hoodie_system_model_fidelity_gate --write-artifacts artifacts/feature_086_system_model_fidelity
src/.venvmac/bin/python -m analysis.hoodie_system_model_fidelity_gate --validate-artifacts --artifact-dir artifacts/feature_086_system_model_fidelity
```

## Validation Commands

```bash
git diff --check
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_runtime_evaluation_*.py'
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_*mleo*.py'
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_system_model_fidelity_gate*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_runtime_evaluation_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_system_model_fidelity_gate*.py'
src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts --artifact-dir artifacts/feature_085_full_audit
src/.venvmac/bin/python -m analysis.hoodie_system_model_fidelity_gate --write-artifacts artifacts/feature_086_system_model_fidelity
src/.venvmac/bin/python -m analysis.hoodie_system_model_fidelity_gate --validate-artifacts --artifact-dir artifacts/feature_086_system_model_fidelity
```

## Artifact Bundle

- `artifacts/feature_086_system_model_fidelity/mechanism_coverage.json`
- `artifacts/feature_086_system_model_fidelity/mechanism_coverage.csv`
- `artifacts/feature_086_system_model_fidelity/system_model_gap_matrix.json`
- `artifacts/feature_086_system_model_fidelity/system_model_gap_matrix.md`
- `artifacts/feature_086_system_model_fidelity/metric_readiness_matrix.json`
- `artifacts/feature_086_system_model_fidelity/metric_readiness_matrix.md`
- `artifacts/feature_086_system_model_fidelity/scenario_mechanism_coverage.json`
- `artifacts/feature_086_system_model_fidelity/hoodie_mleo_tie_evidence.json`
- `artifacts/feature_086_system_model_fidelity/feature_086_system_model_fidelity_report.json`
- `artifacts/feature_086_system_model_fidelity/feature_086_system_model_fidelity_report.md`

## Claim Boundary

- HOODIE remains the Feature 080 proposed method boundary.
- No thesis method, DCQ method, or custom queue redesign is introduced.
- The audit documents interface-only DRL/LSTM/forecast boundaries where full training is not reproduced.
- No full empirical HOODIE reproduction claim is made.
