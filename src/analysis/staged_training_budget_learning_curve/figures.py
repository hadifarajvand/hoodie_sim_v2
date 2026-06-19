from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import CHECKPOINT_BUDGETS, FIGURES_DIR


def _matplotlib():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _save_line_plot(path: Path, title: str, x_values: list[int], y_values: list[float], ylabel: str, *, color: str = "#4c78a8") -> None:
    plt = _matplotlib()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(x_values, y_values, marker="o", color=color, linewidth=2)
    ax.set_title(title)
    ax.set_xlabel("training budget")
    ax.set_ylabel(ylabel)
    ax.set_xticks(x_values)
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _save_dual_line_plot(
    path: Path,
    title: str,
    x_values: list[int],
    series_a: list[float],
    series_b: list[float],
    label_a: str,
    label_b: str,
    ylabel: str,
) -> None:
    plt = _matplotlib()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(x_values, series_a, marker="o", color="#4c78a8", linewidth=2, label=label_a)
    ax.plot(x_values, series_b, marker="o", color="#f58518", linewidth=2, label=label_b)
    ax.set_title(title)
    ax.set_xlabel("training budget")
    ax.set_ylabel(ylabel)
    ax.set_xticks(x_values)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _save_stacked_bar(path: Path, title: str, x_values: list[int], stacks: dict[str, list[float]], ylabel: str) -> None:
    plt = _matplotlib()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bottom = [0.0] * len(x_values)
    colors = {
        "local": "#4c78a8",
        "horizontal": "#f58518",
        "vertical": "#54a24b",
    }
    for label in ("local", "horizontal", "vertical"):
        values = stacks[label]
        ax.bar(x_values, values, bottom=bottom, label=label, color=colors[label])
        bottom = [left + value for left, value in zip(bottom, values)]
    ax.set_title(title)
    ax.set_xlabel("training budget")
    ax.set_ylabel(ylabel)
    ax.set_xticks(x_values)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _save_binary_readiness(path: Path, title: str, x_values: list[int], readiness_values: list[bool]) -> None:
    plt = _matplotlib()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    y_values = [1 if value else 0 for value in readiness_values]
    ax.bar(x_values, y_values, color=["#54a24b" if value else "#e45756" for value in readiness_values])
    ax.set_title(title)
    ax.set_xlabel("training budget")
    ax.set_ylabel("comparison ready")
    ax.set_xticks(x_values)
    ax.set_yticks([0, 1], labels=["no", "yes"])
    ax.set_ylim(0, 1.2)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def generate_figures(*, figures_dir: Path, checkpoint_metrics: list[dict[str, Any]]) -> dict[str, Any]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    budgets = [int(checkpoint["training_budget"]) for checkpoint in checkpoint_metrics]
    evaluation_rewards = [float(checkpoint["evaluation_reward_summary"]["mean_reward"]) for checkpoint in checkpoint_metrics]
    replay_sizes = [float(checkpoint["replay_size"]) for checkpoint in checkpoint_metrics]
    optimizer_steps = [float(checkpoint["optimizer_step_count"]) for checkpoint in checkpoint_metrics]
    loss_values = [float(checkpoint["last_loss"]) if checkpoint.get("last_loss") is not None else 0.0 for checkpoint in checkpoint_metrics]
    readiness_values = [bool(checkpoint["comparison_ready"]) for checkpoint in checkpoint_metrics]
    action_distribution = {
        "local": [float(checkpoint["action_distribution"].get("local", 0)) for checkpoint in checkpoint_metrics],
        "horizontal": [float(checkpoint["action_distribution"].get("horizontal", 0)) for checkpoint in checkpoint_metrics],
        "vertical": [float(checkpoint["action_distribution"].get("vertical", 0)) for checkpoint in checkpoint_metrics],
    }

    figure_names = {
        "figure_01_eval_reward_by_training_budget.png": "Evaluation Reward by Training Budget",
        "figure_02_replay_size_and_optimizer_steps_by_budget.png": "Replay Size and Optimizer Steps by Budget",
        "figure_03_action_distribution_by_training_budget.png": "Action Distribution by Training Budget",
        "figure_04_loss_by_training_budget.png": "Loss by Training Budget",
        "figure_05_comparison_readiness_by_budget.png": "Comparison Readiness by Training Budget",
    }

    _save_line_plot(
        figures_dir / "figure_01_eval_reward_by_training_budget.png",
        figure_names["figure_01_eval_reward_by_training_budget.png"],
        budgets,
        evaluation_rewards,
        "mean evaluation reward",
    )
    _save_dual_line_plot(
        figures_dir / "figure_02_replay_size_and_optimizer_steps_by_budget.png",
        figure_names["figure_02_replay_size_and_optimizer_steps_by_budget.png"],
        budgets,
        replay_sizes,
        optimizer_steps,
        "replay size",
        "optimizer steps",
        "count",
    )
    _save_stacked_bar(
        figures_dir / "figure_03_action_distribution_by_training_budget.png",
        figure_names["figure_03_action_distribution_by_training_budget.png"],
        budgets,
        action_distribution,
        "transition count",
    )
    _save_line_plot(
        figures_dir / "figure_04_loss_by_training_budget.png",
        figure_names["figure_04_loss_by_training_budget.png"],
        budgets,
        loss_values,
        "last loss",
        color="#b279a2",
    )
    _save_binary_readiness(
        figures_dir / "figure_05_comparison_readiness_by_budget.png",
        figure_names["figure_05_comparison_readiness_by_budget.png"],
        budgets,
        readiness_values,
    )

    figure_files = [name for name in figure_names if (figures_dir / name).exists()]
    return {
        "figures_generated": len(figure_files) == len(figure_names),
        "figure_count": len(figure_files),
        "figure_files": figure_files,
        "figure_directory": str(figures_dir),
        "paper_reproduction_figures": False,
    }
