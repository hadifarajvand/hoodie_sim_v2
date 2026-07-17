from __future__ import annotations

import pytest

from src.agents.distributed_hoodie import DistributedHoodiePolicy
from src.environment.echo_control_config import EchoControlConfig
from src.environment.evaluation_gym_adapter import EvaluationHoodieGymEnvironment
from src.environment.topology import TopologyGraph
from src.evaluation.trace_protocol import build_deterministic_trace
from src.policies.action_masking import select_legal_action
from src.policies.policy_interface import PolicyContext


def _topology() -> TopologyGraph:
    return TopologyGraph(
        node_ids=("1", "2"),
        legal_adjacency={"1": ("2",), "2": ("1",)},
        metadata={"non_production_test_topology": True},
    )


def test_method_label_does_not_enable_echo_controls() -> None:
    env = EvaluationHoodieGymEnvironment(
        episode_length=4,
        topology=_topology(),
        policy_name="ECHO_DISABLED",
        echo_controls=EchoControlConfig.disabled(),
        supplied_trace=build_deterministic_trace(
            "disabled", 3, 4, agent_count=2, arrival_probability=1.0
        ),
    )
    env.reset(seed=3)
    assert not env._echo_enabled
    assert env.echo_controls.to_dict() == EchoControlConfig.disabled().to_dict()


def test_control_metadata_is_not_in_learner_observation() -> None:
    env = EvaluationHoodieGymEnvironment(
        episode_length=4,
        topology=_topology(),
        policy_name="ECHO",
        echo_controls=EchoControlConfig.enabled(),
        supplied_trace=build_deterministic_trace(
            "enabled", 4, 4, agent_count=2, arrival_probability=1.0
        ),
    )
    env.reset(seed=4)
    observation = env.observe_flat()
    assert observation["legal_action_mask"]
    assert not any(key.startswith("echo_") for key in observation)
    assert len(
        next(iter(DistributedHoodiePolicy.configured(
            agent_count=2,
            seed=4,
            use_lstm=True,
            learning_rate=7e-7,
            discount_factor=0.99,
            batch_size=2,
            replay_capacity=8,
            target_update_interval=2,
            hidden_dims=(8,),
            topology=_topology(),
        ).agents.values()))._feature_vector(observation)
    ) == 5


def test_destination_exact_mask_is_authoritative_everywhere() -> None:
    context = PolicyContext(
        observation={"source_agent_id": "1", "topology": ("2", "3")},
        legal_action_mask={
            "horizontal": True,
            "offload_horizontal": True,
            "horizontal_2": False,
            "horizontal_3": True,
        },
    )
    with pytest.raises(ValueError, match="Illegal action"):
        select_legal_action(context, "horizontal_2")
    assert select_legal_action(context, "horizontal_3") == "horizontal_3"

    policy = DistributedHoodiePolicy.configured(
        agent_count=3,
        seed=8,
        use_lstm=True,
        learning_rate=7e-7,
        discount_factor=0.99,
        batch_size=2,
        replay_capacity=8,
        target_update_interval=2,
        hidden_dims=(8,),
    )
    agent = policy.learner_for("1")
    legal = agent._legal_actions(context.legal_action_mask, context.observation)
    assert "horizontal_2" not in legal
    assert "horizontal_3" in legal
