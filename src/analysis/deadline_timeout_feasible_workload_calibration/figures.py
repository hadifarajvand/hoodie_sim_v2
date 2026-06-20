from __future__ import annotations

import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/matplotlib-cache")

import matplotlib

matplotlib.use("Agg", force=True)

import matplotlib.pyplot as plt


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def generate_figures(payload: dict[str, Any], figures_dir: Path) -> list[str]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    figure_paths: list[str] = []

    before = payload["before_after_feasibility_comparison"]
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    ax1.bar(["before", "after"], [before["before_overall_feasible_task_ratio"], before["after_overall_feasible_task_ratio"]], color=["#888888", "#2E86AB"])
    ax1.set_ylim(0, 1)
    ax1.set_ylabel("overall feasible task ratio")
    _save(fig1, figures_dir / "figure_01_before_after_feasibility_ratio.png")
    figure_paths.append("figure_01_before_after_feasibility_ratio.png")

    action_path = payload["after_action_path_feasibility"]
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.bar(["local", "horizontal", "vertical"], [action_path["local_feasible_ratio"], action_path["horizontal_feasible_ratio"], action_path["vertical_feasible_ratio"]], color=["#1B998B", "#ED217C", "#2E86AB"])
    ax2.set_ylim(0, 1)
    ax2.set_ylabel("feasible ratio")
    _save(fig2, figures_dir / "figure_02_action_path_feasibility_after_calibration.png")
    figure_paths.append("figure_02_action_path_feasibility_after_calibration.png")

    policy = payload["calibrated_policy_effect_comparison"]["fixed_policy_summaries"]
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    labels = list(policy.keys())
    completed = [policy[name]["completed_count"] for name in labels]
    dropped = [policy[name]["dropped_count"] for name in labels]
    ax3.bar(labels, completed, label="completed", color="#2E86AB")
    ax3.bar(labels, dropped, bottom=completed, label="dropped", color="#F18F01", alpha=0.8)
    ax3.set_ylabel("task count")
    ax3.legend()
    plt.setp(ax3.get_xticklabels(), rotation=20, ha="right")
    _save(fig3, figures_dir / "figure_03_completion_drop_by_policy_after_calibration.png")
    figure_paths.append("figure_03_completion_drop_by_policy_after_calibration.png")

    comparison = payload["checkpoint_50_100_calibrated_comparison"]
    fig4, ax4 = plt.subplots(figsize=(7, 4))
    budgets = [item["training_budget"] for item in comparison["by_checkpoint"]]
    reward_per_task = [item["reward_per_task"] for item in comparison["by_checkpoint"]]
    ax4.plot(budgets, reward_per_task, marker="o", color="#2E86AB")
    ax4.set_xlabel("training budget")
    ax4.set_ylabel("reward per task")
    _save(fig4, figures_dir / "figure_04_50_vs_100_calibrated_metrics.png")
    figure_paths.append("figure_04_50_vs_100_calibrated_metrics.png")

    task_summary = payload["calibrated_task_feasibility_summary"]
    fig5, ax5 = plt.subplots(figsize=(7, 4))
    slacks = [float(record.get("deadline_slack_for_local", 0.0)) for record in task_summary.get("sample_records", [])]
    ax5.hist(slacks, bins=min(10, max(len(slacks), 1)), color="#6A4C93", alpha=0.8)
    ax5.set_xlabel("deadline slack (local)")
    ax5.set_ylabel("count")
    _save(fig5, figures_dir / "figure_05_deadline_slack_before_after.png")
    figure_paths.append("figure_05_deadline_slack_before_after.png")

    return figure_paths
