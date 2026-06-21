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

    state_feature_coverage = dict(payload["state_feature_coverage_audit"].get("state_feature_group_coverage", {}))
    groups = list(state_feature_coverage.keys())
    coverage = [1 if bool(state_feature_coverage[group].get("covered", False)) else 0 for group in groups]

    fig1, ax1 = plt.subplots(figsize=(10, 4.5))
    positions = range(len(groups))
    ax1.bar(list(positions), coverage)
    ax1.set_ylim(0, 1.2)
    ax1.set_xticks(list(positions))
    ax1.set_xticklabels(groups, rotation=20, ha="right")
    _style(ax1, title="State Feature Group Coverage", ylabel="covered")
    figures.append(figures_dir / "figure_01_state_feature_group_coverage.png")
    _save(fig1, figures[-1])

    legacy_vs_new = payload["legacy_vs_new_state_profile_comparison"]
    legacy_candidate_100 = dict(legacy_vs_new.get("legacy_candidate_100", {}))
    new_candidate_100 = dict(legacy_vs_new.get("new_candidate_100", {}))
    action_labels = ["local", "horizontal", "vertical"]
    legacy_counts = [int(legacy_candidate_100.get("action_distribution", {}).get(label, 0)) for label in action_labels]
    new_counts = [int(new_candidate_100.get("action_distribution", {}).get(label, 0)) for label in action_labels]

    fig2, ax2 = plt.subplots(figsize=(10, 4.5))
    width = 0.35
    positions = range(len(action_labels))
    ax2.bar([x - width / 2 for x in positions], legacy_counts, width=width, label="legacy minimal")
    ax2.bar([x + width / 2 for x in positions], new_counts, width=width, label="deadline/queue profile")
    ax2.set_xticks(list(positions))
    ax2.set_xticklabels(action_labels)
    _style(ax2, title="Legacy vs New Candidate Action Distribution", ylabel="count")
    ax2.legend()
    figures.append(figures_dir / "figure_02_legacy_vs_new_action_distribution.png")
    _save(fig2, figures[-1])

    fig3, ax3 = plt.subplots(figsize=(10, 4.5))
    shares = [
        float(legacy_candidate_100.get("dominant_action_share", 0.0)),
        float(new_candidate_100.get("dominant_action_share", 0.0)),
    ]
    ax3.bar(["legacy", "new"], shares, color=["#6c8ebf", "#2f9e44"])
    ax3.set_ylim(0, 1.05)
    _style(ax3, title="Action Collapse Before and After Repair", ylabel="dominant share")
    figures.append(figures_dir / "figure_03_action_collapse_before_after.png")
    _save(fig3, figures[-1])

    selected_diag = dict(payload["selected_action_feasibility_diagnostics"])
    feasibility_values = [
        float(selected_diag.get("legacy_selected_action_feasible_ratio", 0.0)),
        float(selected_diag.get("new_state_selected_action_feasible_ratio", 0.0)),
    ]
    fig4, ax4 = plt.subplots(figsize=(10, 4.5))
    ax4.bar(["legacy", "new"], feasibility_values, color=["#b07aa1", "#4e79a7"])
    ax4.set_ylim(0, 1.05)
    _style(ax4, title="Selected-Action Feasibility Before and After Repair", ylabel="ratio")
    figures.append(figures_dir / "figure_04_selected_action_feasibility_before_after.png")
    _save(fig4, figures[-1])

    new_50_100 = dict(payload["state_profile_50_100_comparison"])
    by_checkpoint = list(new_50_100.get("by_checkpoint", []))
    candidate_50 = dict(by_checkpoint[0]) if len(by_checkpoint) > 0 else {}
    candidate_100 = dict(by_checkpoint[1]) if len(by_checkpoint) > 1 else {}
    completions = [float(candidate_50.get("completion_ratio", 0.0)), float(candidate_100.get("completion_ratio", 0.0))]
    drops = [float(candidate_50.get("drop_ratio", 0.0)), float(candidate_100.get("drop_ratio", 0.0))]
    pending = [max(0.0, 1.0 - c - d) for c, d in zip(completions, drops)]
    fig5, ax5 = plt.subplots(figsize=(10, 4.5))
    x = range(2)
    ax5.bar(x, completions, label="completion")
    ax5.bar(x, drops, bottom=completions, label="drop")
    ax5.bar(x, pending, bottom=[c + d for c, d in zip(completions, drops)], label="pending")
    ax5.set_xticks(list(x))
    ax5.set_xticklabels(["50", "100"])
    ax5.set_ylim(0, 1.05)
    _style(ax5, title="Completion/Drop Ratios for New State Profile", ylabel="ratio")
    ax5.legend()
    figures.append(figures_dir / "figure_05_completion_drop_50_vs_100_new_state.png")
    _save(fig5, figures[-1])

    return figures
