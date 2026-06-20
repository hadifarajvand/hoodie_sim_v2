from __future__ import annotations

import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/matplotlib-cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _style(ax, *, title: str, ylabel: str) -> None:
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.2)


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def generate_figures(payload: dict[str, Any], figures_dir: Path) -> list[Path]:
    checkpoint_metrics = payload["checkpoint_metrics"]
    comparison = payload["checkpoint_50_100_feasibility_comparison"]
    policy_effect = payload["policy_effect_completion_feasibility"]
    runtime_audit = payload["runtime_event_path_audit"]
    task_summary = payload["task_feasibility_summary"]
    by_checkpoint = checkpoint_metrics
    budgets = [int(checkpoint["training_budget"]) for checkpoint in by_checkpoint]

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    width = 0.28
    x = range(len(budgets))
    local_ratios = [float(checkpoint["task_feasibility_summary"].get("local_feasible_ratio", 0.0)) for checkpoint in by_checkpoint]
    horizontal_ratios = [float(checkpoint["task_feasibility_summary"].get("horizontal_feasible_ratio", 0.0)) for checkpoint in by_checkpoint]
    vertical_ratios = [float(checkpoint["task_feasibility_summary"].get("vertical_feasible_ratio", 0.0)) for checkpoint in by_checkpoint]
    ax1.bar([i - width for i in x], local_ratios, width=width, label="local feasible ratio")
    ax1.bar(x, horizontal_ratios, width=width, label="horizontal feasible ratio")
    ax1.bar([i + width for i in x], vertical_ratios, width=width, label="vertical feasible ratio")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels([str(budget) for budget in budgets])
    _style(ax1, title="Action Path Feasibility by Budget", ylabel="ratio")
    ax1.legend()
    _save(fig1, figures_dir / "figure_01_action_path_feasibility_50_vs_100.png")

    fig2, ax2 = plt.subplots(figsize=(12, 5))
    policy_names = list(policy_effect["policy_feasibility_summary"].keys())
    completion_ratios = [float(policy_effect["policy_feasibility_summary"][name]["completion_ratio"]) for name in policy_names]
    drop_ratios = [float(policy_effect["policy_feasibility_summary"][name]["drop_ratio"]) for name in policy_names]
    pending_ratios = [float(policy_effect["policy_feasibility_summary"][name]["pending_count"]) / max(float(policy_effect["policy_feasibility_summary"][name]["canonical_task_count"]), 1.0) for name in policy_names]
    ax2.bar(policy_names, completion_ratios, label="completion ratio")
    ax2.bar(policy_names, drop_ratios, bottom=completion_ratios, label="drop ratio")
    ax2.bar(policy_names, pending_ratios, bottom=[c + d for c, d in zip(completion_ratios, drop_ratios)], label="pending ratio")
    ax2.tick_params(axis="x", rotation=35)
    _style(ax2, title="Completion, Drop, and Pending Ratios by Policy", ylabel="ratio")
    ax2.legend()
    _save(fig2, figures_dir / "figure_02_completion_drop_by_policy.png")

    fig3, ax3 = plt.subplots(figsize=(12, 5))
    labels = ["transmission_started", "transmission_completed", "execution_started", "execution_progress", "execution_completed", "task_completed", "deadline_reached", "deadline_expired", "task_dropped", "reward_emitted", "pending_at_horizon"]
    values = [int(runtime_audit["overall"].get(f"{label}_event_count", 0)) for label in labels]
    ax3.bar(labels, values)
    ax3.tick_params(axis="x", rotation=35)
    _style(ax3, title="Runtime Event Path Counts", ylabel="count")
    _save(fig3, figures_dir / "figure_03_runtime_event_path_counts.png")

    fig4, ax4 = plt.subplots(figsize=(10, 5))
    slacks = [float(record.get("deadline_slack_for_local", 0.0)) for record in task_summary.get("sample_records", [])]
    if slacks:
        ax4.hist(slacks, bins=min(12, max(1, len(slacks) // 2)), color="#4477aa", alpha=0.85)
    _style(ax4, title="Deadline Slack Distribution", ylabel="tasks")
    ax4.set_xlabel("deadline slack (slots)")
    _save(fig4, figures_dir / "figure_04_deadline_slack_distribution.png")

    fig5, ax5 = plt.subplots(figsize=(12, 5))
    policy_names = list(policy_effect["policy_feasibility_summary"].keys())
    feasible_counts = [sum(policy_effect["policy_feasibility_summary"][name]["feasible_task_count_by_action"].values()) for name in policy_names]
    completed_counts = [int(policy_effect["policy_feasibility_summary"][name]["completed_count"]) for name in policy_names]
    ax5.bar(policy_names, feasible_counts, label="feasible tasks")
    ax5.bar(policy_names, completed_counts, label="completed tasks", alpha=0.75)
    ax5.tick_params(axis="x", rotation=35)
    _style(ax5, title="Feasible vs Completed Tasks by Policy", ylabel="count")
    ax5.legend()
    _save(fig5, figures_dir / "figure_05_feasible_vs_completed_tasks.png")

    return [
        figures_dir / "figure_01_action_path_feasibility_50_vs_100.png",
        figures_dir / "figure_02_completion_drop_by_policy.png",
        figures_dir / "figure_03_runtime_event_path_counts.png",
        figures_dir / "figure_04_deadline_slack_distribution.png",
        figures_dir / "figure_05_feasible_vs_completed_tasks.png",
    ]
