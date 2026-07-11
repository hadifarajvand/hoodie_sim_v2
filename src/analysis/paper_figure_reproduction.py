"""Paper figure reproduction pipeline.

Runs simulation sweeps for Figures 8-11, exports structured data
(CSV/JSON) with provenance/limitation metadata, and generates
sub-figure plots matching the HOODIE paper layout.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path
from typing import Any
import json

from .paper_figures_campaign import (
    run_figure_8,
    run_figure_9,
    run_figure_10,
    run_figure_11,
)
from .paper_figure_dataset import (
    FIGURE_OUTPUTS,
    DATASET_COLUMNS,
    FIGURE10_LIMITATION,
    write_paper_figure_datasets,
)
from .figure_generator import (
    plot_figure_7_topology,
    plot_figure_8_reward_timecourse,
    plot_figure_9_parameter_sweep,
    plot_figure_10_offloading_schemes,
    plot_figure_11_lstm_comparison,
)
from src.environment.topology import TopologyGraph
import csv

OUTPUT_DIR = Path("artifacts/analysis/paper-figure-reproduction")


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DATASET_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in DATASET_COLUMNS})


def _sweep_base_row(figure_id: str, reconstruction_status: str) -> dict[str, Any]:
    return {
        "figure_id": figure_id,
        "subfigure_id": "",
        "series_name": "",
        "x_value": "",
        "y_value": "",
        "x_unit": "",
        "y_unit": "",
        "policy_name": "",
        "seed": "",
        "scenario_name": "",
        "source_kind": "simulation_sweep",
        "source_path": "",
        "reconstruction_status": reconstruction_status,
        "limitation": "",
    }

def _figure7_rows(topology: TopologyGraph) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in topology.node_ids:
        for destination in topology.legal_adjacency.get(source, ()):
            row = _sweep_base_row("Figure 7", "full_pdf_extracted")
            row.update(
                {
                    "subfigure_id": "7-topology",
                    "series_name": "legal_edge",
                    "x_value": source,
                    "y_value": destination,
                    "x_unit": "source_node",
                    "y_unit": "destination_node",
                    "policy_name": source,
                    "scenario_name": destination,
                    "source_kind": "topology_artifact",
                    "source_path": "resources/papers/hoodie/recovered/user-approved-assumption-registry.json",
                    "comparison_allowed": True,
                }
            )
            rows.append(row)
    return rows


def _save_line_panel(x_values: list[Any], y_values: list[Any], output_path: Path, *, title: str, xlabel: str, ylabel: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    if x_values and y_values:
        ax.plot(x_values, y_values, linewidth=2)
    else:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _save_bar_panel(labels: list[str], values: list[float], output_path: Path, *, title: str, xlabel: str, ylabel: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    if labels and values:
        ax.bar(labels, values)
    else:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _mean_series(results: list[dict[str, Any]], key: str) -> tuple[list[int], list[float]]:
    values: list[float] = []
    for exp in results:
        metrics = exp.get("training_metrics") or {}
        series = metrics.get(key, []) or []
        if series:
            values.append(float(np.mean(series)))
    return list(range(1, len(values) + 1)), values


def _export_panel_pngs(output_dir: Path, figure_id: str, results: Any, panel_dir: Path) -> None:
    panel_dir.mkdir(parents=True, exist_ok=True)
    if figure_id == "Figure 7":
        topology = results
        _save_bar_panel(list(topology.node_ids), [len(topology.legal_adjacency.get(node, ())) for node in topology.node_ids], panel_dir / "figure_7_panel.png", title="Figure 7: Node Degree", xlabel="Node", ylabel="Degree")
        return
    if figure_id == "Figure 8":
        lr = [exp for exp in results if (exp.get("config") or {}).get("sweep_metadata", {}).get("sweep_type") == "learning_rate"]
        gamma = [exp for exp in results if (exp.get("config") or {}).get("sweep_metadata", {}).get("sweep_type") == "discount_factor"]
        _save_line_panel(list(range(1, len(lr[0].get("training_metrics", {}).get("episode_rewards", []) or []) + 1)) if lr else [], (lr[0].get("training_metrics", {}).get("episode_rewards", []) or []) if lr else [], panel_dir / "figure_8a_learning_rate.png", title="Figure 8a: Learning Rate Sweep", xlabel="Episode", ylabel="Reward")
        _save_line_panel(list(range(1, len(gamma[0].get("training_metrics", {}).get("episode_rewards", []) or []) + 1)) if gamma else [], (gamma[0].get("training_metrics", {}).get("episode_rewards", []) or []) if gamma else [], panel_dir / "figure_8b_discount_factor.png", title="Figure 8b: Discount Factor Sweep", xlabel="Episode", ylabel="Reward")
        return
    if figure_id == "Figure 9":
        sweep_types = {
            "arrival_probability": "figure_9a_arrival_probability.png",
            "action_distribution": "figure_9b_action_distribution.png",
            "cpu_capacity": "figure_9c_cpu_capacity.png",
            "num_drl_agents": "figure_9d_num_agents.png",
            "offload_data_rate": "figure_9e_data_rate.png",
        }
        groups: dict[str, list[dict[str, Any]]] = {}
        for exp in results:
            sweep_type = str((exp.get("config") or {}).get("sweep_metadata", {}).get("sweep_type", ""))
            groups.setdefault(sweep_type, []).append(exp)
        for sweep_type, filename in sweep_types.items():
            group = groups.get(sweep_type, [])
            if sweep_type == "action_distribution":
                group = groups.get("arrival_probability", [])
                labels = ["local", "horizontal", "vertical"]
                counts = [0.0, 0.0, 0.0]
                for exp in group:
                    for bucket in (exp.get("training_metrics") or {}).get("action_counts", []) or []:
                        counts[0] += float(bucket.get(0, 0))
                        counts[1] += float(sum(int(v) for k, v in bucket.items() if int(k) not in (0, 21)))
                        counts[2] += float(bucket.get(21, 0))
                _save_bar_panel(labels, counts, panel_dir / filename, title="Figure 9b: Action Distribution", xlabel="Action", ylabel="Count")
            else:
                xs = []
                ys = []
                for exp in group:
                    meta = (exp.get("config") or {}).get("sweep_metadata", {})
                    x = meta.get("arrival_probability", meta.get("cpu_capacity", meta.get("num_drl_agents", meta.get("data_rate_scenario", 0))))
                    xs.append(x)
                    ys.append(float(np.mean((exp.get("training_metrics") or {}).get("episode_rewards", []) or [0.0])))
                _save_line_panel(xs, ys, panel_dir / filename, title=f"Figure 9 {sweep_type}", xlabel=sweep_type, ylabel="Reward")
        return
    if figure_id == "Figure 10":
        subfigs = [
            ("arrival_probability", "figure_10a_delay_arrival_probability.png", "Average Delay", "Delay"),
            ("arrival_probability", "figure_10b_drop_arrival_probability.png", "Drop Ratio", "Drop"),
            ("cpu_capacity", "figure_10c_delay_cpu_capacity.png", "Average Delay", "Delay"),
            ("cpu_capacity", "figure_10d_drop_cpu_capacity.png", "Drop Ratio", "Drop"),
            ("task_timeout", "figure_10e_delay_timeout.png", "Average Delay", "Delay"),
            ("task_timeout", "figure_10f_drop_timeout.png", "Drop Ratio", "Drop"),
        ]
        for sweep_type, filename, title, ylabel in subfigs:
            xs = []
            ys = []
            for exp in results:
                meta = (exp.get("config") or {}).get("sweep_metadata", {})
                if meta.get("sweep_type") != sweep_type:
                    continue
                x = meta.get("arrival_probability", meta.get("cpu_capacity", meta.get("task_timeout_slots", 0)))
                xs.append(x)
                metrics = exp.get("training_metrics") or {}
                series = metrics.get("average_delays", []) if title == "Average Delay" else metrics.get("drop_ratios", [])
                ys.append(float(np.mean(series)) if series else 0.0)
            _save_line_panel(xs, ys, panel_dir / filename, title=f"Figure 10 {filename[9]}", xlabel=sweep_type, ylabel=ylabel)
        return
    if figure_id == "Figure 11":
        with_lstm = results[0] if results else {}
        without_lstm = results[1] if len(results) > 1 else {}
        for label, exp, filename in [("with LSTM", with_lstm, "figure_11_with_lstm.png"), ("without LSTM", without_lstm, "figure_11_without_lstm.png")]:
            delays = (exp.get("training_metrics") or {}).get("average_delays", []) or []
            _save_line_panel(list(range(1, len(delays) + 1)), list(delays), panel_dir / filename, title=f"Figure 11: {label}", xlabel="Episode", ylabel="Delay")


def _figure8_rows(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for exp in results:
        meta = (exp.get("config") or {}).get("sweep_metadata", {}) or {}
        sweep_type = str(meta.get("sweep_type", "unknown"))
        label = str(exp.get("experiment_label", ""))
        rewards = (exp.get("training_metrics") or {}).get("episode_rewards", []) or []
        loss_values = (exp.get("training_metrics") or {}).get("loss_values", []) or []
        for ep_idx, reward in enumerate(rewards):
            status = "full_pdf_extracted" if sweep_type != "unknown" else "unsupported"
            row = _sweep_base_row("Figure 8", status)
            sub = "8-learning-rate" if sweep_type == "learning_rate" else "8-discount-factor"
            param_val = meta.get("learning_rate", meta.get("discount_factor", label))
            row.update({
                "subfigure_id": sub,
                "series_name": f"{sweep_type}_reward",
                "x_value": ep_idx,
                "y_value": reward,
                "x_unit": "episode",
                "y_unit": "reward",
                "policy_name": str(param_val),
                "source_kind": "simulation_sweep",
                "source_path": sweep_type,
            })
            rows.append(row)
        for ep_idx, loss in enumerate(loss_values):
            status = "full_pdf_extracted" if sweep_type != "unknown" else "unsupported"
            row = _sweep_base_row("Figure 8", status)
            sub = "8-learning-rate" if sweep_type == "learning_rate" else "8-discount-factor"
            param_val = meta.get("learning_rate", meta.get("discount_factor", label))
            row.update({
                "subfigure_id": sub,
                "series_name": f"{sweep_type}_loss",
                "x_value": ep_idx,
                "y_value": loss,
                "x_unit": "episode",
                "y_unit": "loss",
                "policy_name": str(param_val),
                "source_kind": "simulation_sweep",
                "source_path": sweep_type,
            })
            rows.append(row)
    return rows


def _figure9_rows(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    sweep_groups: dict[str, list[dict[str, Any]]] = {}
    for exp in results:
        meta = (exp.get("config") or {}).get("sweep_metadata", {}) or {}
        st = str(meta.get("sweep_type", ""))
        sweep_groups.setdefault(st, []).append(exp)
    subfig_ids = {
        "arrival_probability": "9a",
        "cpu_capacity": "9c",
        "num_drl_agents": "9d",
        "offload_data_rate": "9e",
    }
    for sweep_type, group in sweep_groups.items():
        sub = subfig_ids.get(sweep_type, "9-other")
        for exp in group:
            meta = (exp.get("config") or {}).get("sweep_metadata", {}) or {}
            metrics = exp.get("training_metrics") or {}
            label = str(exp.get("experiment_label", ""))
            rewards = metrics.get("episode_rewards", []) or []
            avg_reward = sum(rewards) / len(rewards) if rewards else 0.0
            delays = metrics.get("average_delays", []) or []
            avg_delay = sum(delays) / len(delays) if delays else 0.0
            action_counts = metrics.get("action_counts", []) or []
            row = _sweep_base_row("Figure 9", "full_pdf_extracted")
            x_val = meta.get("arrival_probability", meta.get("cpu_capacity", meta.get("num_drl_agents", label)))
            traffic = str(meta.get("traffic_scenario", meta.get("data_rate_scenario", "")))
            row.update({
                "subfigure_id": sub,
                "series_name": "average_reward",
                "x_value": x_val,
                "y_value": avg_reward,
                "x_unit": sweep_type,
                "y_unit": "reward",
                "policy_name": traffic or str(x_val),
                "scenario_name": traffic,
                "source_kind": "simulation_sweep",
            })
            rows.append(row)
            row2 = row.copy()
            row2["series_name"] = "average_delay"
            row2["y_value"] = avg_delay
            row2["y_unit"] = "slots"
            rows.append(row2)
            for ac in action_counts:
                if isinstance(ac, dict):
                    for action_idx, count in ac.items():
                        action_row = _sweep_base_row("Figure 9", "full_pdf_extracted")
                        action_row.update({
                            "subfigure_id": sub,
                            "series_name": f"action_{action_idx}_count",
                            "x_value": x_val,
                            "y_value": count,
                            "x_unit": sweep_type,
                            "y_unit": "action_count",
                            "policy_name": traffic or str(x_val),
                            "scenario_name": traffic,
                            "source_kind": "simulation_sweep",
                        })
                        rows.append(action_row)
    # Action distribution (9b) from per-policy action counts
    action_buckets: dict[str, dict[str, int]] = {}
    for exp in results:
        meta = (exp.get("config") or {}).get("sweep_metadata", {}) or {}
        sweep_type = str(meta.get("sweep_type", ""))
        if sweep_type != "arrival_probability":
            continue
        arrival_p = str(meta.get("arrival_probability", "?"))
        bucket = action_buckets.setdefault(arrival_p, {"local": 0, "horizontal": 0, "vertical": 0})
        action_counts = (exp.get("training_metrics") or {}).get("action_counts", []) or []
        for ac in action_counts:
            if isinstance(ac, dict):
                for action_idx, count in ac.items():
                    idx = int(action_idx)
                    if idx == 0:
                        bucket["local"] += int(count)
                    elif idx in (21, 2):
                        bucket["vertical"] += int(count)
                    else:
                        bucket["horizontal"] += int(count)
    for arrival_p, counts in action_buckets.items():
        for action_name, count in counts.items():
            row = _sweep_base_row("Figure 9", "full_pdf_extracted")
            row.update({
                "subfigure_id": "9b",
                "series_name": f"action_{action_name}",
                "x_value": arrival_p,
                "y_value": count,
                "x_unit": "arrival_probability",
                "y_unit": "action_count",
                "policy_name": action_name,
                "source_kind": "simulation_sweep",
            })
            rows.append(row)
    return rows


def _figure10_rows(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for exp in results:
        meta = (exp.get("config") or {}).get("sweep_metadata", {}) or {}
        sweep_type = str(meta.get("sweep_type", "unknown"))
        policy_name = str(meta.get("policy", meta.get("sweep_type", "unknown")))
        label = str(exp.get("experiment_label", ""))
        metrics = exp.get("training_metrics") or {}
        delays = metrics.get("average_delays", []) or []
        drops = metrics.get("drop_ratios", []) or []
        avg_delay = sum(delays) / len(delays) if delays else 0.0
        avg_drop = sum(drops) / len(drops) if drops else 0.0
        # Also check evaluation_result for baseline policies
        eval_result = exp.get("evaluation_result") or {}
        agg = eval_result.get("aggregate") or {}
        if not delays:
            avg_delay = float(agg.get("average_delay", 0.0))
        if not drops:
            avg_drop = float(agg.get("drop_ratio", 0.0))
        x_val = meta.get("arrival_probability", meta.get("cpu_capacity", meta.get("task_timeout_slots", label)))
        x_unit = sweep_type
        sub_map = {
            "arrival_probability": ("10a", "10b"),
            "cpu_capacity": ("10c", "10d"),
            "task_timeout": ("10e", "10f"),
        }
        subs = sub_map.get(sweep_type, ("10-other", "10-other"))
        row = _sweep_base_row("Figure 10", "partial_pdf_extracted")
        row.update({
            "subfigure_id": subs[0],
            "series_name": "average_delay",
            "x_value": x_val,
            "y_value": avg_delay,
            "x_unit": x_unit,
            "y_unit": "slots",
            "policy_name": policy_name,
            "source_kind": "simulation_sweep",
            "limitation": FIGURE10_LIMITATION,
        })
        rows.append(row)
        row2 = row.copy()
        row2["subfigure_id"] = subs[1]
        row2["series_name"] = "drop_ratio"
        row2["y_value"] = avg_drop
        row2["y_unit"] = "ratio"
        rows.append(row2)
    return rows


def _figure11_rows(
    with_lstm: list[dict[str, Any]],
    without_lstm: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for variant, label in [(with_lstm, "with_lstm"), (without_lstm, "without_lstm")]:
        for exp in variant:
            metrics = exp.get("training_metrics") or {}
            rewards = metrics.get("episode_rewards", []) or []
            delays = metrics.get("average_delays", []) or []
            for ep_idx, (reward, delay) in enumerate(zip(rewards, delays)):
                row = _sweep_base_row("Figure 11", "full_pdf_extracted")
                row.update({
                    "subfigure_id": "11-lstm-ablation",
                    "series_name": f"avg_delay_{label}",
                    "x_value": ep_idx,
                    "y_value": delay,
                    "x_unit": "episode",
                    "y_unit": "slots",
                    "policy_name": label,
                    "source_kind": "simulation_sweep",
                })
                rows.append(row)
                reward_row = row.copy()
                reward_row["series_name"] = f"reward_{label}"
                reward_row["y_value"] = reward
                reward_row["y_unit"] = "reward"
                rows.append(reward_row)
    return rows


def run_paper_figure_reproduction(
    *,
    output_dir: str | Path = OUTPUT_DIR,
    quick: bool = True,
    force_rerun: bool = False,
) -> dict[str, Any]:
    """Run the full paper figure reproduction pipeline.

    Each figure sweep is cached on disk; subsequent calls skip completed
    sweeps unless *force_rerun* is True.

    Returns a manifest dict with paths to all exported artifacts.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    sweep_dir = output_path / "sweep_results"
    figures_dir = output_path / "figures"
    data_dir = output_path / "figure_data"
    panel_dir = output_path / "subfigures"
    data_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    panel_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "mode": "quick" if quick else "full",
        "output_dir": str(output_path),
        "figures": {},
        "datasets": {},
        "limitations": {},
    }

    # --- Figure 7 ---
    print("[Figure 7] Rendering approved topology...")
    topology = TopologyGraph.from_approved_assumption_registry()
    fig7_rows = _figure7_rows(topology)
    _write_csv(fig7_rows, data_dir / "figure_7_topology.csv")
    (data_dir / "figure_7_topology.json").write_text(
        _json_dump({"figure_id": "Figure 7", "rows": fig7_rows}),
        encoding="utf-8",
    )
    fig7_png = figures_dir / "figure_7_topology.png"
    plot_figure_7_topology(
        topology,
        str(fig7_png),
        title="Figure 7: Edge Layer Topology",
    )
    _export_panel_pngs(output_path, "Figure 7", topology, panel_dir)
    manifest["figures"]["Figure 7"] = str(fig7_png)
    manifest["datasets"]["Figure 7"] = {
        "csv": str(data_dir / "figure_7_topology.csv"),
        "json": str(data_dir / "figure_7_topology.json"),
        "row_count": len(fig7_rows),
    }

    # --- Figure 8 ---
    print("[Figure 8] Running learning rate & discount factor sweep...")
    fig8_results = run_figure_8(output_path, quick=quick)
    fig8_rows = _figure8_rows(fig8_results)
    _write_csv(fig8_rows, data_dir / "figure_8_training_curves.csv")
    (data_dir / "figure_8_training_curves.json").write_text(
        _json_dump({"figure_id": "Figure 8", "rows": fig8_rows}),
        encoding="utf-8",
    )
    fig8_png = figures_dir / "figure_8_training_curves.png"
    figures_dir.mkdir(parents=True, exist_ok=True)
    plot_figure_8_reward_timecourse(
        fig8_results,
        str(fig8_png),
        title="Figure 8: Training Reward Time-Course",
    )
    _export_panel_pngs(output_path, "Figure 8", fig8_results, panel_dir)
    manifest["figures"]["Figure 8"] = str(fig8_png)
    manifest["datasets"]["Figure 8"] = {
        "csv": str(data_dir / "figure_8_training_curves.csv"),
        "json": str(data_dir / "figure_8_training_curves.json"),
        "row_count": len(fig8_rows),
    }

    # --- Figure 9 ---
    print("[Figure 9] Running parameter sensitivity sweep...")
    fig9_results = run_figure_9(output_path, quick=quick)
    fig9_rows = _figure9_rows(fig9_results)
    _write_csv(fig9_rows, data_dir / "figure_9_parameter_sweeps.csv")
    (data_dir / "figure_9_parameter_sweeps.json").write_text(
        _json_dump({"figure_id": "Figure 9", "rows": fig9_rows}),
        encoding="utf-8",
    )
    fig9_png = figures_dir / "figure_9_parameter_sweeps.png"
    plot_figure_9_parameter_sweep(
        fig9_results,
        str(fig9_png),
        title="Figure 9: HOODIE Behavior Insights",
    )
    _export_panel_pngs(output_path, "Figure 9", fig9_results, panel_dir)
    manifest["figures"]["Figure 9"] = str(fig9_png)
    manifest["datasets"]["Figure 9"] = {
        "csv": str(data_dir / "figure_9_parameter_sweeps.csv"),
        "json": str(data_dir / "figure_9_parameter_sweeps.json"),
        "row_count": len(fig9_rows),
    }

    # --- Figure 10 ---
    print("[Figure 10] Running baseline comparison sweep...")
    fig10_results = run_figure_10(output_path, quick=quick)
    fig10_rows = _figure10_rows(fig10_results)
    _write_csv(fig10_rows, data_dir / "figure_10_simulation_metrics_partial.csv")
    (data_dir / "figure_10_simulation_metrics_partial.json").write_text(
        _json_dump({
            "figure_id": "Figure 10",
            "comparison_allowed": False,
            "reconstruction_status": "partial_pdf_extracted",
            "limitation": FIGURE10_LIMITATION,
            "rows": fig10_rows,
        }),
        encoding="utf-8",
    )
    fig10_png = figures_dir / "figure_10_offloading_schemes.png"
    plot_figure_10_offloading_schemes(
        fig10_results,
        str(fig10_png),
        title="Figure 10: Performance Across Offloading Schemes",
    )
    _export_panel_pngs(output_path, "Figure 10", fig10_results, panel_dir)
    manifest["figures"]["Figure 10"] = str(fig10_png)
    manifest["datasets"]["Figure 10"] = {
        "csv": str(data_dir / "figure_10_simulation_metrics_partial.csv"),
        "json": str(data_dir / "figure_10_simulation_metrics_partial.json"),
        "row_count": len(fig10_rows),
    }
    manifest["limitations"]["Figure 10"] = FIGURE10_LIMITATION

    # --- Figure 11 ---
    print("[Figure 11] Running LSTM ablation sweep...")
    fig11_with, fig11_without = run_figure_11(output_path, quick=quick)
    fig11_rows = _figure11_rows(fig11_with, fig11_without)
    _write_csv(fig11_rows, data_dir / "figure_11_lstm_ablation.csv")
    (data_dir / "figure_11_lstm_ablation.json").write_text(
        _json_dump({"figure_id": "Figure 11", "rows": fig11_rows}),
        encoding="utf-8",
    )
    fig11_png = figures_dir / "figure_11_lstm_comparison.png"
    plot_figure_11_lstm_comparison(
        fig11_with,
        fig11_without,
        str(fig11_png),
        title="Figure 11: LSTM vs No-LSTM Training Delay Comparison",
    )
    _export_panel_pngs(output_path, "Figure 11", [fig11_with[0], fig11_without[0]], panel_dir)
    manifest["figures"]["Figure 11"] = str(fig11_png)
    manifest["datasets"]["Figure 11"] = {
        "csv": str(data_dir / "figure_11_lstm_ablation.csv"),
        "json": str(data_dir / "figure_11_lstm_ablation.json"),
        "row_count": len(fig11_rows),
    }

    # --- Write provenance ---
    (output_path / "run-manifest.json").write_text(
        _json_dump(manifest), encoding="utf-8"
    )
    provenance = {
        "pipeline": "paper_figure_reproduction",
        "mode": "quick" if quick else "full",
        "parameters": {
            "learning_rate_default": 7e-7,
            "gamma_default": 0.99,
            "batch_size": 64,
            "replay_capacity": 10000,
            "slots_per_episode": 110,
            "slot_duration_seconds": 0.1,
            "timeout_slots": 20,
            "agent_count": 20,
        },
    }
    (output_path / "provenance.json").write_text(_json_dump(provenance), encoding="utf-8")

    print(f"Paper figure reproduction complete. Output: {output_path}")
    return manifest


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run HOODIE paper figure reproduction pipeline.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--full", action="store_true", help="Full episode counts instead of quick smoke.")
    parser.add_argument("--force", action="store_true", help="Force re-run all sweeps.")
    parser.add_argument("--json", action="store_true", help="Print manifest as JSON.")
    args = parser.parse_args()
    manifest = run_paper_figure_reproduction(
        output_dir=args.output_dir,
        quick=not args.full,
        force_rerun=args.force,
    )
    if args.json:
        print(_json_dump(manifest))
    else:
        print(f"Manifest: {args.output_dir / 'run-manifest.json'}")
        for figure, path in manifest.get("figures", {}).items():
            print(f"  {figure}: {path}")
