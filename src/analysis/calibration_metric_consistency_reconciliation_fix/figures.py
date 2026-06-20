from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import FIGURES_DIR


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _save_bar(path: Path, title: str, labels: list[str], values: list[float], *, ylabel: str) -> None:
    _ensure_dir(path.parent)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(labels, values, color=["#4c78a8", "#f58518", "#54a24b", "#e45756", "#72b7b2"][: len(labels)])
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def generate_figures(payload: dict[str, Any], figures_dir: Path | None = None) -> list[Path]:
    target_dir = figures_dir or FIGURES_DIR
    _ensure_dir(target_dir)
    figures: list[Path] = []
    after_policy_effect = payload["consistent_policy_effect_comparison"]
    after_reconciliation = payload["reward_terminal_reconciliation_fix"]
    before_after = payload["before_after_consistency_comparison"]
    action_diversity = payload["action_path_diversity_check"]
    comparison_50_100 = payload["consistent_50_100_comparison"]

    p1 = target_dir / "figure_01_reward_reconciliation_before_after.png"
    _save_bar(
        p1,
        "Reward Reconciliation Before / After",
        ["before", "after"],
        [
            float(before_after["before"].get("raw_vs_canonical_reward_delta") or 0.0),
            float(after_reconciliation.get("max_raw_vs_canonical_reward_delta", 0.0)),
        ],
        ylabel="raw vs canonical delta",
    )
    figures.append(p1)

    p2 = target_dir / "figure_02_terminal_reconciliation_before_after.png"
    _save_bar(
        p2,
        "Terminal Reconciliation Before / After",
        ["before", "after"],
        [
            0.0 if not before_after["before"].get("terminal_reconciled") else 1.0,
            1.0 if after_reconciliation.get("terminal_reconciled") else 0.0,
        ],
        ylabel="terminal reconciled",
    )
    figures.append(p2)

    p3 = target_dir / "figure_03_feasibility_universe_consistency.png"
    _save_bar(
        p3,
        "Feasibility Universe Consistency",
        ["selected", "completed_selected"],
        [
            float(after_policy_effect["policy_summaries"]["candidate_policy_at_100"]["selected_action_feasible_task_count"]),
            float(after_policy_effect["policy_summaries"]["candidate_policy_at_100"]["completed_feasible_task_count"]),
        ],
        ylabel="task count",
    )
    figures.append(p3)

    p4 = target_dir / "figure_04_action_path_diversity.png"
    labels = ["local", "horizontal", "vertical"]
    values = [float(action_diversity["feasible_task_count_by_action"][label]) for label in labels]
    _save_bar(p4, "Action Path Diversity", labels, values, ylabel="feasible task count")
    figures.append(p4)

    p5 = target_dir / "figure_05_50_vs_100_consistent_metrics.png"
    _save_bar(
        p5,
        "50 vs 100 Consistent Metrics",
        ["50 completion", "100 completion", "50 reward/task", "100 reward/task"],
        [
            float(comparison_50_100["by_checkpoint"][0]["completion_count"]),
            float(comparison_50_100["by_checkpoint"][1]["completion_count"]),
            float(comparison_50_100["by_checkpoint"][0]["reward_per_task"]),
            float(comparison_50_100["by_checkpoint"][1]["reward_per_task"]),
        ],
        ylabel="value",
    )
    figures.append(p5)
    return figures
