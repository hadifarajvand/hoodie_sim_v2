from __future__ import annotations

from pathlib import Path
from typing import Any


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


def _save_replay_cap_plot(path: Path, title: str, x_values: list[int], replay_sizes: list[float], replay_capacity: float) -> None:
    plt = _matplotlib()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(x_values, replay_sizes, marker="o", linewidth=2, color="#4c78a8", label="observed replay size")
    ax.axhline(replay_capacity, linestyle="--", linewidth=1.5, color="#e45756", label="configured capacity")
    ax.set_title(title)
    ax.set_xlabel("training budget")
    ax.set_ylabel("replay size")
    ax.set_xticks(x_values)
    ax.legend(loc="best")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def generate_figures(*, figures_dir: Path, reward_values: dict[int, float], action_distributions: dict[int, dict[str, int]], replay_sizes: dict[int, int], replay_capacity: int) -> dict[str, Any]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    budgets = sorted(reward_values)
    reward_series = [float(reward_values[budget]) for budget in budgets]
    stacks = {
        "local": [float(action_distributions[budget].get("local", 0)) for budget in budgets],
        "horizontal": [float(action_distributions[budget].get("horizontal", 0)) for budget in budgets],
        "vertical": [float(action_distributions[budget].get("vertical", 0)) for budget in budgets],
    }
    replay_series = [float(replay_sizes[budget]) for budget in budgets]

    figure_files = [
        "figure_01_reward_stability_gate.png",
        "figure_02_vertical_action_collapse_gate.png",
        "figure_03_replay_cap_gate.png",
    ]

    _save_line_plot(
        figures_dir / figure_files[0],
        "Evaluation Reward Stability Gate",
        budgets,
        reward_series,
        "mean evaluation reward",
    )
    _save_stacked_bar(
        figures_dir / figure_files[1],
        "Vertical Action Collapse Gate",
        budgets,
        stacks,
        "transition count",
    )
    _save_replay_cap_plot(
        figures_dir / figure_files[2],
        "Replay Buffer Capacity Gate",
        budgets,
        replay_series,
        float(replay_capacity),
    )

    return {
        "figure_directory": str(figures_dir),
        "figure_files": figure_files,
        "figure_count": len(figure_files),
        "figures_generated": all((figures_dir / name).exists() for name in figure_files),
    }
