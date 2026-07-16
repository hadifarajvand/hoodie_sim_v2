from __future__ import annotations

import numpy as np
import pytest
import torch

from src.agents.distributed_hoodie import DistributedHoodiePolicy
from src.environment.topology import TopologyGraph
from src.policies.action_masking import select_legal_action
from src.policies.interface import PolicyContext as CompatibilityPolicyContext
from src.policies.policy_interface import PolicyContext


def _policy(agent_count: int = 10) -> DistributedHoodiePolicy:
    return DistributedHoodiePolicy.configured(
        agent_count=agent_count,
        seed=7,
        use_lstm=True,
        learning_rate=1e-3,
        discount_factor=0.9,
        batch_size=1,
        replay_capacity=8,
        target_update_interval=2,
        device_name="cpu",
        hidden_dims=(8,),
        lookback=2,
        lstm_hidden=4,
    )


def _context(
    *,
    task_id: int,
    source_agent_id: int = 1,
    destination: str = "6",
    trace_id: str = "trace-1",
) -> PolicyContext:
    return PolicyContext(
        observation={
            "task_id": task_id,
            "source_agent_id": source_agent_id,
            "slot": task_id,
            "size": 1.0,
            "processing_density": 0.297,
            "queue_load": 0.0,
            "topology": (destination,),
            "legal_action_mask": {
                "local": True,
                "horizontal": True,
                "vertical": True,
            },
        },
        legal_action_mask={
            "local": True,
            "horizontal": True,
            "vertical": True,
        },
        trace_history=(trace_id,),
    )


def test_policy_context_has_one_runtime_identity() -> None:
    assert CompatibilityPolicyContext is PolicyContext


def test_each_learner_uses_exact_topology_destinations() -> None:
    topology = TopologyGraph.for_agent_count(10)
    policy = _policy(10)
    for agent_id, agent in policy.agents.items():
        expected = (
            "local",
            *(
                f"horizontal_{destination}"
                for destination in topology.legal_horizontal_destinations(agent_id)
            ),
            "cloud",
        )
        assert agent.action_order == expected
        assert agent.learner.learner.action_dim == len(expected)
        assert agent.learner.learner.online_network.num_actions == len(expected)


def test_destination_specific_action_is_selected_and_evidenced() -> None:
    policy = _policy(10)
    agent = policy.learner_for(1)
    assert agent.action_order == ("local", "horizontal_6", "cloud")

    with torch.no_grad():
        for parameter in agent.learner.learner.online_network.parameters():
            parameter.zero_()
        final_advantage = agent.learner.learner.online_network.advantage_stream[-1]
        final_advantage.bias.copy_(torch.tensor([0.0, 10.0, 0.0]))

    context = _context(task_id=1)
    selected = policy.choose_action(context)
    assert selected == "horizontal_6"
    assert select_legal_action(context, selected) == selected
    assert context.observation["hoodie_action_order"] == (
        "local",
        "horizontal_6",
        "cloud",
    )
    assert context.observation["hoodie_legal_actions"] == (
        "local",
        "horizontal_6",
        "cloud",
    )
    q_values = context.observation["hoodie_q_value_summary"]
    assert isinstance(q_values, dict)
    assert q_values["horizontal_6"] > q_values["local"]
    assert q_values["horizontal_6"] > q_values["cloud"]

    with pytest.raises(ValueError, match="Illegal horizontal destination"):
        select_legal_action(context, "horizontal_2")


def test_multi_agent_routing_never_reuses_the_previous_owner() -> None:
    policy = _policy(10)
    context = PolicyContext(
        observation={
            "task_id": 1,
            "size": 1.0,
            "topology": ("6",),
        },
        legal_action_mask={"local": True},
        trace_history=("trace-1",),
    )
    with pytest.raises(ValueError, match="source_agent_id is required"):
        policy.choose_action(context)


def test_delayed_reward_reuses_exact_decision_and_next_decision_windows() -> None:
    policy = _policy(10)
    agent = policy.learner_for(1)
    first = _context(task_id=1)
    second = _context(task_id=2)

    first_action = policy.choose_action(first)
    first_window = np.asarray(agent.decision_windows["1"], dtype=np.float32)
    policy.choose_action(second)
    second_window = np.asarray(agent.decision_windows["2"], dtype=np.float32)

    policy.record_transition(
        agent_id=1,
        state=dict(first.observation),
        action=first_action,
        reward=-1.0,
        next_state=dict(second.observation),
        done=False,
    )
    transition = agent.learner.replay.as_list()[-1]
    assert np.array_equal(transition.state, first_window)
    assert np.array_equal(transition.next_state, second_window)
    assert "1" not in agent.decision_windows
    assert "2" in agent.decision_windows


def test_checkpoint_roundtrip_preserves_destination_vocabulary() -> None:
    policy = _policy(10)
    exported = policy.export_state()
    restored = DistributedHoodiePolicy.from_state(exported)
    assert restored.learner_for(1).action_order == (
        "local",
        "horizontal_6",
        "cloud",
    )
    assert restored.learner_for(1).learner.learner.action_dim == 3
    restored.validate_topology(TopologyGraph.for_agent_count(10))


def test_checkpoint_action_vocabulary_must_match_evaluation_topology() -> None:
    policy = _policy(10)
    policy.learner_for(1).learner.action_order = (
        "local",
        "horizontal_2",
        "cloud",
    )
    policy.learner_for(1).learner.ACTION_ORDER = (
        "local",
        "horizontal_2",
        "cloud",
    )
    with pytest.raises(ValueError, match="action vocabulary mismatch"):
        policy.validate_topology(TopologyGraph.for_agent_count(10))


def test_new_trace_resets_recurrent_history_without_erasing_replay() -> None:
    policy = _policy(10)
    agent = policy.learner_for(1)
    policy.choose_action(_context(task_id=1, trace_id="trace-1"))
    assert agent.causal_history
    assert agent.decision_windows

    policy.choose_action(_context(task_id=2, trace_id="trace-2"))
    assert agent.active_trace_id == "trace-2"
    assert len(agent.causal_history) == 1
    assert set(agent.decision_windows) == {"2"}
