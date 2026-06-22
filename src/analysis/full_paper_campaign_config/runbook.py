"""Emit the config-only runbook + artifacts for the full HOODIE paper campaign.

This module writes configuration, estimates, and operational runbook artifacts.
It NEVER trains. The only "run" here is artifact generation.

Run::

    python -m src.analysis.full_paper_campaign_config.runbook --json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .config import (
    FullPaperCampaignConfig,
    MEASURED_EVAL_SEC_PER_EPISODE,
    MEASURED_TRAIN_SEC_PER_EPISODE,
    build_full_campaign_config,
)

OUT_DIR = Path("artifacts/production/full-paper-campaign-config-only")
FIGURES = OUT_DIR / "figures"

# Approximate on-disk sizes (bytes) derived from the validated network/replay shapes.
_PARAM_COUNT_APPROX = 2_200_000          # LSTM + 3x1024 + dueling heads
_BYTES_PER_FLOAT = 4
_CHECKPOINT_BYTES = _PARAM_COUNT_APPROX * _BYTES_PER_FLOAT * 3  # online + target + Adam state
_REPLAY_BYTES = 10_000 * (2 * 10 * 30 + 12) * _BYTES_PER_FLOAT  # 2 windows(WxD) + scalars


def _commit() -> str:
    import subprocess

    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


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


def _figure(cfg: FullPaperCampaignConfig) -> str:
    FIGURES.mkdir(parents=True, exist_ok=True)
    eps_x = list(range(0, cfg.number_of_training_episodes + 1, 100))
    eps_y = [cfg.epsilon_at(e) for e in eps_x]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(eps_x, eps_y, color="#1f77b4")
    ax.axvline(cfg.epsilon_decay_episodes, color="red", linestyle="--", label="N_E/2 = 2500")
    ax.set_xlabel("training episode"); ax.set_ylabel("epsilon")
    ax.set_title("Paper epsilon schedule (linear 1->0 over first N_E/2, then 0)")
    ax.legend(); fig.tight_layout()
    p = FIGURES / "figure_01_paper_epsilon_schedule.png"
    fig.savefig(p, dpi=110); plt.close(fig)
    return str(p)


def write_campaign_config_artifacts(emit_json: bool = False) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    runbook = build_runbook()
    runbook["commit_sha"] = _commit()

    (OUT_DIR / "full-campaign-config.json").write_text(json.dumps(runbook["config"], indent=2))
    (OUT_DIR / "compute-time-storage-estimates.json").write_text(json.dumps(runbook["compute_time_estimates"], indent=2))
    (OUT_DIR / "checkpoint-resume-strategy.json").write_text(json.dumps(runbook["checkpoint_resume_strategy"], indent=2))
    (OUT_DIR / "monitoring-and-abort.json").write_text(json.dumps(
        {"monitoring": runbook["monitoring"], "abort_conditions": runbook["abort_conditions"]}, indent=2))
    (OUT_DIR / "expected-artifacts.json").write_text(json.dumps(runbook["expected_artifacts"], indent=2))
    (OUT_DIR / "multi-agent-approximation.json").write_text(json.dumps(runbook["multi_agent_approximation"], indent=2))
    (OUT_DIR / "claim-safety.json").write_text(json.dumps(runbook["claim_safety"], indent=2))
    (OUT_DIR / "runbook.json").write_text(json.dumps(runbook, indent=2))
    fig = _figure(build_full_campaign_config())
    runbook["figure"] = fig
    (OUT_DIR / "runbook.md").write_text(_markdown(runbook))

    if emit_json:
        print(json.dumps({
            "config_only": True,
            "execute": runbook["execute"],
            "N_E": runbook["config"]["number_of_training_episodes_N_E"],
            "estimated_total_hours": runbook["config"]["estimated_total_hours"],
            "estimated_total_hours_range": runbook["compute_time_estimates"]["estimated_total_hours_range"],
            "storage_total_estimate_mb": runbook["compute_time_estimates"]["storage_total_estimate_mb"],
            "multi_agent_status": runbook["multi_agent_approximation"]["status"],
        }, indent=2))
    return runbook


def _markdown(r: dict[str, Any]) -> str:
    cfg = r["config"]; est = r["compute_time_estimates"]; ma = r["multi_agent_approximation"]
    L = [
        "# Full HOODIE Paper Campaign — Config-Only Runbook (N_E=5000)",
        "",
        "> **CONFIG ONLY — this branch does not run the campaign.** Executing 5000 episodes",
        "> is a deliberate, separately authorized action. Nothing here starts training.",
        "",
        "## 1. Configuration (paper-faithful)",
        f"- N_E (training episodes): **{cfg['number_of_training_episodes_N_E']}**  | T = {cfg['episode_length_T']} | N agents = {cfg['number_of_agents_N']}",
        f"- Epsilon: {cfg['epsilon']['start']} -> {cfg['epsilon']['final']} linearly over first {cfg['epsilon']['decay_episodes']} episodes "
        f"({cfg['epsilon']['schedule_unit']}-based), 0 after. _{cfg['epsilon']['paper_reference']}_",
        f"- Target update: every {cfg['target_update']['frequency_N_copy']} {cfg['target_update']['unit']}s. _{cfg['target_update']['paper_reference']}_",
        f"- Optimizer: {cfg['optimizer']['name']} lr={cfg['optimizer']['learning_rate']} loss={cfg['optimizer']['loss']} | gamma={cfg['gamma']} | batch={cfg['batch_size']} | replay={cfg['replay_memory_capacity']}",
        f"- Network: LSTM {cfg['lstm_cells']} cells (lookback {cfg['lstm_lookback_w']}) -> {cfg['q_network_hidden_layers']} -> dueling V/A | Double DQN",
        f"- Reward: {cfg['reward_equation']}",
        f"- Credit assignment: {cfg['credit_assignment']} | Reconciliation: {cfg['reconciliation_profile']}",
        f"- State profile: {cfg['state_representation_profile']} | Calibration: {cfg['calibration_profile']}",
        f"- Eval: {cfg['evaluation_episode_count']} episodes at checkpoints {cfg['eval_at_episodes']}",
        "",
        "## 2. Compute / time / storage estimates",
        f"- Hardware assumption: {est['hardware_assumption']}",
        f"- Measured: {est['measured_train_sec_per_episode']} s/train-episode, {est['measured_eval_sec_per_episode']} s/eval-episode",
        f"- **Training: ~{est['estimated_train_hours']} h** | Evaluation: ~{est['estimated_eval_hours']} h | "
        f"**Total point estimate: ~{cfg['estimated_total_hours']} h** (range {est['estimated_total_hours_range']} h)",
        f"- Caveat: {est['estimate_caveat']}",
        f"- Storage: ~{est['storage_checkpoints_mb']} MB checkpoints ({est['num_checkpoints']} ckpts) + "
        f"~{est['storage_replay_snapshot_mb']} MB replay + artifacts ≈ **~{est['storage_total_estimate_mb']} MB total**",
        "",
        "## 3. Checkpoint / resume strategy",
        f"- Checkpoint every **{r['checkpoint_resume_strategy']['checkpoint_cadence_episodes']} episodes** to "
        f"`{r['checkpoint_resume_strategy']['checkpoint_path_pattern']}`",
        "- Checkpoint contents: " + "; ".join(r["checkpoint_resume_strategy"]["checkpoint_contents"]),
        "- Resume protocol:",
    ]
    for step in r["checkpoint_resume_strategy"]["resume_protocol"]:
        L.append(f"  - {step}")
    L += [f"- Determinism: {r['checkpoint_resume_strategy']['determinism_notes']}", "",
          "## 4. Monitoring"]
    for k, v in r["monitoring"].items():
        if isinstance(v, list):
            L.append(f"- {k}:")
            L += [f"  - `{c}`" for c in v]
        else:
            L.append(f"- {k}: {v}")
    L += ["", "## 5. Abort conditions"]
    for a in r["abort_conditions"]:
        L.append(f"- **{a['condition']}** -> {a['action']}")
    L += ["", "## 6. Expected artifacts",
          f"- Root: `{r['expected_artifacts']['root']}`",
          "- Per checkpoint: " + "; ".join(r["expected_artifacts"]["per_checkpoint"]),
          "- Final: " + "; ".join(r["expected_artifacts"]["final"]),
          f"- Metric schema: {r['expected_artifacts']['metric_schema']}",
          "",
          "## 7. Remaining approximation — shared-parameter trainer vs paper per-EA distributed models",
          f"- **Paper design:** {ma['paper_design']}",
          f"- **Repo implementation:** {ma['repo_implementation']}",
          f"- **Status:** `{ma['status']}`",
          f"- **Impact:** {ma['impact']}",
          f"- **Implication for the full campaign:** {ma['implication_for_full_campaign']}",
          f"- **Scope:** {ma['scope_note']}",
          "",
          "## 8. Claim safety",
          f"- training_5000_run: {r['claim_safety']['training_5000_run']} | config_only: {r['claim_safety']['config_only']}",
          "- No paper-reproduction or superiority claims; reward & environment unmodified.",
          "",
          "## 9. How to execute (when authorized)",
          f"- {r['how_to_execute_when_authorized']['note']}",
          f"- Prerequisite: {r['how_to_execute_when_authorized']['prerequisite']}",
          f"- {r['how_to_execute_when_authorized']['command_sketch']}",
    ]
    return "\n".join(L)


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit config-only full-campaign runbook (never trains).")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--execute", action="store_true", help="(blocked) refuses to run 5000")
    args = parser.parse_args()
    if args.execute:
        raise SystemExit(
            "Refusing to execute: this is a config-only runbook generator. "
            "Running N_E=5000 is a separate, explicitly authorized action and is not implemented here."
        )
    write_campaign_config_artifacts(emit_json=args.json)


if __name__ == "__main__":
    main()
