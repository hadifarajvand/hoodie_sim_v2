from __future__ import annotations

import json

from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.topology import TopologyGraph


def make_horizontal_topology_environment(*, episode_length: int = 4) -> HoodieGymEnvironment:
    env = HoodieGymEnvironment(episode_length=episode_length)
    env.topology = TopologyGraph(
        node_ids=("1", "2", "cloud"),
        legal_adjacency={
            "1": ("2",),
            "2": ("cloud",),
        },
    )
    return env


def make_vertical_topology_environment(*, episode_length: int = 4) -> HoodieGymEnvironment:
    env = HoodieGymEnvironment(episode_length=episode_length)
    env.topology = TopologyGraph(
        node_ids=("1", "2", "cloud"),
        legal_adjacency={
            "1": ("cloud",),
            "2": ("cloud",),
        },
    )
    return env


def attach_one_task_trace_bank(env: HoodieGymEnvironment, *, action: str) -> HoodieGymEnvironment:
    payload = {
        "trace_id": f"synthetic-{action}",
        "seed": 101,
        "metadata": {"mode": "trace_bank", "trace_id": f"synthetic-{action}", "seed": "101"},
        "tasks": [
            {
                "task_id": 1,
                "source_agent_id": 1,
                "arrival_slot": 0,
                "size": 28.0,
                "processing_density": 5.0,
                "timeout_length": 5,
                "absolute_deadline_slot": 5,
                "cycles_required": 140.0,
                "cycles_remaining": 140.0,
            }
        ],
    }
    env.trace_source = type(
        "_SyntheticTraceSource",
        (),
        {
            "mode": "trace_bank",
            "identifier": f"synthetic-{action}",
            "root_path": None,
            "load": staticmethod(lambda payload=payload: json.loads(json.dumps(payload))),
        },
    )()
    return env


class RichLifecycleAuditFixtureEnv:
    def __init__(self, *, path: str) -> None:
        self.path = path
        self.current_task = object()

    def reset(self, seed=None):
        self.current_task = object()
        return {"observation": True}, {}

    def legal_action_mask(self, current_task):
        return {"local": True, "horizontal": True, "vertical": True}

    def step(self, action):
        self.current_task = None
        if self.path == "horizontal":
            events = [
                "selected_action",
                "queued_public",
                "transmission_started",
                "transmission_completed",
                "execution_started",
                "execution_completed",
                "reward_emitted",
            ]
        else:
            events = [
                "selected_action",
                "offloaded_cloud",
                "transmission_started",
                "transmission_completed",
                "execution_started",
                "execution_completed",
                "reward_emitted",
            ]
        return {"observation": True}, -1.0, True, False, {
            "finalized_tasks": [
                {
                    "task_id": "case-audit-fixture-task",
                    "terminal_outcome": "completed",
                    "offload_lifecycle_events": events,
                }
            ]
        }
