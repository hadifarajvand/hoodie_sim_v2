"""Build the config-only runbook payload for the full HOODIE paper campaign.

This module assembles the operational runbook (config, estimates, checkpoint/
resume, monitoring, abort conditions, expected artifacts, approximation note).
It NEVER trains. Artifact writing lives in ``runner.py``.
"""

from __future__ import annotations

from typing import Any

from .config import (
    FullPaperCampaignConfig,
    MEASURED_EVAL_SEC_PER_EPISODE,
    MEASURED_TRAIN_SEC_PER_EPISODE,
    build_full_campaign_config,
)

# Approximate on-disk sizes (bytes) derived from the validated network/replay shapes.
_PARAM_COUNT_APPROX = 2_200_000          # LSTM + 3x1024 + dueling heads
_BYTES_PER_FLOAT = 4
_CHECKPOINT_BYTES = _PARAM_COUNT_APPROX * _BYTES_PER_FLOAT * 3  # online + target + Adam state
_REPLAY_BYTES = 10_000 * (2 * 10 * 30 + 12) * _BYTES_PER_FLOAT  # 2 windows(WxD) + scalars


def _compute_estimates(cfg: FullPaperCampaignConfig) -> dict[str, Any]:
    train_s = cfg.estimated_train_seconds()
    eval_s = cfg.estimated_eval_seconds()
    n_checkpoints = cfg.number_of_training_episodes // cfg.checkpoint_every_episodes
    checkpoint_storage = n_checkpoints * _CHECKPOINT_BYTES
    total_storage = checkpoint_storage + _REPLAY_BYTES + 200 * 1024 * 1024  # +~200MB artifacts/logs
    return {
        "hardware_assumption": "single CPU core (no GPU; model is small, GPU gives little benefit)",
        "measured_train_sec_per_episode": MEASURED_TRAIN_SEC_PER_EPISODE,
        "measured_eval_sec_per_episode": MEASURED_EVAL_SEC_PER_EPISODE,
        "train_episodes": cfg.number_of_training_episodes,
        "estimated_train_hours": round(train_s / 3600.0, 2),
        "estimated_eval_hours": round(eval_s / 3600.0, 2),
        "estimated_total_hours_point": round((train_s + eval_s) / 3600.0, 2),
        "estimated_total_hours_range": [
            round((cfg.number_of_training_episodes * 1.6 + eval_s) / 3600.0, 2),
            round((cfg.number_of_training_episodes * 2.6 + eval_s) / 3600.0, 2),
        ],
        "estimate_caveat": (
            "Per-episode time may rise modestly once the replay buffer fills (more "
            "consistent per-step batch updates); range brackets 1.6-2.6 s/episode."
        ),
        "num_checkpoints": n_checkpoints,
        "storage_checkpoints_mb": round(checkpoint_storage / (1024 * 1024), 1),
        "storage_replay_snapshot_mb": round(_REPLAY_BYTES / (1024 * 1024), 1),
        "storage_total_estimate_mb": round(total_storage / (1024 * 1024), 1),
    }


def _checkpoint_resume_strategy(cfg: FullPaperCampaignConfig) -> dict[str, Any]:
    return {
        "checkpoint_cadence_episodes": cfg.checkpoint_every_episodes,
        "checkpoint_contents": [
            "online_network.state_dict()",
            "target_network.state_dict()",
            "optimizer.state_dict() (Adam moments)",
            "cumulative_training_episode_count",
            "optimizer_step_count",
            "target_sync_count",
            "exploration RNG state + cumulative episode index (for epsilon schedule)",
            "replay buffer snapshot (optional; deterministic re-fill also acceptable)",
            "seed bundle (training/eval trace generation, replay sampling)",
        ],
        "checkpoint_path_pattern": "artifacts/production/full-paper-campaign-run/checkpoints/ckpt_ep{episode:05d}.pt",
        "resume_protocol": [
            "Locate the highest-numbered ckpt_ep*.pt.",
            "Load all four state_dicts and counters; restore exploration episode index.",
            "Resume train_to_budget from cumulative_training_episode_count to N_E=5000.",
            "Epsilon is a pure function of the cumulative episode index, so resume is exact.",
            "Re-anchor the eval trace bank by seed (disjoint from training bank).",
        ],
        "determinism_notes": (
            "All seeds are fixed; epsilon is episode-indexed; target sync is episode-indexed. "
            "Resume reproduces the same trajectory as an uninterrupted run if replay is snapshotted; "
            "if replay is re-filled, minor sampling drift is possible but schedule/sync stay exact."
        ),
    }


def _monitoring(cfg: FullPaperCampaignConfig) -> dict[str, Any]:
    return {
        "progress_log": "tail -f artifacts/production/full-paper-campaign-run/progress.jsonl",
        "watch_loss_and_epsilon": (
            "Monitor: each checkpoint row should report loss_is_finite=true and the "
            "episode-indexed epsilon (1.0 at ep0 -> 0.0 at ep2500 -> 0.0 after)."
        ),
        "watch_action_distribution": (
            "Per-checkpoint candidate eval action_distribution should begin to spread "
            "from pure-local toward a mix as epsilon decays past ~ep2500."
        ),
        "watch_reconciliation": (
            "Every candidate/baseline row must keep reward_reconciled=true, "
            "terminal_reconciled=true, raw_vs_canonical_delta=0, coverage=1.0."
        ),
        "suggested_commands": [
            "grep -c 'checkpoint_written' artifacts/production/full-paper-campaign-run/progress.jsonl",
            "python -m src.analysis.paper_faithful_simulation_production.runner --json  # schema check on latest metrics",
        ],
    }


