"""Compute/time/storage estimates for the full paper campaign (config only).

All time figures are grounded in measured per-episode timing from this repo
(single CPU core). Storage figures derive from the validated network/replay shapes.
No training is performed here.
"""

from __future__ import annotations

from typing import Any

from .config import (
    FullPaperCampaignConfig,
    MEASURED_EVAL_SEC_PER_EPISODE,
    MEASURED_TRAIN_SEC_PER_EPISODE,
)

# Per-episode timing bracket (s/episode). Per-episode cost can rise modestly once
# the replay buffer fills and per-step batch updates run consistently.
TRAIN_SEC_LOW = 1.6
TRAIN_SEC_EXPECTED = MEASURED_TRAIN_SEC_PER_EPISODE  # 1.73 measured
TRAIN_SEC_HIGH = 2.6

# Approximate on-disk sizes derived from the validated shapes.
PARAM_COUNT_APPROX = 2_200_000           # LSTM + 3x1024 + dueling heads
BYTES_PER_FLOAT = 4
CHECKPOINT_BYTES = PARAM_COUNT_APPROX * BYTES_PER_FLOAT * 3   # online + target + Adam
REPLAY_SNAPSHOT_BYTES = 10_000 * (2 * 10 * 30 + 12) * BYTES_PER_FLOAT
ARTIFACT_OVERHEAD_BYTES = 200 * 1024 * 1024  # metrics/figures/logs headroom


def _hours(seconds: float) -> float:
    return round(seconds / 3600.0, 2)


def build_estimates(cfg: FullPaperCampaignConfig) -> dict[str, Any]:
    n_train = cfg.number_of_training_episodes
    candidate_evals = len(cfg.eval_at_episodes)
    comparator_evals = 4 + 2  # 4 fixed baselines + 2 oracle policies
    eval_episode_total = (candidate_evals + comparator_evals) * cfg.evaluation_episode_count

    train_low = n_train * TRAIN_SEC_LOW
    train_exp = n_train * TRAIN_SEC_EXPECTED
    train_high = n_train * TRAIN_SEC_HIGH
    eval_s = eval_episode_total * MEASURED_EVAL_SEC_PER_EPISODE

    n_checkpoints = n_train // cfg.checkpoint_every_episodes
    checkpoint_storage = n_checkpoints * CHECKPOINT_BYTES
    total_storage = checkpoint_storage + REPLAY_SNAPSHOT_BYTES + ARTIFACT_OVERHEAD_BYTES

    return {
        "hardware_assumption": "single CPU core (no GPU; small model, GPU yields little benefit)",
        "measured_train_sec_per_episode": TRAIN_SEC_EXPECTED,
        "measured_eval_sec_per_episode": MEASURED_EVAL_SEC_PER_EPISODE,
        "train_seconds_per_episode_range": {"low": TRAIN_SEC_LOW, "expected": TRAIN_SEC_EXPECTED, "high": TRAIN_SEC_HIGH},
        "eval_seconds_per_episode": MEASURED_EVAL_SEC_PER_EPISODE,
        "train_episodes": n_train,
        "eval_episode_total": eval_episode_total,
        "training_hours": {"low": _hours(train_low), "expected": _hours(train_exp), "high": _hours(train_high)},
        "evaluation_hours": _hours(eval_s),
        "total_wall_hours": {
            "low": _hours(train_low + eval_s),
            "expected": _hours(train_exp + eval_s),
            "high": _hours(train_high + eval_s),
        },
        "checkpoint_count": n_checkpoints,
        "checkpoint_interval_episodes": cfg.checkpoint_every_episodes,
        "storage_checkpoints_mb": round(checkpoint_storage / (1024 * 1024), 1),
        "storage_replay_snapshot_mb": round(REPLAY_SNAPSHOT_BYTES / (1024 * 1024), 1),
        "storage_artifact_overhead_mb": round(ARTIFACT_OVERHEAD_BYTES / (1024 * 1024), 1),
        "storage_total_estimate_mb": round(total_storage / (1024 * 1024), 1),
        "estimate_caveat": (
            "Per-episode time may rise modestly once replay fills; low/expected/high "
            "bracket 1.6/1.73/2.6 s per training episode."
        ),
    }
