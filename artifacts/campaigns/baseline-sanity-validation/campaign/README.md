# Baseline Reproduction Campaign

This campaign orchestrates the evaluation matrix and bundle packaging only.

## Outputs

- `campaign-manifest.json`
- `campaign-summary.json`
- `policy-summary.json`
- `scenario-summary.json`
- `determinism-check.json`
- `README.md`

## Constraints

No dependency files changed.
No training, plotting, or policy behavior changes are introduced by this campaign.
HoodieGymEnvironment remains lifecycle owner; CampaignRunner is orchestration-only.
