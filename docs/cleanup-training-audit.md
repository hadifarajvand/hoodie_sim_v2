# Training Pipeline Audit

## Files

| File | Purpose | Status |
|------|---------|--------|
| `src/training/training_loop.py` | Legacy `TrainingLoop` — trains `HoodieAgent` via `EvaluationRunner`, used by `src/run_pipeline.py` (full experiment pipeline) | **Active, not superseded** |
| `src/training/delayed_reward_training.py` | Delayed reward staging for tasks that complete after the slot they were dispatched | Active (used by `TrainingLoop`) |
| `src/training/seed_management.py` | Dataclass for training/eval seeds | Active |
| `src/training/training_logging.py` | `TrainingLogger` for episode progress | Active |
| `src/analysis/full_training_reproduction_campaign/trainer.py` | `DDQNTrainer` — paper-faithful Double DQN with `PaperHoodieDuelingNetwork` | **Active, separate path** |

## Verdict

**No overlap, no deprecation.** Two independent training paths:

1. **Legacy path** (`run_pipeline.py` → `TrainingLoop` → `HoodieAgent`): for the full experiment pipeline with comparison policies (FLC, HO, VO, RO, MLEO, BCO). Uses `EvaluationRunner` and `SlotEngine`.

2. **Paper reproduction path** (`CampaignConfig` → `DDQNTrainer` → `PaperHoodieDuelingNetwork`): dedicated 5000-episode Double DQN campaign with paper-default hyperparameters (7e-7 LR, W=10, T=110, epsilon-greedy decay).

Keep both. No changes needed.
