# Repair plan

1. Add EpsilonGreedyExploration to DDQNTrainer (default None = legacy behavior).
2. Use epsilon-greedy selection in _episode_rollout during training.
3. Add Q-value + exploration diagnostics.
4. Enable the schedule in the production training session.

Rollback: set trainer.exploration=None. No environment/reward/dependency change.
