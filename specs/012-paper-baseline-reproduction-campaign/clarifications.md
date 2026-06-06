# Clarifications: Paper Baseline Reproduction Campaign

## Session 2026-05-06

- Q: Does this train HOODIE or any DRL policy? → A: No. This feature only runs already implemented policies.
- Q: Does this change policy decision behavior? → A: No. Existing policy implementations must remain untouched.
- Q: Does this change metric formulas? → A: No. It aggregates existing matrix metrics only.
- Q: Does this generate paper plots? → A: No. No plotting. No figure generation.
- Q: Does this use pandas, numpy, matplotlib, seaborn, scipy, or external trackers? → A: No. Stdlib only.
- Q: Does the campaign runner directly step HoodieGymEnvironment? → A: No. It must call EvaluationMatrixRunner. It must not duplicate the matrix runner’s environment loop.
- Q: What makes this different from feature 009? → A: Feature 009 runs a matrix. Feature 012 wraps matrix execution into a campaign-level reproduction workflow with campaign manifests, grouped summaries, reproducibility bundle generation/reference, and deterministic campaign validation.
- Q: What is the minimum useful campaign? → A: A campaign config, campaign runner, grouped summaries, manifest, determinism check artifact, README, reproducibility bundle integration, and tests.
- Q: Should missing or failed runs be silently ignored? → A: No. Campaign artifacts must record expected run count, discovered run count, and validation/determinism status.
- Q: Are scenario/policy aliases allowed? → A: No. Use exact registry names only.
