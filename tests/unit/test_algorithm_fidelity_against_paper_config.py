from __future__ import annotations

from src.analysis.algorithm_fidelity_against_paper_repair.config import (
    AlgorithmFidelityConfig,
    EVALUATION_EPISODE_COUNT,
    MAX_TRAINING_BUDGET,
    PAPER_EPSILON_DECAY_EPISODES,
    PAPER_EPSILON_FINAL,
    PAPER_EPSILON_START,
    PAPER_TARGET_UPDATE_APPROVAL,
    PAPER_TARGET_UPDATE_EVIDENCE,
    PAPER_TARGET_UPDATE_FREQUENCY,
    TRAINING_BUDGETS,
    build_profile,
)
from src.analysis.full_training_reproduction_campaign.config import TargetUpdateContract


def test_algorithm_fidelity_against_paper_repair_config_matches_paper_smoke_bounds() -> None:
    cfg = AlgorithmFidelityConfig()
    assert cfg.training_budgets == TRAINING_BUDGETS
    assert cfg.max_training_budget == MAX_TRAINING_BUDGET
    assert cfg.evaluation_episode_count == EVALUATION_EPISODE_COUNT
    assert cfg.paper_epsilon_start == PAPER_EPSILON_START
    assert cfg.paper_epsilon_final == PAPER_EPSILON_FINAL
    assert cfg.paper_epsilon_decay_episodes == PAPER_EPSILON_DECAY_EPISODES
    assert cfg.paper_target_update_frequency == PAPER_TARGET_UPDATE_FREQUENCY
    assert cfg.to_dict()["calibration_profile"] == "paper_aligned_feasible_v1"
    assert cfg.to_dict()["state_representation_profile"] == "deadline_queue_feasibility_v1"
    assert build_profile().training_budgets == TRAINING_BUDGETS


def test_algorithm_fidelity_against_paper_repair_episode_target_update_requires_explicit_paper_alignment() -> None:
    contract = TargetUpdateContract(
        update_frequency=PAPER_TARGET_UPDATE_FREQUENCY,
        target_update_unit="episode",
        approval_status=PAPER_TARGET_UPDATE_APPROVAL,
        paper_evidence_status=PAPER_TARGET_UPDATE_EVIDENCE,
    )
    assert contract.should_sync(episode_count=PAPER_TARGET_UPDATE_FREQUENCY) is True
    assert contract.should_sync(episode_count=PAPER_TARGET_UPDATE_FREQUENCY - 1) is False
