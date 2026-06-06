# Data Model: Paper Baseline Reproduction Campaign

## Entities

### CampaignConfig
- `campaign_name`: campaign identifier
- `policy_names`: ordered list of approved policy names
- `scenario_names`: ordered list of approved scenario names
- `seeds`: ordered list of fixed seeds
- `output_dir`: root directory for campaign, matrix, and bundle outputs
- `episode_length`: optional override for campaign runs
- `created_at_override`: deterministic timestamp override
- `dependency_change_note`: human-readable dependency stability note

### CampaignRunResult
- `campaign_name`: campaign identifier used for the run
- `matrix_result_count`: number of matrix run results produced
- `bundle_output_dir`: path to the reproducibility bundle output
- `campaign_output_dir`: path to the campaign artifact directory
- `campaign_artifacts`: list or map of generated campaign artifact paths

### Campaign Artifacts
- `campaign-manifest.json`: campaign provenance and inventory
- `campaign-summary.json`: aggregated campaign metrics
- `policy-summary.json`: grouped summary by policy
- `scenario-summary.json`: grouped summary by scenario
- `determinism-check.json`: repeated-run comparison results
- `README.md`: human-readable description of the campaign outputs

## Relationships

- `CampaignConfig` drives `EvaluationMatrixConfig`.
- `CampaignRunner` invokes `EvaluationMatrixRunner` and passes along the campaign configuration.
- `CampaignRunner` references the reproducibility bundle output produced after the matrix run.
- `CampaignRunResult` records the campaign output paths and counts derived from the matrix results.

## Validation Rules

- Policy and scenario names must match approved registry names exactly.
- Campaign summaries must aggregate only the metrics already emitted by the matrix runner.
- Determinism checks must compare repeated runs using identical configuration and timestamp override.
- Campaign output paths must be deterministic when the override is supplied.
