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
    terminal_reconciliations = [checkpoint["raw_vs_canonical_terminal_reconciliation"] for checkpoint in checkpoint_metrics]
    reward_reconciliations = [checkpoint["reward_reconciliation_after_terminal_repair"] for checkpoint in checkpoint_metrics]
    paper_metrics = [checkpoint["paper_aligned_diagnostic_metrics"] for checkpoint in checkpoint_metrics]
    audits = [checkpoint["completion_path_audit"] for checkpoint in checkpoint_metrics]

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    width = 0.35
    x = range(len(budgets))
    raw_terminal_counts = [int(rec.get("raw_terminal_event_count", 0)) for rec in terminal_reconciliations]
    canonical_terminal_counts = [int(rec.get("canonical_terminal_task_count", 0)) for rec in terminal_reconciliations]
    ax1.bar([i - width / 2 for i in x], raw_terminal_counts, width=width, label="raw terminal outcome events")
    ax1.bar([i + width / 2 for i in x], canonical_terminal_counts, width=width, label="canonical terminal tasks")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels([str(budget) for budget in budgets])
    _figure_style(ax1, title="Terminal Event Reconciliation by Budget", ylabel="count")
    ax1.legend()
    _save(fig1, figures_dir / "figure_01_terminal_event_reconciliation_50_vs_100.png")

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    completion = [float(metric.get("canonical_completion_ratio", 0.0)) for metric in paper_metrics]
    drop = [float(metric.get("canonical_drop_ratio", 0.0)) for metric in paper_metrics]
    pending = [float(metric.get("canonical_pending_ratio", 0.0)) for metric in paper_metrics]
    ax2.bar(budgets, completion, label="completion ratio")
    ax2.bar(budgets, drop, bottom=completion, label="drop ratio")
    ax2.bar(budgets, pending, bottom=[c + d for c, d in zip(completion, drop)], label="pending ratio")
    ax2.set_xticks(budgets)
    _figure_style(ax2, title="Completion, Drop, and Pending Ratios by Budget", ylabel="ratio")
    ax2.legend()
    _save(fig2, figures_dir / "figure_02_completion_drop_pending_50_vs_100.png")

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    raw_reward_totals = [float(rec.get("raw_event_reward_total", 0.0)) for rec in reward_reconciliations]
    canonical_reward_totals = [float(rec.get("canonical_task_reward_total", 0.0)) for rec in reward_reconciliations]
    ax3.bar([i - width / 2 for i in x], raw_reward_totals, width=width, label="raw event reward")
    ax3.bar([i + width / 2 for i in x], canonical_reward_totals, width=width, label="canonical task reward")
    ax3.set_xticks(list(x))
    ax3.set_xticklabels([str(budget) for budget in budgets])
    _figure_style(ax3, title="Raw vs Canonical Reward Reconciliation by Budget", ylabel="reward")
    ax3.legend()
    _save(fig3, figures_dir / "figure_03_reward_reconciliation_50_vs_100.png")

    fig4, ax4 = plt.subplots(figsize=(12, 5))
    policy_results = payload["policy_effect_50_100_after_terminal_repair"]["policy_results"]
    policy_names = list(policy_results.keys())
    policy_rewards = [float(result["evaluation_reward_summary"]["mean_reward"]) for result in policy_results.values()]
    ax4.bar(policy_names, policy_rewards)
    ax4.tick_params(axis="x", rotation=30)
    _figure_style(ax4, title="Policy Effect After Terminal Repair", ylabel="mean reward")
    _save(fig4, figures_dir / "figure_04_policy_effect_50_vs_100.png")

    fig5, ax5 = plt.subplots(figsize=(12, 5))
    audit_50 = audits[0] if audits else {}
    audit_100 = audits[1] if len(audits) > 1 else {}
    labels = ["execution_completed", "task_completed", "deadline_reached", "deadline_expired", "task_dropped", "reward_emitted", "pending_at_horizon"]
    values_50 = [
        int(audit_50.get("execution_completed_event_count", 0)),
        int(audit_50.get("task_completed_event_count", 0)),
        int(audit_50.get("deadline_reached_event_count", 0)),
        int(audit_50.get("deadline_expired_event_count", 0)),
        int(audit_50.get("task_dropped_event_count", 0)),
        int(audit_50.get("reward_emitted_event_count", 0)),
        int(audit_50.get("pending_at_horizon_count", 0)),
    ]
    values_100 = [
        int(audit_100.get("execution_completed_event_count", 0)),
        int(audit_100.get("task_completed_event_count", 0)),
        int(audit_100.get("deadline_reached_event_count", 0)),
        int(audit_100.get("deadline_expired_event_count", 0)),
        int(audit_100.get("task_dropped_event_count", 0)),
        int(audit_100.get("reward_emitted_event_count", 0)),
        int(audit_100.get("pending_at_horizon_count", 0)),
    ]
    bar_positions = range(len(labels))
    ax5.bar([i - width / 2 for i in bar_positions], values_50, width=width, label="50 episodes")
    ax5.bar([i + width / 2 for i in bar_positions], values_100, width=width, label="100 episodes")
    ax5.set_xticks(list(bar_positions))
    ax5.set_xticklabels(labels, rotation=25)
    _figure_style(ax5, title="Completion Path Event Counts", ylabel="count")
    ax5.legend()
    _save(fig5, figures_dir / "figure_05_completion_path_event_counts.png")

    return [
        figures_dir / "figure_01_terminal_event_reconciliation_50_vs_100.png",
        figures_dir / "figure_02_completion_drop_pending_50_vs_100.png",
        figures_dir / "figure_03_reward_reconciliation_50_vs_100.png",
        figures_dir / "figure_04_policy_effect_50_vs_100.png",
        figures_dir / "figure_05_completion_path_event_counts.png",
    ]
