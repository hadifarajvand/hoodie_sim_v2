# HOODIE Superiority Gap Diagnosis

## Current action-selection path

Current HOODIE action selection is implemented in `src/agents/hoodie_agent.py`:

1. `HoodieAgent.choose_action()` builds a history window from the current `PolicyContext`.
2. It collects the legal actions from `context.legal_action_mask`.
3. It calls `HoodieModel.forward(history, legal_actions)`.
4. It passes the resulting Q-values to `DoubleDQNSelector.select_action()`.
5. The selected action is returned directly.

This is a deterministic placeholder path, not a learned inference path.
The current untrained fallback is still deterministic, but it now scores legal actions
through the model path using observation-provided fallback hints instead of collapsing
to the first legal action.

## Does it use trained Q-values?

Not in any meaningful trained sense.

Evidence:

- `src/agents/hoodie_model.py` computes a synthetic `state_value` from `len(history.observations) + len(history.trace_history)`.
- `src/agents/dueling_dqn.py` uses `value_weight=1.0` and default-empty `advantage_weights`.
- `src/agents/double_dqn.py` selects the maximum Q-value among legal actions.
- `src/agents/hoodie_agent.py` now provides `export_state()` and `from_state()` so learned state can be reloaded from a checkpoint artifact.

Because all legal actions receive the same baseline score when `advantage_weights` is empty, `max(...)` falls back to the first legal action encountered unless learned preferences or fallback hints shift the scores.

## Does replay-buffer usage affect action selection?

Yes, after training has run.

Evidence:

- `src/agents/replay_buffer.py` stores transitions and exposes `sample()`.
- `src/agents/hoodie_agent.py` now exposes `learn_from_replay()`, so sampled replay can update `HoodieModel.learned_action_preferences`.
- `src/training/training_loop.py` records transitions after action selection and now consumes sampled replay transitions through the learning step.

The replay buffer can still be populated, but it is no longer inert storage once training has run.

## Do delayed rewards affect model parameters?

Yes, in the current learning path after training is run.

Evidence:

- `src/training/delayed_reward_training.py` stages and releases delayed transitions.
- `src/training/training_loop.py` records released transitions into the replay buffer and now feeds sampled replay transitions into `HoodieAgent.learn_from_replay()`.
- `src/agents/hoodie_model.py` updates `learned_action_preferences` with a deterministic preference rule:
  `new_preference = old_preference + learning_rate * (reward - old_preference)`.
- `src/agents/hoodie_agent.py` copies learned preferences into the target network snapshot.

So delayed rewards are staged, stored, sampled, and now update policy parameters deterministically.
The rule remains assumption-backed unless the exact paper equation is recovered.

## Why HOODIE currently matches FLC/BCO in practice

The current HOODIE behavior is deterministic and constrained by the legal-action mask.
Before learning, the score path can prefer offload-capable legal actions when the observation
provides explicit fallback hints. After training, the learned preference update can move the action
ranking away from the untrained fallback.

- `HoodieModel` now carries `learned_action_preferences`, but they are initialized empty.
- `DuelingDQN` still has no learned advantage weights.
- `DoubleDQNSelector` still selects the max legal Q-value deterministically.
- `HoodieModel.forward()` still adds deterministic fallback hints from the observation, and learned preferences are added separately from those hints.

That means the previous local-collapse failure mode is gone, replay is no longer inert after
training, and training can now move the policy away from its untrained fallback behavior, but the
learning rule is still not claimed to be paper-faithful.

`BCO` can also match this collapse when its observation lacks a usable `balance_hint`, because `src/policies/bco.py` falls back to the first legal action as well.

## Missing components blocking superiority

The following paper-backed components are still missing or effectively inert:

- State/history representation that materially changes action scoring.
- Q-network action scoring with learned weights.
- Double/Dueling DQN selection based on trained online and target networks.
- Delayed reward training updates that affect model parameters.
- Target network synchronization that matters to inference.
- Replay buffer sampling that drives learning updates.

## Paper evidence required before implementation

Before claiming HOODIE superiority, the implementation needs paper-backed or explicitly approved evidence for:

- The exact state/history features HOODIE consumes.
- The actual Q-network architecture and action scoring path.
- How Double DQN chooses online actions and target values.
- How Dueling DQN combines value and advantage streams.
- How delayed rewards are converted into training targets.
- When target network updates occur and how they affect inference.
- How replay buffer contents are sampled and used during updates.

## Recommended implementation order

1. Recover and document the missing paper-backed HOODIE state/history representation.
2. Implement real action scoring that uses the recovered features.
3. Wire delayed-reward training updates into parameter changes.
4. Add replay-buffer sampling into the learning step.
5. Add target-network synchronization that affects evaluation-backed policy weights.
6. Only then compare HOODIE against FLC, BCO, RO, HO, VO, and MLEO for superiority.

## Bottom line

The current codebase contains a structurally named HOODIE agent, but not a paper-faithful learned
HOODIE policy. It is no longer pure tie-breaking or inert replay: untrained behavior still relies
on deterministic fallback hints, trained behavior can update learned preferences from delayed
rewards, and trained state can be exported and reloaded, but the learning rule remains
assumption-backed rather than paper-exact.
