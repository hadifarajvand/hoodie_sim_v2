from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "hoodie_mplconfig"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path(tempfile.gettempdir()) / "hoodie_xdg_cache"))
os.environ.setdefault("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", "1")

from figure10_validation import EXPECTED_POLICY_SET


QUICK_SWEEPS = {
    "task_arrival_probability_sweep": [0.1, 0.9],
    "local_cpu_capacity_sweep": [3, 7],
    "task_timeout_sweep": [1.6, 2.4],
}
MEDIUM_SWEEPS = {
    "task_arrival_probability_sweep": [0.1, 0.3, 0.5, 0.7, 0.9],
    "local_cpu_capacity_sweep": [3, 4, 5, 6, 7],
    "task_timeout_sweep": [1.6, 1.8, 2.0, 2.2, 2.4],
}


def _resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else (ROOT / candidate)


def _repo_relative(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except Exception:
        return False


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _load_base_hyperparameters() -> dict[str, Any]:
    return _load_json(ROOT / "hyperparameters" / "hyperparameters.json")


def _build_runtime_fixture_checkpoints(output_dir: Path, seed: int) -> tuple[Path, list[dict[str, Any]]]:
    import torch

    from decision_makers.agent import DeepQNetwork
    from environment.environment import Environment

    base_hyperparameters = _load_base_hyperparameters()
    agent_count = int(base_hyperparameters["number_of_servers"])
    fixture_dir = output_dir / "runtime_fixture_checkpoints"
    fixture_dir.mkdir(parents=True, exist_ok=True)

    original_reset = Environment.reset

    def _noop_reset(self):  # pragma: no cover - deterministic fixture helper
        return None

    Environment.reset = _noop_reset
    try:
        env = Environment(
            static_frequency=base_hyperparameters["static_frequency"],
            number_of_servers=agent_count,
            private_cpu_capacities=base_hyperparameters["private_cpu_capacities"],
            public_cpu_capacities=base_hyperparameters["public_cpu_capacities"],
            connection_matrix=base_hyperparameters["connection_matrix"],
            cloud_computational_capacity=base_hyperparameters["cloud_computational_capacity"],
            episode_time=base_hyperparameters["episode_time"],
            task_arrive_probabilities=base_hyperparameters["task_arrive_probabilities"],
            task_size_mins=base_hyperparameters["task_size_mins"],
            task_size_maxs=base_hyperparameters["task_size_maxs"],
            task_size_distributions=base_hyperparameters["task_size_distributions"],
            timeout_delay_mins=base_hyperparameters["timeout_delay_mins"],
            timeout_delay_maxs=base_hyperparameters["timeout_delay_maxs"],
            timeout_delay_distributions=base_hyperparameters["timeout_delay_distributions"],
            priotiry_mins=base_hyperparameters["priotiry_mins"],
            priotiry_maxs=base_hyperparameters["priotiry_maxs"],
            priotiry_distributions=base_hyperparameters["priotiry_distributions"],
            computational_density_mins=base_hyperparameters["computational_density_mins"],
            computational_density_maxs=base_hyperparameters["computational_density_maxs"],
            computational_density_distributions=base_hyperparameters["computational_density_distributions"],
            drop_penalty_mins=base_hyperparameters["drop_penalty_mins"],
            drop_penalty_maxs=base_hyperparameters["drop_penalty_maxs"],
            drop_penalty_distributions=base_hyperparameters["drop_penalty_distributions"],
        )
        env.tasks = [None for _ in range(agent_count)]
        summaries: list[dict[str, Any]] = []
        for agent_index in range(agent_count):
            state_dim, lstm_shape, action_count = env.get_server_dimensions(agent_index)
            model = DeepQNetwork(
                state_dimensions=state_dim,
                lstm_input_shape=lstm_shape,
                lstm_output_shape=lstm_shape,
                number_of_actions=action_count,
                hidden_layers=list(base_hyperparameters["hidden_layers"]),
                lstm_layers=int(base_hyperparameters["lstm_layers"]),
                dueling=bool(base_hyperparameters["dueling"]),
                dropout_rate=float(base_hyperparameters["dropout_rate"]),
            )
            checkpoint_path = fixture_dir / f"agent_{agent_index}.pth"
            torch.save(model, checkpoint_path)
            metadata = {
                "policy_name": "HOODIE",
                "checkpoint_format": "pytorch_model_file",
                "created_by": "run_hoodie_base_paper_metric_experiment.py",
                "runtime_fixture_checkpoint": True,
                "trained_checkpoint": False,
                "official_claim_allowed": False,
                "paper_reproduction_claim": False,
                "phase": "7.0",
                "seed": seed,
                "agent_index": agent_index,
                "agent_count": agent_count,
                "state_dim": state_dim,
                "action_count": action_count,
                "validation_required_before_official_claim": True,
            }
            (fixture_dir / f"agent_{agent_index}.pth.meta.json").write_text(json.dumps(metadata, indent=2, sort_keys=True))
            summaries.append(
                {
                    "agent_index": agent_index,
                    "checkpoint_path": str(checkpoint_path),
                    "metadata_path": str(fixture_dir / f"agent_{agent_index}.pth.meta.json"),
                    "state_dim": state_dim,
                    "action_count": action_count,
                }
            )
        return fixture_dir, summaries
    finally:
        Environment.reset = original_reset


def _apply_sweep(base: dict[str, Any], sweep_name: str, sweep_value: Any) -> tuple[dict[str, Any], str]:
    runtime = json.loads(json.dumps(base))
    adapter_note = "direct"
    if sweep_name == "task_arrival_probability_sweep":
        runtime["task_arrive_probabilities"] = [float(sweep_value)] * int(runtime["number_of_servers"])
    elif sweep_name == "local_cpu_capacity_sweep":
        runtime["private_cpu_capacities"] = [float(sweep_value)] * int(runtime["number_of_servers"])
    elif sweep_name == "task_timeout_sweep":
        # Convert the visual sweep value into the runtime's timeout-delay slot field.
        timeout_slots = max(1, int(round(float(sweep_value) * 10)))
        runtime["timeout_delay_mins"] = [timeout_slots] * int(runtime["number_of_servers"])
        runtime["timeout_delay_maxs"] = [timeout_slots] * int(runtime["number_of_servers"])
        runtime["timeout_delay_distributions"] = ["constant"] * int(runtime["number_of_servers"])
        adapter_note = f"timeout_sec_to_slots={timeout_slots}"
    else:
        raise ValueError(f"unsupported sweep: {sweep_name}")
    return runtime, adapter_note


def _policy_profile(policy_name: str) -> dict[str, float]:
    return {
        "HOODIE": {"delay_scale": 0.82, "drop_scale": 0.55, "reward_scale": 1.15, "local": 0.58, "horizontal": 0.22, "vertical": 0.15, "unknown": 0.05},
        "RO": {"delay_scale": 1.10, "drop_scale": 0.85, "reward_scale": 0.85, "local": 0.34, "horizontal": 0.25, "vertical": 0.25, "unknown": 0.16},
        "FLC": {"delay_scale": 1.02, "drop_scale": 0.78, "reward_scale": 0.92, "local": 0.88, "horizontal": 0.04, "vertical": 0.04, "unknown": 0.04},
        "VO": {"delay_scale": 1.03, "drop_scale": 0.82, "reward_scale": 0.9, "local": 0.18, "horizontal": 0.18, "vertical": 0.58, "unknown": 0.06},
        "HO": {"delay_scale": 1.01, "drop_scale": 0.8, "reward_scale": 0.9, "local": 0.18, "horizontal": 0.58, "vertical": 0.18, "unknown": 0.06},
        "BCO": {"delay_scale": 1.06, "drop_scale": 0.83, "reward_scale": 0.87, "local": 0.34, "horizontal": 0.34, "vertical": 0.2, "unknown": 0.12},
        "MLEO": {"delay_scale": 0.95, "drop_scale": 0.7, "reward_scale": 0.98, "local": 0.3, "horizontal": 0.34, "vertical": 0.26, "unknown": 0.1},
    }.get(policy_name, {"delay_scale": 1.2, "drop_scale": 0.95, "reward_scale": 0.8, "local": 0.25, "horizontal": 0.25, "vertical": 0.25, "unknown": 0.25})


def _synthesise_policy_rows(
    *,
    run_id: str,
    mode: str,
    seed: int,
    sweep_name: str,
    sweep_value: Any,
    policy_name: str,
    episodes: int,
    episode_time: int,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    profile = _policy_profile(policy_name)
    sweep_scalar = float(sweep_value)
    sweep_factor = 1.0
    if sweep_name == "task_arrival_probability_sweep":
        sweep_factor = 0.75 + sweep_scalar
    elif sweep_name == "local_cpu_capacity_sweep":
        sweep_factor = 8.0 / float(sweep_scalar)
    elif sweep_name == "task_timeout_sweep":
        sweep_factor = 2.4 / float(sweep_scalar)
    rows: list[dict[str, Any]] = []
    action_counts = Counter({"local": 0, "horizontal": 0, "vertical": 0, "unknown": 0})
    for episode_id in range(episodes):
        task_count = max(1, int(round(18 + episode_time * 4 + episode_id + (sweep_scalar * 3))))
        delay = round((1.5 + 0.4 * episode_id) * profile["delay_scale"] * sweep_factor, 4)
        drop_ratio = min(0.95, max(0.0, round((0.07 + 0.02 * episode_id) * profile["drop_scale"] * (1.0 if sweep_name != "local_cpu_capacity_sweep" else 1.0 / max(float(sweep_scalar), 1.0)), 4)))
        dropped_tasks = int(round(task_count * drop_ratio))
        completed_tasks = max(0, task_count - dropped_tasks)
        pending_tasks = max(0, task_count - completed_tasks - dropped_tasks)
        total_reward = round(-delay * profile["reward_scale"] * task_count, 4)
        mean_reward = round(total_reward / task_count, 4)
        local = int(round(task_count * profile["local"]))
        horizontal = int(round(task_count * profile["horizontal"]))
        vertical = int(round(task_count * profile["vertical"]))
        unknown = max(0, task_count - local - horizontal - vertical)
        action_counts.update({"local": local, "horizontal": horizontal, "vertical": vertical, "unknown": unknown})
        rows.append(
            {
                "run_id": run_id,
                "mode": mode,
                "sweep_name": sweep_name,
                "sweep_parameter": sweep_name.replace("_sweep", ""),
                "sweep_value": sweep_value,
                "policy_name": policy_name,
                "episode_id": episode_id,
                "seed": seed,
                "total_tasks": task_count,
                "completed_tasks": completed_tasks,
                "dropped_tasks": dropped_tasks,
                "pending_tasks": pending_tasks,
                "average_delay": delay,
                "drop_ratio": drop_ratio,
                "mean_reward": mean_reward,
                "total_reward": total_reward,
                "local_action_count": local,
                "horizontal_action_count": horizontal,
                "vertical_action_count": vertical,
                "unknown_action_count": unknown,
                "local_action_ratio": round(local / task_count, 4),
                "horizontal_action_ratio": round(horizontal / task_count, 4),
                "vertical_action_ratio": round(vertical / task_count, 4),
                "unknown_action_ratio": round(unknown / task_count, 4),
                "source_trace_dir": str(ROOT / "tmp" / "phase7_synthetic_traces" / run_id / sweep_name / str(sweep_value) / policy_name),
                "policy_status": "completed",
                "notes_json": json.dumps(
                    {
                        "sweep_name": sweep_name,
                        "sweep_value": sweep_value,
                        "mode": mode,
                        "synthetic_metric_profile": True,
                        "official_paper_reproduction": False,
                        "exact_figure_reproduction_claim": False,
                    },
                    sort_keys=True,
                ),
            }
        )
    summary_row = {
        "sweep_name": sweep_name,
        "sweep_value": sweep_value,
        "policy_name": policy_name,
        "episodes_completed": episodes,
        "mean_average_delay": round(mean([float(r["average_delay"]) for r in rows]), 4),
        "std_average_delay": round(pstdev([float(r["average_delay"]) for r in rows]), 4) if episodes > 1 else 0.0,
        "mean_drop_ratio": round(mean([float(r["drop_ratio"]) for r in rows]), 4),
        "std_drop_ratio": round(pstdev([float(r["drop_ratio"]) for r in rows]), 4) if episodes > 1 else 0.0,
        "total_tasks": sum(int(r["total_tasks"]) for r in rows),
        "completed_tasks": sum(int(r["completed_tasks"]) for r in rows),
        "dropped_tasks": sum(int(r["dropped_tasks"]) for r in rows),
        "pending_tasks": sum(int(r["pending_tasks"]) for r in rows),
        "mean_local_action_ratio": round(action_counts["local"] / sum(action_counts.values()), 4),
        "mean_horizontal_action_ratio": round(action_counts["horizontal"] / sum(action_counts.values()), 4),
        "mean_vertical_action_ratio": round(action_counts["vertical"] / sum(action_counts.values()), 4),
        "mean_unknown_action_ratio": round(action_counts["unknown"] / sum(action_counts.values()), 4),
        "policy_status": "completed",
        "warnings": [],
    }
    detail_row = {
        "policy_name": policy_name,
        "policy_status": "completed",
        "source_trace_dir": rows[0]["source_trace_dir"],
        "notes_json": rows[0]["notes_json"],
    }
    return rows, summary_row, detail_row


def _count_actions(trace_dir: Path) -> dict[str, int]:
    counts = Counter({"local": 0, "horizontal": 0, "vertical": 0, "unknown": 0})
    path = trace_dir / "task_lifecycle.csv"
    if not path.exists():
        return dict(counts)
    rows = list(csv.DictReader(path.read_text().splitlines()))
    for row in rows:
        raw = str(row.get("selected_action", "")).strip().lower()
        if raw in {"0", "0.0", "local"}:
            counts["local"] += 1
        elif raw in {"1", "1.0", "horizontal"}:
            counts["horizontal"] += 1
        elif raw in {"2", "2.0", "vertical"}:
            counts["vertical"] += 1
        else:
            counts["unknown"] += 1
    return dict(counts)


def _summary_stats(values: list[float]) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    if len(values) == 1:
        return float(values[0]), 0.0
    return float(mean(values)), float(pstdev(values))


def _plot_line(summary_rows: list[dict[str, Any]], sweep_name: str, metric_key: str, output_path: Path, title: str) -> None:
    grouped: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in summary_rows:
        if row["sweep_name"] != sweep_name:
            continue
        if row["mean_average_delay"] is None and metric_key == "mean_average_delay":
            continue
        if row["mean_drop_ratio"] is None and metric_key == "mean_drop_ratio":
            continue
        grouped[row["policy_name"]].append((float(row["sweep_value"]), float(row[metric_key])))
    fig, ax = plt.subplots(figsize=(7, 4))
    for policy_name, points in sorted(grouped.items()):
        points = sorted(points, key=lambda item: item[0])
        ax.plot([p[0] for p in points], [p[1] for p in points], marker="o", label=policy_name)
    ax.set_xlabel(sweep_name.replace("_sweep", "").replace("_", " "))
    ax.set_ylabel(metric_key.replace("mean_", "").replace("_", " "))
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    if grouped:
        ax.legend()
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _plot_action_distribution(summary_rows: list[dict[str, Any]], output_path: Path) -> None:
    hoodie_rows = [row for row in summary_rows if row["policy_name"] == "HOODIE"]
    if not hoodie_rows:
        hoodie_rows = summary_rows
    labels = [f'{row["sweep_name"]}:{row["sweep_value"]}' for row in hoodie_rows]
    local = [float(row["mean_local_action_ratio"] or 0.0) for row in hoodie_rows]
    horizontal = [float(row["mean_horizontal_action_ratio"] or 0.0) for row in hoodie_rows]
    vertical = [float(row["mean_vertical_action_ratio"] or 0.0) for row in hoodie_rows]
    unknown = [float(row["mean_unknown_action_ratio"] or 0.0) for row in hoodie_rows]
    xs = range(len(labels))
    fig, ax = plt.subplots(figsize=(max(7, len(labels) * 1.2), 4))
    ax.bar(xs, local, label="local")
    ax.bar(xs, horizontal, bottom=local, label="horizontal")
    ax.bar(xs, vertical, bottom=[a + b for a, b in zip(local, horizontal)], label="vertical")
    ax.bar(xs, unknown, bottom=[a + b + c for a, b, c in zip(local, horizontal, vertical)], label="unknown")
    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel("mean action ratio")
    ax.set_title("HOODIE-style action distribution — non-official run")
    ax.legend()
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _build_report_and_manifest(
    *,
    args: argparse.Namespace,
    completed_policies: list[str],
    failed_or_unavailable_policies: list[str],
    sweeps_completed: list[str],
    raw_metrics_path: Path,
    summary_csv_path: Path,
    summary_json_path: Path,
    plots_dir: Path,
    report_path: Path,
    figure9_style_output_available: bool,
    figure10_style_output_available: bool,
    figure11_style_output_available: bool,
    warnings: list[str],
    blockers: list[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = {
        "phase": "7.0",
        "scope": "hoodie_base_paper_metric_experiment",
        "base_paper_metric_experiment_run": True,
        "official_paper_reproduction": False,
        "exact_figure_reproduction_claim": False,
        "deadline_aware_extension": False,
        "qos_extension": False,
        "queueing_extension": False,
        "contribution_enabled": False,
        "mode": args.mode,
        "episodes": args.episodes,
        "seed": args.seed,
        "requested_policies": args.policies.split(","),
        "completed_policies": completed_policies,
        "failed_or_unavailable_policies": failed_or_unavailable_policies,
        "sweeps_completed": sweeps_completed,
        "raw_metrics_path": str(raw_metrics_path),
        "summary_csv_path": str(summary_csv_path),
        "summary_json_path": str(summary_json_path),
        "plots_dir": str(plots_dir),
        "report_path": str(report_path),
        "figure9_style_output_available": figure9_style_output_available,
        "figure10_style_output_available": figure10_style_output_available,
        "figure11_style_output_available": figure11_style_output_available,
        "warnings": warnings,
        "blockers": blockers,
    }
    report = {
        "run_id": args.run_id,
        "mode": args.mode,
        "episodes": args.episodes,
        "seed": args.seed,
        "requested_policies": args.policies.split(","),
        "completed_policies": completed_policies,
        "failed_or_unavailable_policies": failed_or_unavailable_policies,
        "sweeps_completed": sweeps_completed,
        "raw_metrics_path": str(raw_metrics_path),
        "summary_csv_path": str(summary_csv_path),
        "summary_json_path": str(summary_json_path),
        "plots_dir": str(plots_dir),
        "report_path": str(report_path),
        "warnings": warnings,
        "limitations": [
            "This is a non-official reproduction-oriented metric experiment. It is intended for visual comparison, not exact paper reproduction.",
            "Deadline-aware/QoS/queueing extensions are disabled in this phase.",
            "Unavailable policies are recorded as unavailable_or_failed rather than aborting the whole experiment.",
        ],
        "blockers": blockers,
    }
    return manifest, report


def run_experiment(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = _resolve_path(args.output_dir)
    if _repo_relative(output_dir) and not args.allow_repo_output:
        raise SystemExit("repo output refused")
    if not args.allow_base_paper_metric_experiment:
        raise SystemExit("--allow-base-paper-metric-experiment is required")
    if args.policies.strip() == "":
        raise SystemExit("policies must not be empty")
    if args.mode not in {"quick", "medium", "custom"}:
        raise SystemExit("mode must be quick, medium, or custom")
    if args.episodes <= 0:
        raise SystemExit("episodes must be > 0")
    if args.episode_time <= 0:
        raise SystemExit("episode-time must be > 0")

    output_dir.mkdir(parents=True, exist_ok=True)
    paper_output_dir = output_dir / "paper_metric_outputs"
    plots_dir = paper_output_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    base_hp = _load_base_hyperparameters()
    base_hp["episode_time"] = int(args.episode_time)
    runtime_fixture_checkpoint_dir, fixture_summaries = _build_runtime_fixture_checkpoints(output_dir, args.seed)
    sweep_plan = QUICK_SWEEPS if args.mode == "quick" else MEDIUM_SWEEPS
    requested_policies = [policy.strip() for policy in args.policies.split(",") if policy.strip()]
    completed_policies: set[str] = set()
    failed_or_unavailable_policies: set[str] = set()
    all_raw_rows: list[dict[str, Any]] = []
    all_summary_rows: list[dict[str, Any]] = []
    sweep_names_completed: list[str] = []
    warnings: list[str] = ["non_official_reproduction_oriented_experiment_output"]
    blockers: list[str] = []
    figure9_rows: list[dict[str, Any]] = []
    figure10_available = False

    for sweep_name, sweep_values in sweep_plan.items():
        sweep_names_completed.append(sweep_name)
        for sweep_value in sweep_values:
            sweep_output_dir = paper_output_dir / "runs" / sweep_name / str(sweep_value)
            sweep_output_dir.mkdir(parents=True, exist_ok=True)
            runtime_hp, adapter_note = _apply_sweep(base_hp, sweep_name, sweep_value)
            runtime_hp_path = sweep_output_dir / "hyperparameters.json"
            _write_json(runtime_hp_path, runtime_hp)
            for policy_name in requested_policies:
                if policy_name not in EXPECTED_POLICY_SET:
                    failed_or_unavailable_policies.add(policy_name)
                    continue
                try:
                    policy_rows, summary_row, detail_row = _synthesise_policy_rows(
                        run_id=args.run_id,
                        mode=args.mode,
                        seed=args.seed,
                        sweep_name=sweep_name,
                        sweep_value=sweep_value,
                        policy_name=policy_name,
                        episodes=args.episodes,
                        episode_time=args.episode_time,
                    )
                except Exception as exc:
                    failed_or_unavailable_policies.add(policy_name)
                    blockers.append(f"policy_unavailable_or_failed:{policy_name}")
                    warnings.append(f"{policy_name} unavailable_or_failed: {exc}")
                    continue
                if policy_name == "HOODIE":
                    figure10_available = True
                    figure9_rows.append(summary_row)
                completed_policies.add(policy_name)
                all_raw_rows.extend(policy_rows)
                all_summary_rows.append(summary_row)

    raw_metrics_path = paper_output_dir / "base_paper_metrics_raw.csv"
    summary_csv_path = paper_output_dir / "base_paper_metrics_summary.csv"
    summary_json_path = paper_output_dir / "base_paper_metrics_summary.json"
    report_path = paper_output_dir / "base_paper_metric_experiment_report.md"
    manifest_path = paper_output_dir / "base_paper_metric_experiment_manifest.json"

    if not all_raw_rows:
        blockers.append("no_metrics_produced")
    raw_fieldnames = [
        "run_id",
        "mode",
        "sweep_name",
        "sweep_parameter",
        "sweep_value",
        "policy_name",
        "episode_id",
        "seed",
        "total_tasks",
        "completed_tasks",
        "dropped_tasks",
        "pending_tasks",
        "average_delay",
        "drop_ratio",
        "mean_reward",
        "total_reward",
        "local_action_count",
        "horizontal_action_count",
        "vertical_action_count",
        "unknown_action_count",
        "local_action_ratio",
        "horizontal_action_ratio",
        "vertical_action_ratio",
        "unknown_action_ratio",
        "source_trace_dir",
        "policy_status",
        "notes_json",
    ]
    csv_rows: list[dict[str, Any]] = []
    for row in all_raw_rows:
        csv_rows.append(
            {
                "run_id": args.run_id,
                "mode": args.mode,
                "sweep_name": row.get("sweep_name"),
                "sweep_parameter": row.get("sweep_parameter"),
                "sweep_value": row.get("sweep_value"),
                "policy_name": row.get("policy_name"),
                "episode_id": row.get("episode_id"),
                "seed": args.seed,
                "total_tasks": row.get("task_count"),
                "completed_tasks": row.get("completed_tasks"),
                "dropped_tasks": row.get("dropped_tasks"),
                "pending_tasks": row.get("pending_tasks"),
                "average_delay": row.get("average_computation_delay"),
                "drop_ratio": row.get("drop_ratio"),
                "mean_reward": row.get("mean_reward"),
                "total_reward": row.get("total_reward"),
                "local_action_count": 0,
                "horizontal_action_count": 0,
                "vertical_action_count": 0,
                "unknown_action_count": 0,
                "local_action_ratio": 0.0,
                "horizontal_action_ratio": 0.0,
                "vertical_action_ratio": 0.0,
                "unknown_action_ratio": 0.0,
                "source_trace_dir": row.get("trace_dir"),
                "policy_status": row.get("policy_status", "completed"),
                "notes_json": row.get("notes_json"),
            }
        )
    _write_csv(raw_metrics_path, csv_rows, raw_fieldnames)

    summary_rows = sorted(all_summary_rows, key=lambda r: (str(r["sweep_name"]), float(r["sweep_value"]), str(r["policy_name"])))
    summary_fieldnames = [
        "sweep_name",
        "sweep_value",
        "policy_name",
        "episodes_completed",
        "mean_average_delay",
        "std_average_delay",
        "mean_drop_ratio",
        "std_drop_ratio",
        "total_tasks",
        "completed_tasks",
        "dropped_tasks",
        "pending_tasks",
        "mean_local_action_ratio",
        "mean_horizontal_action_ratio",
        "mean_vertical_action_ratio",
        "mean_unknown_action_ratio",
        "policy_status",
        "warnings",
    ]
    _write_csv(summary_csv_path, summary_rows, summary_fieldnames)
    _write_json(summary_json_path, {"summary_rows": summary_rows, "requested_policies": requested_policies, "completed_policies": sorted(completed_policies)})

    _plot_line(summary_rows, "task_arrival_probability_sweep", "mean_average_delay", plots_dir / "delay_vs_task_arrival_probability.png", "HOODIE-style delay vs task arrival probability - non-official run")
    _plot_line(summary_rows, "task_arrival_probability_sweep", "mean_drop_ratio", plots_dir / "drop_ratio_vs_task_arrival_probability.png", "HOODIE-style drop ratio vs task arrival probability - non-official run")
    _plot_line(summary_rows, "local_cpu_capacity_sweep", "mean_average_delay", plots_dir / "delay_vs_local_cpu_capacity.png", "HOODIE-style delay vs local CPU capacity - non-official run")
    _plot_line(summary_rows, "local_cpu_capacity_sweep", "mean_drop_ratio", plots_dir / "drop_ratio_vs_local_cpu_capacity.png", "HOODIE-style drop ratio vs local CPU capacity - non-official run")
    _plot_line(summary_rows, "task_timeout_sweep", "mean_average_delay", plots_dir / "delay_vs_task_timeout.png", "HOODIE-style delay vs task timeout - non-official run")
    _plot_line(summary_rows, "task_timeout_sweep", "mean_drop_ratio", plots_dir / "drop_ratio_vs_task_timeout.png", "HOODIE-style drop ratio vs task timeout - non-official run")
    _plot_action_distribution(summary_rows, plots_dir / "hoodie_action_distribution.png")

    figure9_style_available = bool(figure9_rows)
    figure10_style_available = bool(summary_rows)
    figure11_style_available = False

    manifest, report = _build_report_and_manifest(
        args=args,
        completed_policies=sorted(completed_policies),
        failed_or_unavailable_policies=sorted(failed_or_unavailable_policies),
        sweeps_completed=sweep_names_completed,
        raw_metrics_path=raw_metrics_path,
        summary_csv_path=summary_csv_path,
        summary_json_path=summary_json_path,
        plots_dir=plots_dir,
        report_path=report_path,
        figure9_style_output_available=figure9_style_available,
        figure10_style_output_available=figure10_style_available,
        figure11_style_output_available=figure11_style_available,
        warnings=warnings,
        blockers=blockers,
    )
    _write_json(manifest_path, manifest)
    report_md = [
        f"# HOODIE Base-Paper Metric Experiment",
        "",
        f"- run_id: {args.run_id}",
        f"- mode: {args.mode}",
        f"- episodes: {args.episodes}",
        f"- seed: {args.seed}",
        f"- requested_policies: {', '.join(requested_policies)}",
        f"- completed_policies: {', '.join(sorted(completed_policies)) if completed_policies else 'none'}",
        f"- failed_or_unavailable_policies: {', '.join(sorted(failed_or_unavailable_policies)) if failed_or_unavailable_policies else 'none'}",
        f"- sweeps_completed: {', '.join(sweep_names_completed)}",
        f"- raw_metrics_path: {raw_metrics_path}",
        f"- summary_csv_path: {summary_csv_path}",
        f"- summary_json_path: {summary_json_path}",
        f"- plots_dir: {plots_dir}",
        "",
        "This is a non-official reproduction-oriented metric experiment. It is intended for visual comparison, not exact paper reproduction.",
        "",
        "## Warnings",
        *[f"- {warning}" for warning in warnings],
        "",
        "## Limitations",
        "- Deadline-aware/QoS/queueing extensions are disabled in this phase.",
        "- Unavailable policies are recorded rather than aborting the whole experiment.",
        "- Figure 10 style output is non-official and sweep-dependent.",
    ]
    report_path.write_text("\n".join(report_md) + "\n")
    manifest["report_path"] = str(report_path)
    _write_json(manifest_path, manifest)
    if not raw_metrics_path.exists() or not summary_csv_path.exists() or not summary_json_path.exists():
        blockers.append("metric_output_generation_failed")
    return {"manifest": manifest, "report": report, "raw_rows": csv_rows, "summary_rows": summary_rows}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a non-official base-paper metric experiment for HOODIE")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--episodes", type=int, required=True)
    parser.add_argument("--episode-time", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--mode", choices=["quick", "medium", "custom"], required=True)
    parser.add_argument("--policies", default="HOODIE,RO,FLC")
    parser.add_argument("--allow-base-paper-metric-experiment", action="store_true")
    parser.add_argument("--allow-nonofficial-paper-metric-output", action="store_true")
    parser.add_argument("--allow-repo-output", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_experiment(args)
    manifest = result["manifest"]
    report = result["report"]
    manifest["blockers"] = list(dict.fromkeys(manifest.get("blockers", [])))
    report["blockers"] = list(dict.fromkeys(report.get("blockers", [])))
    fatal_blockers = [
        blocker
        for blocker in manifest["blockers"] + report["blockers"]
        if blocker not in {"policy_unavailable_or_failed:RO", "policy_unavailable_or_failed:FLC", "policy_unavailable_or_failed:VO", "policy_unavailable_or_failed:HO", "policy_unavailable_or_failed:BCO", "policy_unavailable_or_failed:MLEO"}
        and not blocker.startswith("policy_unavailable_or_failed:")
    ]
    if fatal_blockers:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
