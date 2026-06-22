"""Full paper campaign executor (N_E=5000) — only runs when explicitly authorized.

Reuses the validated training/eval machinery (StateRepresentationTrainingSession,
horizon-aware reconciled metric rows, fixed-policy suite, capacity-split oracle).
Trains incrementally with checkpoints, evaluates at the configured checkpoints,
monitors abort conditions, and emits the full set of execution artifacts.

This module performs NO training on import. It is invoked only by
``runner.run(execute_full_campaign=True)`` after the explicit flag + env guard.
"""

from __future__ import annotations

import json
import time
import traceback
from pathlib import Path
from typing import Any, Callable

import torch

from src.analysis.full_training_reproduction_campaign.trainer import EpsilonGreedyExploration
from src.analysis.full_training_reproduction_campaign.config import TargetUpdateContract
from src.analysis.paper_faithful_simulation_production.profiles import ProductionProfile
from src.analysis.paper_faithful_simulation_production.simulation_runner import _metric_row
from src.analysis.state_profile_decision_time_integration_recovery.config import (
    StateRepresentationRepairConfig,
    NEW_STATE_REPRESENTATION_PROFILE,
)
from src.analysis.state_profile_decision_time_integration_recovery.policy_probe import (
    StateRepresentationTrainingSession,
)

from .config import build_full_campaign_config

OUT_DIR = Path("artifacts/production/full-paper-campaign-execution-run")
FIGURES = OUT_DIR / "figures"
CKPT_DIR = OUT_DIR / "checkpoints"
PROGRESS = OUT_DIR / "progress.jsonl"

CHECKPOINT_BUDGETS = list(range(250, 5001, 250))          # 250..5000 step 250
EVAL_AT = [250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]


def _ProductionProfileFull() -> ProductionProfile:
    """A profile object for _metric_row schema fields (budgets unused for eval rows)."""
    return ProductionProfile()


def _append_progress(record: dict[str, Any]) -> None:
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    with PROGRESS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def _save_checkpoint(session: Any, episode: int) -> str:
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    t = session.trainer
    path = CKPT_DIR / f"ckpt_ep{episode:05d}.pt"
    torch.save(
        {
            "episode": episode,
            "online_state_dict": t.online_network.state_dict(),
            "target_state_dict": t.target_network.state_dict(),
            "optimizer_state_dict": t.optimizer.state_dict(),
            "optimizer_step_count": t.optimizer_step_count,
            "target_sync_count": t.target_sync_count,
            "cumulative_training_episode_count": session.training_episode_count,
        },
        path,
    )
    return str(path)


def _abort_check_eval_row(row: dict[str, Any]) -> str | None:
    if not row.get("reward_reconciled", False):
        return "reward_reconciliation_failed"
    if not row.get("terminal_reconciled", False):
        return "terminal_reconciliation_failed"
    if abs(float(row.get("raw_vs_canonical_reward_delta", 1.0))) > 1e-9:
        return "raw_vs_canonical_delta_nonzero"
    return None


def _dominant_action(row: dict[str, Any]) -> str:
    counts = {
        "local": int(row.get("action_local_count", 0)),
        "horizontal": int(row.get("action_horizontal_count", 0)),
        "vertical": int(row.get("action_vertical_count", 0)),
    }
    return max(counts, key=counts.get)


