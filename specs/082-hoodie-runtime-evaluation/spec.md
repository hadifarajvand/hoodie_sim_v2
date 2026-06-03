# Feature 082 — HOODIE Runtime Evaluation Repair Spec

## Reference
All implementation must follow the GitHub Spec Kit workflow: https://github.com/github/spec-kit

## Goal
Repair Feature 082 policy adapters:
- HOODIE_PROPOSED must not collapse to LOCAL_ONLY
- ORIGINAL_HOODIE_BASELINE must not collapse to CLOUD_ONLY
- Ensure decision traces and artifacts reflect real runtime differences

## Non-Goals
- No DCQ logic
- No thesis method
- No queue redesign
- No statistical superiority claim
- No empirical full-paper reproduction

## Required Artifacts
- raw_rows.json/csv
- aggregate_by_policy.json/csv
- ranking_by_metric.json/csv
- feature_082_runtime_evaluation_report.json/md
- execution_manifest.json

## Validation
- HOODIE_PROPOSED != LOCAL_ONLY
- ORIGINAL_HOODIE_BASELINE != CLOUD_ONLY
- Unit and integration tests must cover identity differences
- Artifact regeneration verified
- Scope proof explicit