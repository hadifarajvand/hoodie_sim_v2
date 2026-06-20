from __future__ import annotations

from pathlib import Path
from typing import Any


def _matplotlib():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _save_stacked_bar(path: Path, title: str, x_values: list[int], series: dict[str, list[float]], ylabel: str, *, hatch: str | None = None) -> None:
    plt = _matplotlib()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    bottom = [0.0] * len(x_values)
    colors = {
        "local": "#4c78a8",
        "horizontal": "#f58518",
        "vertical": "#54a24b",
        "completed": "#54a24b",
        "dropped": "#e45756",
        "pending": "#72b7b2",
    }
    for label, values in series.items():
        ax.bar(x_values, values, bottom=bottom, label=label, color=colors.get(label, "#4c78a8"), hatch=hatch)
        bottom = [current + value for current, value in zip(bottom, values)]
    ax.set_title(title)
    ax.set_xlabel("training budget")
    ax.set_ylabel(ylabel)
    ax.set_xticks(x_values)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _save_dual_line_plot(path: Path, title: str, x_values: list[int], series_a: list[float], series_b: list[float], label_a: str, label_b: str, ylabel: str) -> None:
    plt = _matplotlib()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(x_values, series_a, marker="o", linewidth=2, color="#4c78a8", label=label_a)
    ax.plot(x_values, series_b, marker="o", linewidth=2, color="#f58518", label=label_b)
    ax.set_title(title)
    ax.set_xlabel("training budget")
    ax.set_ylabel(ylabel)
    ax.set_xticks(x_values)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _save_heatmap(path: Path, title: str, rows: list[str], columns: list[str], matrix: list[list[int]]) -> None:
    plt = _matplotlib()
    fig, ax = plt.subplots(figsize=(10, max(6, len(rows) * 0.28)))
    image = ax.imshow(matrix, aspect="auto", interpolation="nearest", cmap="Blues", vmin=0, vmax=1)
    ax.set_title(title)
    ax.set_xticks(range(len(columns)), labels=columns, rotation=20, ha="right")
    ax.set_yticks(range(len(rows)), labels=rows)
    for row_index, row in enumerate(matrix):
        for col_index, value in enumerate(row):
            ax.text(col_index, row_index, str(value), ha="center", va="center", color="black", fontsize=8)
    fig.colorbar(image, ax=ax, fraction=0.04, pad=0.02)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _policy_label(policy_name: str) -> str:
    return policy_name.replace("_", " ")


