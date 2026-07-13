"""Figure generation scripts for paper Figures 7, 8, 9, 10, 11.

Generates publication-quality plots from collected training metrics
and parameter sweep experiment data. Each plot function produces
paper-sub-figure panels with (a)/(b)/(c) labeling.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional
import re

DEBUG_STEP_FIGURE_INPUTS = {
    "Figure 8": Path("artifacts/analysis/debug-steps/figure_8_sweep/sweep_results.json"),
    "Figure 9": Path("artifacts/analysis/debug-steps/figure_9_sensitivity/sweep_results.json"),
    "Figure 10": Path("artifacts/analysis/debug-steps/figure_10_baselines/sweep_results.json"),
    "Figure 11_lstm": Path("artifacts/analysis/debug-steps/figure_11_lstm/sweep_results.json"),
    "Figure 11_no_lstm": Path("artifacts/analysis/debug-steps/figure_11_no_lstm/sweep_results.json"),
}

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    sns = None

if HAS_SEABORN:
    plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_palette("husl")


def _apply_publication_style(ax=None):
    if ax is None:
        ax = plt.gca()
    if HAS_SEABORN:
        sns.despine(ax=ax)
    ax.grid(True, alpha=0.3)
    return ax


def load_sweep_results(results_dir: str):
    results_path = Path(results_dir)
    if results_path.is_dir():
        results_path = results_path / "sweep_results.json"
    with open(results_path) as f:
        return json.load(f)


def render_status_figure(output_path: str | Path, title: str, missing: list[str]) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis("off")
    ax.text(
        0.02,
        0.95,
        "\n".join([title, "", "Export blocked.", "Missing/invalid:", *[f"- {item}" for item in missing]]),
        va="top",
        ha="left",
        family="monospace",
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_export_manifest(output_dir: str | Path, manifest: dict[str, object]) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _average(values: list[float]) -> float:
    return float(np.mean(values)) if values else 0.0


def _metadata_value(config: dict, key: str):
    meta = config.get("sweep_metadata", {}) if isinstance(config, dict) else {}
    return meta.get(key)

# -- Figure 7 ----------------------------------------------------------------

def plot_figure_7_topology(
    topology,
    output_path: str,
    title: str = "Edge Layer Topology",
) -> None:
    """Figure 7: 20-node topology adjacency heatmap."""
    node_ids = list(getattr(topology, "node_ids", ()) or ())
    adjacency = getattr(topology, "legal_adjacency", {}) or {}
    size = len(node_ids)
    matrix = np.zeros((size, size), dtype=int)
    index_by_node = {node_id: idx for idx, node_id in enumerate(node_ids)}

    for source, destinations in adjacency.items():
        source_idx = index_by_node.get(source)
        if source_idx is None:
            continue
        for destination in destinations or ():
            destination_idx = index_by_node.get(destination)
            if destination_idx is None:
                continue
            matrix[source_idx, destination_idx] = 1

    fig, ax = plt.subplots(figsize=(9, 8))
    heatmap = ax.imshow(matrix, cmap="Blues", interpolation="nearest", vmin=0, vmax=1)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Destination node")
    ax.set_ylabel("Source node")
    ax.set_xticks(range(size))
    ax.set_yticks(range(size))
    ax.set_xticklabels(node_ids, rotation=90, fontsize=7)
    ax.set_yticklabels(node_ids, fontsize=7)
    ax.set_xticks(np.arange(-0.5, size, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, size, 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)
    fig.colorbar(heatmap, ax=ax, fraction=0.046, pad=0.04, label="Legal link")
    _apply_publication_style(ax)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# -- Figure 8 ----------------------------------------------------------------

def plot_figure_8_reward_timecourse(
    results: list[dict],
    output_path: str,
    title: str = "Training Reward Time-Course",
) -> None:
    """Figure 8: two-panel layout.

    (a) Per-episode reward for learning rate sweep.
    (b) Per-episode reward for discount factor sweep.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    lr_results = [r for r in results if _metadata_value(r.get("config", {}), "sweep_type") == "learning_rate"]
    gamma_results = [r for r in results if _metadata_value(r.get("config", {}), "sweep_type") == "discount_factor"]

    def _plot_panel(ax, group, xlabel, panel_label):
        if not group:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
            ax.set_title(f"{panel_label}: {xlabel}")
            return
        for exp in sorted(group, key=lambda e: str(e.get("experiment_label", ""))):
            rewards = (exp.get("training_metrics") or {}).get("episode_rewards", []) or []
            if not rewards:
                continue
            label = str(exp.get("experiment_label", ""))
            episodes = list(range(1, len(rewards) + 1))
            running_avg = np.cumsum(rewards) / np.arange(1, len(rewards) + 1)
            ax.plot(episodes, running_avg, label=label, linewidth=2)
        ax.set_title(f"({panel_label}) {xlabel}")
        ax.set_xlabel("Episode")
        ax.set_ylabel("Average Reward")
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(fontsize=8)
        _apply_publication_style(ax)

    _plot_panel(axes[0], lr_results, "Learning Rate", "a")
    _plot_panel(axes[1], gamma_results, "Discount Factor", "b")

    fig.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# -- Figure 9 ----------------------------------------------------------------

