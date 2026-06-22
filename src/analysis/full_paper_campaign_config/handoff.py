"""Generate the user-execution handoff artifacts for the full paper campaign.

This module writes the handoff package only. It never trains and never executes
the 5000-episode campaign.

Run::

    python -m src.analysis.full_paper_campaign_config.handoff --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

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
from .executor import CHECKPOINT_BUDGETS, EVAL_AT, OUT_DIR as RUN_OUT_DIR

OUT_DIR = Path("artifacts/production/full-paper-campaign-user-execution-handoff")
BRANCH = "full-paper-campaign-user-execution-handoff"
REPO = "/Users/hadi/Documents/GitHub/hoodie_sim_v2"

FULL_COMMAND = (
    "cd /Users/hadi/Documents/GitHub/hoodie_sim_v2\n"
    "PY=/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venvmac/bin/python\n\n"
    "git fetch origin\n"
    f"git checkout {BRANCH}\n"
    f"git reset --hard origin/{BRANCH}\n\n"
    "HOODIE_EXECUTE_FULL_CAMPAIGN=1 $PY -m src.analysis.full_paper_campaign_config.runner "
    "--execute-full-campaign --json"
)
DRY_RUN_COMMAND = (
    "cd /Users/hadi/Documents/GitHub/hoodie_sim_v2\n"
    "PY=/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venvmac/bin/python\n\n"
    "$PY -m src.analysis.full_paper_campaign_config.runner --dry-run --json"
)


def _commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def _w(name: str, payload: Any) -> None:
    p = OUT_DIR / name
    p.write_text(payload if isinstance(payload, str) else json.dumps(payload, indent=2), encoding="utf-8")


def _execution_guard_validation() -> dict[str, Any]:
    return {
        "requires_flag": "--execute-full-campaign",
        "requires_env": f"{EXECUTION_ENV_CONFIRMATION}=1",
        "refusal_message_without_flag": EXECUTION_DISABLED_MESSAGE,
        "authorized_when_flag_only": execution_authorized(True, {}),                  # False
        "authorized_when_env_only": execution_authorized(False, {EXECUTION_ENV_CONFIRMATION: "1"}),  # False
        "authorized_when_both": execution_authorized(True, {EXECUTION_ENV_CONFIRMATION: "1"}),       # True
        "guard_correct": (
            execution_authorized(True, {}) is False
            and execution_authorized(False, {EXECUTION_ENV_CONFIRMATION: "1"}) is False
            and execution_authorized(True, {EXECUTION_ENV_CONFIRMATION: "1"}) is True
        ),
    }


def _post_run_instructions() -> str:
    return "\n".join([
        "# Post-Run Instructions",
        "",
        "After running the full campaign command, please return the following evidence:",
        "",
        "```text",
        "Run completed or aborted:",
        "Exit code:",
        "Wall time:",
        "Last checkpoint completed:",
        "Path of full-campaign artifacts:",
        "Any error output:",
        "git status:",
        "```",
        "",
        f"Full-campaign artifacts are written under: `{RUN_OUT_DIR}/`",
        "Checkpoints (~660 MB) are written under that directory's `checkpoints/` and are gitignored.",
        "",
        "Once you paste the evidence back, I will analyze the results, generate the comparison",
        "artifacts and figures, run the tests, and commit/push the completed execution results.",
    ])


def _user_execution_command_md(cfg, est) -> str:
    return "\n".join([
        "# Full Paper Campaign — User Execution Command",
        "",
        "> Execution requires BOTH the explicit flag AND the env confirmation. Without both, the",
        "> runner refuses and prints the disabled message. The agent will NOT run this for you.",
        "",
        "## Run the full campaign (manual)",
        "```bash",
        FULL_COMMAND,
        "```",
        "",
        "## Dry-run / config validation (safe, no training)",
        "```bash",
        DRY_RUN_COMMAND,
        "```",
        "",
        "## What it will do",
        f"- Train N_E={cfg['number_of_training_episodes_N_E']} episodes (T={cfg['episode_length_T']}), "
        f"checkpoint every 250 episodes ({len(CHECKPOINT_BUDGETS)} checkpoints).",
        f"- Evaluate candidate at {EVAL_AT} vs fixed_local/horizontal/vertical, random_legal, capacity_proportional_split.",
        f"- Estimated wall time: ~{est['total_wall_hours']['expected']} h "
        f"(range {est['total_wall_hours']['low']}–{est['total_wall_hours']['high']} h) on {est['hardware_assumption']}.",
        f"- Estimated storage: ~{est['storage_total_estimate_mb']} MB (checkpoints gitignored).",
        f"- Writes artifacts under `{RUN_OUT_DIR}/`.",
        "",
        "## Abort behavior",
        "- Aborts safely on: NaN/Inf loss, raw-vs-canonical delta != 0, terminal coverage < 1.0,",
        "  reconciliation failure, checkpoint write failure, disk full, wall time > 2x upper estimate,",
        "  metric-schema break, or unexpected exception. On abort it still writes abort-status.json,",
        "  monitoring-log-summary.json, and a partial run manifest.",
    ])


def run(emit_json: bool = False) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = build_full_campaign_config()
    est = build_estimates(cfg)
    guard = _execution_guard_validation()
    cs = claim_safety()
    config_checks = validate_config(cfg)

    _w("full-campaign-command.txt", FULL_COMMAND + "\n")
    _w("user-execution-command.md", _user_execution_command_md(cfg.to_dict(), est))
    _w("dry-run-validation.json", {
        "command": "python -m src.analysis.full_paper_campaign_config.runner --dry-run --json",
        "config": cfg.to_dict(),
        "estimates": est,
        "all_config_guards_pass": all_guards_pass(cfg),
        "config_checks": config_checks,
    })
    _w("execution-guard-validation.json", guard)
    _w("post-run-instructions.md", _post_run_instructions())
    _w("claim-safety.json", cs)

    verdict = (
        "full_campaign_user_execution_handoff_ready"
        if all_guards_pass(cfg) and guard["guard_correct"] and cs["claim_safety_passed"]
        else "full_campaign_user_execution_handoff_blocked"
    )
    report = {
        "branch": BRANCH,
        "commit_sha": _commit(),
        "executed_5000": False,
        "execution_path_wired": True,
        "execution_requires": ["--execute-full-campaign", f"{EXECUTION_ENV_CONFIRMATION}=1"],
        "full_execution_command": FULL_COMMAND,
        "dry_run_command": DRY_RUN_COMMAND,
        "config_checks": config_checks,
        "all_config_guards_pass": all_guards_pass(cfg),
        "execution_guard_validation": guard,
        "checkpoint_budgets": CHECKPOINT_BUDGETS,
        "eval_at": EVAL_AT,
        "output_artifact_path": str(RUN_OUT_DIR),
        "estimates": est,
        "claim_safety": cs,
        "verdict": verdict,
        "recommended_next_step": "user_runs_full_campaign_command",
    }
    _w("handoff-final-report.json", report)
    _w("handoff-final-report.md", _final_md(report))

    if emit_json:
        print(json.dumps({
            "executed_5000": False,
            "execution_path_wired": True,
            "guard_correct": guard["guard_correct"],
            "all_config_guards_pass": report["all_config_guards_pass"],
            "verdict": verdict,
            "recommended_next_step": report["recommended_next_step"],
        }, indent=2))
    return report


def _final_md(r: dict[str, Any]) -> str:
    return "\n".join([
        "# Full Paper Campaign — User Execution Handoff Report",
        "",
        f"- **Verdict:** `{r['verdict']}`",
        f"- **Next step:** `{r['recommended_next_step']}`",
        f"- Executed 5000: {r['executed_5000']} | Execution path wired: {r['execution_path_wired']}",
        f"- Execution requires: {', '.join(r['execution_requires'])}",
        f"- Config guards pass: {r['all_config_guards_pass']} | Execution guard correct: {r['execution_guard_validation']['guard_correct']}",
        f"- Output artifacts: `{r['output_artifact_path']}/`",
        "",
        "## Full execution command",
        "```bash",
        r["full_execution_command"],
        "```",
        "",
        "## Dry-run command",
        "```bash",
        r["dry_run_command"],
        "```",
        "",
        "## Claim safety",
        "- No paper-reproduction / exact-numerical / performance / baseline-superiority claims are made.",
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate full-campaign user-execution handoff (never trains).")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    run(emit_json=args.json)


if __name__ == "__main__":
    main()
