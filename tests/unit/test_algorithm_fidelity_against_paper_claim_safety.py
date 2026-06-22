from __future__ import annotations

from src.analysis.algorithm_fidelity_against_paper_repair.config import AlgorithmFidelityConfig
from src.analysis.algorithm_fidelity_against_paper_repair.runner import ALGO_EXPLORATION_KWARGS


def test_algorithm_fidelity_against_paper_repair_claim_safety_inputs_do_not_include_forbidden_settings() -> None:
    cfg = AlgorithmFidelityConfig()
    assert cfg.max_training_budget == 1000
    assert ALGO_EXPLORATION_KWARGS["schedule_unit"] == "episode"
    assert ALGO_EXPLORATION_KWARGS["epsilon_start"] == 1.0
    assert ALGO_EXPLORATION_KWARGS["epsilon_final"] == 0.0
    assert ALGO_EXPLORATION_KWARGS["epsilon_decay_steps"] == 2500
    assert ALGO_EXPLORATION_KWARGS["seed"] == 53
    assert "5000" not in str(ALGO_EXPLORATION_KWARGS)
