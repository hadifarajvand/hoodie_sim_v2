#!/usr/bin/env python3
"""Bounded executable smoke for the current HOODIE runtime surface.

This is deliberately not a paper-scale experiment. It verifies that the
editable-install package is complete, the production executor imports, a real
recurrent DDQN update runs, and the corrected matrix/dependency contract is
materialized as 17 training plus 288 evaluation jobs.
"""

from __future__ import annotations

from dataclasses import asdict
import json
import math
from pathlib import Path
import tempfile

import numpy as np
import torch


def _runtime_import_smoke() -> dict[str, str]:
    import hoodie  # noqa: F401
    import hoodie.experiments  # noqa: F401
    import src.agents.hoodie_agent  # noqa: F401
    import src.environment.topology  # noqa: F401
    import src.evaluation.runner  # noqa: F401
    import src.hoodie.experiments.cli  # noqa: F401
    import src.hoodie.experiments.production_campaign  # noqa: F401
    import src.policies.policy_interface  # noqa: F401
    import src.training.seed_management  # noqa: F401

    return {
        "public_package": "hoodie",
        "runtime_package": "src",
        "production_executor": "src.hoodie.experiments.production_campaign",
        "status": "ok",
    }


def _learner_smoke() -> dict[str, object]:
    from src.agents.recurrent_ddqn import RecurrentDoubleDQNAgent

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
    if loss is None or not math.isfinite(float(loss)):
        raise AssertionError(f"real learner update did not produce a finite loss: {loss!r}")
    if learner.learner.optimizer.param_groups[0]["lr"] != 1e-3:
        raise AssertionError("optimizer does not use the configured learning rate")

    window = torch.ones((1, 3, 5), dtype=torch.float32)
    learner.learner.online_network.eval()
    with torch.no_grad():
        first = learner.learner.online_network(window)
        second = learner.learner.online_network(window)
    if not torch.allclose(first, second):
        raise AssertionError("LSTM forward leaked hidden state between calls")

    return {
        "loss": float(loss),
        "learning_rate": learner.learner.optimizer.param_groups[0]["lr"],
        "training_steps": learner.learner.training_steps,
        "target_update_steps": learner.learner.target_update_steps,
        "device": str(learner.learner.device),
        "deterministic_forward": True,
    }


def _matrix_smoke(output_root: Path) -> dict[str, object]:
    from src.hoodie.experiments.matrix_patch import install_matrix_patch

    install_matrix_patch()
    from src.hoodie.experiments import job_matrix
    from src.hoodie.experiments.distributed_v2 import build_shard_plan

    campaign_id = "figures-8-11-corrected-smoke"
    rows = job_matrix.build_production_job_matrix(campaign_id)
    counts = job_matrix.validate_production_job_matrix(rows)
    payload = [asdict(row) for row in rows]

    training = [row for row in payload if row["job_type"] == "training"]
    evaluation = [row for row in payload if row["job_type"] == "evaluation"]
    if (len(training), len(evaluation), len(payload)) != (17, 288, 305):
        raise AssertionError(
            f"corrected matrix count mismatch: {len(training)}/{len(evaluation)}/{len(payload)}"
        )
    if not all(
        row["physical_contract"].get("backend") == "worker-selected"
        for row in payload
    ):
        raise AssertionError("matrix contains a non worker-selected backend")

    training_ids = {row["job_id"] for row in training}
    for row in evaluation:
        dependency = row.get("checkpoint_dependency")
        if row["policy"] == "HOODIE" and dependency not in training_ids:
            raise AssertionError(
                f"HOODIE evaluation has invalid checkpoint dependency: {row['job_id']} -> {dependency}"
            )
        if row["policy"] != "HOODIE" and dependency is not None:
            raise AssertionError(
                f"baseline evaluation unexpectedly depends on a checkpoint: {row['job_id']}"
            )

    matrix_path = output_root / "smoke-matrix.json"
    matrix_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    plan = build_shard_plan(
        campaign_id,
        training_shards=17,
        evaluation_shards=48,
        matrix_path=matrix_path,
    )
    if plan["total_jobs"] != 305:
        raise AssertionError(plan)
    if plan["training_jobs"] != 17 or plan["evaluation_jobs"] != 288:
        raise AssertionError(plan)

    return {
        **counts,
        "training_shards": 17,
        "evaluation_shards": 48,
        "plan_hash": plan["plan_hash"],
        "worker_selected_backend": True,
        "checkpoint_dependencies_valid": True,
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hoodie-runtime-smoke-") as temp_dir:
        output_root = Path(temp_dir)
        result = {
            "smoke_kind": "bounded-runtime-import-learner-matrix",
            "paper_scale_started": False,
            "imports": _runtime_import_smoke(),
            "learner": _learner_smoke(),
            "matrix": _matrix_smoke(output_root),
            "status": "HOODIE_RUNTIME_SMOKE_PASSED",
        }
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
