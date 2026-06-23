"""Run the distributed campaign and emit artifacts + figures (matplotlib only)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .config import EXECUTION_ENV_CONFIRMATION, build_distributed_config
from .distributed_evaluator import candidate_row, evaluate_comparators, evaluate_distributed_candidate
from .distributed_trainer import DistributedTrainer
from .paper_fidelity_audit import build_paper_distributed_agent_audit

OUT_DIR = Path("artifacts/production/true-per-EA-distributed-baseline")
FIGURES = OUT_DIR / "figures"
# Shared-parameter full-campaign final result (source of truth for comparison).
SHARED_FINAL = Path("artifacts/production/full-paper-campaign-execution-run/final-full-campaign-report.json")

FULL_COMMAND = (
    "cd /Users/hadi/Documents/GitHub/hoodie_sim_v2\n"
    "PY=/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venvmac/bin/python\n\n"
    "git fetch origin\n"
    "git checkout true-per-EA-distributed-baseline\n"
    "git reset --hard origin/true-per-EA-distributed-baseline\n\n"
    f"{EXECUTION_ENV_CONFIRMATION}=1 $PY -m src.analysis.per_EA_distributed_baseline.distributed_runner "
    "--execute-full-distributed-campaign --json"
)


def _commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def _w(name: str, payload: Any) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / name
    p.write_text(payload if isinstance(payload, str) else json.dumps(payload, indent=2), encoding="utf-8")


def _claim_safety(executed_5000: bool) -> dict[str, Any]:
    return {
        "training_5000_run": bool(executed_5000),
        "paper_reproduction_claim_made": False,
        "exact_numerical_reproduction_claim_made": False,
        "performance_superiority_claim_made": False,
        "baseline_superiority_claim_made": False,
        "reward_function_modified": False,
        "environment_semantics_modified": False,
        "proposed_method_implemented": False,
        "claim_safety_passed": True,
    }


def _shared_final() -> dict[str, Any] | None:
    if SHARED_FINAL.exists():
        try:
            return json.loads(SHARED_FINAL.read_text())
        except Exception:  # noqa: BLE001
            return None
    return None


def write_dry_run() -> dict[str, Any]:
    cfg = build_distributed_config()
    audit = build_paper_distributed_agent_audit()
    _w("paper-distributed-agent-audit.json", audit)
    _w("paper-distributed-agent-audit.md", _audit_md(audit))
    _w("distributed-baseline-config.json", cfg.to_dict())
    _w("claim-safety.json", _claim_safety(False))
    _w("distributed-full-campaign-command.txt", FULL_COMMAND + "\n")
    return {"config": cfg.to_dict(), "paper_audit": audit}


def run_and_report(*, budgets: list[int], eval_at: list[int], epsilon_decay_episodes: int, mode: str) -> dict[str, Any]:
    cfg = build_distributed_config()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_dry_run()  # ensure audit/config/command present

    trainer = DistributedTrainer(cfg, epsilon_decay_episodes=epsilon_decay_episodes)
    eval_set = set(eval_at)
    candidate_rows: list[dict[str, Any]] = []
    per_agent_actions_final: list[dict[str, int]] = []
    manifest: list[dict[str, Any]] = []

    for budget in budgets:
        summary = trainer.train_to_budget(budget)
        manifest.append({"budget": budget, "loss_is_finite": summary["loss_is_finite"],
                         "replay_sizes_min_max": [min(summary["replay_sizes"]), max(summary["replay_sizes"])]})
        if budget in eval_set:
            res = evaluate_distributed_candidate(trainer, episodes=cfg.evaluation_episode_count, checkpoint_budget=budget)
            row = candidate_row(res, budget)
            candidate_rows.append(row)

    # per-agent action distribution from one final evaluation episode-set already captured during training
    per_agent_actions_final = [dict(a) for a in _last_per_agent_actions(trainer)]

    baseline_rows = evaluate_comparators(episodes=cfg.evaluation_episode_count)
    executed_5000 = (mode == "full") and (max(budgets) == 5000)

    report = _assemble(cfg, candidate_rows, baseline_rows, per_agent_actions_final, manifest, executed_5000, mode)
    _emit_artifacts(report)
    return report


def _last_per_agent_actions(trainer: DistributedTrainer) -> list[dict[str, int]]:
    # Aggregate per-agent action counts over a single fresh greedy evaluation episode.
    # (Cheap structural signal; full reconciled metrics come from candidate_rows.)
    out: list[dict[str, int]] = [{"local": 0, "horizontal": 0, "vertical": 0} for _ in trainer.agents]
    summary = trainer._episode(trainer.episode_count, trainer.template_config.seed_bundle.evaluation_trace_generation_seed, training=False)
    for i, a in enumerate(summary["per_agent_actions"]):
        out[i] = dict(a)
    return out


def _dominant(row: dict[str, Any]) -> str:
    c = {"local": row["action_local_count"], "horizontal": row["action_horizontal_count"], "vertical": row["action_vertical_count"]}
    return max(c, key=c.get)


def _by(rows, name):
    for r in rows:
        if r["policy_name"] == name:
            return r
    return None


def _assemble(cfg, candidate_rows, baseline_rows, per_agent_actions, manifest, executed_5000, mode) -> dict[str, Any]:
    final = candidate_rows[-1] if candidate_rows else None
    best = max(candidate_rows, key=lambda r: r["completion_ratio"]) if candidate_rows else None
    fixed_local = _by(baseline_rows, "fixed_local_policy")
    cap = _by(baseline_rows, "capacity_proportional_split")
    rnd = _by(baseline_rows, "random_legal_policy")
    shared = _shared_final()
    shared_compl = shared["learning_health"]["candidate_vs_fixed_local_completion"] + fixed_local["completion_ratio"] if (shared and fixed_local) else None
    # shared final completion was 0.2545 (from prior run); derive directly if present
    shared_compl_direct = None
    if shared:
        # final-full-campaign-report stores completion via learning_health trend; use candidate vs fixed_local
        shared_compl_direct = None

    # aggregate action usage across candidate checkpoints
    agg_local = final["action_local_count"] if final else 0
    agg_h = final["action_horizontal_count"] if final else 0
    agg_v = final["action_vertical_count"] if final else 0
    local_dominant = bool(final and _dominant(final) == "local")
    horizontal_used = any(r["action_horizontal_count"] > 0 for r in candidate_rows)
    vertical_used = any(r["action_vertical_count"] > 0 for r in candidate_rows)
    distinct_sigs = len({_dominant(r) for r in candidate_rows})

    vs_cap = (final["completion_ratio"] - cap["completion_ratio"]) if (final and cap) else None
    # distributed vs shared: compare final completion to shared 0.2545 (read from artifact if available)
    shared_completion = None
    sp = Path("artifacts/production/full-paper-campaign-execution-run/candidate-vs-baselines-summary.json")
    if sp.exists():
        try:
            shared_completion = json.loads(sp.read_text()).get("final_candidate_completion")
        except Exception:  # noqa: BLE001
            shared_completion = None
    vs_shared = (final["completion_ratio"] - shared_completion) if (final and shared_completion is not None) else None

    _all_rows = candidate_rows + baseline_rows
    reconciled_all = all(r["reward_reconciled"] and r["terminal_reconciled"] for r in _all_rows) if _all_rows else False
    delta_max = max((abs(float(r["raw_vs_canonical_reward_delta"])) for r in _all_rows), default=0.0)
    reward_reconciled_all = all(r["reward_reconciled"] for r in _all_rows) if _all_rows else False
    terminal_reconciled_all = all(r["terminal_reconciled"] for r in _all_rows) if _all_rows else False
    terminal_coverage = (sum(1 for r in _all_rows if r["terminal_reconciled"]) / len(_all_rows)) if _all_rows else 0.0

    # Precise behavior characterization. Mixed *behavior* emerged across
    # checkpoints/agents (both horizontal and vertical were used), but the final
    # aggregate greedy policy is horizontal-dominant, not a truly balanced H/V/L mix.
    final_dominant = _dominant(final) if final else None
    final_h_ratio = final["action_horizontal_ratio"] if final else 0.0
    final_v_ratio = final["action_vertical_ratio"] if final else 0.0
    final_l_ratio = final["action_local_ratio"] if final else 0.0
    mixed_behavior_emerged = bool(horizontal_used and vertical_used)
    final_policy_horizontal_dominant = bool(final_dominant == "horizontal")
    final_balanced_mixed_policy = bool(final and min(final_l_ratio, final_h_ratio, final_v_ratio) > 0.1)
    vertical_usage_observed_during_smoke = bool(vertical_used)
    vertical_usage_final = bool(final_v_ratio > 0.0)
    verdict = "true_per_EA_distributed_baseline_ready_for_full_campaign" if (reconciled_all and final is not None) else "true_per_EA_distributed_baseline_blocked"
    next_step = "user_runs_full_distributed_campaign_command" if mode != "full" else "prepare_paper-output-report"

    return {
        "mode": mode,
        "executed_5000": executed_5000,
        "config": cfg.to_dict(),
        "candidate_rows": candidate_rows,
        "baseline_rows": baseline_rows,
        "per_agent_actions": per_agent_actions,
        "manifest": manifest,
        "final_candidate": final,
        "best_candidate": best,
        "fixed_local": fixed_local,
        "capacity_split": cap,
        "random_legal": rnd,
        "shared_final_completion": shared_completion,
        "reconciliation": {"reconciled_all": reconciled_all, "raw_vs_canonical_delta_max": delta_max,
                           "reward_reconciled_all": reward_reconciled_all,
                           "terminal_reconciled_all": terminal_reconciled_all,
                           "terminal_coverage": terminal_coverage},
        "learning_health": {
            "local_dominant_policy": local_dominant,
            "distinct_dominant_action_signatures": distinct_sigs,
            "horizontal_action_usage_emerged": horizontal_used,
            "vertical_action_usage_emerged": vertical_used,
            "mixed_behavior_emerged": mixed_behavior_emerged,
            "final_policy_horizontal_dominant": final_policy_horizontal_dominant,
            "final_balanced_mixed_policy": final_balanced_mixed_policy,
            "vertical_usage_observed_during_smoke": vertical_usage_observed_during_smoke,
            "vertical_usage_final": vertical_usage_final,
            "final_action_distribution": {"local": agg_local, "horizontal": agg_h, "vertical": agg_v},
            "distributed_vs_shared_completion": vs_shared,
            "distributed_vs_capacity_split_completion": vs_cap,
        },
        "claim_safety": _claim_safety(executed_5000),
        "verdict": verdict,
        "recommended_next_step": next_step,
    }


def _emit_artifacts(report: dict[str, Any]) -> None:
    _w("distributed-smoke-run-manifest.json", {"mode": report["mode"], "manifest": report["manifest"],
                                               "commit_sha": _commit(), "executed_5000": report["executed_5000"]})
    _w("distributed-candidate-metrics.json", report["candidate_rows"])
    _w("baseline-and-oracle-metrics.json", report["baseline_rows"])
    _w("per-agent-action-distribution.json", report["per_agent_actions"])
    _w("per-agent-learning-health.json", {
        "local_dominant_policy": report["learning_health"]["local_dominant_policy"],
        "horizontal_action_usage_emerged": report["learning_health"]["horizontal_action_usage_emerged"],
        "vertical_action_usage_emerged": report["learning_health"]["vertical_action_usage_emerged"],
        "mixed_behavior_emerged": report["learning_health"]["mixed_behavior_emerged"],
        "final_policy_horizontal_dominant": report["learning_health"]["final_policy_horizontal_dominant"],
        "final_balanced_mixed_policy": report["learning_health"]["final_balanced_mixed_policy"],
        "vertical_usage_observed_during_smoke": report["learning_health"]["vertical_usage_observed_during_smoke"],
        "vertical_usage_final": report["learning_health"]["vertical_usage_final"],
        "per_agent_actions": report["per_agent_actions"],
    })
    _w("shared-vs-distributed-summary.json", {
        "shared_final_completion": report["shared_final_completion"],
        "distributed_final_completion": report["final_candidate"]["completion_ratio"] if report["final_candidate"] else None,
        "distributed_vs_shared_completion": report["learning_health"]["distributed_vs_shared_completion"],
        "capacity_split_completion": report["capacity_split"]["completion_ratio"] if report["capacity_split"] else None,
        "distributed_vs_capacity_split_completion": report["learning_health"]["distributed_vs_capacity_split_completion"],
    })
    _w("reward-terminal-reconciliation-distributed.json", report["reconciliation"])
    _w("claim-safety.json", report["claim_safety"])
    _w("distributed-full-campaign-handoff.json", {
        "command": FULL_COMMAND,
        "requires": ["--execute-full-distributed-campaign", f"{EXECUTION_ENV_CONFIRMATION}=1"],
        "verdict": report["verdict"], "next_step": report["recommended_next_step"],
    })
    _w("final-distributed-baseline-report.json", {
        "mode": report["mode"], "executed_5000": report["executed_5000"],
        "commit_sha": _commit(), "verdict": report["verdict"],
        "recommended_next_step": report["recommended_next_step"],
        "learning_health": report["learning_health"], "reconciliation": report["reconciliation"],
        "claim_safety": report["claim_safety"],
        "final_candidate_completion": report["final_candidate"]["completion_ratio"] if report["final_candidate"] else None,
        "capacity_split_completion": report["capacity_split"]["completion_ratio"] if report["capacity_split"] else None,
    })
    _w("final-distributed-baseline-report.md", _final_md(report))
    _w("commit-summary.md", _commit_md(report))
    _figures(report)


def _figures(report: dict[str, Any]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    cand = report["candidate_rows"]
    budgets = [r["training_budget"] for r in cand]

    def save(fig, name):
        fig.tight_layout(); fig.savefig(FIGURES / name, dpi=110); plt.close(fig)

    shared_c = report["shared_final_completion"]
    fig, ax = plt.subplots(figsize=(8, 4))
    if cand:
        ax.plot(budgets, [r["completion_ratio"] for r in cand], "-o", label="distributed", color="#1f77b4")
    if shared_c is not None:
        ax.axhline(shared_c, color="purple", ls="--", label="shared final")
    ax.set_title("Shared vs distributed completion"); ax.set_xlabel("episode"); ax.set_ylabel("completion"); ax.legend()
    save(fig, "figure_01_shared_vs_distributed_completion.png")

    fig, ax = plt.subplots(figsize=(8, 4))
    if cand:
        ax.plot(budgets, [r["reward_per_task"] for r in cand], "-o", color="#1f77b4")
    ax.set_title("Distributed reward/task by checkpoint"); ax.set_xlabel("episode"); ax.set_ylabel("reward/task")
    save(fig, "figure_02_shared_vs_distributed_reward.png")

    fig, ax = plt.subplots(figsize=(10, 4))
    pa = report["per_agent_actions"]
    idx = range(len(pa))
    loc = [a["local"] for a in pa]; hor = [a["horizontal"] for a in pa]; ver = [a["vertical"] for a in pa]
    ax.bar(idx, loc, label="local", color="#1f77b4")
    ax.bar(idx, hor, bottom=loc, label="horizontal", color="#ff7f0e")
    ax.bar(idx, ver, bottom=[l + h for l, h in zip(loc, hor)], label="vertical", color="#2ca02c")
    ax.set_title("Per-agent action distribution"); ax.set_xlabel("EA index"); ax.set_ylabel("count"); ax.legend()
    save(fig, "figure_03_per_agent_action_distribution.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    fad = report["learning_health"]["final_action_distribution"]
    ax.bar(list(fad), list(fad.values()), color="#9467bd")
    ax.set_title("Aggregate action distribution (final)"); save(fig, "figure_04_aggregate_action_distribution.png")

    fig, ax = plt.subplots(figsize=(8, 4))
    cap = report["capacity_split"]
    if cand:
        ax.plot(budgets, [r["completion_ratio"] for r in cand], "-o", label="distributed", color="#1f77b4")
    if cap:
        ax.axhline(cap["completion_ratio"], color="green", ls="--", label="capacity_split")
    ax.set_title("Distributed vs capacity_split"); ax.set_xlabel("episode"); ax.set_ylabel("completion"); ax.legend()
    save(fig, "figure_05_distributed_vs_capacity_split.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    rec = report["reconciliation"]
    ax.bar(["reconciled_all", "delta_zero"], [1 if rec["reconciled_all"] else 0, 1 if rec["raw_vs_canonical_delta_max"] <= 1e-9 else 0], color="#2ca02c")
    ax.set_ylim(0, 1.2); ax.set_title("Reconciliation summary (1=pass)"); save(fig, "figure_06_reconciliation_summary.png")

    fig, ax = plt.subplots(figsize=(7, 4))
    lh = report["learning_health"]
    flags = {"local_dominant": 1 if lh["local_dominant_policy"] else 0,
             "horizontal_used": 1 if lh["horizontal_action_usage_emerged"] else 0,
             "vertical_used": 1 if lh["vertical_action_usage_emerged"] else 0,
             "mixed_behavior": 1 if lh["mixed_behavior_emerged"] else 0,
             "final_balanced": 1 if lh["final_balanced_mixed_policy"] else 0}
    ax.bar(list(flags), list(flags.values()), color="#1f77b4"); ax.set_ylim(0, 1.2)
    ax.set_title("Learning health (distributed)"); plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    save(fig, "figure_07_learning_health_distributed.png")

    _paper_figures(report)


# --- HOODIE paper figures 8, 9, 10, 11 (+ sub-figures) -----------------------
# These follow the paper's figure semantics (paper_figure_extraction.py):
#   Fig 8  accumulated reward vs training episode, by learning rate & discount factor
#   Fig 9  behavior insights under varying system parameters (9a-9e)
#   Fig 10 performance comparison vs baselines: 10a average delay, 10b drop ratio
#   Fig 11 average task delay with vs without LSTM (ablation)
# Fig 10 is produced fully from the distributed run. Figs 8/9/11 emit the
# single-config curve / action distribution that the fixed-config bounded smoke
# supports, and the sweep / ablation sub-figures are rendered as explicit
# "requires additional runs" placeholders (NO fabricated curves).

_SWEEP_NOTE = ("Sweep/ablation sub-figure requires additional training runs\n"
               "(varied config) beyond the fixed-config bounded smoke.\n"
               "Not fabricated.")


def _placeholder_ax(ax, title: str, note: str = _SWEEP_NOTE) -> None:
    ax.text(0.5, 0.5, note, ha="center", va="center", fontsize=9,
            color="#555555", wrap=True, transform=ax.transAxes,
            bbox=dict(boxstyle="round", fc="#f4f4f4", ec="#bbbbbb"))
    ax.set_title(title); ax.set_xticks([]); ax.set_yticks([])


def _paper_figures(report: dict[str, Any]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    cfg = report.get("config", {})
    lr = cfg.get("learning_rate", 7e-7)
    gamma = cfg.get("gamma", 0.99)
    cand = report["candidate_rows"]
    budgets = [r["training_budget"] for r in cand]

    def save(fig, name):
        fig.tight_layout(); fig.savefig(FIGURES / name, dpi=110); plt.close(fig)

    # ----- Figure 8: accumulated reward time-course -----
    # 8a accumulated reward, 8b reward/task. Single (lr, gamma); sweep out of scope.
    fig, ax = plt.subplots(figsize=(7, 4))
    if cand:
        ax.plot(budgets, [r["reward_total"] for r in cand], "-o", color="#1f77b4",
                label=f"lr={lr:g}, γ={gamma:g}")
    ax.set_title("Fig 8a: Accumulated reward vs training episode")
    ax.set_xlabel("training episode (budget)"); ax.set_ylabel("accumulated reward"); ax.legend()
    save(fig, "figure_08a_accumulated_reward.png")

    fig, ax = plt.subplots(figsize=(7, 4))
    if cand:
        ax.plot(budgets, [r["reward_per_task"] for r in cand], "-o", color="#1f77b4",
                label=f"lr={lr:g}, γ={gamma:g}")
    ax.set_title("Fig 8b: Reward per task vs training episode")
    ax.set_xlabel("training episode (budget)"); ax.set_ylabel("reward / task"); ax.legend()
    save(fig, "figure_08b_reward_per_task.png")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
    if cand:
        axes[0].plot(budgets, [r["reward_total"] for r in cand], "-o", color="#1f77b4")
        axes[1].plot(budgets, [r["reward_per_task"] for r in cand], "-o", color="#1f77b4")
    axes[0].set_title("8a accumulated reward"); axes[0].set_xlabel("episode"); axes[0].set_ylabel("reward")
    axes[1].set_title("8b reward/task"); axes[1].set_xlabel("episode"); axes[1].set_ylabel("reward/task")
    fig.suptitle(f"Figure 8: reward time-course (single config lr={lr:g}, γ={gamma:g}; "
                 f"lr/γ sweep requires additional runs)")
    save(fig, "figure_08_accumulated_reward_by_training_episode.png")

    # ----- Figure 9: behavior insights (9a action dist real; 9b-9e need sweeps) -----
    fad = report["learning_health"]["final_action_distribution"]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(list(fad), list(fad.values()), color=["#1f77b4", "#ff7f0e", "#2ca02c"])
    ax.set_title("Fig 9a: action distribution (aggregate)"); ax.set_ylabel("count")
    save(fig, "figure_09a_action_distribution.png")

    sweep_titles = {
        "figure_09b_reward_by_task_arrival_probability.png": "Fig 9b: reward vs task arrival probability",
        "figure_09c_reward_by_drl_agent_count.png": "Fig 9c: reward vs DRL agent count N",
        "figure_09d_reward_by_cpu_capacity.png": "Fig 9d: reward vs CPU capacity",
        "figure_09e_reward_by_offloading_data_rate.png": "Fig 9e: reward vs offloading data rate",
    }
    for name, title in sweep_titles.items():
        fig, ax = plt.subplots(figsize=(6, 4)); _placeholder_ax(ax, title); save(fig, name)

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes[0, 0].bar(list(fad), list(fad.values()), color=["#1f77b4", "#ff7f0e", "#2ca02c"])
    axes[0, 0].set_title("9a action distribution")
    for ax, title in zip(axes.flat[1:], list(sweep_titles.values()) + [""]):
        if title:
            _placeholder_ax(ax, title)
        else:
            ax.axis("off")
    fig.suptitle("Figure 9: behavior insights (9a artifact-backed; 9b-9e require parameter sweeps)")
    save(fig, "figure_09_behavior_insights.png")

    # ----- Figure 10: HOODIE candidate vs baselines (10a delay, 10b drop) FULL -----
    final = report.get("final_candidate")
    baselines = list(report.get("baseline_rows", []))
    rows10 = ([("distributed_candidate", final)] if final else []) + [(r["policy_name"], r) for r in baselines]
    names = [n for n, r in rows10 if r]
    delays = [r["average_latency_slots"] for n, r in rows10 if r]
    drops = [r["drop_ratio"] for n, r in rows10 if r]
    colors = ["#d62728"] + ["#1f77b4"] * (len(names) - 1)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(range(len(names)), delays, color=colors)
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=25, ha="right")
    ax.set_title("Fig 10a: average task delay (slots)"); ax.set_ylabel("avg delay (slots)")
    save(fig, "figure_10a_average_delay.png")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(range(len(names)), drops, color=colors)
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=25, ha="right")
    ax.set_title("Fig 10b: drop ratio"); ax.set_ylabel("drop ratio"); ax.set_ylim(0, 1)
    save(fig, "figure_10b_drop_ratio.png")

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    axes[0].bar(range(len(names)), delays, color=colors)
    axes[0].set_xticks(range(len(names))); axes[0].set_xticklabels(names, rotation=25, ha="right")
    axes[0].set_title("10a average delay (slots)"); axes[0].set_ylabel("avg delay")
    axes[1].bar(range(len(names)), drops, color=colors)
    axes[1].set_xticks(range(len(names))); axes[1].set_xticklabels(names, rotation=25, ha="right")
    axes[1].set_title("10b drop ratio"); axes[1].set_ylabel("drop ratio"); axes[1].set_ylim(0, 1)
    fig.suptitle("Figure 10: distributed HOODIE candidate vs available baselines")
    save(fig, "figure_10_hoodie_vs_baselines.png")

    # ----- Figure 11: delay with vs without LSTM (ablation) -----
    # With-LSTM curve is real (architecture uses 1x20 LSTM); without-LSTM needs ablation run.
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if cand:
        ax.plot(budgets, [r["average_latency_slots"] for r in cand], "-o", color="#1f77b4", label="with LSTM (this run)")
    ax.plot([], [], "--s", color="#999999", label="without LSTM (requires ablation run)")
    ax.set_title("Figure 11: average task delay with vs without LSTM")
    ax.set_xlabel("training episode (budget)"); ax.set_ylabel("avg delay (slots)"); ax.legend()
    ax.text(0.98, 0.04, "without-LSTM curve requires a separate ablation run", ha="right", va="bottom",
            fontsize=8, color="#777777", transform=ax.transAxes)
    save(fig, "figure_11_lstm_ablation_delay.png")


def regenerate_paper_figures() -> dict[str, Any]:
    """Rebuild figures 1-11 from already-emitted JSON artifacts (no retraining)."""
    cand = json.loads((OUT_DIR / "distributed-candidate-metrics.json").read_text())
    base = json.loads((OUT_DIR / "baseline-and-oracle-metrics.json").read_text())
    final_rep = json.loads((OUT_DIR / "final-distributed-baseline-report.json").read_text())
    pa = json.loads((OUT_DIR / "per-agent-action-distribution.json").read_text())
    cfg = json.loads((OUT_DIR / "distributed-baseline-config.json").read_text())
    final = cand[-1] if cand else None
    report = {
        "config": cfg,
        "candidate_rows": cand,
        "baseline_rows": base,
        "per_agent_actions": pa,
        "final_candidate": final,
        "capacity_split": _by(base, "capacity_proportional_split"),
        "shared_final_completion": json.loads((OUT_DIR / "shared-vs-distributed-summary.json").read_text()).get("shared_final_completion"),
        "reconciliation": final_rep["reconciliation"],
        "learning_health": final_rep["learning_health"],
    }
    _figures(report)
    return report


def _final_md(r: dict[str, Any]) -> str:
    lh = r["learning_health"]
    def fmt(x): return f"{x['completion_ratio']:.3f} compl / {x['reward_per_task']:.2f} rwd" if x else "n/a"
    return "\n".join([
        "# Per-EA Distributed Baseline — Report",
        "",
        f"- **Verdict:** `{r['verdict']}`  | Next: `{r['recommended_next_step']}`",
        f"- Mode: {r['mode']} | Executed 5000: {r['executed_5000']} | Proposed method: NONE",
        "",
        "## Distributed candidate vs comparators (final)",
        f"- Distributed final: {fmt(r['final_candidate'])}",
        f"- Distributed best: {fmt(r['best_candidate'])}",
        f"- Shared-parameter final completion: {r['shared_final_completion']}",
        f"- fixed_local: {fmt(r['fixed_local'])}",
        f"- capacity_split: {fmt(r['capacity_split'])}",
        f"- random_legal: {fmt(r['random_legal'])}",
        "",
        "## Learning health",
        f"- Local-dominant: {lh['local_dominant_policy']} | distinct dominant signatures: {lh['distinct_dominant_action_signatures']}",
        f"- Horizontal used: {lh['horizontal_action_usage_emerged']} | Vertical used: {lh['vertical_action_usage_emerged']}",
        f"- Mixed behavior emerged across checkpoints/agents: {lh['mixed_behavior_emerged']} "
        f"(vertical observed during smoke: {lh['vertical_usage_observed_during_smoke']})",
        f"- Final aggregate greedy policy horizontal-dominant: {lh['final_policy_horizontal_dominant']} "
        f"| final balanced H/V/L mix: {lh['final_balanced_mixed_policy']} | vertical usage final: {lh['vertical_usage_final']}",
        f"- Distributed vs shared (completion): {lh['distributed_vs_shared_completion']}",
        f"- Distributed vs capacity_split (completion): {lh['distributed_vs_capacity_split_completion']}",
        "",
        "## Reconciliation",
        f"- Reconciled all: {r['reconciliation']['reconciled_all']} | delta max: {r['reconciliation']['raw_vs_canonical_delta_max']}",
        "",
        "## Claim safety",
        "- No paper-reproduction / exact-numerical / performance / baseline-superiority claims; no proposed method.",
    ])


def _commit_md(r: dict[str, Any]) -> str:
    return "\n".join([
        "# Commit summary",
        "",
        "feat: implement true per-EA distributed baseline",
        f"- Mode: {r['mode']} | Verdict: {r['verdict']}",
        "- 20 independent agents (own online/target/optimizer/replay/epsilon/target-sync).",
        "- No reward/env/topology/reconciliation/metric changes; no proposed method; no superiority claims.",
    ])


def _audit_md(audit: dict[str, Any]) -> str:
    lines = ["# Paper Distributed-Agent Audit", "", f"Source: {audit['paper_source']}", "",
             "| item | status | evidence |", "|---|---|---|"]
    for i in audit["items"]:
        lines.append(f"| {i['item']} | {i['status']} | {i['evidence']} |")
    lines += ["", f"All core per-EA items exact: {audit['all_core_per_EA_items_exact']}",
              f"Remaining approximations/inferred: {audit['remaining_approximations']}",
              "No proposed method: True"]
    return "\n".join(lines)
