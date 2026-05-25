# Data Model: Feature 060B

## BindFullCampaignRealTorchTrainerReport

Fields:

- `feature_id`
- `prerequisite_tags_verified`
- `feature_060a_audit_verified`
- `torch_environment_summary`
- `real_trainer_binding_summary`
- `feature_060_repair_summary`
- `campaign_execution_summary`
- `training_metrics_summary`
- `evaluation_metrics_summary`
- `artifact_regeneration_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## RealTrainerBindingSummary

Must prove Feature 060 now imports and executes real trainer, learner, or network code. Required fields:

- `real_binding_verified`
- `torch_import_used`
- `torchrl_available`
- `real_trainer_import_used`
- `real_trainer_instantiated`
- `real_trainer_update_or_train_called`
- `scalar_fallback_drives_campaign_claim`

## Feature060RepairSummary

Must prove regenerated Feature 060 artifacts support the campaign claim through the real trainer-bound path.

## ArtifactRegenerationSummary

Must list regenerated Feature 060 artifacts and prove each exists.
