from __future__ import annotations

from pathlib import Path
from typing import Any

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
    figures: list[Path] = []

    decision_audit = dict(payload["decision_state_injection_audit"])
    train_eval = dict(payload["train_eval_state_profile_consistency"])
    replay_alignment = dict(payload["replay_state_alignment_audit"])

    fig1, ax1 = plt.subplots(figsize=(10, 4.5))
    ax1.bar(
        ["decision injection", "train/eval profile", "replay alignment"],
        [
            1.0 if decision_audit.get("decision_state_contains_current_task", False) else 0.0,
            1.0 if train_eval.get("train_eval_state_profile_match", False) else 0.0,
            1.0 if replay_alignment.get("replay_transition_state_matches_action_state", False) else 0.0,
        ],
    )
    ax1.set_ylim(0, 1.1)
    _style(ax1, title="Decision-Time State Injection Checks", ylabel="passed")
    figures.append(figures_dir / "figure_01_decision_state_injection_before_after.png")
    _save(fig1, figures[-1])

    policy_effect = dict(payload["policy_effect_after_decision_state_fix"])
    candidate_50 = dict(policy_effect.get("candidate_policy_at_50", {}))
    candidate_100 = dict(policy_effect.get("candidate_policy_at_100", {}))
    action_labels = ["local", "horizontal", "vertical"]
    fig2, ax2 = plt.subplots(figsize=(10, 4.5))
    width = 0.35
    positions = range(len(action_labels))
    ax2.bar([x - width / 2 for x in positions], [int(candidate_50.get("action_distribution", {}).get(label, 0)) for label in action_labels], width=width, label="50 episodes")
    ax2.bar([x + width / 2 for x in positions], [int(candidate_100.get("action_distribution", {}).get(label, 0)) for label in action_labels], width=width, label="100 episodes")
    ax2.set_xticks(list(positions))
    ax2.set_xticklabels(action_labels)
    ax2.legend()
    _style(ax2, title="Action Distribution After Decision-State Fix", ylabel="count")
    figures.append(figures_dir / "figure_02_action_distribution_after_decision_state_fix.png")
    _save(fig2, figures[-1])

    action_collapse = dict(payload["action_collapse_after_decision_state_fix"])
    fig3, ax3 = plt.subplots(figsize=(10, 4.5))
    ax3.bar(
        ["legacy", "new"],
        [
            float(action_collapse.get("legacy", {}).get("dominant_action_share", 0.0)),
            float(action_collapse.get("new_state", {}).get("dominant_action_share", 0.0)),
        ],
        color=["#6c8ebf", "#2f9e44"],
    )
    ax3.set_ylim(0, 1.05)
    _style(ax3, title="Action Collapse After Decision-State Fix", ylabel="dominant share")
    figures.append(figures_dir / "figure_03_action_collapse_after_decision_state_fix.png")
    _save(fig3, figures[-1])

    selected_diag = dict(payload["selected_action_feasibility_after_decision_state_fix"])
    fig4, ax4 = plt.subplots(figsize=(10, 4.5))
    ax4.bar(
        ["legacy", "new"],
        [
            float(selected_diag.get("legacy_selected_action_feasible_ratio", 0.0)),
            float(selected_diag.get("new_state_selected_action_feasible_ratio", 0.0)),
        ],
        color=["#b07aa1", "#4e79a7"],
    )
    ax4.set_ylim(0, 1.05)
    _style(ax4, title="Selected-Action Feasibility After Decision-State Fix", ylabel="ratio")
    figures.append(figures_dir / "figure_04_selected_action_feasibility_after_decision_state_fix.png")
    _save(fig4, figures[-1])

    fig5, ax5 = plt.subplots(figsize=(10, 4.5))
    x = range(2)
    completions = [float(candidate_50.get("completion_ratio", 0.0)), float(candidate_100.get("completion_ratio", 0.0))]
    drops = [float(candidate_50.get("drop_ratio", 0.0)), float(candidate_100.get("drop_ratio", 0.0))]
    pending = [max(0.0, 1.0 - c - d) for c, d in zip(completions, drops)]
    ax5.bar(x, completions, label="completion")
    ax5.bar(x, drops, bottom=completions, label="drop")
    ax5.bar(x, pending, bottom=[c + d for c, d in zip(completions, drops)], label="pending")
    ax5.set_xticks(list(x))
    ax5.set_xticklabels(["50", "100"])
    ax5.set_ylim(0, 1.05)
    ax5.legend()
    _style(ax5, title="Completion/Drop Ratios After Decision-State Fix", ylabel="ratio")
    figures.append(figures_dir / "figure_05_completion_drop_after_decision_state_fix.png")
    _save(fig5, figures[-1])

    return figures
