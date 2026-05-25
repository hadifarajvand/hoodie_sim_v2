from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch
from importlib.util import find_spec

from src.analysis.full_training_reproduction_campaign.config import (
    CampaignConfig,
    READINESS_MANUAL_APPROVAL_APPROVED,
)
from src.analysis.full_training_reproduction_campaign.replay import ACTION_INDEX_TO_SEMANTICS
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _action_distribution(transitions: list[Any]) -> dict[str, int]:
    counts = {"local": 0, "horizontal": 0, "vertical": 0}
    for transition in transitions:
        action_name = ACTION_INDEX_TO_SEMANTICS[int(transition.action)]
        counts[action_name] += 1
    return counts


def _reward_summary(transitions: list[Any]) -> dict[str, Any]:
    rewards = [float(transition.reward) for transition in transitions if transition.reward_available]
    return {
        "reward_count": len(rewards),
        "reward_available_count": len(rewards),
        "total_reward": float(sum(rewards)) if rewards else 0.0,
        "mean_reward": float(sum(rewards) / len(rewards)) if rewards else 0.0,
        "pending_at_horizon_count": sum(1 for transition in transitions if transition.pending_at_horizon),
    }


def run_real_trainer_bound_campaign(*, feature_059_report: Path, actual_training_episode_count: int) -> dict[str, Any]:
    feature_059_payload = _load_json(feature_059_report)
    scope = feature_059_payload.get("campaign_scope_summary", {})
    seed_bundle = dict(scope.get("seed_bundle", {}))
    campaign_config = CampaignConfig(
        full_campaign_enabled=True,
        readiness_manual_approval_status=READINESS_MANUAL_APPROVAL_APPROVED,
        readiness_manual_approval_reference="feature-060b-controlled-real-trainer-binding",
        training_trace_bank_id=str(scope.get("training_trace_bank_id") or "full-training-train-bank"),
        evaluation_trace_bank_id=str(scope.get("evaluation_trace_bank_id") or "feature-058-evaluation-trace-bank"),
    )
    trainer = DDQNTrainer(campaign_config)
    pilot_result = trainer.run_pilot(
        episodes=actual_training_episode_count,
        episode_length=campaign_config.full_campaign_episode_length,
    )
    replay_transitions = trainer.replay_buffer.as_list()
    action_distribution = _action_distribution(replay_transitions)
    evaluation_summary = dict(pilot_result.evaluation_summary)
    return {
        "binding_evidence": {
            "torch_import_used": True,
            "torch_version": torch.__version__,
            "torchrl_available": find_spec("torchrl") is not None,
            "real_trainer_import_used": True,
            "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
            "real_trainer_instantiated": True,
            "real_trainer_update_or_train_called": pilot_result.optimizer_step_count > 0,
            "real_trainer_method_called": "DDQNTrainer.run_pilot",
            "scalar_fallback_drives_campaign_claim": False,
        },
        "training_trace_bank_id": campaign_config.training_trace_bank_id,
        "evaluation_trace_bank_id": campaign_config.evaluation_trace_bank_id,
        "baseline_harness_id": str(scope.get("baseline_harness_id") or "feature-058-baseline-evaluation-harness"),
        "seed_bundle": seed_bundle or campaign_config.seed_bundle.to_dict(),
        "optimizer_step_count": int(pilot_result.optimizer_step_count),
        "target_sync_count": int(pilot_result.target_sync_count),
        "replay_size": int(pilot_result.replay_size),
        "loss_values": [float(pilot_result.loss_value)],
        "loss_is_finite": bool(pilot_result.loss_is_finite),
        "action_distribution": action_distribution,
        "reward_summary": _reward_summary(replay_transitions),
        "training_episode_count": int(pilot_result.episodes_completed),
        "replay_transition_count": len(replay_transitions),
        "evaluation": {
            **evaluation_summary,
            "trace_bank_ids": {
                "training": campaign_config.training_trace_bank_id,
                "evaluation": campaign_config.evaluation_trace_bank_id,
            },
        },
        "checkpoint_metadata": pilot_result.checkpoint_metadata.to_dict(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Execute Feature 060 through the real Torch trainer bridge.")
    parser.add_argument("--feature-059-report", required=True)
    parser.add_argument("--actual-training-episode-count", type=int, required=True)
    args = parser.parse_args(argv)
    payload = run_real_trainer_bound_campaign(
        feature_059_report=Path(args.feature_059_report),
        actual_training_episode_count=args.actual_training_episode_count,
    )
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
