from __future__ import annotations

import copy
import random

import numpy as np
import torch

from src.agents.ddqn import DDQNLearner


def _learner() -> DDQNLearner:
    return DDQNLearner(input_dim=4, action_dim=3, hidden_dims=(8,), seed=11, capacity=20, batch_size=4, warmup_size=4, target_update_interval=2)


def test_checkpoint_roundtrip_preserves_online_target_replay_and_rng_state() -> None:
    learner = _learner()
    for index in range(8):
        state = np.full((4,), float(index), dtype=np.float32)
        next_state = np.full((4,), float(index + 1), dtype=np.float32)
        learner.record_transition(state, index % 3, float(index), next_state, index == 7, np.array([True, True, True]))
    learner.learn_from_replay()

    snapshot = learner.state_dict()
    clone = _learner()
    clone.load_state_dict(copy.deepcopy(snapshot))

    state = torch.zeros(4)
    legal = torch.tensor([True, True, True])
    assert learner.select_action(state, legal, 0.0, evaluation=True) == clone.select_action(state, legal, 0.0, evaluation=True)
    assert snapshot["training_steps"] == clone.training_steps
    assert snapshot["target_update_steps"] == clone.target_update_steps
    assert len(snapshot["replay_buffer"]["items"]) == len(clone.replay_buffer.state_dict()["items"])
    original_item = snapshot["replay_buffer"]["items"][0]
    clone_item = clone.replay_buffer.state_dict()["items"][0]
    assert original_item.action == clone_item.action
    assert original_item.reward == clone_item.reward


def test_checkpoint_restore_keeps_random_generators_in_sync() -> None:
    learner = _learner()
    snapshot = learner.state_dict()
    random.random()
    np.random.random()
    torch.rand(1)
    clone = _learner()
    clone.load_state_dict(snapshot)
    assert isinstance(clone.state_dict()["python_random_state"], tuple)
    assert isinstance(clone.state_dict()["numpy_random_state"], tuple)
    assert torch.equal(clone.state_dict()["torch_random_state"], learner.state_dict()["torch_random_state"])
