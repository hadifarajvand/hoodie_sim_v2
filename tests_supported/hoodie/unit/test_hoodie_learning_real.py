import random
import tempfile
from pathlib import Path

import numpy as np
import torch

from src.agents.ddqn import DDQNLearner, DuelingQNetwork, ReplayBuffer, Transition, masked_epsilon_greedy
from src.agents.lstm_dueling_dqn import LSTM_Dueling_DQN
from src.policies.bco import BalancedCooperationOffloadingPolicy
from src.policies.flc import FullLocalComputingPolicy
from src.policies.ho import HorizontalOffloadingPolicy
from src.policies.mleo import MinimumLatencyEstimateOffloadingPolicy
from src.policies.policy_interface import PolicyContext
from src.policies.ro import RandomOffloadingPolicy
from src.policies.vo import VerticalOffloadingPolicy
from src.evaluation.paired_evaluation import TaskRecord, validate_fairness, paired_metric_summary


def make_learner(target_update_interval=2):
    return DDQNLearner(input_dim=4, action_dim=3, hidden_dims=(8,), seed=7, capacity=20, batch_size=4, warmup_size=4, target_update_interval=target_update_interval)


def test_dueling_network_shape_and_streams_influence():
    net = DuelingQNetwork(4, 3, hidden_dims=(8,), seed=1)
    x = torch.randn(2, 4)
    q = net(x)
    assert q.shape == (2, 3)
    with torch.no_grad():
        net.value_head[-1].bias.fill_(1.0)
        net.advantage_head[-1].bias.copy_(torch.tensor([0.0, 1.0, 2.0]))
        q2 = net(x)
    assert not torch.allclose(q, q2)


def test_illegal_actions_and_epsilon_behavior():
    q = torch.tensor([1.0, 9.0, 2.0])
    legal = torch.tensor([True, False, True])
    assert masked_epsilon_greedy(q, legal, 0.0, random.Random(0)) == 2
    picks = {masked_epsilon_greedy(q, legal, 1.0, random.Random(seed)) for seed in range(20)}
    assert picks <= {0, 2}


def test_replay_buffer_seeded_not_prefix():
    buffer = ReplayBuffer(capacity=10, seed=3, batch_size=4)
    for index in range(6):
        arr = np.full((4,), float(index), dtype=np.float32)
        buffer.add(Transition(arr, index % 3, float(index), arr + 1, False, np.array([True, True, True])))
    first = buffer.sample(4)
    buffer2 = ReplayBuffer(capacity=10, seed=3, batch_size=4)
    for index in range(6):
        arr = np.full((4,), float(index), dtype=np.float32)
        buffer2.add(Transition(arr, index % 3, float(index), arr + 1, False, np.array([True, True, True])))
    assert tuple(t.action for t in first) == tuple(t.action for t in buffer2.sample(4))
    assert tuple(t.action for t in first) != tuple(t.action for t in buffer.as_list()[:4])


def test_double_dqn_terminal_and_sync():
    learner = make_learner(target_update_interval=2)
    for index in range(8):
        state = np.full((4,), float(index), dtype=np.float32)
        next_state = np.full((4,), float(index + 1), dtype=np.float32)
        learner.record_transition(state, index % 3, 1.0, next_state, index == 7, np.array([True, True, True]))
    before = {k: v.clone() for k, v in learner.target_network.state_dict().items()}
    online_before = {k: v.clone() for k, v in learner.online_network.state_dict().items()}
    out = learner.learn_from_replay()
    assert out and "loss" in out
    after = learner.target_network.state_dict()
    assert all(torch.equal(before[k], after[k]) for k in before)
    assert any(not torch.equal(online_before[k], learner.online_network.state_dict()[k]) for k in online_before)
    learner.learn_from_replay()
    after_sync = learner.target_network.state_dict()
    assert any(not torch.equal(before[k], after_sync[k]) for k in before)