def generate_figures(
    *,
    figures_dir: Path,
    checkpoint_metrics: list[dict[str, Any]],
    policy_effect_diagnostic: dict[str, Any],
    state_feature_coverage_audit: list[dict[str, Any]],
) -> dict[str, Any]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    budgets = [int(checkpoint["training_budget"]) for checkpoint in checkpoint_metrics]
    eval_action_distribution = {
        "local": [float(checkpoint["evaluation_action_distribution"].get("local", 0)) for checkpoint in checkpoint_metrics],
        "horizontal": [float(checkpoint["evaluation_action_distribution"].get("horizontal", 0)) for checkpoint in checkpoint_metrics],
        "vertical": [float(checkpoint["evaluation_action_distribution"].get("vertical", 0)) for checkpoint in checkpoint_metrics],
    }
    per_action_completed = {
        action: [float(checkpoint["per_action_outcome_summary"][action]["completed_count"]) for checkpoint in checkpoint_metrics]
        for action in ("local", "horizontal", "vertical")
    }
    per_action_dropped = {
        action: [float(checkpoint["per_action_outcome_summary"][action]["dropped_count"]) for checkpoint in checkpoint_metrics]
        for action in ("local", "horizontal", "vertical")
    }
    reward_by_action = {
        action: [float(checkpoint["reward_decomposition"]["reward_by_action"].get(action, 0.0)) for checkpoint in checkpoint_metrics]
        for action in ("local", "horizontal", "vertical")
    }
    replay_vertical_share = [
        float(checkpoint["replay_window_action_distribution"].get("vertical", 0)) / max(float(checkpoint["replay_size"]), 1.0)
        for checkpoint in checkpoint_metrics
    ]
    cumulative_vertical_share = [
        float(checkpoint["cumulative_training_action_distribution"].get("vertical", 0))
        / max(float(sum(checkpoint["cumulative_training_action_distribution"].values())), 1.0)
        for checkpoint in checkpoint_metrics
    ]

    policy_items = list(policy_effect_diagnostic["policy_results"].items())
    policy_labels = [_policy_label(name) for name, _ in policy_items]
    policy_mean_rewards = [float(result["mean_reward"]) for _, result in policy_items]

    figure_files = []

    _save_stacked_bar(
        figures_dir / "figure_01_evaluation_action_distribution_by_budget.png",
        "Evaluation Action Distribution by Training Budget",
        budgets,
        eval_action_distribution,
        "evaluation decisions",
    )
    figure_files.append("figure_01_evaluation_action_distribution_by_budget.png")

    plt = _matplotlib()
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    for action, values in per_action_completed.items():
        axes[0].plot(budgets, values, marker="o", linewidth=2, label=action)
    for action, values in per_action_dropped.items():
        axes[1].plot(budgets, values, marker="o", linewidth=2, label=action)
    axes[0].set_title("Completed Count by Action and Budget")
    axes[1].set_title("Dropped Count by Action and Budget")
    axes[1].set_xlabel("training budget")
    axes[0].set_ylabel("completed")
    axes[1].set_ylabel("dropped")
    axes[0].grid(True, axis="y", alpha=0.25)
    axes[1].grid(True, axis="y", alpha=0.25)
    axes[0].legend(loc="best")
    axes[1].legend(loc="best")
    fig.tight_layout()
    fig.savefig(figures_dir / "figure_02_per_action_drop_completion_by_budget.png")
    plt.close(fig)
    figure_files.append("figure_02_per_action_drop_completion_by_budget.png")

    plt = _matplotlib()
    fig, ax = plt.subplots(figsize=(10, 4.8))
    bottom = [0.0] * len(budgets)
    for action in ("local", "horizontal", "vertical"):
        values = reward_by_action[action]
        ax.bar(budgets, values, bottom=bottom, label=action)
        bottom = [current + value for current, value in zip(bottom, values)]
    ax.set_title("Reward Decomposition by Action")
    ax.set_xlabel("training budget")
    ax.set_ylabel("total reward")
    ax.set_xticks(budgets)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(figures_dir / "figure_03_reward_decomposition_by_action.png")
    plt.close(fig)
    figure_files.append("figure_03_reward_decomposition_by_action.png")

    _save_dual_line_plot(
        figures_dir / "figure_04_replay_window_vs_cumulative_training_actions.png",
        "Replay Window vs Cumulative Training Vertical Share",
        budgets,
        replay_vertical_share,
        cumulative_vertical_share,
        "replay window vertical share",
        "cumulative training vertical share",
        "vertical share",
    )
    figure_files.append("figure_04_replay_window_vs_cumulative_training_actions.png")

    plt = _matplotlib()
    fig, ax = plt.subplots(figsize=(10, 4.8))
    x_positions = list(range(len(policy_labels)))
    ax.bar(x_positions, policy_mean_rewards, color="#4c78a8")
    ax.set_title("Policy Effect Mean Reward")
    ax.set_ylabel("mean reward")
    ax.set_xticks(x_positions, labels=policy_labels, rotation=25, ha="right")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(figures_dir / "figure_05_policy_effect_mean_reward.png")
    plt.close(fig)
    figure_files.append("figure_05_policy_effect_mean_reward.png")

    columns = [
        "env_obs",
        "policy_state",
        "replay_transition",
        "eval_diagnostics",
    ]
    rows = [entry["field_name"] for entry in state_feature_coverage_audit]
    matrix = [
        [
            int(entry["available_in_environment_observation"]),
            int(entry["included_in_policy_state_vector"]),
            int(entry["included_in_replay_transition"]),
            int(entry["included_in_evaluation_diagnostics"]),
        ]
        for entry in state_feature_coverage_audit
    ]
    _save_heatmap(
        figures_dir / "figure_06_state_feature_coverage_matrix.png",
        "State Feature Coverage Matrix",
        rows,
        columns,
        matrix,
    )
    figure_files.append("figure_06_state_feature_coverage_matrix.png")

    return {
        "figures_generated": len(figure_files) == 6,
        "figure_count": len(figure_files),
        "figure_files": figure_files,
        "figure_directory": str(figures_dir),
    }
