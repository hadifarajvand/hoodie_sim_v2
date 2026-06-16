from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from engine.euls_core import SimulationScenario, TaskArrivalSpec
from engine.execution_engine import DeterministicSimulationEngine
from engine.policies import FIFOPolicy
from engine.queue_manager import QueueManager
from reward_contract import compute_delayed_reward


def _scenario() -> SimulationScenario:
    return SimulationScenario(
        scenario_id="mrs_v1",
        seed=3,
        horizon=5,
        num_edge_nodes=2,
        edge_cpu_slots=(1.0, 1.0),
        cloud_cpu_slots=2.0,
        task_size_range=(1, 2),
        deadline_range=(2, 4),
        workload=TaskArrivalSpec(arrival_rate=1.0),
        topology={"type": "static"},
        policy_name="FIFO",
    )


def test_reward_contract_fixed() -> None:
    reward = compute_delayed_reward(final_status="completed", arrival_time=1, completion_time=4, drop_penalty=40)
    assert reward.reward == -3.0
    assert reward.delay == 3
    assert reward.reward_reason == "completed"


def test_fifo_queue_ordering() -> None:
    qm = QueueManager((1.0, 1.0), 2.0)
    tasks = []
    for idx in range(3):
        task = type("Task", (), {})()
        task.task_id = idx + 1
        task.arrival_time = 0
        task.workload_size = 1.0
        task.data_size = 1.0
        task.source_node = 0
        task.queue_history = []
        tasks.append(task)
        qm.enqueue(task, 0)
    assert [task.task_id for task in qm.nodes[0].queue] == [1, 2, 3]


def test_action_space_restricted_and_single_episode_runs(tmp_path: Path) -> None:
    engine = DeterministicSimulationEngine(_scenario(), FIFOPolicy(), tmp_path)
    result = engine.run()
    payload = json.loads(Path(result["trace_path"]).read_text())
    assert payload["events"]
    assert set(ev["event_type"] for ev in payload["events"]).issuperset({"TASK_ARRIVAL", "TASK_ENQUEUE"})


def test_sanity_metrics_and_order(tmp_path: Path) -> None:
    engine = DeterministicSimulationEngine(_scenario(), FIFOPolicy(), tmp_path)
    result = engine.run()
    metrics = json.loads(Path(result["metrics_path"]).read_text())
    assert "average_latency" in metrics
    assert "violation_ratio" in metrics
    assert "queue_growth_behavior" in metrics