def run_full_campaign(
    *,
    smoke_budgets: list[int] | None = None,
    eval_at: list[int] | None = None,
    epsilon_decay_episodes: int | None = None,
    upper_estimate_seconds: float = 4.22 * 3600,
) -> dict[str, Any]:
    """Execute the full (or smoke) campaign. Returns the final report dict."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # fresh progress log per run
    if PROGRESS.exists():
        PROGRESS.unlink()

    cfg = build_full_campaign_config()
    budgets = smoke_budgets or CHECKPOINT_BUDGETS
    eval_set = set(eval_at if eval_at is not None else EVAL_AT)
    decay = epsilon_decay_episodes if epsilon_decay_episodes is not None else cfg.epsilon_decay_episodes

    session = StateRepresentationTrainingSession(
        config=StateRepresentationRepairConfig(),
        state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE,
    )
    # Paper-aligned episode-based epsilon (1->0 over first N_E/2 episodes) + per-task credit.
    session.trainer.exploration = EpsilonGreedyExploration(
        epsilon_start=cfg.epsilon_start,
        epsilon_final=cfg.epsilon_final,
        epsilon_decay_steps=decay,
        decay_type="linear",
        schedule_unit="episode",
        seed=53,
    )
    session.trainer.per_task_credit_assignment = True
    # Episode-based target sync (N_copy episodes).
    contract = TargetUpdateContract(
        update_frequency=cfg.target_update_frequency,
        target_update_unit="episode",
        approval_status="paper_aligned_episode_sync_approved",
        paper_evidence_status="ocr_recovered_algorithm_1_episode_copy",
    )
    session.campaign_config.target_update_contract = contract
    session.trainer.config.target_update_contract = contract

    profile = _ProductionProfileFull()
    started = time.time()
    abort_reason: str | None = None
    candidate_rows: list[dict[str, Any]] = []
    checkpoint_manifest: list[dict[str, Any]] = []
    action_by_checkpoint: dict[str, Any] = {}

    _append_progress({"event": "campaign_started", "budgets": budgets, "eval_at": sorted(eval_set), "ts": started})

    try:
        for budget in budgets:
            train_summary = session.train_to_budget(budget)
            if not bool(train_summary.get("loss_is_finite", True)):
                abort_reason = "loss_nan_or_inf"
                _append_progress({"event": "abort", "reason": abort_reason, "budget": budget})
                break
            ckpt_path = _save_checkpoint(session, budget)
            elapsed = time.time() - started
            eps_now = session.trainer.exploration.epsilon_for_episode(budget)
            prog = {
                "event": "checkpoint_written", "budget": budget, "checkpoint": ckpt_path,
                "loss_value": train_summary.get("loss_value"),
                "loss_is_finite": train_summary.get("loss_is_finite"),
                "epsilon_at_budget": eps_now,
                "optimizer_step_count": session.trainer.optimizer_step_count,
                "target_sync_count": session.trainer.target_sync_count,
                "elapsed_s": round(elapsed, 1),
            }
            checkpoint_manifest.append({"budget": budget, "path": ckpt_path, "elapsed_s": round(elapsed, 1)})

            if budget in eval_set:
                result = session.candidate_policy_result(checkpoint_budget=budget)
                row, _ = _metric_row(
                    policy_name=f"candidate_at_{budget}", training_budget=budget,
                    evaluation_result=result, profile=profile, commit="full-campaign",
                )
                ab = _abort_check_eval_row(row)
                candidate_rows.append(row)
                action_by_checkpoint[str(budget)] = {
                    "local": row["action_local_count"], "horizontal": row["action_horizontal_count"],
                    "vertical": row["action_vertical_count"], "dominant": _dominant_action(row),
                }
                prog.update({
                    "completion_ratio": row["completion_ratio"], "drop_ratio": row["drop_ratio"],
                    "reward_per_task": row["reward_per_task"], "dominant_action": _dominant_action(row),
                    "reward_reconciled": row["reward_reconciled"], "terminal_reconciled": row["terminal_reconciled"],
                    "raw_vs_canonical_reward_delta": row["raw_vs_canonical_reward_delta"],
                })
                if ab:
                    abort_reason = ab
                    _append_progress({"event": "abort", "reason": ab, "budget": budget})
                    _append_progress(prog)
                    break

            _append_progress(prog)

            if (time.time() - started) > 2 * upper_estimate_seconds:
                abort_reason = "wall_time_exceeded_2x_upper_estimate"
                _append_progress({"event": "abort", "reason": abort_reason, "budget": budget})
                break
    except Exception as exc:  # noqa: BLE001
        abort_reason = f"exception:{type(exc).__name__}"
        _append_progress({"event": "abort", "reason": abort_reason, "traceback": traceback.format_exc()[:2000]})

    # Comparators (evaluate once; independent of training) — best-effort even on abort.
    baseline_rows: list[dict[str, Any]] = []
    try:
        fixed_results = session.fixed_policy_results()
        for name, res in fixed_results.items():
            row, _ = _metric_row(policy_name=name, training_budget=None,
                                 evaluation_result=res, profile=profile, commit="full-campaign")
            baseline_rows.append(row)
        # capacity-proportional split oracle on the same session (vendored, no cross-branch import)
        cap_res = _evaluate_capacity_split(session)
        cap_row, _ = _metric_row(policy_name="capacity_proportional_split", training_budget=None,
                                 evaluation_result=cap_res, profile=profile, commit="full-campaign")
        baseline_rows.append(cap_row)
    except Exception as exc:  # noqa: BLE001
        _append_progress({"event": "comparator_eval_error", "error": f"{type(exc).__name__}: {exc}"})

    wall = time.time() - started
    _append_progress({"event": "campaign_finished", "abort_reason": abort_reason, "wall_s": round(wall, 1)})

    return _assemble_report(
        cfg=cfg, budgets=budgets, eval_set=sorted(eval_set), candidate_rows=candidate_rows,
        baseline_rows=baseline_rows, checkpoint_manifest=checkpoint_manifest,
        action_by_checkpoint=action_by_checkpoint, abort_reason=abort_reason, wall=wall,
        q_diag=session.trainer.q_value_diagnostics() if hasattr(session.trainer, "q_value_diagnostics") else {},
    )


# Capacity-proportional split oracle (private 10 : public 10 : cloud 3), vendored here
# so this branch has no dependency on oracle_validation (which lives on another branch).
_CAP_WEIGHTS = {"local": 10.0, "horizontal": 10.0, "vertical": 3.0}


def _capacity_split_policy(seed: int = 53) -> Callable:
    import random as _r

    rng = _r.Random(seed)

    def _p(state_tensor, legal_action_mask, context):
        legal = [a for a in ("local", "horizontal", "vertical") if legal_action_mask.get(a, False)]
        if not legal:
            return "local"
        weights = [_CAP_WEIGHTS[a] for a in legal]
        return rng.choices(legal, weights=weights, k=1)[0]

    return _p


def _evaluate_capacity_split(session: Any) -> dict[str, Any]:
    from src.analysis.state_profile_decision_time_integration_recovery.policy_probe import (
        _patched_calibrated_session_environment,
        _patched_decision_time_state_injection,
    )
    from src.analysis.state_profile_decision_time_integration_recovery.state_profile_adapter import (
        patched_terminal_evaluator_state_profile,
    )
    from src.analysis.terminal_lifecycle_accounting_50_100_comparison.repaired_terminal_evaluator import (
        evaluate_policy_on_trace_bank_terminal_repaired,
    )

    cfg = session.campaign_config
    with _patched_calibrated_session_environment(session), \
         patched_terminal_evaluator_state_profile(cfg.state_representation_profile), \
         _patched_decision_time_state_injection(session.trainer):
        return evaluate_policy_on_trace_bank_terminal_repaired(
            trainer=session.trainer,
            policy_name="capacity_proportional_split",
            policy_fn=_capacity_split_policy(),
            evaluation_episode_count=session.config.evaluation_episode_count,
            episode_length=session.config.episode_length,
            seed_base=cfg.seed_bundle.evaluation_trace_generation_seed,
            checkpoint_budget=100,
            policy_kind="fixed",
            evaluation_trace_bank_id=cfg.evaluation_trace_bank_id,
            record_sample_limit=session.config.record_sample_limit,
        )


def _by_name(rows: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for r in rows:
        if r.get("policy_name") == name:
            return r
    return None


def _assemble_report(*, cfg, budgets, eval_set, candidate_rows, baseline_rows,
                     checkpoint_manifest, action_by_checkpoint, abort_reason, wall, q_diag) -> dict[str, Any]:
    fixed_local = _by_name(baseline_rows, "fixed_local_policy")
    cap_split = _by_name(baseline_rows, "capacity_proportional_split")
    random_legal = _by_name(baseline_rows, "random_legal_policy")
    final_candidate = candidate_rows[-1] if candidate_rows else None
    best_candidate = max(candidate_rows, key=lambda r: r["completion_ratio"]) if candidate_rows else None

    # learning-health
    signatures = {str(r["training_budget"]): _dominant_action(r) for r in candidate_rows}
    distinct = len(set(signatures.values()))
    collapse = distinct == 1
    matches_local = bool(final_candidate and fixed_local and
                         _dominant_action(final_candidate) == _dominant_action(fixed_local) and collapse)
    completion_trend = (
        candidate_rows[-1]["completion_ratio"] - candidate_rows[0]["completion_ratio"]
        if len(candidate_rows) >= 2 else 0.0
    )
    reward_trend = (
        candidate_rows[-1]["reward_per_task"] - candidate_rows[0]["reward_per_task"]
        if len(candidate_rows) >= 2 else 0.0
    )
    vs_local = (final_candidate["completion_ratio"] - fixed_local["completion_ratio"]) if (final_candidate and fixed_local) else None
    vs_cap = (final_candidate["completion_ratio"] - cap_split["completion_ratio"]) if (final_candidate and cap_split) else None

    reconciled_all = all(r["reward_reconciled"] and r["terminal_reconciled"] for r in candidate_rows + baseline_rows) if (candidate_rows or baseline_rows) else False
    delta_max = max((abs(float(r["raw_vs_canonical_reward_delta"])) for r in candidate_rows + baseline_rows), default=0.0)

    if abort_reason:
        verdict = "full_campaign_aborted_diagnostics_ready"
        next_step = "rerun_with_resume_after_abort"
    elif (not collapse) and (vs_cap is not None and vs_cap >= -0.005):
        verdict = "full_campaign_completed_ready_for_method_extension"
        next_step = "add_proposed_method"
    else:
        verdict = "full_campaign_completed_learning_still_blocked"
        next_step = "implement_true_per_EA_distributed_models"

    return {
        "config": cfg.to_dict(),
        "budgets_trained": budgets,
        "eval_at": eval_set,
        "candidate_rows": candidate_rows,
        "baseline_rows": baseline_rows,
        "checkpoint_manifest": checkpoint_manifest,
        "action_by_checkpoint": action_by_checkpoint,
        "abort_reason": abort_reason,
        "wall_seconds": round(wall, 1),
        "wall_hours": round(wall / 3600.0, 3),
        "q_value_diagnostics": q_diag,
        "learning_health": {
            "candidate_action_collapse_detected": collapse,
            "distinct_action_signatures": distinct,
            "candidate_matches_fixed_local": matches_local,
            "completion_trend_first_to_last": completion_trend,
            "reward_per_task_trend_first_to_last": reward_trend,
            "candidate_vs_fixed_local_completion": vs_local,
            "candidate_vs_capacity_split_completion": vs_cap,
            "mixed_policy_learned": (not collapse) and completion_trend > 0.0,
        },
        "reconciliation": {
            "reconciled_all": reconciled_all,
            "raw_vs_canonical_delta_max": delta_max,
        },
        "final_candidate": final_candidate,
        "best_candidate": best_candidate,
        "fixed_local": fixed_local,
        "capacity_split": cap_split,
        "random_legal": random_legal,
        "verdict": verdict,
        "recommended_next_step": next_step,
    }
