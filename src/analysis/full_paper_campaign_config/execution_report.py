"""Write full-campaign execution artifacts + figures (matplotlib only)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .config import build_full_campaign_config
from .executor import OUT_DIR, FIGURES, PROGRESS
from .guards import claim_safety

EXECUTION_COMMAND = (
    "HOODIE_EXECUTE_FULL_CAMPAIGN=1 "
    "python -m src.analysis.full_paper_campaign_config.runner --execute-full-campaign --json"
)
DRY_RUN_COMMAND = "python -m src.analysis.full_paper_campaign_config.runner --dry-run --json"


def _commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def _w(name: str, payload: Any) -> None:
    p = OUT_DIR / name
    if isinstance(payload, str):
        p.write_text(payload, encoding="utf-8")
    else:
        p.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _monitoring_summary() -> dict[str, Any]:
    if not PROGRESS.exists():
        return {"events": 0}
    rows = [json.loads(l) for l in PROGRESS.read_text().splitlines() if l.strip()]
    checkpoints = [r for r in rows if r.get("event") == "checkpoint_written"]
    return {
        "events": len(rows),
        "checkpoints_written": len(checkpoints),
        "aborts": [r for r in rows if r.get("event") == "abort"],
        "first_event": rows[0] if rows else None,
        "last_event": rows[-1] if rows else None,
        "max_loss": max((float(r["loss_value"]) for r in checkpoints if r.get("loss_value") is not None), default=None),
    }


def _figs(report: dict[str, Any]) -> list[str]:
    FIGURES.mkdir(parents=True, exist_ok=True)
    out: list[str] = []
    cfg = build_full_campaign_config()
    cand = report["candidate_rows"]
    budgets = [r["training_budget"] for r in cand]

    def save(fig, name):
        p = FIGURES / name
        fig.tight_layout(); fig.savefig(p, dpi=110); plt.close(fig); out.append(str(p))

    # 01 epsilon schedule actual
    xs = list(range(0, cfg.number_of_training_episodes + 1, 100))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(xs, [cfg.epsilon_at(e) for e in xs], color="#1f77b4")
    ax.axvline(cfg.epsilon_decay_episodes, color="red", ls="--", label="N_E/2")
    ax.set_title("Epsilon schedule (actual config)"); ax.set_xlabel("episode"); ax.set_ylabel("epsilon"); ax.legend()
    save(fig, "figure_01_epsilon_schedule_actual.png")

    # 02 completion/drop by checkpoint
    fig, ax = plt.subplots(figsize=(8, 4))
    if cand:
        ax.plot(budgets, [r["completion_ratio"] for r in cand], "-o", label="completion", color="#2ca02c")
        ax.plot(budgets, [r["drop_ratio"] for r in cand], "-o", label="drop", color="#d62728")
    ax.set_title("Completion / drop by checkpoint"); ax.set_xlabel("episode"); ax.set_ylabel("ratio"); ax.legend()
    save(fig, "figure_02_completion_drop_by_checkpoint.png")

    # 03 reward by checkpoint
    fig, ax = plt.subplots(figsize=(8, 4))
    if cand:
        ax.plot(budgets, [r["reward_per_task"] for r in cand], "-o", color="#1f77b4")
    ax.set_title("Reward per task by checkpoint"); ax.set_xlabel("episode"); ax.set_ylabel("reward/task")
    save(fig, "figure_03_reward_by_checkpoint.png")

    # 04 action distribution by checkpoint (stacked)
    fig, ax = plt.subplots(figsize=(8, 4))
    if cand:
        loc = [r["action_local_count"] for r in cand]
        hor = [r["action_horizontal_count"] for r in cand]
        ver = [r["action_vertical_count"] for r in cand]
        ax.bar(range(len(budgets)), loc, label="local", color="#1f77b4")
        ax.bar(range(len(budgets)), hor, bottom=loc, label="horizontal", color="#ff7f0e")
        ax.bar(range(len(budgets)), ver, bottom=[l + h for l, h in zip(loc, hor)], label="vertical", color="#2ca02c")
        ax.set_xticks(range(len(budgets))); ax.set_xticklabels(budgets, rotation=45)
    ax.set_title("Action distribution by checkpoint"); ax.set_xlabel("episode"); ax.set_ylabel("count"); ax.legend()
    save(fig, "figure_04_action_distribution_by_checkpoint.png")

    # 05 candidate vs fixed_local vs capacity_split
    fig, ax = plt.subplots(figsize=(8, 4))
    fl = report.get("fixed_local"); cs = report.get("capacity_split")
    if cand:
        ax.plot(budgets, [r["completion_ratio"] for r in cand], "-o", label="candidate", color="#1f77b4")
    if fl:
        ax.axhline(fl["completion_ratio"], color="red", ls="--", label="fixed_local")
    if cs:
        ax.axhline(cs["completion_ratio"], color="green", ls="--", label="capacity_split")
    ax.set_title("Candidate vs fixed_local vs capacity_split (completion)")
    ax.set_xlabel("episode"); ax.set_ylabel("completion ratio"); ax.legend()
    save(fig, "figure_05_candidate_vs_fixed_local_vs_capacity_split.png")

    # 06 q-value state-action discrimination
    fig, ax = plt.subplots(figsize=(8, 4))
    q = report.get("q_value_diagnostics") or {}
    keys = [k for k in ("q_local_mean", "q_horizontal_mean", "q_vertical_mean") if k in q]
    if keys:
        ax.bar([k.replace("q_", "").replace("_mean", "") for k in keys], [q[k] for k in keys], color="#9467bd")
    else:
        ax.text(0.5, 0.5, "q diagnostics unavailable", ha="center")
    ax.set_title("Q-value mean by action (state-action discrimination)")
    save(fig, "figure_06_q_value_state_action_discrimination.png")

    # 07 reconciliation summary
    fig, ax = plt.subplots(figsize=(8, 4))
    rec = report["reconciliation"]
    ax.bar(["reconciled_all", "delta_zero"], [1 if rec["reconciled_all"] else 0,
           1 if rec["raw_vs_canonical_delta_max"] <= 1e-9 else 0], color="#2ca02c")
    ax.set_ylim(0, 1.2); ax.set_title("Reconciliation summary (1=pass)")
    save(fig, "figure_07_reconciliation_summary.png")

    # 08 learning health summary
    fig, ax = plt.subplots(figsize=(8, 4))
    lh = report["learning_health"]
    flags = {
        "no_collapse": 0 if lh["candidate_action_collapse_detected"] else 1,
        "mixed_learned": 1 if lh["mixed_policy_learned"] else 0,
        "compl_up": 1 if lh["completion_trend_first_to_last"] > 0 else 0,
        "reward_up": 1 if lh["reward_per_task_trend_first_to_last"] > 0 else 0,
    }
    ax.bar(list(flags), list(flags.values()), color="#1f77b4")
    ax.set_ylim(0, 1.2); ax.set_title("Learning-health summary (1=yes)")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    save(fig, "figure_08_learning_health_summary.png")
    return out


def write_execution_artifacts(report: dict[str, Any], dry_run_output: dict[str, Any] | None) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lh = report["learning_health"]; rec = report["reconciliation"]
    _w("execution-command.txt", EXECUTION_COMMAND + "\n" + DRY_RUN_COMMAND + "\n")
    _w("dry-run-output.json", dry_run_output or {})
    _w("full-campaign-config-used.json", report["config"])
    _w("full-campaign-run-manifest.json", {
        "budgets_trained": report["budgets_trained"], "eval_at": report["eval_at"],
        "wall_seconds": report["wall_seconds"], "wall_hours": report["wall_hours"],
        "abort_reason": report["abort_reason"], "commit_sha": _commit(),
    })
    _w("checkpoint-manifest.json", report["checkpoint_manifest"])
    _w("monitoring-log-summary.json", _monitoring_summary())
    _w("candidate-checkpoint-metrics.json", report["candidate_rows"])
    _w("baseline-and-oracle-metrics.json", report["baseline_rows"])
    _w("candidate-vs-baselines-summary.json", {
        "final_candidate_completion": report["final_candidate"]["completion_ratio"] if report["final_candidate"] else None,
        "fixed_local_completion": report["fixed_local"]["completion_ratio"] if report["fixed_local"] else None,
        "random_legal_completion": report["random_legal"]["completion_ratio"] if report["random_legal"] else None,
        "candidate_vs_fixed_local_completion": lh["candidate_vs_fixed_local_completion"],
    })
    _w("candidate-vs-capacity-split-summary.json", {
        "capacity_split_completion": report["capacity_split"]["completion_ratio"] if report["capacity_split"] else None,
        "candidate_vs_capacity_split_completion": lh["candidate_vs_capacity_split_completion"],
    })
    _w("learning-health-full-campaign.json", lh)
    _w("q-value-diagnostics-full-campaign.json", report["q_value_diagnostics"])
    _w("action-distribution-by-checkpoint.json", report["action_by_checkpoint"])
    _w("reward-terminal-reconciliation-full-campaign.json", rec)
    _w("claim-safety.json", claim_safety())
    _w("abort-status.json", {"aborted": report["abort_reason"] is not None, "abort_reason": report["abort_reason"]})

    figs = _figs(report)
    final = {
        "branch": "full-paper-campaign-execution-run",
        "commit_sha": _commit(),
        "executed_5000": report["abort_reason"] is None and max(report["budgets_trained"]) == 5000,
        "abort_reason": report["abort_reason"],
        "wall_hours": report["wall_hours"],
        "verdict": report["verdict"],
        "recommended_next_step": report["recommended_next_step"],
        "learning_health": lh,
        "reconciliation": rec,
        "claim_safety": claim_safety(),
        "figures": figs,
    }
    _w("final-full-campaign-report.json", final)
    _w("final-full-campaign-report.md", _final_md(report, final))
    _w("commit-summary.md", _commit_md(report))
    return final


def _final_md(report, final) -> str:
    lh = report["learning_health"]
    def fmt(r): return f"{r['completion_ratio']:.3f} compl / {r['reward_per_task']:.2f} rwd-task" if r else "n/a"
    return "\n".join([
        "# Full Paper Campaign — Execution Report",
        "",
        f"- **Verdict:** `{final['verdict']}`",
        f"- **Next step:** `{final['recommended_next_step']}`",
        f"- Executed 5000: {final['executed_5000']} | Abort: {final['abort_reason']} | Wall: {final['wall_hours']} h",
        "",
        "## Candidate vs comparators (final)",
        f"- Final candidate: {fmt(report['final_candidate'])}",
        f"- Best candidate: {fmt(report['best_candidate'])}",
        f"- fixed_local: {fmt(report['fixed_local'])}",
        f"- capacity_split: {fmt(report['capacity_split'])}",
        f"- random_legal: {fmt(report['random_legal'])}",
        "",
        "## Learning health",
        f"- Action collapse: {lh['candidate_action_collapse_detected']} (distinct signatures {lh['distinct_action_signatures']})",
        f"- Matches fixed_local: {lh['candidate_matches_fixed_local']}",
        f"- Mixed policy learned: {lh['mixed_policy_learned']}",
        f"- Completion trend: {lh['completion_trend_first_to_last']:+.4f} | Reward/task trend: {lh['reward_per_task_trend_first_to_last']:+.3f}",
        f"- Candidate vs capacity_split: {lh['candidate_vs_capacity_split_completion']}",
        "",
        "## Reconciliation",
        f"- Reconciled all: {report['reconciliation']['reconciled_all']} | delta max: {report['reconciliation']['raw_vs_canonical_delta_max']}",
        "",
        "## Claim safety",
        "- No paper-reproduction / exact-numerical / performance / baseline-superiority claims are made.",
    ])


def _commit_md(report) -> str:
    return "\n".join([
        "# Commit summary",
        "",
        "run: execute full paper campaign with guarded config",
        f"- Verdict: {report['verdict']}",
        f"- Abort: {report['abort_reason']}",
        f"- Wall: {report['wall_hours']} h",
        "- No reward/env/topology/reconciliation/metric semantics changed; no superiority claims.",
    ])