def plot_figure_9_parameter_sweep(
    results: list[dict],
    output_path: str,
    title: str = "HOODIE Behavior Insights",
) -> None:
    """Figure 9: 2x3 layout panels (a)-(e) with paper-aligned axes."""
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    axes = axes.flatten()

    # Build structured rows from sweep data
    rows = []
    for exp_result in results:
        config = exp_result.get("config", {})
        meta = config.get("sweep_metadata", {}) if isinstance(config, dict) else {}
        metrics = exp_result.get("training_metrics", {}) or {}
        action_counts_raw = metrics.get("action_counts", []) or []
        total_action_counts: dict[str, int] = {"local": 0, "horizontal": 0, "vertical": 0}
        for ac in action_counts_raw:
            if isinstance(ac, dict):
                for action_id, count in ac.items():
                    action_int = int(action_id)
                    if action_int == 0:
                        total_action_counts["local"] += int(count)
                    elif action_int in (21, 2):
                        total_action_counts["vertical"] += int(count)
                    else:
                        total_action_counts["horizontal"] += int(count)
        rows.append({
            "metadata": meta,
            "avg_reward": _average(metrics.get("episode_rewards", []) or []),
            "action_counts": total_action_counts,
        })

    def _series(ax, subset, group_key, x_key, panel_label, title_text, xlabel):
        if not subset:
            ax.text(0.5, 0.5, f"{panel_label}: No data", ha="center", va="center", transform=ax.transAxes)
            ax.set_title(f"({panel_label}) {title_text}")
            return
        group_key_val = group_key if group_key else None
        groups = sorted({row["metadata"].get(group_key_val) for row in subset}, key=str) if group_key_val else ["all"]
        plotted_any = False
        for group in groups:
            points = [row for row in subset if group_key_val is None or row["metadata"].get(group_key_val) == group]
            points = [row for row in points if row["metadata"].get(x_key) is not None]
            points = sorted(points, key=lambda row: float(row["metadata"].get(x_key, 0.0)))
            xs = [float(row["metadata"].get(x_key, 0.0)) for row in points]
            ys = [row["avg_reward"] for row in points]
            if not xs:
                continue
            if group_key_val == "num_drl_agents" and group not in ("all", None, ""):
                label = f"N={int(group)}"
            elif group_key_val == "traffic_scenario" and group not in ("all", None, ""):
                label = str(group).title()
            elif group_key_val == "data_rate_scenario" and group not in ("all", None, ""):
                label = str(group).replace("-", " ").title()
            elif group_key_val:
                label = "all" if group in (None, "") else str(group).replace("-", " ").title()
            else:
                label = "all"
            ax.plot(xs, ys, marker="o", linewidth=2, label=label)
            plotted_any = True
        if not plotted_any:
            ax.text(0.5, 0.5, "Insufficient sweep points", ha="center", va="center", transform=ax.transAxes)
        ax.set_title(f"({panel_label}) {title_text}")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Average Reward")
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(fontsize=8)
        _apply_publication_style(ax)
        return plotted_any

    # (a) Reward vs Task Arrival Probability by N agents
    arrival_rows = [row for row in rows if row["metadata"].get("sweep_type") == "arrival_probability" and not row["metadata"].get("policy")]
    _series(axes[0], arrival_rows, "num_drl_agents", "arrival_probability", "a",
            "Reward vs Task Arrival Probability", "Task Arrival Probability")
    axes[0].set_title("(a) Average Reward vs. Task Arrival Probability")
    axes[0].set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
    axes[0].set_xlim(0.05, 0.95)
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        axes[0].legend(fontsize=8, title="N agents")
    axes[0].set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])

    fig7_note = None

    # (b) Action type distribution
    ax = axes[1]
    action_labels = ["Local", "Horizontal", "Vertical"]
    width = 0.16
    probabilities = [0.1, 0.3, 0.5, 0.7, 0.9]
    centers = np.arange(len(action_labels))
    for p_idx, prob in enumerate(probabilities):
        matching = [row for row in arrival_rows if abs(float(row["metadata"].get("arrival_probability", -1.0)) - prob) < 0.01]
        counts = []
        for act_name in ["local", "horizontal", "vertical"]:
            counts.append(sum(row["action_counts"][act_name] for row in matching))
        ax.bar(centers + (p_idx - 2) * width, counts, width=width, label=f"P={prob:g}")
    ax.set_title("(b) Action Type Distribution")
    ax.set_xlabel("Action Type")
    ax.set_ylabel("Action Count")
    ax.set_xticks(centers)
    ax.set_xticklabels(action_labels)
    ax.legend(fontsize=7)
    _apply_publication_style(ax)

    # (c) Reward vs CPU capacity by agent count
    cpu_rows = [row for row in rows if row["metadata"].get("sweep_type") == "cpu_capacity"]
    _series(axes[2], cpu_rows, "num_drl_agents", "cpu_capacity", "c",
            "Reward vs CPU Capacity", "CPU Capacity (GHz)")
    axes[2].set_title("(c) Average Reward vs. CPU Computation Capacity")
    axes[2].set_xticks([4, 5, 6, 7, 8, 9])
    axes[2].set_xlim(4, 9)
    handles, labels = axes[2].get_legend_handles_labels()
    if handles:
        axes[2].legend(fontsize=8, title="N agents")
    axes[2].set_xticks([4, 5, 6, 7, 8, 9])

    # (d) Reward vs N agents by traffic scenario
    traffic_rows = [row for row in rows if row["metadata"].get("sweep_type") == "num_drl_agents" and row["metadata"].get("traffic_scenario")]
    _series(axes[3], traffic_rows, "traffic_scenario", "num_drl_agents", "d",
            "Reward vs Number of Agents", "Number of Agents (N)")
    axes[3].set_title("(d) Average Reward vs. Number of Agents by Traffic Scenario")
    axes[3].set_xticks([10, 15, 20, 25, 30])
    axes[3].set_xlim(10, 30)
    handles, labels = axes[3].get_legend_handles_labels()
    if handles:
        axes[3].legend(fontsize=8)
    axes[3].set_xticks([10, 15, 20, 25, 30])

    # (e) Reward vs N agents by data-rate scenario
    rate_rows = [row for row in rows if row["metadata"].get("sweep_type") == "offload_data_rate" and row["metadata"].get("num_drl_agents") is not None]
    _series(axes[4], rate_rows, "data_rate_scenario", "num_drl_agents", "e",
            "Reward vs Number of Agents", "Number of Agents (N)")
    axes[4].set_title("(e) Average Reward vs. Number of Agents by Data-Rate Scenario")
    axes[4].set_xticks([10, 15, 20])
    axes[4].set_xlim(10, 20)
    handles, labels = axes[4].get_legend_handles_labels()
    if handles:
        axes[4].legend(fontsize=8)
    axes[4].set_xticks([10, 15, 20])

    fig.delaxes(axes[5])
    fig.suptitle(title, fontsize=16, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# -- Figure 10 ---------------------------------------------------------------

def plot_figure_10_offloading_schemes(
    results: list[dict],
    output_path: str,
    title: str = "Performance Across Offloading Schemes",
) -> None:
    """Figure 10: 2x3 layout panels (a)-(f).

    Each sweep dimension shows per-policy curves for delay and drop ratio.
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    # Index all results by (sweep_type, policy, x_value)
    indexed: dict[str, dict[str, list[dict]]] = {}
    for exp in results:
        cfg = exp.get("config", {})
        meta = cfg.get("sweep_metadata", {}) if isinstance(cfg, dict) else {}
        sweep_type = str(meta.get("sweep_type", ""))
        policy = str(meta.get("policy", "unknown"))
        label = str(exp.get("experiment_label", ""))
        if policy == "unknown":
            # Try to extract from label
            for known in ["RO", "FLC", "VO", "HO", "BCO", "MLEO", "HOODIE"]:
                if known in label:
                    policy = known
                    break
        metrics = exp.get("training_metrics", {}) or {}
        delays = metrics.get("average_delays", []) or []
        drops = metrics.get("drop_ratios", []) or []
        avg_delay = _average(delays)
        avg_drop = _average(drops)
        # Check evaluation_result fallback
        eval_res = exp.get("evaluation_result") or {}
        agg = eval_res.get("aggregate") or {}
        if not delays:
            avg_delay = float(agg.get("average_delay", 0.0))
        if not drops:
            avg_drop = float(agg.get("drop_ratio", 0.0))

        x_val = meta.get("arrival_probability", meta.get("cpu_capacity", meta.get("task_timeout_slots", None)))
        if x_val is None:
            # extract numeric from label
            nums = re.findall(r"[-+]?\d*\.?\d+", label)
            if nums:
                x_val = float(nums[-1])

        key = (sweep_type, policy)
        if key not in indexed:
            indexed[key] = {"delay": [], "drop": []}
        indexed[key]["delay"].append((float(x_val) if x_val is not None else 0.0, avg_delay))
        indexed[key]["drop"].append((float(x_val) if x_val is not None else 0.0, avg_drop))

    # Define sub-figure layout: (sweep_dim, delay_title, drop_title, xlabel)
    subfigs = [
        ("arrival_probability", "Avg Delay vs Arrival Prob", "Drop Ratio vs Arrival Prob", "Arrival Probability"),
        ("cpu_capacity", "Avg Delay vs CPU Capacity", "Drop Ratio vs CPU Capacity", "CPU Capacity (GHz)"),
        ("task_timeout", "Avg Delay vs Timeout", "Drop Ratio vs Timeout", "Timeout (slots)"),
    ]

    POLICY_STYLES = {
        "RO": {"marker": "o", "ls": "-", "color": "#1f77b4"},
        "VO": {"marker": "^", "ls": "-.", "color": "#2ca02c"},
        "VCO": {"marker": "^", "ls": "-.", "color": "#2ca02c"},
        "FLC": {"marker": "s", "ls": "--", "color": "#ff7f0e"},
        "HO": {"marker": "D", "ls": ":", "color": "#d62728"},
        "MLEO": {"marker": "<", "ls": "--", "color": "#8c564b"},
        "BCO": {"marker": "v", "ls": "-", "color": "#9467bd"},
        "HOODIE": {"marker": "o", "ls": "-", "color": "#000000", "linewidth": 3},
    }
    POLICY_ORDER = ["RO", "VO", "VCO", "FLC", "HO", "MLEO", "BCO", "HOODIE"]

    def _policy_label(policy: str) -> str:
        return "hoodie" if policy == "HOODIE" else policy

    for col_idx, (sweep_dim, delay_title, drop_title, xlabel) in enumerate(subfigs):
        delay_ax = axes[col_idx]
        drop_ax = axes[col_idx + 3]

        policies_drawn_delay: set[str] = set()
        policies_drawn_drop: set[str] = set()

        for policy in POLICY_ORDER:
            for (s_type, p), data in sorted(indexed.items()):
                if s_type != sweep_dim or p != policy:
                    continue
                style = POLICY_STYLES.get(policy, {"marker": "o", "ls": "-", "color": "#333333"})
                delay_pts = sorted(data["delay"], key=lambda p: p[0])
                drop_pts = sorted(data["drop"], key=lambda p: p[0])
                if delay_pts:
                    xs, ys = zip(*delay_pts)
                    delay_ax.plot(xs, ys, label=_policy_label(policy) if policy not in policies_drawn_delay else "",
                                  marker=style["marker"], linestyle=style["ls"], color=style["color"],
                                  linewidth=style.get("linewidth", 2))
                    policies_drawn_delay.add(policy)
                if drop_pts:
                    xs, ys = zip(*drop_pts)
                    drop_ax.plot(xs, ys, label=_policy_label(policy) if policy not in policies_drawn_drop else "",
                                 marker=style["marker"], linestyle=style["ls"], color=style["color"],
                                 linewidth=style.get("linewidth", 2))
                    policies_drawn_drop.add(policy)

        for ax, title_text, drawn in [
            (delay_ax, delay_title, policies_drawn_delay),
            (drop_ax, drop_title, policies_drawn_drop),
        ]:
            if not drawn:
                ax.text(0.5, 0.5, "Insufficient sweep points", ha="center", va="center", transform=ax.transAxes)
            ax.set_xlabel(xlabel)
            ax.set_title(title_text)
            _apply_publication_style(ax)
        delay_ax.set_ylabel("Average Delay (slots)")
        drop_ax.set_ylabel("Drop Ratio")

    # Add legend centered at top of figure
    handles, labels = axes[0].get_legend_handles_labels()
    all_labels = set()
    unique: list = []
    for h, l in zip(handles, labels):
        if l and l not in all_labels:
            all_labels.add(l)
            unique.append((h, l))
    if unique:
        fig.legend([h for h, _ in unique], [l for _, l in unique],
                   loc="upper center", ncol=len(unique), fontsize=9, frameon=True,
                   bbox_to_anchor=(0.5, 1.02))
    axes[5].axis("off")
    plt.subplots_adjust(top=0.82)
    fig.suptitle(title, fontsize=16, fontweight="bold", y=0.995)

    fig.suptitle(title, fontsize=16, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# -- Figure 11 ---------------------------------------------------------------

def plot_figure_11_lstm_comparison(
    lstm_results: list[dict],
    no_lstm_results: list[dict],
    output_path: str,
    title: str = "LSTM vs No-LSTM Training Delay Comparison",
) -> None:
    """Figure 11: single-axis LSTM vs no-LSTM training curves."""
    fig, ax = plt.subplots(figsize=(10, 6))

    def _nominally_disabled_but_effectively_enabled(results: list[dict]) -> bool:
        for exp_result in results:
            config = exp_result.get("config", {})
            meta = config.get("sweep_metadata", {}) if isinstance(config, dict) else {}
            if meta.get("lstm_enabled") is False and meta.get("lstm_effective_enabled") is True:
                return True
        return False

    no_lstm_blocked = _nominally_disabled_but_effectively_enabled(no_lstm_results)

    if no_lstm_blocked:
        ax.text(0.5, 0.5,
                "No-LSTM sweep requested, but network path still forces LSTM on.\nComparison blocked.",
                ha="center", va="center", transform=ax.transAxes, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        return

    def _episode_series(results: list[dict]) -> tuple[list[int], list[float]]:
        if not results:
            return [], []
        delays = results[0].get("training_metrics", {}).get("average_delays", []) or []
        return list(range(1, len(delays) + 1)), delays

    lstm_x, lstm_y = _episode_series(lstm_results)
    no_lstm_x, no_lstm_y = _episode_series(no_lstm_results)

    has_data = False
    if no_lstm_x:
        ax.plot(no_lstm_x, no_lstm_y, label="Without LSTM", linewidth=2)
        has_data = True
    if lstm_x:
        ax.plot(lstm_x, lstm_y, label="With LSTM", linewidth=2)
        has_data = True

    if not has_data:
        ax.text(0.5, 0.5, "No delay data available",
                ha="center", va="center", transform=ax.transAxes, fontsize=12)
    else:
        ax.legend()
    ax.set_xlabel("Episode")
    ax.set_ylabel("Average Delay (slots)")
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# -- Aggregate ---------------------------------------------------------------

def generate_all_figures(
    sweep_results_dir: str,
    output_dir: str,
    lstm_sweep_dir: Optional[str] = None,
    no_lstm_sweep_dir: Optional[str] = None,
) -> None:
    """Generate all figures (8, 9, 10, 11) from sweep results directory."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    results = load_sweep_results(sweep_results_dir)

    plot_figure_8_reward_timecourse(
        results,
        str(output_path / "figure_8_reward_timecourse.png"),
        "Figure 8: Training Reward Time-Course",
    )
    plot_figure_9_parameter_sweep(
        results,
        str(output_path / "figure_9_parameter_sweep.png"),
        "Figure 9: Performance vs System Parameters",
    )
    plot_figure_10_offloading_schemes(
        results,
        str(output_path / "figure_10_offloading_schemes.png"),
        "Figure 10: Performance Across Offloading Schemes",
    )

    if lstm_sweep_dir and no_lstm_sweep_dir:
        lstm_results = load_sweep_results(lstm_sweep_dir)
        no_lstm_results = load_sweep_results(no_lstm_sweep_dir)
        plot_figure_11_lstm_comparison(
            lstm_results,
            no_lstm_results,
            str(output_path / "figure_11_lstm_comparison.png"),
            "Figure 11: LSTM vs No-LSTM Training Delay Comparison",
        )
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Requires LSTM/no-LSTM sweep outputs.",
                ha="center", va="center", transform=ax.transAxes, fontsize=12)
        ax.set_title("Figure 11: LSTM vs No-LSTM Training Delay Comparison",
                     fontsize=14, fontweight="bold")
        plt.tight_layout()
        plt.savefig(output_path / "figure_11_lstm_comparison.png",
                   dpi=300, bbox_inches="tight")
        plt.close()


