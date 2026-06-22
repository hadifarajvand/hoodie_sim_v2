# Training failure audit

Root cause: **missing epsilon-greedy exploration** in the training rollout. The trainer chose actions greedily (argmax) with no exploration, so replay filled with local-only transitions and the policy collapsed to fixed-local. Double-DQN/target/dueling wiring was verified correct. Fix: enable a configurable epsilon-greedy schedule during training only (paper Algorithm 1 line 16).
