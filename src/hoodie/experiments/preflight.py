from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import tempfile
from typing import Any

import numpy as np
import torch

from src.agents.distributed_hoodie import DistributedHoodiePolicy
from src.agents.recurrent_ddqn import RecurrentDoubleDQNAgent
from src.environment.topology import TopologyGraph
from src.evaluation.trace_protocol import build_deterministic_trace

from .contract_mapping import (
    build_environment_config,
    build_evaluation_config,
    build_link_rate_config,
    build_training_config,
    validate_contract_mapping,
)
from .job_matrix import validate_production_job_matrix
from .matrix_patch import install_matrix_patch
from .panel_registry import PANEL_REGISTRY
from .production_patch import paper_epsilon


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_preflight() -> dict[str, Any]:
    install_matrix_patch()
    from . import job_matrix

    campaign_id = "figures-8-11-preflight"
    rows = job_matrix.build_production_job_matrix(campaign_id)
    counts = validate_production_job_matrix(rows)
    _check(counts["total"] == 305, f"unexpected matrix size: {counts}")
    _check(counts["training"] == 17, f"unexpected training count: {counts}")
    _check(counts["evaluation"] == 288, f"unexpected evaluation count: {counts}")

    contract_errors: dict[str, list[str]] = {}
    for row in rows:
        source = PANEL_REGISTRY[row.panel_id].source_contract
        mismatches = validate_contract_mapping(row, source)
        if mismatches:
            contract_errors[row.job_id] = mismatches
        if row.job_type == "training":
            build_training_config(row, source, trace_hash="preflight", output_dir=None)
        else:
            build_evaluation_config(row, source, trace_id="preflight", output_dir=None)
        build_environment_config(row, source)
        build_link_rate_config(row, source)
    _check(not contract_errors, f"contract mapping errors: {contract_errors}")

    _check(paper_epsilon(0, 5000) == 1.0, "epsilon must start at one")
    _check(paper_epsilon(2499, 5000) > 0.0, "epsilon must remain positive before midpoint")
    _check(paper_epsilon(2500, 5000) == 0.0, "epsilon must be zero at midpoint")
    _check(paper_epsilon(4999, 5000) == 0.0, "epsilon must stay zero")

    topology_metrics: dict[str, dict[str, int | bool]] = {}
    for agent_count in (10, 15, 20, 25, 30):
        topology = TopologyGraph.for_agent_count(agent_count)
        _check(topology.node_count() == agent_count, "topology node count mismatch")
        _check(topology.is_connected(), f"topology N={agent_count} must be connected")
        topology_metrics[str(agent_count)] = {
            "node_count": topology.node_count(),
            "edge_count": topology.edge_count(),
            "connected": topology.is_connected(),
        }

    trace = build_deterministic_trace(
        "preflight-trace",
        seed=7,
        episode_length=6,
        agent_count=5,
        arrival_probability=1.0,
        timeout_length=3,
        drain_slots=1,
        task_sizes=(1.0, 3.0),
        processing_density=0.297,
    )
    _check(len(trace.tasks) == 25, "trace task count mismatch")
    _check({task.size for task in trace.tasks}.issubset({1.0, 3.0}), "trace ignored task-size contract")

    learner = RecurrentDoubleDQNAgent(
        state_dim=5,
        lookback=3,
        seed=3,
        hidden_dims=(16, 16),
        lstm_hidden=4,
        use_lstm=True,
        learning_rate=1e-3,
        gamma=0.9,
        batch_size=2,
        capacity=8,
        warmup_size=2,
        target_update_interval=2,
        device_name="cpu",
    )
    state = np.zeros((3, 5), dtype=np.float32)
    next_state = np.ones((3, 5), dtype=np.float32)
    legal_mask = np.asarray([True, True, True], dtype=bool)
    for action in (0, 1):
        learner.learner.record_transition(
            state,
            action,
            reward=float(action + 1),
            next_state=next_state,
            done=False,
            legal_mask=legal_mask,
        )
    loss = learner.update(batch_size=2)
    _check(loss is not None and np.isfinite(loss), "recurrent DDQN did not produce a finite loss")
    _check(abs(learner.learner.optimizer.param_groups[0]["lr"] - 1e-3) < 1e-15, "optimizer learning rate not wired")

    policy = DistributedHoodiePolicy.configured(
        agent_count=2,
        seed=5,
        use_lstm=True,
        learning_rate=1e-3,
        discount_factor=0.9,
        batch_size=2,
        replay_capacity=8,
        target_update_interval=2,
        device_name="cpu",
        hidden_dims=(16, 16),
        lookback=3,
        lstm_hidden=4,
    )
    exported = policy.export_state()
    restored = DistributedHoodiePolicy.from_state(exported)
    _check(len(restored.agents) == 2, "distributed checkpoint lost learners")
    _check(restored.device_string() == "cpu", "checkpoint device portability failed")
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "checkpoint.pt"
        torch.save(exported, path)
        loaded = torch.load(path, map_location="cpu", weights_only=False)
        roundtrip = DistributedHoodiePolicy.from_state(loaded)
        _check(len(roundtrip.agents) == 2, "serialized checkpoint roundtrip failed")

    source_paths = {
        panel_id: contract.source_contract.get("source_citation")
        for panel_id, contract in PANEL_REGISTRY.items()
    }
    _check(
        all(not str(path).startswith("/") for path in source_paths.values() if path),
        f"absolute source citation leaked through registry: {source_paths}",
    )

    return {
        "status": "passed",
        "matrix": counts,
        "contract_rows_checked": len(rows),
        "topologies": topology_metrics,
        "trace_tasks": len(trace.tasks),
        "finite_recurrent_loss": float(loss),
        "distributed_checkpoint_agents": len(restored.agents),
        "torch_version": torch.__version__,
    }


def main() -> int:
    try:
        print(json.dumps(run_preflight(), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": f"{exc.__class__.__name__}: {exc}"}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
