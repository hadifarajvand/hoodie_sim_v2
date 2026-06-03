# Plan

Input: base HOODIE paper sources and the current simulator implementation.

Steps:
- validate scope
- load paper-grounded formulas
- model action, queue, reward, learning, and communication interfaces
- classify implementation coverage
- compute readiness level
- generate proposed-method report

No ranking.
No baseline evaluation.
No thesis/DCQ extension.

## Current Progress

- Implemented: hybrid action selection, private/offloading/public queue timing, reward/cost mapping, distributed edge-agent decision, DQN interface, replay memory, inference mode, and pub-sub metadata.
- Partial: Double DQN target rule, Dueling DQN value/advantage interface, LSTM forecast/recovery interface, epsilon-greedy training schedule.
- Next component to tighten: `double_dqn_target_rule`.
- Readiness remains `mostly_implemented` because the learning-internal interfaces are still not full trainable modules.
