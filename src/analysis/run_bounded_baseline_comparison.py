from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer

OUTPUT_DIR = Path("artifacts/analysis/bounded-baseline-comparison")
PILOT_EPISODES = 3
PILOT_EPISODE_LENGTH = 50


def _config_hash(config: CampaignConfig) -> str:
    payload = json.dumps(config.to_dict(), sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _run_single_path(config: CampaignConfig, path_name: str) -> dict[str, Any]:
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

    for ep_idx in range(PILOT_EPISODES):
        summary = trainer._episode_rollout(
            episode_id=ep_idx,
            seed=config.seed_bundle.training_trace_generation_seed + ep_idx,
            episode_length=PILOT_EPISODE_LENGTH,
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

    avg_reward = total_reward / reward_count if reward_count > 0 else 0.0

    return {
        "path_name": path_name,
        "pilot_constraint": f"{PILOT_EPISODES} episodes x {PILOT_EPISODE_LENGTH} slots",
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
            "total_transition_count": total_transition_count,
            "episodes_completed": episodes_completed,
            "average_reward": avg_reward,
            "total_reward": total_reward,
            "reward_count": reward_count,
            "loss_summary": {
                "count": len(all_loss_values),
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
    }


def run_bounded_baseline_comparison() -> dict[str, Any]:
    legacy_config = CampaignConfig()
    paper_config = CampaignConfig.paper_default()

    legacy_result = _run_single_path(legacy_config, "legacy")
    paper_result = _run_single_path(paper_config, "paper_default")

    verdict = "pass" if (
        legacy_result["metrics"]["episodes_completed"] == PILOT_EPISODES
        and paper_result["metrics"]["episodes_completed"] == PILOT_EPISODES
        and legacy_result["metrics"]["loss_summary"]["all_finite"]
        and paper_result["metrics"]["loss_summary"]["all_finite"]
        and legacy_result["metrics"]["legal_action_only"]
        and paper_result["metrics"]["legal_action_only"]
        and legacy_result["metrics"]["total_transition_count"] > 0
        and paper_result["metrics"]["total_transition_count"] > 0
    ) else "fail"

    return {
        "comparison_type": "bounded-baseline-comparison",
        "pilot_constraint": f"{PILOT_EPISODES} episodes x {PILOT_EPISODE_LENGTH} slots",
        "legacy": legacy_result,
        "paper_default": paper_result,
        "verdict": verdict,
    }


def write_artifacts(report: dict[str, Any]) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "bounded-baseline-comparison.json"
    md_path = OUTPUT_DIR / "bounded-baseline-comparison.md"

    json_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Bounded Baseline Comparison Evidence",
        "",
        f"- **Verdict**: `{report['verdict']}`",
        f"- **Constraint**: {report['pilot_constraint']}",
        "",
    ]

    for path_name in ["legacy", "paper_default"]:
        path = report[path_name]
        cfg = path["config_summary"]
        m = path["metrics"]
        lines.extend([
            f"## {path_name.capitalize()} Path",
            "",
            "### Config",
            f"- state_dim: `{cfg['state_dim']}`",
            f"- action_count: `{cfg['action_count']}`",
            f"- lookback_w: `{cfg['lookback_w']}`",
            f"- config_hash: `{cfg['config_hash']}`... (sha256 prefix)",
            f"- full_campaign_enabled: `{cfg['full_campaign_enabled']}`",
            "",
            "### Metrics",
            f"- episodes_completed: `{m['episodes_completed']}`",
            f"- total_transition_count: `{m['total_transition_count']}`",
            f"- average_reward: `{m['average_reward']:.6f}`",
            f"- loss_count: `{m['loss_summary']['count']}`",
            f"- loss_all_finite: `{m['loss_summary']['all_finite']}`",
            f"- loss_no_nan: `{m['loss_summary']['no_nan']}`",
            f"- loss_no_inf: `{m['loss_summary']['no_inf']}` ",            f"- loss_mean: `{m['loss_summary']['mean']}`",
            f"- loss_min: `{m['loss_summary']['min']}`",
            f"- loss_max: `{m['loss_summary']['max']}`",
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

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


if __name__ == "__main__":
    report = run_bounded_baseline_comparison()
    json_path, md_path = write_artifacts(report)
    print(f"JSON: {json_path}")
    print(f"MD:   {md_path}")
    print(f"Verdict: {report['verdict']}")
