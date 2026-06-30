#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Tuple

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer


def _config_hash(config: CampaignConfig) -> str:
    payload = json.dumps(config.to_dict(), sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def run_completion_positive_diagnostic(
    episodes: int = 3,
    episode_length: int = 200,
) -> Dict[str, Any]:
    """
    Run a bounded completion-positive diagnostic for the paper_default HOODIE baseline.

    Returns a report dictionary with the following keys:
      - diagnostic_type
      - bounded_constraint
      - config_summary
      - episode_summaries
      - metrics
      - verdict
      - interpretation
    """
    config = CampaignConfig.paper_default()
    trainer = DDQNTrainer(config)
    config_hash = _config_hash(config)

    episode_summaries: list[dict[str, Any]] = []
    all_loss_values: list[float] = []
    total_transition_count = 0
    total_completed = 0
    total_dropped = 0
    total_pending_at_horizon = 0
    total_reward = 0.0
    reward_count = 0
    illegal_action_count = 0

    for ep_idx in range(episodes):
        summary = trainer._episode_rollout(
            episode_id=ep_idx,
            seed=config.seed_bundle.training_trace_generation_seed + ep_idx,
            episode_length=episode_length,
            training=True,
        )
        episode_summaries.append(summary)
        all_loss_values.extend(summary["loss_values"])
        total_transition_count += summary["transition_count"]
        total_completed += summary["completed_task_count"]
        total_dropped += summary["dropped_task_count"]
        total_pending_at_horizon += summary["pending_at_horizon_count"]
        illegal_action_count += summary["illegal_action_count"]

    transitions = trainer.replay_buffer.as_list()
    for t in transitions:
        if t.reward_available:
            total_reward += float(t.reward)
            reward_count += 1

    loss_finite = all(math.isfinite(v) for v in all_loss_values) if all_loss_values else True
    no_nan = not any(math.isnan(v) for v in all_loss_values) if all_loss_values else True
    no_inf = not any(math.isinf(v) for v in all_loss_values) if all_loss_values else True
    legal_only = illegal_action_count == 0
    episodes_completed = len(episode_summaries)
    all_episodes_ran = episodes_completed == episodes

    avg_reward = total_reward / reward_count if reward_count > 0 else 0.0

    # Verdict rules
    if (
        all_episodes_ran
        and loss_finite
        and no_nan
        and no_inf
        and legal_only
        and total_transition_count > 0
    ):
        if total_completed > 0:
            verdict = "pass_completion_positive"
        else:
            verdict = "pass_mechanics_only"
    else:
        verdict = "fail"

    # Interpretation
    if verdict == "pass_completion_positive":
        interpretation = (
            "Full-campaign readiness can proceed to final approval gate. "
            "Non-zero task completions observed in bounded diagnostic."
        )
    elif verdict == "pass_mechanics_only":
        interpretation = (
            "Full-campaign should not start yet; environment/task-arrival timing needs audit. "
            "Zero task completions observed in bounded diagnostic."
        )
    else:
        interpretation = "Diagnostic failed. Check logs for details."

    report: dict[str, Any] = {
        "diagnostic_type": "completion_positive_diagnostic",
        "bounded_constraint": f"{episodes} episodes x {episode_length} slots",
        "config_summary": {
            "state_dim": config.state_dim,
            "action_count": config.action_count,
            "lookback_w": config.lookback_w,
            "learning_rate": config.learning_rate,
            "gamma": config.gamma,
            "batch_size": config.batch_size,
            "horizontal_data_rate_mbps": config.horizontal_data_rate_mbps,
            "vertical_data_rate_mbps": config.vertical_data_rate_mbps,
            "full_campaign_enabled": config.full_campaign_enabled,
            "config_hash": config_hash[:16],
        },
        "episode_summaries": [
            {
                "episode_id": i,
                "transition_count": s["transition_count"],
                "completed_task_count": s["completed_task_count"],
                "dropped_task_count": s["dropped_task_count"],
                "pending_at_horizon_count": s["pending_at_horizon_count"],
                "illegal_action_count": s["illegal_action_count"],
                "loss_count": len(s["loss_values"]),
            }
            for i, s in enumerate(episode_summaries)
        ],
        "metrics": {
            "episodes_completed": episodes_completed,
            "episode_length": episode_length,
            "total_transition_count": total_transition_count,
            "average_reward": avg_reward,
            "total_reward": total_reward,
            "reward_count": reward_count,
            "loss_count": len(all_loss_values),
            "loss_summary": {
                "all_finite": loss_finite,
                "no_nan": no_nan,
                "no_inf": no_inf,
                "min": min(all_loss_values) if all_loss_values else None,
                "max": max(all_loss_values) if all_loss_values else None,
                "mean": mean(all_loss_values) if all_loss_values else None,
            },
            "completed_task_count": total_completed,
            "dropped_task_count": total_dropped,
            "pending_at_horizon_count": total_pending_at_horizon,
            "illegal_action_count": illegal_action_count,
            "legal_action_only": legal_only,
            "optimizer_step_count": trainer.optimizer_step_count,
            "target_sync_count": trainer.target_sync_count,
            "replay_size": len(trainer.replay_buffer),
        },
        "verdict": verdict,
        "interpretation": interpretation,
    }

    return report


def write_artifacts(report: dict[str, Any]) -> tuple[Path, Path]:
    OUTPUT_DIR = Path("artifacts/analysis/completion-positive-diagnostic")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "completion-positive-diagnostic.json"
    md_path = OUTPUT_DIR / "completion-positive-diagnostic.md"

    json_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    verdict = report["verdict"]
    m = report["metrics"]
    cfg = report["config_summary"]
    lines = [
        f"# Completion-Positive Diagnostic Evidence",
        "",
        f"- **Verdict**: `{verdict}`",
        f"- **Constraint**: {report['bounded_constraint']}",
        "",
    ]

    for path_name in ["config_summary", "metrics"]:
        if path_name == "config_summary":
            cfg = report["config_summary"]
            lines.extend([
                "## Config Confirmation",
                "",
                f"- state_dim: `{cfg['state_dim']}`",
                f"- action_count: `{cfg['action_count']}`",
                f"- lookback_w: `{cfg['lookback_w']}`",
                f"- learning_rate: `{cfg['learning_rate']}`",
                f"- gamma: `{cfg['gamma']}`",
                f"- batch_size: `{cfg['batch_size']}`",
                f"- horizontal_data_rate_mbps: `{cfg['horizontal_data_rate_mbps']}`",
                f"- vertical_data_rate_mbps: `{cfg['vertical_data_rate_mbps']}`",
                f"- full_campaign_enabled: `{cfg['full_campaign_enabled']}`",
                f"- config_hash: `{cfg['config_hash']}`... (sha256 prefix)",
                "",
            ])
        else:
            m = report["metrics"]
            lines.extend([
                "## Metrics Summary",
                "",
                f"- episodes_completed: `{m['episodes_completed']}`",
                f"- episode_length: `{m['episode_length']}`",
                f"- total_transition_count: `{m['total_transition_count']}`",
                f"- average_reward: `{m['average_reward']:.6f}`",
                f"- total_reward: `{m['total_reward']:.6f}`",
                f"- reward_count: `{m['reward_count']}`",
                f"- loss_count: `{m['loss_count']}`",
                f"- loss_all_finite: `{m['loss_summary']['all_finite']}`",
                f"- loss_no_nan: `{m['loss_summary']['no_nan']}`",
                f"- loss_no_inf: `{m['loss_summary']['no_inf']}`",
                f"- loss_min: `{m['loss_summary']['min']:.6f}`" if m['loss_summary']['min'] is not None else "- loss_min: `None`",
                f"- loss_max: `{m['loss_summary']['max']:.6f}`" if m['loss_summary']['max'] is not None else "- loss_max: `None`",
                f"- loss_mean: `{m['loss_summary']['mean']:.6f}`" if m['loss_summary']['mean'] is not None else "- loss_mean: `None`",
                f"- completed_task_count: `{m['completed_task_count']}`",
                f"- dropped_task_count: `{m['dropped_task_count']}`",
                f"- pending_at_horizon_count: `{m['pending_at_horizon_count']}`",
                f"- illegal_action_count: `{m['illegal_action_count']}`",
                f"- legal_action_only: `{m['legal_action_only']}`",
                f"- optimizer_step_count: `{m['optimizer_step_count']}`",
                f"- target_sync_count: `{m['target_sync_count']}`",
                f"- replay_size: `{m['replay_size']}`",
                "",
            ])

    lines.extend([
        "## Interpretation",
        "",
        report["interpretation"],
        "",
    ])

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


if __name__ == "__main__":
    report = run_completion_positive_diagnostic()
    json_path, md_path = write_artifacts(report)
    print(f"JSON: {json_path}")
    print(f"MD:   {md_path}")
    print(f"Verdict: {report['verdict']}")