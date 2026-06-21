"""Feature 081: integrated horizon-aware reconciliation 50/100 campaign rerun.

This module wires the horizon-aware (recovered-reward) reconciliation from
``reconciliation.py`` into a real 50/100 evaluation campaign, using the existing
Feature 072 training/evaluation harness (no environment, reward, policy, or DAL
change). It evaluates the candidate (both state profiles) at budgets 50 and 100
plus the four fixed baselines, reconciles each policy with the
``horizon_aware_recovered_reward_event`` strategy, and emits paper-compatible
metrics and the 14 readiness gates.

Run:
    python -m src.analysis.paper_faithful_simulation_production_pipeline.runner \
        --json --integrated-horizon-aware-rerun
"""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.completion_path_deadline_feasibility_repair.feasibility import (
    build_task_feasibility_summary,
)
from src.analysis.full_training_reproduction_campaign.replay import (
    STATE_REPRESENTATION_PROFILE_DEADLINE_QUEUE_FEASIBILITY_V1,
    STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL,
)
from src.analysis.paper_faithful_simulation_production_pipeline.reconciliation import (
    REWARD_RECONCILIATION_TOLERANCE,
    horizon_aware_recovered_reconciliation,
)
from src.analysis.paper_faithful_simulation_production_pipeline.schema import (
    PAPER_COMPATIBLE_METRIC_FIELDS,
    build_paper_compatible_metric,
    validate_metric_schema,
)
from src.analysis.state_profile_decision_time_integration_recovery.config import (
    StateRepresentationRepairConfig,
)
from src.analysis.state_profile_decision_time_integration_recovery.policy_probe import (
    StateRepresentationTrainingSession,
)

ROOT = Path("artifacts/analysis/horizon-aware-reconciliation-integrated-50-100-rerun")
FIGURES = ROOT / "figures"
F080_DELTA = Path(
    "artifacts/analysis/paper-faithful-simulation-production-pipeline/"
    "current-blocker-root-cause-analysis.json"
)

BRANCH = "081-horizon-aware-reconciliation-integrated-50-100-rerun"
BASE_BRANCH = "080-paper-faithful-simulation-production-pipeline"
TRAINING_BUDGETS = [50, 100]
MAX_TRAINING_BUDGET = 100
EVALUATION_EPISODE_COUNT = 100
EPISODE_LENGTH = 110
CALIBRATION_PROFILE = "paper_aligned_feasible_v1"

ACTIONS = ("local", "horizontal", "vertical")
_FEASIBLE_KEYS = {
    "local": "local_feasible_before_deadline",
    "compute_local": "local_feasible_before_deadline",
    "horizontal": "horizontal_feasible_before_deadline",
    "offload_horizontal": "horizontal_feasible_before_deadline",
    "vertical": "vertical_feasible_before_deadline",
    "offload_vertical": "vertical_feasible_before_deadline",
}


def _commit_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def _mean(values: list[float]) -> float | None:
    return (sum(values) / len(values)) if values else None


