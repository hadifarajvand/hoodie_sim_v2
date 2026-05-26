# Data Model: Feature 062

## MultiSeedCampaignAblationBatchReport

Fields:

- `feature_id`
- `batch_items_covered`
- `prerequisite_tags_verified`
- `feature_061_verified`
- `multi_seed_gate_summary`
- `multi_seed_campaign_summary`
- `multi_seed_aggregation_summary`
- `ablation_gate_summary`
- `ablation_execution_summary`
- `artifact_manifest_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## MultiSeedGateSummary

Must define:

- deterministic seed set
- seed count
- bounded per-seed budget
- trace-bank ID
- metric schema
- real-trainer binding evidence

## MultiSeedCampaignSummary

Must define seed-level controlled results for trained policy and baselines. Configured and actual execution budgets must be stored separately.

## MultiSeedAggregationSummary

Must include sample count, mean, min, max, and optional variance/std for supported numeric metrics. Schema-only metrics must be marked as not claimed rather than silently dropped.

## AblationGateSummary

Must define the supported ablation variants and whether each is executable or blocked with exact blocker evidence.

## AblationExecutionSummary

Must report per-variant outputs under the same seed set, trace-bank constraints, and metric schema.

## SafetySummary

Must prove no dependency drift, no policy drift, no environment contract drift, no reward timing change, no prior artifact rewrite, no paper reproduction claim, no unsupported superiority claim, no uncontrolled campaign loop, and no checkpoint binary creation.
