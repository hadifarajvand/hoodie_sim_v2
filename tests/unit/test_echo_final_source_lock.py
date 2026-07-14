from __future__ import annotations

import json
from pathlib import Path


SOURCE_LOCK = Path("configs/echo_final/source_lock.json")


def _load() -> dict[str, object]:
    return json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))


def test_final_echo_scope_is_limited() -> None:
    payload = _load()
    deltas = payload["method_contract"]["echo_deltas"]
    assert deltas == [
        "ert_source_queue_scheduling",
        "deadline_feasible_route_filtering",
        "minimum_lateness_fallback",
        "fixed_deadline_drop_penalty",
    ]
    assert "smdp" in payload["method_contract"]["excluded"]
    assert "new_state_vector" in payload["method_contract"]["excluded"]
    assert "new_q_target" in payload["method_contract"]["excluded"]


def test_hoodie_table_4_defaults_are_frozen() -> None:
    defaults = _load()["hoodie_defaults"]
    assert defaults["task_arrival_probability"] == 0.5
    assert defaults["horizontal_rate_mbps"] == 30.0
    assert defaults["vertical_rate_mbps"] == 10.0
    assert defaults["edge_agents"] == 20
    assert defaults["private_cpu_ghz"] == 5.0
    assert defaults["public_edge_cpu_ghz"] == 5.0
    assert defaults["cloud_cpu_ghz"] == 30.0
    assert defaults["training_episodes"] == 5000
    assert defaults["slot_duration_seconds"] == 0.1
    assert defaults["default_timeout_slots"] == 20
    assert defaults["learning_rate"] == 7e-7
    assert defaults["discount_factor"] == 0.99
    assert defaults["q_hidden_layers"] == [1024, 1024, 1024]
    assert defaults["target_copy_iterations"] == 2000
    assert defaults["lstm_lookback_slots"] == 10
    assert defaults["lstm_hidden_cells"] == 20
    assert defaults["replay_capacity"] == 10000
    assert defaults["hoodie_drop_penalty"] == 40.0
    assert defaults["batch_size"] == 64


def test_topology_contract_is_regular_and_unique() -> None:
    topology = _load()["topology"]
    edges = [tuple(edge) for edge in topology["edge_list"]]
    assert topology["node_count"] == 20
    assert topology["undirected_edge_count"] == 30
    assert len(edges) == 30
    assert len(set(edges)) == 30
    degrees = {node: 0 for node in range(1, 21)}
    for left, right in edges:
        assert left != right
        assert 1 <= left <= 20
        assert 1 <= right <= 20
        degrees[left] += 1
        degrees[right] += 1
    assert set(degrees.values()) == {3}


def test_sweeps_and_figure_numbering_are_frozen() -> None:
    figures = _load()["figures"]
    assert figures["figure_5_arrival"]["x_values"] == [0.1, 0.3, 0.5, 0.7, 0.9]
    assert figures["figure_6_capacity"]["x_values_ghz"] == [3.0, 4.0, 5.0, 6.0, 7.0]
    assert figures["figure_7_timeout"]["delay_panel_x_seconds"] == [9.6, 9.8, 10.0, 10.2, 10.4]
    assert figures["figure_7_timeout"]["drop_panel_x_seconds"] == [1.6, 1.8, 2.0, 2.2, 2.4]
    assert figures["figure_4_topology"]["action"] == "reuse_verified"


def test_deadline_and_statistics_contract() -> None:
    payload = _load()
    deadline = payload["deadline_contract"]
    assert deadline["completion_at_deadline_is_success"] is True
    assert deadline["unfinished_at_deadline_is_removed"] is True
    assert deadline["violation_ratio_equals_drop_ratio"] is True
    assert deadline["drain_slots_rule"] == "max_timeout_slots_at_operating_point"
    statistics = payload["statistics"]
    assert statistics["seeds"] == list(range(10))
    assert statistics["held_out_episodes_per_seed"] == 200
    assert statistics["paired_task_traces"] is True
    assert statistics["confidence_interval"] == 0.95
