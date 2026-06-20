from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _figure_style(ax, *, title: str, ylabel: str) -> None:
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
    budgets = [int(checkpoint["training_budget"]) for checkpoint in checkpoint_metrics]
    evaluation_summaries = [checkpoint["evaluation_reward_summary"] for checkpoint in checkpoint_metrics]
    raw_reward_totals = [float(summary.get("raw_event_reward_total", 0.0)) for summary in evaluation_summaries]
    canonical_reward_totals = [float(summary.get("canonical_task_reward_total", 0.0)) for summary in evaluation_summaries]
    raw_reward_counts = [int(summary.get("raw_event_reward_count", 0)) for summary in evaluation_summaries]
    canonical_reward_counts = [int(summary.get("canonical_task_reward_count", 0)) for summary in evaluation_summaries]
    raw_terminal_counts = [int(summary.get("raw_terminal_event_count", 0)) for summary in evaluation_summaries]
    canonical_terminal_counts = [int(summary.get("terminal_transition_count", 0)) for summary in evaluation_summaries]

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    width = 0.35
    x = range(len(budgets))
    ax1.bar([i - width / 2 for i in x], raw_reward_totals, width=width, label="raw event reward")
    ax1.bar([i + width / 2 for i in x], canonical_reward_totals, width=width, label="canonical task reward")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels([str(budget) for budget in budgets])
    _figure_style(ax1, title="Raw vs Canonical Reward by Training Budget", ylabel="reward")
    ax1.legend()
    _save(fig1, figures_dir / "figure_01_raw_vs_canonical_reward_reconciliation.png")

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.bar([i - width / 2 for i in x], raw_reward_counts, width=width, label="raw reward events")
    ax2.bar([i + width / 2 for i in x], canonical_reward_counts, width=width, label="canonical reward tasks")
    ax2.set_xticks(list(x))
    ax2.set_xticklabels([str(budget) for budget in budgets])
    _figure_style(ax2, title="Reward Event Coverage by Training Budget", ylabel="count")
    ax2.legend()
    _save(fig2, figures_dir / "figure_02_reward_event_coverage_by_budget.png")

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.bar([i - width / 2 for i in x], raw_terminal_counts, width=width, label="raw terminal events")
    ax3.bar([i + width / 2 for i in x], canonical_terminal_counts, width=width, label="canonical terminal tasks")
    ax3.set_xticks(list(x))
    ax3.set_xticklabels([str(budget) for budget in budgets])
    _figure_style(ax3, title="Terminal Event Coverage by Training Budget", ylabel="count")
    ax3.legend()
    _save(fig3, figures_dir / "figure_03_terminal_event_coverage_by_budget.png")

    fig4, ax4 = plt.subplots(figsize=(10, 5))
    completion = [float(summary.get("canonical_completion_ratio", 0.0)) for summary in evaluation_summaries]
    drop = [float(summary.get("canonical_drop_ratio", 0.0)) for summary in evaluation_summaries]
    pending = [float(summary.get("canonical_pending_ratio", 0.0)) for summary in evaluation_summaries]
    ax4.bar(budgets, completion, label="completion ratio")
    ax4.bar(budgets, drop, bottom=completion, label="drop ratio")
    ax4.bar(budgets, pending, bottom=[c + d for c, d in zip(completion, drop)], label="pending ratio")
    ax4.set_xticks(budgets)
    _figure_style(ax4, title="Canonical Outcome Ratios by Training Budget", ylabel="ratio")
    ax4.legend()
    _save(fig4, figures_dir / "figure_04_completion_drop_pending_ratios_by_budget.png")

    fig5, ax5 = plt.subplots(figsize=(12, 5))
    policy_results = payload["policy_effect_after_repair"]["policy_results"]
    policy_names = list(policy_results.keys())
    policy_rewards = [
        float(result.get("canonical_task_reward_total", result.get("evaluation_reward_summary", {}).get("canonical_task_reward_total", 0.0)))
        / max(float(result.get("canonical_task_reward_count", result.get("evaluation_reward_summary", {}).get("canonical_task_reward_count", 1))), 1.0)
        for result in policy_results.values()
    ]
    ax5.bar(policy_names, policy_rewards)
    ax5.tick_params(axis="x", rotation=30)
    _figure_style(ax5, title="Policy Effect After Repair", ylabel="canonical reward per task")
    _save(fig5, figures_dir / "figure_05_policy_effect_after_repair.png")

    return [
        figures_dir / "figure_01_raw_vs_canonical_reward_reconciliation.png",
        figures_dir / "figure_02_reward_event_coverage_by_budget.png",
        figures_dir / "figure_03_terminal_event_coverage_by_budget.png",
        figures_dir / "figure_04_completion_drop_pending_ratios_by_budget.png",
        figures_dir / "figure_05_policy_effect_after_repair.png",
    ]
