# Commit summary

fix: repair training stability and exploration collapse

- Added configurable epsilon-greedy exploration to the training rollout (paper Algorithm 1 line 16).
- Default-None preserves legacy campaign behavior; enabled only in the production training session.
- Added epsilon, Q-value, replay-balance, target/double-DQN, dueling, and loss diagnostics.
- No environment, reward, task, topology, reconciliation, metric-schema, DAL, or dependency change.
