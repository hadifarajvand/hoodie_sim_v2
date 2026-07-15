from __future__ import annotations

from src.analysis.distributed_multi_agent_hoodie_training.agent import DistributedAgent
from src.analysis.distributed_multi_agent_hoodie_training.policy import DistributedEpsilonGreedyPolicy
from src.analysis.distributed_multi_agent_hoodie_training.registry import DistributedAgentRegistry
from src.analysis.distributed_multi_agent_hoodie_training.replay import DistributedReplayBuffer, DistributedReplayTransition
from src.analysis.distributed_multi_agent_hoodie_training.schedule import EpsilonScheduleState


def test_distributed_registry_owns_independent_agent_state() -> None:
    registry = DistributedAgentRegistry.build(["ea-1", "ea-2"])
    assert registry.summary()["agent_count"] == 2
    assert registry.agents["ea-1"] is not registry.agents["ea-2"]
    assert registry.agents["ea-1"].online_network_owner_agent_id == "ea-1"
    assert registry.agents["ea-2"].target_network_owner_agent_id == "ea-2"


def test_distributed_policy_respects_legal_mask_and_seeded_choice() -> None:
    policy = DistributedEpsilonGreedyPolicy(epsilon_start=1.0, epsilon_end=0.0, decay_steps=10)
    first = policy.choose(legal_action_mask=[False, True, True], step=0, rng_seed=7, epsilon_state=EpsilonScheduleState())
    second = policy.choose(legal_action_mask=[False, True, True], step=0, rng_seed=7, epsilon_state=EpsilonScheduleState())
    assert first == second
    assert first in (1, 2)


def test_distributed_replay_buffer_keeps_transition_ownership() -> None:
    buffer = DistributedReplayBuffer()
    transition = DistributedReplayTransition(
        originating_agent_id="ea-1",
        acting_agent_id="ea-2",
        selected_destination_id="ea-3",
        action_index=1,
        paper_state_snapshot={"task_id": 1},
        legal_action_mask=[True, False, True],
        delayed_reward_available=True,
        terminal_reason="completed",
        task_id="task-1",
        arrival_slot=1,
        completion_or_drop_slot=4,
    )
    buffer.add(transition)
    agent = DistributedAgent(agent_id="ea-1", online_network_owner_agent_id="ea-1", target_network_owner_agent_id="ea-1")
    agent.replay_buffer.add(transition)
    assert buffer.transitions[0].originating_agent_id == "ea-1"
    assert agent.summary()["replay_size"] == 1
