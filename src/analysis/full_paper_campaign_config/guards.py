"""Safety guards for the full paper campaign (config only).

These guards enforce that the 5000-episode campaign cannot start by accident:
execution requires an explicit flag AND an explicit environment confirmation, and
the config-only branch deliberately leaves the training path unwired.
"""

from __future__ import annotations

import os
from typing import Any

from .config import FullPaperCampaignConfig

EXECUTION_DISABLED_MESSAGE = (
    "Full campaign execution is disabled by default. "
    "Pass --execute-full-campaign only after explicit user approval."
)
# Even with the flag, the config-only branch requires this env var to be set to a
# deliberate value; it is never set here, so 5000 cannot be launched from this branch.
EXECUTION_ENV_CONFIRMATION = "HOODIE_EXECUTE_FULL_CAMPAIGN"


def validate_config(cfg: FullPaperCampaignConfig) -> dict[str, bool]:
    """Return the guard checks required by the campaign spec."""
    return {
        "config_only_execute_false": cfg.execute is False,
        "N_E_is_5000": cfg.number_of_training_episodes == 5000,
        "episode_length_is_110": cfg.episode_length == 110,
        "epsilon_schedule_paper_aligned": (
            cfg.epsilon_start == 1.0
            and cfg.epsilon_final == 0.0
            and cfg.epsilon_decay_episodes == 2500
            and cfg.epsilon_schedule_unit == "episode"
        ),
        "target_sync_2000_episodes": (
            cfg.target_update_frequency == 2000 and cfg.target_update_unit == "episode"
        ),
        "learning_rate_7e_7": cfg.learning_rate == 7e-7,
        "gamma_0_99": cfg.gamma == 0.99,
        "batch_64": cfg.batch_size == 64,
        "replay_10000": cfg.replay_memory_capacity == 10_000,
        "per_task_delayed_reward_credit_enabled": cfg.credit_assignment == "per_task_delayed_reward",
        "horizon_aware_reconciliation_enabled": (
            cfg.reconciliation_profile == "horizon_aware_recovered_reward_event"
        ),
    }


def all_guards_pass(cfg: FullPaperCampaignConfig) -> bool:
    return all(validate_config(cfg).values())


def claim_safety() -> dict[str, Any]:
    return {
        "training_5000_run": False,
        "config_only": True,
        "paper_reproduction_claim_made": False,
        "exact_numerical_reproduction_claim_made": False,
        "performance_superiority_claim_made": False,
        "baseline_superiority_claim_made": False,
        "reward_function_modified": False,
        "environment_semantics_modified": False,
        "claim_safety_passed": True,
    }


def execution_authorized(execute_flag: bool, env: dict[str, str] | None = None) -> bool:
    """Execution requires BOTH the explicit flag and an explicit env confirmation.

    The config-only branch never sets the env var, so this returns False here.
    """
    env = env if env is not None else dict(os.environ)
    return bool(execute_flag) and env.get(EXECUTION_ENV_CONFIRMATION) == "1"
