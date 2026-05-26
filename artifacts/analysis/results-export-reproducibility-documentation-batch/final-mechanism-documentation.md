# Final Mechanism Documentation

## Faithful Components
- real Torch trainer binding
- selected-action/outcome evidence
- multi-seed campaign gate
- mechanism ablation controls

## Implemented Simplifications
- controlled materialization of prior artifacts
- no new training loop
- no new evaluation semantics

## Deviation Notes
- documentation package exports only committed evidence
- schema-only metrics are explicitly not claimed

## Real Torch Trainer Binding
{
  "real_trainer_binding_verified": true,
  "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer"
}

## Selected-Action/Outcome Evidence
{
  "source": "artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json",
  "status": "documented"
}

## Multi-Seed and Ablation Limits
- controlled experiment data only
- ablation blocked variants remain blocked with exact blockers

## Non-Claims
- no paper reproduction claim
- no unsupported superiority claim
- no production performance claim