def test_checkpoint_roundtrip_and_resume():
    learner = make_learner()
    for index in range(8):
        state = np.full((4,), float(index), dtype=np.float32)
        next_state = np.full((4,), float(index + 1), dtype=np.float32)
        learner.record_transition(state, index % 3, 1.0, next_state, False, np.array([True, True, True]))
    learner.learn_from_replay()
    payload = learner.state_dict()
    clone = make_learner()
    clone.load_state_dict(payload)
    state = torch.zeros(4)
    legal = torch.tensor([True, True, True])
    assert learner.select_action(state, legal, 0.0, evaluation=True) == clone.select_action(state, legal, 0.0, evaluation=True)


def test_lstm_path_and_ablation():
    model = LSTM_Dueling_DQN(state_dim=6, lookback=3, num_actions=4, hidden_sizes=[8], lstm_hidden=5, use_lstm=True)
    x = torch.randn(2, 3, 6)
    q = model(x)
    assert q.shape == (2, 4)
    feat_a = model.forecast_features(x)
    model_no = LSTM_Dueling_DQN(state_dim=6, lookback=3, num_actions=4, hidden_sizes=[8], lstm_hidden=5, use_lstm=False)
    feat_b = model_no.forecast_features(x)
    assert not torch.allclose(feat_a, feat_b)


def test_lstm_no_future_leakage():
    model = LSTM_Dueling_DQN(state_dim=6, lookback=3, num_actions=4, hidden_sizes=[8], lstm_hidden=5, use_lstm=True)
    x1 = torch.zeros(1, 3, 6)
    x2 = x1.clone()
    x2[:, -1, :] = 5.0
    f1 = model.forecast_features(x1)
    f2 = model.forecast_features(x2)
    assert not torch.allclose(f1, f2)


def test_baseline_contracts_and_fairness():
    context = PolicyContext(observation={"latency_estimates": {"local": 5.0, "horizontal": 2.0, "vertical": 10.0}, "balance_hint": {"local": 5.0, "horizontal": 2.0, "vertical": 1.0}}, legal_action_mask={"local": True, "horizontal": True, "vertical": True}, trace_history=())
    assert FullLocalComputingPolicy().choose_action(context) in {"local", "compute_local"}
    assert RandomOffloadingPolicy(seed=1).choose_action(context) in {"local", "horizontal", "vertical", "compute_local", "offload_horizontal", "offload_vertical"}
    assert HorizontalOffloadingPolicy().choose_action(context) in {"horizontal", "offload_horizontal", "local", "compute_local", "vertical", "offload_vertical"}
    assert VerticalOffloadingPolicy().choose_action(context) in {"vertical", "offload_vertical", "local", "compute_local", "horizontal", "offload_horizontal"}
    assert BalancedCooperationOffloadingPolicy().choose_action(context) in {"horizontal", "vertical", "local", "compute_local"}
    assert MinimumLatencyEstimateOffloadingPolicy().choose_action(context) == "horizontal"
    record = TaskRecord("c", "r", "p", 0, "h", "t", "a", 1, 2, "local", "dest", 3, "completed", 1.0, 0.2, 0.3, 0.4, 1.0, "o", "x", "y")
    summary = paired_metric_summary([record])
    assert summary.offered_tasks == 1 and summary.completed_tasks == 1
    validate_fairness({"trace_hash": "h", "offered_tasks": 1, "task_ids": ["t"], "topology_hash": "x", "physical_configuration": "y", "horizon": 1, "seed_set": [0], "metric_denominator": 1, "warmup_handling": "same", "checkpoint_selection_rule": "same"}, {"trace_hash": "h", "offered_tasks": 1, "task_ids": ["t"], "topology_hash": "x", "physical_configuration": "y", "horizon": 1, "seed_set": [0], "metric_denominator": 1, "warmup_handling": "same", "checkpoint_selection_rule": "same"})
