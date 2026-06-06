# Clarifications: Paper Result Reporting & Reproducibility Artifacts

## Session 2026-05-06

- Q: Does this generate paper plots? → A: No. No plotting in this feature.
- Q: Does this recompute metrics? → A: No. It packages existing matrix outputs and validates artifact completeness.
- Q: Does this modify EvaluationMatrixRunner metrics? → A: No. It may call the runner in tests, but it must not change metric formulas.
- Q: Does this introduce pandas, matplotlib, seaborn, or reportlab? → A: No. Stdlib only.
- Q: Does this run training? → A: No.
- Q: What is the minimum complete bundle? → A: manifest.json, run-config.json, artifact-index.json, validation-summary.json, README.md.
- Q: Should timestamps make tests nondeterministic? → A: No. The builder must accept a deterministic timestamp override.
- Q: Should missing artifacts fail hard? → A: The builder must record missing artifacts in validation-summary.json and set pass=false. Tests may assert this behavior.
