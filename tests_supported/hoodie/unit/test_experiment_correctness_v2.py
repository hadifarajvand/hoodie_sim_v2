from __future__ import annotations

import numpy as np
import torch

from src.agents.recurrent_ddqn import RecurrentDoubleDQNAgent
from src.environment.topology import TopologyGraph
from src.evaluation.trace_protocol import build_deterministic_trace
from src.hoodie.experiments.contract_mapping import (
    build_environment_config,
    build_link_rate_config,
    build_training_config,
)
from src.hoodie.experiments.matrix_patch import install_matrix_patch
from src.hoodie.experiments.panel_registry import PANEL_REGISTRY
from src.hoodie.experiments.production_patch import paper_epsilon


def _rows():
    install_matrix_patch()
    from src.hoodie.experiments import job_matrix

    return job_matrix.build_production_job_matrix("test-campaign")


def test_corrected_matrix_has_real_training_series_and_dependencies() -> None:
    rows = _rows()
    training = [row for row in rows if row.job_type == "training"]
    evaluation = [row for row in rows if row.job_type == "evaluation"]
    assert len(rows) == 305
    assert len(training) == 17
    assert len(evaluation) == 288
    training_ids = {row.job_id for row in training}
    assert all(
        row.checkpoint_dependency in training_ids
        for row in evaluation
        if row.policy == "HOODIE"
    )
    assert all(
        row.checkpoint_dependency is None
        for row in evaluation
        if row.policy != "HOODIE"
    )
    figure_8a = [
        row
        for row in training
        if row.panel_id == "figure_8a"
        and not row.training_contract.get("reference_only")
    ]
    assert {row.independent_value for row in figure_8a} == {
        1e-9,
        5e-9,
        1e-8,
        1e-7,
        5e-7,
        7e-7,
    }


def test_figure_9_scenario_panels_use_agent_count_on_x_axis() -> None:
    rows = _rows()
    for panel_id in ("figure_9d", "figure_9e"):
        panel_rows = [row for row in rows if row.panel_id == panel_id]
        assert panel_rows
        assert {row.independent_variable for row in panel_rows} == {"number_of_agents"}
        assert {int(row.independent_value) for row in panel_rows} == {10, 15, 20, 25, 30}
        assert len({row.series_name for row in panel_rows}) == 3


def test_contract_sweeps_reach_runtime_configuration() -> None:
    rows = _rows()
    arrival = next(
        row
        for row in rows
        if row.panel_id == "figure_10a"
        and row.policy == "HOODIE"
        and row.independent_value == 0.9
    )
    source = PANEL_REGISTRY[arrival.panel_id].source_contract
    assert build_environment_config(arrival, source).arrival_probability == 0.9

    cpu = next(
        row
        for row in rows
        if row.panel_id == "figure_10b"
        and row.policy == "FLC"
        and row.independent_value == 7
    )
    runtime = build_environment_config(cpu, PANEL_REGISTRY[cpu.panel_id].source_contract)
    assert runtime.local_service_capacity == 7
    assert runtime.public_service_capacity == 7

    rate = next(row for row in rows if row.panel_id == "figure_9e" and row.series_name == "Balanced")
    links = build_link_rate_config(rate, PANEL_REGISTRY[rate.panel_id].source_contract)
    assert links.horizontal_data_rate_mbps == 10
    assert links.vertical_data_rate_mbps == 30

    training = next(row for row in rows if row.job_id == "train-figure8a-lr-7e-07")
    config = build_training_config(
        training,
        PANEL_REGISTRY[training.panel_id].source_contract,
        trace_hash="test",
        output_dir=None,
    )
    assert config.learning_rate == 7e-7
    assert config.discount_factor == 0.99
    assert config.batch_size == 64
    assert config.target_network_update_frequency == 2000


def test_paper_epsilon_schedule() -> None:
    assert paper_epsilon(0, 5000) == 1.0
    assert paper_epsilon(2499, 5000) > 0.0
    assert paper_epsilon(2500, 5000) == 0.0
    assert paper_epsilon(4999, 5000) == 0.0


def test_recurrent_ddqn_learns_with_mse_and_actual_optimizer_rate() -> None:
    learner = RecurrentDoubleDQNAgent(
        state_dim=5,
        lookback=3,
        hidden_dims=(16, 16),
        lstm_hidden=4,
        batch_size=2,
        warmup_size=2,
        capacity=8,
        target_update_interval=2,
        learning_rate=1e-3,
        gamma=0.9,
        seed=3,
        device_name="cpu",
    )
    state = np.zeros((3, 5), dtype=np.float32)
    next_state = np.ones((3, 5), dtype=np.float32)
    mask = np.array([True, True, True])
    learner.learner.record_transition(state, 0, 1.0, next_state, False, mask)
    learner.learner.record_transition(state, 1, -1.0, next_state, True, mask)
    loss = learner.update(2)
    assert loss is not None
    assert np.isfinite(loss)
    assert learner.learner.optimizer.param_groups[0]["lr"] == 1e-3


def test_lstm_forward_has_no_cross_call_hidden_state_leakage() -> None:
    learner = RecurrentDoubleDQNAgent(
        state_dim=5,
        lookback=3,
        hidden_dims=(8,),
        lstm_hidden=4,
        batch_size=2,
        warmup_size=2,
        capacity=8,
        seed=4,
        device_name="cpu",
    )
    window = torch.ones((1, 3, 5), dtype=torch.float32)
    learner.learner.online_network.eval()
    first = learner.learner.online_network(window)
    second = learner.learner.online_network(window)
    assert torch.allclose(first, second)


def test_trace_honors_workload_and_topology_family() -> None:
    trace = build_deterministic_trace(
        "scenario",
        seed=7,
        episode_length=6,
        agent_count=5,
        arrival_probability=1.0,
        timeout_length=3,
        drain_slots=1,
        task_sizes=(1.0, 3.0),
    )
    assert len(trace.tasks) == 25
    assert {task.size for task in trace.tasks}.issubset({1.0, 3.0})
    for count in (10, 15, 20, 25, 30):
        topology = TopologyGraph.for_agent_count(count)
        assert topology.node_count() == count
        assert topology.connected_component_count() == 5
