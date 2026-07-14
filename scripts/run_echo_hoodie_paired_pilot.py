#!/usr/bin/env python3
"""Run a bounded, paired ECHO-versus-HOODIE pilot on the shared simulator.

This runner produces real simulator measurements.  It deliberately does not use
or transform digitized article curves.  The pilot is an execution and mechanism
validation gate, not publication-grade evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from pathlib import Path
from typing import Any

import torch

from src.agents.hoodie_agent import HoodieAgent
from src.config.training_config import TrainingConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.evaluation.config import EvaluationConfig
from src.evaluation.runner import EvaluationRunner
from src.training.seed_management import SeedManagement
from src.training.training_loop import TrainingLoop

METHODS = ("ECHO", "HOODIE")


def _dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )


def _training_config(
    method: str,
    *,
    episodes: int,
    episode_length: int,
    drain_slots: int,
    seed: int,
    output_dir: Path,
) -> TrainingConfig:
    return TrainingConfig(
        learning_rate=7e-7,
        batch_size=64,
        replay_buffer_capacity=10_000,
        target_network_update_frequency=2_000,
        episode_count=episodes,
        episode_length=episode_length,
        discount_factor=0.99,
        drain_slots=drain_slots,
        seed_management=SeedManagement(
            training_seed=seed,
            evaluation_seed=seed,
        ),
        policy_name=method,
        trace_id="paired-pilot-train",
        trace_mode="deterministic_seed",
        device="cpu",
        replay_seed=seed + 17,
        torch_seed=seed + 29,
        output_dir=output_dir / "training" / method.lower(),
    )


def _evaluation_config(
    method: str,
    *,
    episodes: int,
    episode_length: int,
    drain_slots: int,
    seed: int,
    output_dir: Path,
) -> EvaluationConfig:
    return EvaluationConfig(
        policy_name=method,
        seed=seed,
        trace_id="paired-pilot-heldout",
        episode_count=episodes,
        episode_length=episode_length,
        drain_slots=drain_slots,
        trace_mode="deterministic_seed",
        device="cpu",
        output_dir=output_dir / "evaluation" / method.lower(),
    )


def _validate_accounting(result: dict[str, Any]) -> None:
    for trace in result["per_trace"]:
        completed = int(trace["completed_tasks"])
        dropped = int(trace["dropped_tasks"])
        total = int(trace["total_tasks"])
        if completed + dropped != total:
            raise RuntimeError(
                "task accounting failed for "
                f"{trace['policy_name']}:{trace['trace_id']}: "
                f"{completed}+{dropped}!={total}"
            )
        for record in trace.get("raw_records", []):
            if record.get("terminal_outcome") not in {"completed", "dropped"}:
                raise RuntimeError(
                    f"unresolved task in {trace['policy_name']}:{trace['trace_id']}"
                )
            if not record.get("selected_action"):
                raise RuntimeError(
                    f"missing selected action in {trace['policy_name']}:{trace['trace_id']}"
                )


def _trace_key(trace: dict[str, Any]) -> tuple[str, int]:
    return str(trace["trace_id"]), int(trace["seed"])


def _paired_rows(results: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    by_method = {
        method: {_trace_key(trace): trace for trace in result["per_trace"]}
        for method, result in results.items()
    }
    echo_keys = set(by_method["ECHO"])
    hoodie_keys = set(by_method["HOODIE"])
    if echo_keys != hoodie_keys:
        raise RuntimeError(
            "paired-trace contract failed: ECHO and HOODIE trace/seed sets differ"
        )

    rows: list[dict[str, Any]] = []
    for trace_id, seed in sorted(echo_keys):
        echo = by_method["ECHO"][(trace_id, seed)]
        hoodie = by_method["HOODIE"][(trace_id, seed)]
        rows.append(
            {
                "trace_id": trace_id,
                "seed": seed,
                "echo_total_tasks": int(echo["total_tasks"]),
                "hoodie_total_tasks": int(hoodie["total_tasks"]),
                "echo_completed_tasks": int(echo["completed_tasks"]),
                "hoodie_completed_tasks": int(hoodie["completed_tasks"]),
                "echo_dropped_tasks": int(echo["dropped_tasks"]),
                "hoodie_dropped_tasks": int(hoodie["dropped_tasks"]),
                "echo_drop_ratio": float(echo["drop_ratio"]),
                "hoodie_drop_ratio": float(hoodie["drop_ratio"]),
                "echo_average_delay_slots": float(echo["average_delay"]),
                "hoodie_average_delay_slots": float(hoodie["average_delay"]),
                "drop_ratio_difference_echo_minus_hoodie": (
                    float(echo["drop_ratio"]) - float(hoodie["drop_ratio"])
                ),
                "delay_difference_echo_minus_hoodie_slots": (
                    float(echo["average_delay"]) - float(hoodie["average_delay"])
                ),
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"refusing to write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_pilot(
    *,
    output_dir: Path,
    train_episodes: int,
    evaluation_episodes: int,
    episode_length: int,
    drain_slots: int,
    training_seed: int,
    evaluation_seed: int,
    arrival_probability: float,
    timeout_slots: int,
) -> dict[str, Any]:
    if train_episodes <= 0 or evaluation_episodes <= 0:
        raise ValueError("episode counts must be positive")
    if episode_length <= drain_slots:
        raise ValueError("episode_length must be greater than drain_slots")

    output_dir.mkdir(parents=True, exist_ok=True)
    topology = TopologyGraph.from_approved_assumption_registry()
    runtime = SharedRuntimeParameters(
        arrival_probability=arrival_probability,
        agent_count=20,
        timeout_slots=timeout_slots,
    )

    results: dict[str, dict[str, Any]] = {}
    training_summaries: dict[str, list[dict[str, Any]]] = {}
    elapsed_seconds: dict[str, float] = {}

    for method in METHODS:
        random.seed(training_seed)
        torch.manual_seed(training_seed)
        agent = HoodieAgent(policy_name=method)
        train_config = _training_config(
            method,
            episodes=train_episodes,
            episode_length=episode_length,
            drain_slots=drain_slots,
            seed=training_seed,
            output_dir=output_dir,
        )
        started = time.perf_counter()
        summaries = TrainingLoop(
            policy=agent,
            config=train_config,
            topology=topology,
            runtime_parameters=runtime,
        ).run()
        elapsed_seconds[f"{method.lower()}_training"] = time.perf_counter() - started
        training_summaries[method] = [
            {
                "episode_index": summary.episode_index,
                "trace_id": summary.trace_id,
                "transitions_recorded": summary.transitions_recorded,
                "replay_buffer_size": summary.replay_buffer_size,
            }
            for summary in summaries
        ]

        evaluation = EvaluationRunner(
            policy=agent,
            config=_evaluation_config(
                method,
                episodes=evaluation_episodes,
                episode_length=episode_length,
                drain_slots=drain_slots,
                seed=evaluation_seed,
                output_dir=output_dir,
            ),
            topology=topology,
            runtime_parameters=runtime,
        )
        started = time.perf_counter()
        result = evaluation.run()
        elapsed_seconds[f"{method.lower()}_evaluation"] = (
            time.perf_counter() - started
        )
        _validate_accounting(result)
        results[method] = result
        _dump_json(output_dir / "raw" / f"{method.lower()}_result.json", result)

    paired_rows = _paired_rows(results)
    _write_csv(output_dir / "paired_trace_metrics.csv", paired_rows)

    summary_rows = []
    for method in METHODS:
        aggregate = results[method]["aggregate"]
        summary_rows.append(
            {
                "method": method,
                "average_delay_slots": float(aggregate["average_delay"]),
                "drop_ratio": float(aggregate["drop_ratio"]),
                "throughput": int(aggregate["throughput"]),
                "train_episodes": train_episodes,
                "evaluation_episodes": evaluation_episodes,
                "episode_length": episode_length,
                "drain_slots": drain_slots,
                "arrival_probability": arrival_probability,
                "timeout_slots": timeout_slots,
            }
        )
    _write_csv(output_dir / "summary.csv", summary_rows)

    manifest = {
        "scientific_status": "bounded_real_simulator_pilot_not_publication_campaign",
        "digitized_curves_used": False,
        "paired_trace_contract": True,
        "methods": list(METHODS),
        "training_seed": training_seed,
        "evaluation_seed": evaluation_seed,
        "train_eval_seeds_disjoint": training_seed != evaluation_seed,
        "train_episodes": train_episodes,
        "evaluation_episodes": evaluation_episodes,
        "episode_length": episode_length,
        "drain_slots": drain_slots,
        "arrival_probability": arrival_probability,
        "timeout_slots": timeout_slots,
        "topology_nodes": list(topology.node_ids),
        "runtime_parameters": {
            "slot_duration": runtime.slot_duration,
            "local_service_capacity": runtime.local_service_capacity,
            "public_service_capacity": runtime.public_service_capacity,
            "cloud_service_capacity": runtime.cloud_service_capacity,
        },
        "elapsed_seconds": elapsed_seconds,
        "training_summaries": training_summaries,
        "aggregate_results": {
            method: results[method]["aggregate"] for method in METHODS
        },
        "files": [
            "summary.csv",
            "paired_trace_metrics.csv",
            "raw/echo_result.json",
            "raw/hoodie_result.json",
        ],
    }
    _dump_json(output_dir / "pilot_manifest.json", manifest)
    return manifest


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a real paired ECHO-HOODIE simulator pilot."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/analysis/echo-hoodie-paired-pilot"),
    )
    parser.add_argument("--train-episodes", type=int, default=10)
    parser.add_argument("--evaluation-episodes", type=int, default=10)
    parser.add_argument("--episode-length", type=int, default=110)
    parser.add_argument("--drain-slots", type=int, default=10)
    parser.add_argument("--training-seed", type=int, default=431)
    parser.add_argument("--evaluation-seed", type=int, default=743)
    parser.add_argument("--arrival-probability", type=float, default=0.5)
    parser.add_argument("--timeout-slots", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    manifest = run_pilot(
        output_dir=args.output_dir,
        train_episodes=args.train_episodes,
        evaluation_episodes=args.evaluation_episodes,
        episode_length=args.episode_length,
        drain_slots=args.drain_slots,
        training_seed=args.training_seed,
        evaluation_seed=args.evaluation_seed,
        arrival_probability=args.arrival_probability,
        timeout_slots=args.timeout_slots,
    )
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(f"Wrote {args.output_dir / 'pilot_manifest.json'}")
        print(json.dumps(manifest["aggregate_results"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
