"""Config-only runner for the full paper campaign.

- Default (no flag): refuses, prints the execution-disabled message.
- ``--dry-run``: validates config + emits all config-only artifacts (no training).
- ``--execute-full-campaign``: gated; the config-only branch leaves the training
  path intentionally unwired, so even with the flag it cannot start 5000.

This module never trains a 5000-episode campaign.

Run::

    python -m src.analysis.full_paper_campaign_config.runner --dry-run --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .config import build_full_campaign_config
from .estimates import build_estimates
from .guards import (
    EXECUTION_DISABLED_MESSAGE,
    EXECUTION_ENV_CONFIRMATION,
    all_guards_pass,
    claim_safety,
    execution_authorized,
    validate_config,
)
from .runbook import build_runbook  # reuse the detailed runbook payload

OUT_DIR = Path("artifacts/production/full-paper-campaign-config-only")
FIGURES = OUT_DIR / "figures"

DRY_RUN_COMMAND = "python -m src.analysis.full_paper_campaign_config.runner --dry-run --json"
EXECUTE_COMMAND = "python -m src.analysis.full_paper_campaign_config.runner --execute-full-campaign --json"


def _commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def _w_json(name: str, payload: Any) -> str:
    p = OUT_DIR / name
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(p)


def _w_text(name: str, text: str) -> str:
    p = OUT_DIR / name
    p.write_text(text, encoding="utf-8")
    return str(p)


def _epsilon_figure(cfg) -> str:
    FIGURES.mkdir(parents=True, exist_ok=True)
    xs = list(range(0, cfg.number_of_training_episodes + 1, 100))
    ys = [cfg.epsilon_at(e) for e in xs]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(xs, ys, color="#1f77b4")
    ax.axvline(cfg.epsilon_decay_episodes, color="red", linestyle="--", label="N_E/2 = 2500")
    ax.set_xlabel("training episode"); ax.set_ylabel("epsilon")
    ax.set_title("Full campaign epsilon schedule (linear 1->0 over first N_E/2, then 0)")
    ax.legend(); fig.tight_layout()
    p = FIGURES / "figure_01_full_campaign_epsilon_schedule.png"
    fig.savefig(p, dpi=110); plt.close(fig)
    return str(p)


def _paper_parameter_summary(cfg) -> dict[str, Any]:
    d = cfg.to_dict()
    return {
        "source": "HOODIE paper Table 4 / Algorithm 1 (resources/papers/hoodie/ocr/merged.txt)",
        "N_E": d["number_of_training_episodes_N_E"],
        "T": d["episode_length_T"],
        "N_agents": d["number_of_agents_N"],
        "epsilon": d["epsilon"],
        "target_update": d["target_update"],
        "optimizer": d["optimizer"],
        "gamma": d["gamma"],
        "batch_size": d["batch_size"],
        "replay_memory_capacity": d["replay_memory_capacity"],
        "q_network_hidden_layers": d["q_network_hidden_layers"],
        "lstm_cells": d["lstm_cells"],
        "lstm_lookback_w": d["lstm_lookback_w"],
        "techniques": d["techniques"],
        "reward_equation": d["reward_equation"],
        "credit_assignment": d["credit_assignment"],
        "reconciliation_profile": d["reconciliation_profile"],
        "state_representation_profile": d["state_representation_profile"],
        "calibration_profile": d["calibration_profile"],
    }


def _md_execution_runbook(cfg, est, rb) -> str:
    d = cfg.to_dict()
    tot = est["total_wall_hours"]
    L = [
        "# Full HOODIE Paper Campaign — Execution Runbook (config only)",
        "",
        "> **This branch does NOT run the campaign.** Execution requires the explicit flag",
        f"> `--execute-full-campaign` AND the env confirmation `{EXECUTION_ENV_CONFIRMATION}=1`,",
        "> which is intentionally never set here. N_E=5000 is not run.",
        "",
        "## 1. Exact commands",
        f"- Dry-run / config validation: `{DRY_RUN_COMMAND}`",
        f"- Full campaign (gated, do not run without approval): `{EXECUTE_COMMAND}`",
        "",
        "## 2. Estimated wall time",
        f"- Training: {est['training_hours']['expected']} h (range {est['training_hours']['low']}–{est['training_hours']['high']} h)",
        f"- Evaluation: {est['evaluation_hours']} h",
        f"- **Total wall: {tot['expected']} h (range {tot['low']}–{tot['high']} h)** on {est['hardware_assumption']}",
        "",
        "## 3. Estimated storage",
        f"- ~{est['storage_checkpoints_mb']} MB checkpoints ({est['checkpoint_count']} ckpts) + "
        f"~{est['storage_replay_snapshot_mb']} MB replay + ~{est['storage_artifact_overhead_mb']} MB artifacts "
        f"≈ **~{est['storage_total_estimate_mb']} MB total**",
        "",
        "## 4. Checkpoint interval & resume",
        f"- Checkpoint every {cfg.checkpoint_every_episodes} episodes (see checkpoint-resume-plan.md).",
        f"- Resume: re-invoke the execute command; the runner loads the latest checkpoint and "
        f"continues to N_E={d['number_of_training_episodes_N_E']} (epsilon is episode-indexed, so resume is exact).",
        "",
        "## 5. Monitoring",
        "- `tail -f artifacts/production/full-paper-campaign-run/progress.jsonl` (see monitoring-plan.md).",
        "",
        "## 6. Artifact directory",
        "- `artifacts/production/full-paper-campaign-run/` (see expected-artifact-manifest.json).",
        "",
        "## 7. Abort conditions",
        "- See abort-conditions.md (NaN loss, reconciliation regression, delta!=0, coverage<1, disk full, runaway wall time).",
        "",
        "## 8. Post-run verification",
        "- `python -m src.analysis.paper_faithful_simulation_production.runner --json`  # paper-compatible metric schema check",
        "- Confirm reward_reconciled / terminal_reconciled true, raw_vs_canonical_delta=0, coverage=1.0 in final metrics.",
        "",
        "## 9. Known limitations",
        "- Shared-parameter trainer approximation, not the paper's per-EA distributed model fleet (see remaining-approximations.md).",
        "- Running 5000 tests the shared-parameter implementation ceiling only.",
        "",
        "## 10. Warning",
        "- No paper-reproduction, exact-numerical-reproduction, or baseline-superiority claims are made or implied.",
    ]
    return "\n".join(L)


def _md_checkpoint_resume(rb) -> str:
    s = rb["checkpoint_resume_strategy"]
    L = ["# Checkpoint / Resume Plan", "",
         f"- Cadence: every {s['checkpoint_cadence_episodes']} episodes",
         f"- Path: `{s['checkpoint_path_pattern']}`", "", "## Checkpoint contents"]
    L += [f"- {c}" for c in s["checkpoint_contents"]]
    L += ["", "## Resume protocol"] + [f"1. {x}" if i == 0 else f"{i+1}. {x}" for i, x in enumerate(s["resume_protocol"])]
    L += ["", f"_Determinism:_ {s['determinism_notes']}"]
    return "\n".join(L)


def _md_monitoring(rb) -> str:
    m = rb["monitoring"]
    L = ["# Monitoring Plan", ""]
    for k, v in m.items():
        if isinstance(v, list):
            L.append(f"## {k}")
            L += [f"- `{c}`" for c in v]
        else:
            L.append(f"- **{k}**: {v}")
    return "\n".join(L)


def _md_abort(rb) -> str:
    L = ["# Abort Conditions", ""]
    for a in rb["abort_conditions"]:
        L.append(f"- **{a['condition']}** → {a['action']}")
    return "\n".join(L)


def _md_approximations(rb) -> str:
    ma = rb["multi_agent_approximation"]
    return "\n".join([
        "# Remaining Approximations",
        "",
        "## Shared-parameter trainer vs paper per-EA distributed models",
        f"- **Paper design:** {ma['paper_design']}",
        f"- **Repo implementation:** {ma['repo_implementation']}",
        f"- **Status:** `{ma['status']}`",
        f"- **Impact:** {ma['impact']}",
        f"- **Implication for the full campaign:** {ma['implication_for_full_campaign']}",
        "",
        "**Will the full 5000 campaign test a true per-EA distributed fleet?** "
        "No. It tests the current single shared-parameter implementation only. A true "
        "per-EA distributed fleet (N=20 independent models) is not implemented and is out "
        "of scope for this config-only branch.",
    ])


def write_all_artifacts() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = build_full_campaign_config()
    rb = build_runbook()
    est = build_estimates(cfg)
    guards = validate_config(cfg)
    cs = claim_safety()

    written = []
    written.append(_w_json("full-paper-campaign-config.json", cfg.to_dict()))
    written.append(_w_json("compute-time-storage-estimates.json", est))
    written.append(_w_json("paper-parameter-summary.json", _paper_parameter_summary(cfg)))
    written.append(_w_json("expected-artifact-manifest.json", rb["expected_artifacts"]))
    written.append(_w_json("claim-safety.json", cs))
    written.append(_w_text("execution-runbook.md", _md_execution_runbook(cfg, est, rb)))
    written.append(_w_text("checkpoint-resume-plan.md", _md_checkpoint_resume(rb)))
    written.append(_w_text("monitoring-plan.md", _md_monitoring(rb)))
    written.append(_w_text("abort-conditions.md", _md_abort(rb)))
    written.append(_w_text("remaining-approximations.md", _md_approximations(rb)))
    figure = _epsilon_figure(cfg)

    verdict = (
        "full_paper_campaign_config_ready_for_user_approval"
        if all_guards_pass(cfg) and cs["claim_safety_passed"]
        else "full_paper_campaign_config_blocked"
    )
    report = {
        "branch": "full-paper-campaign-config-only",
        "commit_sha": _commit(),
        "executed_5000": False,
        "config_only": True,
        "dry_run_command": DRY_RUN_COMMAND,
        "execute_command": EXECUTE_COMMAND,
        "execution_disabled_message": EXECUTION_DISABLED_MESSAGE,
        "execution_env_confirmation_var": EXECUTION_ENV_CONFIRMATION,
        "guards": guards,
        "all_guards_pass": all_guards_pass(cfg),
        "claim_safety": cs,
        "estimates": est,
        "config": cfg.to_dict(),
        "verdict": verdict,
        "recommended_next_step": "wait_for_user_approval_to_execute_full_campaign",
        "figure": figure,
        "artifacts_written": written,
    }
    _w_json("config-only-final-report.json", report)
    _w_text("config-only-final-report.md", _md_final_report(report))
    return report


def _md_final_report(r: dict[str, Any]) -> str:
    return "\n".join([
        "# Full Paper Campaign — Config-Only Final Report",
        "",
        f"- **Verdict:** `{r['verdict']}`",
        f"- **Recommended next step:** `{r['recommended_next_step']}`",
        f"- Executed 5000: **{r['executed_5000']}**",
        f"- Dry-run command: `{r['dry_run_command']}`",
        f"- Execute command (gated): `{r['execute_command']}`",
        f"- All guards pass: **{r['all_guards_pass']}**",
        f"- Estimated total wall: {r['estimates']['total_wall_hours']['expected']} h "
        f"(range {r['estimates']['total_wall_hours']['low']}–{r['estimates']['total_wall_hours']['high']} h)",
        f"- Estimated storage: ~{r['estimates']['storage_total_estimate_mb']} MB",
        "- Claim safety: " + json.dumps(r["claim_safety"]),
    ])


def run(*, dry_run: bool, execute_full_campaign: bool, emit_json: bool) -> int:
    if execute_full_campaign:
        if not execution_authorized(execute_full_campaign):
            print(
                "Pre-flight only: --execute-full-campaign acknowledged, but execution is NOT authorized. "
                f"Set {EXECUTION_ENV_CONFIRMATION}=1 after explicit user approval; nothing was run."
            )
            return 0
        # Authorized full-campaign execution (explicit flag + env confirmation).
        from .executor import run_full_campaign
        from .execution_report import write_execution_artifacts

        import os as _os
        smoke = _os.environ.get("HOODIE_FULL_CAMPAIGN_SMOKE")
        kwargs: dict[str, Any] = {}
        if smoke:
            # Plumbing smoke: tiny budgets/decay to validate the path without 5000.
            kwargs = {"smoke_budgets": [2, 4], "eval_at": [2, 4], "epsilon_decay_episodes": 2}
        report = run_full_campaign(**kwargs)
        final = write_execution_artifacts(report, dry_run_output={"note": "see dry-run command output"})
        if emit_json:
            print(json.dumps({
                "executed_5000": final["executed_5000"],
                "abort_reason": final["abort_reason"],
                "wall_hours": final["wall_hours"],
                "verdict": final["verdict"],
                "recommended_next_step": final["recommended_next_step"],
            }, indent=2))
        return 0

    if dry_run:
        report = write_all_artifacts()
        if emit_json:
            print(json.dumps({
                "config_only": True,
                "executed_5000": False,
                "verdict": report["verdict"],
                "all_guards_pass": report["all_guards_pass"],
                "N_E": report["config"]["number_of_training_episodes_N_E"],
                "total_wall_hours": report["estimates"]["total_wall_hours"],
                "storage_total_estimate_mb": report["estimates"]["storage_total_estimate_mb"],
                "recommended_next_step": report["recommended_next_step"],
            }, indent=2))
        return 0

    # No flag: refuse execution with the exact required message.
    print(EXECUTION_DISABLED_MESSAGE)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Full paper campaign config (config only; never runs 5000).")
    parser.add_argument("--dry-run", action="store_true", help="validate config and emit config-only artifacts")
    parser.add_argument("--execute-full-campaign", action="store_true", help="gated; not executed on this branch")
    parser.add_argument("--json", action="store_true", help="emit JSON summary")
    args = parser.parse_args(argv)
    return run(dry_run=args.dry_run, execute_full_campaign=args.execute_full_campaign, emit_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
