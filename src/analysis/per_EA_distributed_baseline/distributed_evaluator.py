"""Evaluate the distributed per-EA candidate + comparators with reconciliation.

Candidate eval routes each task's greedy action to the OWNING EA's network, reusing
the validated horizon-aware reconciliation evaluator. The decision-time state
encoding is shared (host trainer) while the network weights are per-agent — a
documented approximation (training is genuinely per-EA). Comparators (fixed
policies + capacity_proportional_split oracle) reuse the existing suite unchanged.
"""

from __future__ import annotations

import random
from typing import Any, Callable

from src.environment.gym_adapter import HoodieGymEnvironment
from src.analysis.paper_faithful_simulation_production.profiles import ProductionProfile
from src.analysis.paper_faithful_simulation_production.simulation_runner import _metric_row
from src.analysis.state_profile_decision_time_integration_recovery.config import (
    StateRepresentationRepairConfig,
    NEW_STATE_REPRESENTATION_PROFILE,
)
from src.analysis.state_profile_decision_time_integration_recovery.policy_probe import (
    StateRepresentationTrainingSession,
    _patched_calibrated_session_environment,
    _patched_decision_time_state_injection,
)
from src.analysis.state_profile_decision_time_integration_recovery.state_profile_adapter import (
    patched_terminal_evaluator_state_profile,
)
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.repaired_terminal_evaluator import (
    evaluate_policy_on_trace_bank_terminal_repaired,
)

from .distributed_trainer import DistributedTrainer, calibrated_environment

_CAP_WEIGHTS = {"local": 10.0, "horizontal": 10.0, "vertical": 3.0}


def _capacity_split_policy(seed: int = 53) -> Callable:
    rng = random.Random(seed)

    def _p(state_tensor, legal_action_mask, context):
        legal = [a for a in ("local", "horizontal", "vertical") if legal_action_mask.get(a, False)]
        if not legal:
            return "local"
        return rng.choices(legal, weights=[_CAP_WEIGHTS[a] for a in legal], k=1)[0]

    return _p


def evaluate_distributed_candidate(trainer: DistributedTrainer, *, episodes: int, checkpoint_budget: int) -> dict[str, Any]:
    host = trainer.agents[0]
    cfg = host.config
    holder: dict[str, Any] = {"task": None}

    with calibrated_environment(), \
         patched_terminal_evaluator_state_profile(cfg.state_representation_profile), \
         _patched_decision_time_state_injection(host):
        inj_observe = HoodieGymEnvironment.observe_flat

        def _stash_observe(self, current_task=None):  # type: ignore[no-untyped-def]
            holder["task"] = current_task if current_task is not None else self.current_task
            return inj_observe(self, current_task)

        def _policy_fn(state_tensor, legal_action_mask, context):
            task = holder["task"]
            owner = trainer._owner(task) if task is not None else 0
            return trainer.agents[owner].policy.choose_action(state_tensor, legal_action_mask)

        HoodieGymEnvironment.observe_flat = _stash_observe  # type: ignore[assignment]
        try:
            return evaluate_policy_on_trace_bank_terminal_repaired(
                trainer=host,
                policy_name=f"distributed_candidate_at_{checkpoint_budget}",
                policy_fn=_policy_fn,
                evaluation_episode_count=episodes,
                episode_length=cfg.evaluation_episode_length,
                seed_base=cfg.seed_bundle.evaluation_trace_generation_seed,
                checkpoint_budget=checkpoint_budget,
                policy_kind="candidate",
                evaluation_trace_bank_id=cfg.evaluation_trace_bank_id,
            )
        finally:
            HoodieGymEnvironment.observe_flat = inj_observe  # type: ignore[assignment]


def evaluate_comparators(*, episodes: int) -> list[dict[str, Any]]:
    """Fixed baselines + capacity_proportional_split oracle (network-independent)."""
    session = StateRepresentationTrainingSession(
        config=StateRepresentationRepairConfig(),
        state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE,
    )
    profile = ProductionProfile()
    rows: list[dict[str, Any]] = []
    fixed = session.fixed_policy_results()
    for name, res in fixed.items():
        row, _ = _metric_row(policy_name=name, training_budget=None, evaluation_result=res,
                             profile=profile, commit="per-ea-distributed")
        rows.append(row)
    cfg = session.campaign_config
    with _patched_calibrated_session_environment(session), \
         patched_terminal_evaluator_state_profile(cfg.state_representation_profile), \
         _patched_decision_time_state_injection(session.trainer):
        cap = evaluate_policy_on_trace_bank_terminal_repaired(
            trainer=session.trainer, policy_name="capacity_proportional_split",
            policy_fn=_capacity_split_policy(), evaluation_episode_count=episodes,
            episode_length=session.config.episode_length,
            seed_base=cfg.seed_bundle.evaluation_trace_generation_seed,
            checkpoint_budget=100, policy_kind="fixed",
            evaluation_trace_bank_id=cfg.evaluation_trace_bank_id,
            record_sample_limit=session.config.record_sample_limit,
        )
    cap_row, _ = _metric_row(policy_name="capacity_proportional_split", training_budget=None,
                             evaluation_result=cap, profile=profile, commit="per-ea-distributed")
    rows.append(cap_row)
    return rows


def candidate_row(result: dict[str, Any], budget: int) -> dict[str, Any]:
    row, _ = _metric_row(policy_name=f"distributed_candidate_at_{budget}", training_budget=budget,
                         evaluation_result=result, profile=ProductionProfile(), commit="per-ea-distributed")
    return row
