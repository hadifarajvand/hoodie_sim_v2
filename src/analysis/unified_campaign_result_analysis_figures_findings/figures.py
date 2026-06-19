from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import REQUIRED_FIGURES


def _save_bar_chart(path: Path, title: str, labels: list[str], values: list[float], ylabel: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(labels, values, color=["#4c78a8", "#f58518", "#54a24b", "#b279a2"][: len(labels)])
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def generate_figures(
    *,
    figures_dir: Path,
    training: dict[str, Any],
    baseline: dict[str, Any],
    campaign_summary: dict[str, Any],
) -> dict[str, Any]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    action_distribution = training.get("action_distribution", {})
    _save_bar_chart(
        figures_dir / "figure_01_training_action_distribution.png",
        "Training Action Distribution",
        ["local", "horizontal", "vertical"],
        [float(action_distribution.get(name, 0)) for name in ("local", "horizontal", "vertical")],
        "transition count",
    )

    reward = training.get("reward_summary", {})
    _save_bar_chart(
        figures_dir / "figure_02_training_reward_summary.png",
        "Training Reward Summary",
        ["reward_count", "reward_available_count", "pending_at_horizon_count"],
        [
            float(reward.get("reward_count", 0)),
            float(reward.get("reward_available_count", 0)),
            float(reward.get("pending_at_horizon_count", 0)),
        ],
        "count",
    )

    per_policy = baseline.get("per_policy_metrics", {})
    labels = list(per_policy)
    horizontal_counts = [
        float(per_policy[name].get("action_distribution", {}).get("horizontal", 0))
        for name in labels
    ]
    _save_bar_chart(
        figures_dir / "figure_03_baseline_policy_action_distribution.png",
        "Baseline Policy Horizontal Action Counts",
        labels,
        horizontal_counts,
        "horizontal action count",
    )

    configured = campaign_summary.get("configured_budget", {})
    actual_pairs = [
        ("training", "training_episode_count", "actual_training_episode_count"),
        ("evaluation", "evaluation_episode_count", "actual_evaluation_episode_count"),
        ("baseline", "baseline_evaluation_episode_count", "actual_baseline_evaluation_episode_count"),
    ]
    _save_bar_chart(
        figures_dir / "figure_04_campaign_budget_integrity.png",
        "Campaign Budget Integrity",
        [item[0] for item in actual_pairs],
        [float(campaign_summary.get(actual_key, 0) - configured.get(configured_key, 0)) for _, configured_key, actual_key in actual_pairs],
        "actual minus configured episodes",
    )

    figure_files = [name for name in REQUIRED_FIGURES if (figures_dir / name).exists()]
    return {
        "figures_generated": len(figure_files) == len(REQUIRED_FIGURES),
        "figure_count": len(figure_files),
        "figure_files": figure_files,
        "figure_directory": str(figures_dir),
        "paper_reproduction_figures": False,
    }