def generate_debug_step_figures(output_dir: str) -> dict[str, str]:
    """Generate Figures 8-11 directly from known debug-step sweep artifacts."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    figure8_results = load_sweep_results(str(DEBUG_STEP_FIGURE_INPUTS["Figure 8"]))
    figure9_results = load_sweep_results(str(DEBUG_STEP_FIGURE_INPUTS["Figure 9"]))
    figure10_results = load_sweep_results(str(DEBUG_STEP_FIGURE_INPUTS["Figure 10"]))
    figure11_lstm_results = load_sweep_results(str(DEBUG_STEP_FIGURE_INPUTS["Figure 11_lstm"]))
    figure11_no_lstm_results = load_sweep_results(str(DEBUG_STEP_FIGURE_INPUTS["Figure 11_no_lstm"]))

    figure8_path = output_path / "figure_8_reward_timecourse.png"
    figure9_path = output_path / "figure_9_parameter_sweep.png"
    figure10_path = output_path / "figure_10_offloading_schemes.png"
    figure11_path = output_path / "figure_11_lstm_comparison.png"

    plot_figure_8_reward_timecourse(figure8_results, str(figure8_path), "Figure 8: Training Reward Time-Course")
    plot_figure_9_parameter_sweep(figure9_results, str(figure9_path), "Figure 9: Performance vs System Parameters")
    plot_figure_10_offloading_schemes(figure10_results, str(figure10_path), "Figure 10: Performance Across Offloading Schemes")
    plot_figure_11_lstm_comparison(
        figure11_lstm_results,
        figure11_no_lstm_results,
        str(figure11_path),
        "Figure 11: LSTM vs No-LSTM Training Delay Comparison",
    )

    return {
        "Figure 8": str(figure8_path),
        "Figure 9": str(figure9_path),
        "Figure 10": str(figure10_path),
        "Figure 11": str(figure11_path),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate paper figures from sweep results")
    parser.add_argument("--sweep-results")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--lstm-sweep")
    parser.add_argument("--no-lstm-sweep")
    parser.add_argument("--debug-step", action="store_true", help="Generate Figures 8-11 from known debug-step sweep artifacts")
    args = parser.parse_args()
    if args.debug_step:
        outputs = generate_debug_step_figures(args.output_dir)
        print(json.dumps(outputs, indent=2, sort_keys=True))
    else:
        if not args.sweep_results:
            raise SystemExit("--sweep-results is required unless --debug-step is used")
        generate_all_figures(
            args.sweep_results,
            args.output_dir,
            args.lstm_sweep,
            args.no_lstm_sweep,
        )
        print(f"Figures generated in {args.output_dir}")
