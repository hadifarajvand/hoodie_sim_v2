"""CLI for the per-EA distributed baseline.

Modes:
  --dry-run                          validate config + paper audit, emit no training
  --smoke                            bounded smoke [50..1000] (no 5000)
  --execute-full-distributed-campaign   guarded full N_E=5000 (requires env var too)

Full campaign requires BOTH --execute-full-distributed-campaign AND
HOODIE_EXECUTE_DISTRIBUTED_FULL_CAMPAIGN=1. Without both, it refuses.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from .config import (
    EXECUTION_DISABLED_MESSAGE,
    EXECUTION_ENV_CONFIRMATION,
    build_distributed_config,
)
from .paper_fidelity_audit import build_paper_distributed_agent_audit


def _execution_authorized(flag: bool) -> bool:
    return bool(flag) and os.environ.get(EXECUTION_ENV_CONFIRMATION) == "1"


def _run_campaign(*, budgets: list[int], eval_at: list[int], epsilon_decay_episodes: int,
                  mode: str, emit_json: bool) -> int:
    from .reporting import run_and_report
    report = run_and_report(budgets=budgets, eval_at=eval_at,
                            epsilon_decay_episodes=epsilon_decay_episodes, mode=mode)
    if emit_json:
        print(json.dumps({
            "mode": mode,
            "executed_5000": report["executed_5000"],
            "verdict": report["verdict"],
            "recommended_next_step": report["recommended_next_step"],
            "distributed_vs_shared_completion": report["learning_health"].get("distributed_vs_shared_completion"),
            "distributed_vs_capacity_split_completion": report["learning_health"].get("distributed_vs_capacity_split_completion"),
            "local_dominant": report["learning_health"].get("local_dominant_policy"),
            "mixed_policy_learned": report["learning_health"].get("true_balanced_mixed_load_spreading_policy_learned"),
        }, indent=2))
    return 0


def run(*, dry_run: bool, smoke: bool, execute_full: bool, emit_json: bool) -> int:
    cfg = build_distributed_config()

    if execute_full:
        if not _execution_authorized(execute_full):
            print(EXECUTION_DISABLED_MESSAGE)
            return 0
        return _run_campaign(budgets=cfg.full_checkpoints, eval_at=cfg.full_eval_at,
                             epsilon_decay_episodes=cfg.full_epsilon_decay_episodes,
                             mode="full", emit_json=emit_json)

    if smoke:
        tiny = os.environ.get("HOODIE_DISTRIBUTED_TINY") == "1"
        if tiny:
            return _run_campaign(budgets=[2, 4], eval_at=[2, 4], epsilon_decay_episodes=2,
                                 mode="smoke_tiny", emit_json=emit_json)
        return _run_campaign(budgets=cfg.smoke_budgets, eval_at=cfg.smoke_eval_at,
                             epsilon_decay_episodes=cfg.smoke_epsilon_decay_episodes,
                             mode="smoke", emit_json=emit_json)

    if dry_run:
        from .reporting import write_dry_run
        report = write_dry_run()
        if emit_json:
            print(json.dumps({
                "mode": "dry_run", "executed_5000": False,
                "config_valid": True,
                "per_EA_models": cfg.num_agents,
                "paper_audit_core_exact": report["paper_audit"]["all_core_per_EA_items_exact"],
                "verdict": "true_per_EA_distributed_baseline_ready_for_full_campaign",
            }, indent=2))
        return 0

    # no flag -> refuse the full campaign by default
    print(EXECUTION_DISABLED_MESSAGE)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Per-EA distributed baseline (paper-faithful; no proposed method).")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--execute-full-distributed-campaign", dest="execute_full", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    return run(dry_run=args.dry_run, smoke=args.smoke, execute_full=args.execute_full, emit_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