def _abort_conditions() -> list[dict[str, str]]:
    return [
        {"condition": "loss becomes NaN/Inf", "action": "abort; inspect td-target-loss; do not continue"},
        {"condition": "reward_reconciled or terminal_reconciled becomes false at any checkpoint",
         "action": "abort; reconciliation regression must be root-caused before resuming"},
        {"condition": "raw_vs_canonical_reward_delta != 0", "action": "abort; reward accounting corrupted"},
        {"condition": "terminal_event_coverage_ratio < 1.0", "action": "abort; horizon recovery incomplete"},
        {"condition": "wall-clock exceeds 2x upper estimate (~ >9h)", "action": "pause; profile per-episode cost"},
        {"condition": "checkpoint write fails / disk full", "action": "abort; free storage, resume from last good ckpt"},
        {"condition": "epsilon not reaching 0 by episode 2500", "action": "abort; schedule misconfigured"},
    ]


def _expected_artifacts() -> dict[str, Any]:
    return {
        "root": "artifacts/production/full-paper-campaign-run/",
        "per_checkpoint": [
            "candidate-metrics-ep{N}.json (paper-compatible schema)",
            "checkpoints/ckpt_ep{N}.pt",
        ],
        "final": [
            "candidate-metrics-full-campaign.json",
            "baseline-and-oracle-metrics.json",
            "reward-terminal-reconciliation-full-campaign.json",
            "learning-health-full-campaign.json",
            "readiness-gates.json",
            "claim-safety.json",
            "final-report.json",
            "final-report.md",
            "figures/ (learning curve, action distribution vs episode, candidate vs oracle)",
        ],
        "metric_schema": "PAPER_COMPATIBLE_METRIC_FIELDS (energy/cost = None, not_implemented)",
    }


def _multi_agent_approximation() -> dict[str, Any]:
    return {
        "paper_design": (
            "HOODIE is distributed multi-agent: each of the N=20 EAs runs its own DRL "
            "model (theta_n), trained on its own local task traffic; agents do not share "
            "parameters and do not know other agents' decisions (paper lines 99, 401, 405, "
            "587). Inference deploys N separate Q-models."
        ),
        "repo_implementation": (
            "A single shared-parameter trainer (one online + one target network) selects "
            "for whichever EA's task is current. This is a centralized shared-policy "
            "approximation of the paper's per-EA distributed models."
        ),
        "status": "known_approximation_not_repaired",
        "impact": (
            "A shared policy averaged over 20 heterogeneous EAs (different topology "
            "positions/neighbors) tends toward a generic policy and cannot personalize "
            "per-EA load-spreading the way per-EA models can. This is the leading "
            "candidate explanation for residual local-collapse beyond training budget."
        ),
        "implication_for_full_campaign": (
            "Running N_E=5000 on the shared-parameter trainer tests the shared-policy "
            "ceiling, NOT the paper's per-EA distributed ceiling. If the shared agent "
            "still underperforms the capacity-split oracle after 5000, the next step is a "
            "per-EA distributed trainer (20 models), each trained to its own N_E."
        ),
        "scope_note": "Implementing per-EA distributed training is out of scope for this config-only branch.",
    }


def build_runbook() -> dict[str, Any]:
    cfg = build_full_campaign_config()
    return {
        "title": "Full HOODIE Paper Campaign — Config-Only Runbook (N_E=5000)",
        "execute": False,
        "do_not_run_5000_here": True,
        "config": cfg.to_dict(),
        "compute_time_estimates": _compute_estimates(cfg),
        "checkpoint_resume_strategy": _checkpoint_resume_strategy(cfg),
        "monitoring": _monitoring(cfg),
        "abort_conditions": _abort_conditions(),
        "expected_artifacts": _expected_artifacts(),
        "multi_agent_approximation": _multi_agent_approximation(),
        "preserved_verified_mechanisms": [
            "per-task delayed reward credit assignment (validated on reward-signal branch)",
            "horizon-aware recovered reconciliation (delta=0, coverage=1.0)",
            "paper-compatible metric schema",
            "episode-based epsilon schedule + episode-based target sync (algorithm-fidelity branch)",
        ],
        "claim_safety": {
            "training_5000_run": False,
            "config_only": True,
            "paper_reproduction_claim_made": False,
            "performance_superiority_claim_made": False,
            "reward_function_modified": False,
            "environment_semantics_modified": False,
        },
        "how_to_execute_when_authorized": {
            "note": "Execution is a deliberate, separate, authorized action — NOT part of this branch.",
            "prerequisite": "explicit operator approval + storage/time budget confirmed",
            "command_sketch": (
                "A dedicated runner (e.g. --full-campaign-execute) would consume this config, "
                "honor checkpoint/resume, and emit the expected artifacts. It is intentionally "
                "NOT implemented here so this branch cannot start a 5000-episode run."
            ),
        },
    }