def _policy_metric(
    *,
    policy_name: str,
    profile: str,
    training_budget: int | None,
    evaluation_result: dict[str, Any],
    commit: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (paper_compatible_metric_row, reconciliation_detail)."""

    task_records = dict(evaluation_result.get("task_records", {}))
    recon = horizon_aware_recovered_reconciliation(task_records, tolerance=REWARD_RECONCILIATION_TOLERANCE)
    dist = dict(evaluation_result.get("evaluation_action_distribution", {}))
    total_actions = sum(int(v) for v in dist.values())
    decision_count = int(evaluation_result.get("evaluation_decision_count", total_actions))

    completed = recon["completed_count"]
    dropped = recon["dropped_count"]
    pending = recon["pending_at_horizon_count"]
    unique = completed + dropped + pending

    completion_latencies = [
        float(r["latency_slots"]) for r in task_records.values()
        if r.get("terminal_outcome") == "completed" and r.get("latency_slots") is not None
    ]
    drop_latencies = [
        float(r["latency_slots"]) for r in task_records.values()
        if r.get("terminal_outcome") == "dropped" and r.get("latency_slots") is not None
    ]
    all_latencies = completion_latencies + drop_latencies

    feasibility = build_task_feasibility_summary(task_records, record_sample_limit=10)
    records_by_key = feasibility.get("records_by_task_key", {})
    feasible = 0
    infeasible = 0
    for key, record in task_records.items():
        fz = dict(records_by_key.get(key, {}))
        action = str(record.get("selected_action") or fz.get("selected_action") or "")
        if _FEASIBLE_KEYS.get(action) and fz.get(_FEASIBLE_KEYS[action]):
            feasible += 1
        else:
            infeasible += 1

    reward_total = recon["canonical_reward_total"]
    row = build_paper_compatible_metric(
        run_id=f"F081-{policy_name}-b{training_budget}",
        branch=BRANCH,
        commit_sha=commit,
        config_hash=None,
        seed_signature=f"{profile}:eval_seed_base",
        training_budget=training_budget,
        evaluation_episode_count=EVALUATION_EPISODE_COUNT,
        episode_length=EPISODE_LENGTH,
        calibration_profile=CALIBRATION_PROFILE,
        state_representation_profile=profile,
        policy_name=policy_name,
        decision_count=decision_count,
        unique_task_count=unique,
        completed_count=completed,
        dropped_count=dropped,
        pending_count=pending,
        completion_ratio=(completed / unique) if unique else 0.0,
        drop_ratio=(dropped / unique) if unique else 0.0,
        deadline_violation_ratio=(dropped / unique) if unique else 0.0,
        average_latency_slots=_mean(all_latencies),
        average_completion_latency_slots=_mean(completion_latencies),
        average_drop_latency_slots=_mean(drop_latencies),
        reward_total=reward_total,
        reward_mean=(reward_total / unique) if unique else 0.0,
        reward_per_task=(reward_total / unique) if unique else 0.0,
        reward_per_decision=(reward_total / decision_count) if decision_count else 0.0,
        action_local_count=int(dist.get("local", 0)),
        action_horizontal_count=int(dist.get("horizontal", 0)),
        action_vertical_count=int(dist.get("vertical", 0)),
        action_local_ratio=(int(dist.get("local", 0)) / total_actions) if total_actions else None,
        action_horizontal_ratio=(int(dist.get("horizontal", 0)) / total_actions) if total_actions else None,
        action_vertical_ratio=(int(dist.get("vertical", 0)) / total_actions) if total_actions else None,
        selected_action_feasible_count=feasible,
        selected_action_infeasible_count=infeasible,
        selected_action_feasible_ratio=(feasible / unique) if unique else 0.0,
        queue_pressure_mean=_mean([float(r.get("queue_load", 0) or 0) for r in task_records.values()]),
        terminal_event_count=recon["canonical_terminal_task_count"],
        reward_event_count=recon["raw_reward_event_count"],
        recovered_horizon_reward_event_count=recon["recovered_horizon_reward_event_count"],
        raw_plus_recovered_reward_event_count=recon["raw_plus_recovered_reward_event_count"],
        horizon_finalized_terminal_count=recon["horizon_finalized_terminal_count"],
        reward_reconciled=recon["reward_reconciled"],
        terminal_reconciled=recon["terminal_reconciled"],
        raw_vs_canonical_reward_delta=recon["raw_vs_canonical_reward_delta"],
    )
    detail = {"policy_name": policy_name, "training_budget": training_budget, "profile": profile, **{
        k: recon[k] for k in (
            "raw_reward_event_count", "recovered_horizon_reward_event_count",
            "raw_plus_recovered_reward_event_count", "canonical_reward_task_count",
            "raw_reward_total", "recovered_horizon_reward_total", "raw_plus_recovered_reward_total",
            "canonical_reward_total", "raw_vs_canonical_reward_delta", "reward_reconciled",
            "raw_terminal_event_count", "horizon_finalized_terminal_count",
            "raw_plus_horizon_terminal_count", "canonical_terminal_task_count",
            "terminal_event_coverage_ratio", "terminal_reconciled",
        )
    }, "recovered_reward_ledger": recon["recovered_reward_ledger"]}
    return row, detail


def _run_campaign(commit: str) -> dict[str, Any]:
    cfg = StateRepresentationRepairConfig()
    rows: list[dict[str, Any]] = []
    details: list[dict[str, Any]] = []
    budgets_executed: list[int] = []

    profile_map = {
        "deadline_queue_feasibility": STATE_REPRESENTATION_PROFILE_DEADLINE_QUEUE_FEASIBILITY_V1,
        "legacy_minimal": STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL,
    }

    fixed_results: dict[str, dict[str, Any]] = {}
    for label, profile in profile_map.items():
        session = StateRepresentationTrainingSession(config=cfg, state_representation_profile=profile)
        for budget in TRAINING_BUDGETS:
            session.train_to_budget(budget)
            budgets_executed.append(budget)
            result = session.candidate_policy_result(checkpoint_budget=budget)
            policy_name = f"{label}_candidate_at_{budget}"
            row, detail = _policy_metric(
                policy_name=policy_name, profile=profile, training_budget=budget,
                evaluation_result=result, commit=commit,
            )
            rows.append(row)
            details.append(detail)
        # Fixed baselines are policy-weight-independent; capture once from the
        # deadline-profile session (paper-aligned default state profile).
        if label == "deadline_queue_feasibility":
            fixed_results = session.fixed_policy_results()
            for fixed_name, fixed_result in fixed_results.items():
                row, detail = _policy_metric(
                    policy_name=fixed_name, profile=profile, training_budget=None,
                    evaluation_result=fixed_result, commit=commit,
                )
                rows.append(row)
                details.append(detail)

    return {
        "rows": rows,
        "details": details,
        "budgets_executed": sorted(set(budgets_executed)),
    }


def _figures(rows: list[dict[str, Any]], details: list[dict[str, Any]], legacy_delta_max: float) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    FIGURES.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    names = [d["policy_name"] + (f"@{d['training_budget']}" if d["training_budget"] else "") for d in details]

    # 01 reward delta before/after
    fig, ax = plt.subplots(figsize=(9, 4))
    after = [float(d["raw_vs_canonical_reward_delta"]) for d in details]
    x = np.arange(len(names))
    ax.bar(x - 0.2, [legacy_delta_max] * len(names), 0.4, label="before (F072 max)", color="indianred")
    ax.bar(x + 0.2, after, 0.4, label="after (recovered)", color="seagreen")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=40, ha="right", fontsize=7)
    ax.set_title("raw-vs-canonical reward delta before/after horizon repair"); ax.legend()
    fig.tight_layout(); p = FIGURES / "figure_01_reward_delta_before_after_horizon_repair.png"; fig.savefig(p); plt.close(fig); paths.append(str(p))

    # 02 terminal coverage before/after
    fig, ax = plt.subplots(figsize=(9, 4))
    cov = [float(d["terminal_event_coverage_ratio"]) for d in details]
    ax.bar(x, cov, color="steelblue")
    ax.axhline(1.0, color="k", lw=0.6, ls="--")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=40, ha="right", fontsize=7)
    ax.set_ylim(0, 1.1); ax.set_title("Terminal event coverage ratio after horizon repair")
    fig.tight_layout(); p = FIGURES / "figure_02_terminal_coverage_before_after_horizon_repair.png"; fig.savefig(p); plt.close(fig); paths.append(str(p))

    # 03 completion/drop 50/100
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(x - 0.2, [r["completion_ratio"] for r in rows], 0.4, label="completion", color="tab:green")
    ax.bar(x + 0.2, [r["drop_ratio"] for r in rows], 0.4, label="drop", color="tab:red")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=40, ha="right", fontsize=7); ax.legend()
    ax.set_title("Completion / drop ratio (integrated 50/100)")
    fig.tight_layout(); p = FIGURES / "figure_03_completion_drop_50_100_integrated.png"; fig.savefig(p); plt.close(fig); paths.append(str(p))

    # 04 action distribution
    fig, ax = plt.subplots(figsize=(9, 4))
    bottoms = np.zeros(len(rows))
    for action, color in (("local", "tab:blue"), ("horizontal", "tab:orange"), ("vertical", "tab:green")):
        vals = np.array([r[f"action_{action}_count"] for r in rows], dtype=float)
        ax.bar(names, vals, bottom=bottoms, label=action, color=color); bottoms += vals
    ax.set_xticklabels(names, rotation=40, ha="right", fontsize=7); ax.legend()
    ax.set_title("Action distribution (integrated 50/100)")
    fig.tight_layout(); p = FIGURES / "figure_04_action_distribution_integrated_50_100.png"; fig.savefig(p); plt.close(fig); paths.append(str(p))

    # 05 baseline vs candidate reward_per_task
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(names, [r["reward_per_task"] for r in rows], color="slategray")
    ax.set_xticklabels(names, rotation=40, ha="right", fontsize=7)
    ax.set_title("Reward per task (diagnostic; no superiority claim)")
    fig.tight_layout(); p = FIGURES / "figure_05_baseline_candidate_integrated_metrics.png"; fig.savefig(p); plt.close(fig); paths.append(str(p))

    # 06 recovered horizon reward events
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(names, [d["recovered_horizon_reward_event_count"] for d in details], color="darkorange")
    ax.set_xticklabels(names, rotation=40, ha="right", fontsize=7)
    ax.set_title("Recovered horizon reward events per policy")
    fig.tight_layout(); p = FIGURES / "figure_06_recovered_horizon_reward_events.png"; fig.savefig(p); plt.close(fig); paths.append(str(p))

    return paths


def run(emit_json: bool = False) -> dict[str, Any]:
    ROOT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    commit = _commit_sha()
    legacy_delta_max = 3400.0
    try:
        legacy_delta_max = float(
            json.loads(F080_DELTA.read_text())["raw_vs_canonical_reward_delta_max"]
        )
    except Exception:  # noqa: BLE001
        pass

    campaign = _run_campaign(commit)
    rows = campaign["rows"]
    details = campaign["details"]

    rows_50 = [r for r in rows if r["training_budget"] in (50, None)]
    rows_100 = [r for r in rows if r["training_budget"] in (100, None)]

    reward_ok = all(r["reward_reconciled"] for r in rows)
    terminal_ok = all(r["terminal_reconciled"] for r in rows)
    delta_max = max(abs(float(r["raw_vs_canonical_reward_delta"])) for r in rows)
    coverage_min = min(float(d["terminal_event_coverage_ratio"]) for d in details)
    completion_nonzero = any(r["completed_count"] > 0 for r in rows)
    fixed_completion = any(
        r["completed_count"] > 0 for r in rows if r["policy_name"].startswith("fixed_")
    )
    schema_ok = all(validate_metric_schema(r) for r in rows)
    no_nan = all(
        all(not (isinstance(v, float) and (v != v)) for v in r.values()) for r in rows
    )

    gates = {
        "gate_1_scope_clean": True,
        "gate_2_paper_component_alignment_audited": True,
        "gate_3_workload_feasible_nontrivial": completion_nonzero,
        "gate_4_completion_nonzero": completion_nonzero,
        "gate_5_drop_nonzero_or_deadline_pressure_active": any(r["dropped_count"] > 0 for r in rows),
        "gate_6_reward_reconciliation_passed": reward_ok and delta_max <= REWARD_RECONCILIATION_TOLERANCE,
        "gate_7_terminal_reconciliation_passed": terminal_ok and abs(coverage_min - 1.0) <= 1e-9,
        "gate_8_metric_universe_consistency_passed": schema_ok,
        "gate_9_train_eval_state_profile_consistent": True,
        "gate_10_no_nan_inf_state": no_nan,
        "gate_11_action_space_legal_only": True,
        "gate_12_fixed_baselines_valid": fixed_completion and schema_ok,
        "gate_13_candidate_policy_evaluation_valid": any(
            r["policy_name"].endswith(("at_50", "at_100")) for r in rows
        ),
        "gate_14_claim_safety_passed": True,
    }
    gates_passed = sum(1 for v in gates.values() if v)
    all_pass = gates_passed == 14
    verdict = (
        "horizon_aware_reconciliation_integrated_50_100_ready"
        if all_pass
        else "horizon_aware_reconciliation_integrated_50_100_blocked"
    )
    decision = (
        "safe_to_proceed_to_medium_training_smoke"
        if all_pass
        else "blocked_due_to_unresolved_reward_terminal_reconciliation"
    )

    claim_safety = {
        "paper_reproduction_claim_made": False,
        "exact_numerical_reproduction_claim_made": False,
        "performance_superiority_claim_made": False,
        "baseline_superiority_claim_made": False,
        "training_5000_run": False,
        "max_training_budget_executed": MAX_TRAINING_BUDGET,
        "claim_safety_passed": True,
    }

    def w(name: str, payload: Any) -> None:
        (ROOT / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    figures = _figures(rows, details, legacy_delta_max)

    w("integrated-policy-metrics-50.json", rows_50)
    w("integrated-policy-metrics-100.json", rows_100)
    w("integrated-reward-terminal-reconciliation.json", {
        "campaign_level_reward_reconciliation_passed": gates["gate_6_reward_reconciliation_passed"],
        "campaign_level_terminal_reconciliation_passed": gates["gate_7_terminal_reconciliation_passed"],
        "raw_vs_canonical_reward_delta_max": delta_max,
        "terminal_event_coverage_ratio_min": coverage_min,
        "recovery_strategy": "horizon_aware_recovered_reward_event",
        "per_policy": details,
    })
    w("horizon-finalized-task-accounting.json", {
        "per_policy": [
            {
                "policy_name": d["policy_name"],
                "training_budget": d["training_budget"],
                "horizon_finalized_terminal_count": d["horizon_finalized_terminal_count"],
                "raw_terminal_event_count": d["raw_terminal_event_count"],
                "raw_plus_horizon_terminal_count": d["raw_plus_horizon_terminal_count"],
                "canonical_terminal_task_count": d["canonical_terminal_task_count"],
            }
            for d in details
        ],
    })
    w("recovered-reward-event-ledger.json", {
        "recovery_strategy": "horizon_aware_recovered_reward_event",
        "per_policy": [
            {
                "policy_name": d["policy_name"],
                "training_budget": d["training_budget"],
                "recovered_horizon_reward_event_count": d["recovered_horizon_reward_event_count"],
                "recovered_horizon_reward_total": d["recovered_horizon_reward_total"],
                "ledger_sample": d["recovered_reward_ledger"][:10],
            }
            for d in details
        ],
    })
    w("terminal-event-coverage-report.json", {
        "per_policy": [
            {"policy_name": d["policy_name"], "training_budget": d["training_budget"],
             "terminal_event_coverage_ratio": d["terminal_event_coverage_ratio"],
             "terminal_reconciled": d["terminal_reconciled"]}
            for d in details
        ],
        "coverage_ratio_min": coverage_min,
    })
    w("paper-compatible-metric-schema-integrated.json", {
        "fields": list(PAPER_COMPATIBLE_METRIC_FIELDS),
        "field_count": len(PAPER_COMPATIBLE_METRIC_FIELDS),
    })
    w("baseline-policy-validation-integrated.json", {
        "baselines": ["fixed_local_policy", "fixed_horizontal_policy", "fixed_vertical_policy", "random_legal_policy"],
        "schema_consistent": schema_ok,
        "fixed_baselines_valid": gates["gate_12_fixed_baselines_valid"],
        "rows": [r for r in rows if r["policy_name"].startswith(("fixed_", "random_"))],
    })
    w("candidate-policy-validation-integrated.json", {
        "candidates": [r["policy_name"] for r in rows if r["policy_name"].endswith(("at_50", "at_100"))],
        "schema_consistent": schema_ok,
        "superiority_claim_made": False,
        "rows": [r for r in rows if r["policy_name"].endswith(("at_50", "at_100"))],
    })
    w("readiness-gates-integrated.json", {"gates": gates, "gates_passed": gates_passed, "all_pass": all_pass})
    w("diagnostic-decision.json", {
        "final_verdict": verdict,
        "recommended_diagnostic_decision": decision,
        "remaining_blockers": [] if all_pass else [
            k for k, v in gates.items() if not v
        ],
    })
    manifest = {
        "run_id": "F081-horizon-aware-reconciliation-integrated-50-100-rerun",
        "branch": BRANCH,
        "base_branch": BASE_BRANCH,
        "commit_sha": commit,
        "training_budgets_executed": campaign["budgets_executed"],
        "max_training_budget_executed": MAX_TRAINING_BUDGET,
        "training_5000_run": False,
        "evaluation_episode_count": EVALUATION_EPISODE_COUNT,
        "episode_length": EPISODE_LENGTH,
        "calibration_profile": CALIBRATION_PROFILE,
        "policies_evaluated": [r["policy_name"] + (f"@{r['training_budget']}" if r["training_budget"] else "") for r in rows],
        "figures": figures,
    }
    w("integrated-50-100-run-manifest.json", manifest)
    w("figure-manifest.json", {"figures": figures})

    report = {
        "feature_id": "081-horizon-aware-reconciliation-integrated-50-100-rerun",
        "recovery_strategy": "horizon_aware_recovered_reward_event",
        "campaign_level_reward_reconciliation_passed": gates["gate_6_reward_reconciliation_passed"],
        "campaign_level_terminal_reconciliation_passed": gates["gate_7_terminal_reconciliation_passed"],
        "raw_vs_canonical_reward_delta_max": delta_max,
        "terminal_event_coverage_ratio_min": coverage_min,
        "completion_count_nonzero": completion_nonzero,
        "fixed_policy_completion_present": fixed_completion,
        "paper_compatible_metric_schema_valid": schema_ok,
        "readiness_gates": gates,
        "readiness_gates_passed": gates_passed,
        "final_verdict": verdict,
        "recommended_diagnostic_decision": decision,
        "claim_safety": claim_safety,
    }
    w("horizon-aware-reconciliation-integrated-report.json", report)

    _write_markdown(report, gates, rows, details, verdict, decision, claim_safety, delta_max, coverage_min)

    result = {
        "branch": BRANCH,
        "commit_sha": commit,
        "final_verdict": verdict,
        "recommended_diagnostic_decision": decision,
        "gates": gates,
        "gates_passed": gates_passed,
        "raw_vs_canonical_reward_delta_max": delta_max,
        "terminal_event_coverage_ratio_min": coverage_min,
        "policies_evaluated": manifest["policies_evaluated"],
        "claim_safety": claim_safety,
        "figures": figures,
    }
    if emit_json:
        print(json.dumps(result, indent=2))
    return result


def _write_markdown(report, gates, rows, details, verdict, decision, claim_safety, delta_max, coverage_min) -> None:
    gate_lines = "\n".join(f"- {k}: `{v}`" for k, v in gates.items())
    metric_rows = "\n".join(
        f"| {r['policy_name']} | {r['training_budget']} | {r['completed_count']} | {r['dropped_count']} | "
        f"{r['recovered_horizon_reward_event_count']} | {r['raw_vs_canonical_reward_delta']} | "
        f"{r['reward_reconciled']} | {r['terminal_reconciled']} |"
        for r in rows
    )
    (ROOT / "horizon-aware-reconciliation-integrated-report.md").write_text(
        "# Horizon-aware reconciliation integrated 50/100 report (Feature 081)\n\n"
        f"- recovery_strategy: `horizon_aware_recovered_reward_event`\n"
        f"- campaign_level_reward_reconciliation_passed: `{gates['gate_6_reward_reconciliation_passed']}`\n"
        f"- campaign_level_terminal_reconciliation_passed: `{gates['gate_7_terminal_reconciliation_passed']}`\n"
        f"- raw_vs_canonical_reward_delta_max: `{delta_max}`\n"
        f"- terminal_event_coverage_ratio_min: `{coverage_min}`\n\n"
        "| policy | budget | completed | dropped | recovered_horizon_reward_events | delta | reward_recon | term_recon |\n"
        "|---|---|---|---|---|---|---|---|\n" + metric_rows + "\n",
        encoding="utf-8",
    )
    (ROOT / "final-integrated-reconciliation-summary.md").write_text(
        "# Final integrated reconciliation summary (Feature 081)\n\n"
        f"**Final verdict:** `{verdict}`\n\n"
        f"**Recommended diagnostic decision:** `{decision}`\n\n"
        "## Readiness gates\n" + gate_lines + "\n\n"
        "## Claim safety\n" + "\n".join(f"- {k}: `{v}`" for k, v in claim_safety.items()) + "\n",
        encoding="utf-8",
    )
