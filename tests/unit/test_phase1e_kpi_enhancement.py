from __future__ import annotations

import pytest
from src.analysis.full_training_reproduction_campaign.trainer import EvaluationSummary, DDQNTrainer
from src.analysis.full_training_reproduction_campaign.config import CampaignConfig


def test_evaluation_summary_structure():
    """Verify EvaluationSummary enhanced fields have correct structure and values."""
    eval_summary = EvaluationSummary(
        evaluation_episode_count=3,
        mean_reward=2.0,
        completed_task_count=5,
        dropped_task_count=0,
        terminal_transition_count=8,
        reward_bearing_transition_count=8,
        trace_bank_disjoint=True,
        trace_bank_ids={"training": "train", "evaluation": "eval"},
        trace_ids=["trace1", "trace2", "trace3"],
        evaluation_on_training_traces=False,
        candidate_reproduction_supported=False,
        completion_rate_by_destination={"ea1": 0.5},
        reward_per_episode=[1.0, 2.0, 3.0],
        topology_usage_stats={"local": 10, "horizontal": 5, "vertical": 3},
    )
    
    data = eval_summary.to_dict()
    
    assert "completion_rate_by_destination" in data
    assert "reward_per_episode" in data
    assert "topology_usage_stats" in data
    assert isinstance(data["completion_rate_by_destination"], dict)
    assert isinstance(data["reward_per_episode"], list)
    assert isinstance(data["topology_usage_stats"], dict)
    assert data["completion_rate_by_destination"]["ea1"] == 0.5
    assert data["reward_per_episode"] == [1.0, 2.0, 3.0]
    assert data["topology_usage_stats"]["local"] == 10


@pytest.mark.parametrize("config_dim", [3, 74])
def test_evaluation_includes_enhanced_kpi_fields(config_dim):
    """Live evaluation with pilot trainer produces enhanced KPI fields."""
    cfg = CampaignConfig(state_dim=config_dim, action_count=22)
    trainer = DDQNTrainer(cfg)
    
    result = trainer.evaluate(episodes=2)
    
    # Enhanced fields present and well-formed
    assert hasattr(result, 'completion_rate_by_destination'), "Missing completion_rate_by_destination field"
    assert hasattr(result, 'reward_per_episode'), "Missing reward_per_episode field"
    assert hasattr(result, 'topology_usage_stats'), "Missing topology_usage_stats field"
    
    data = result.to_dict()
    for field in ['completion_rate_by_destination', 'reward_per_episode', 'topology_usage_stats']:
        assert field in data, f"Field {field} not present in to_dict() output"
        assert isinstance(data[field], (dict, list)), f"Field {field} has wrong type: {type(data[field])}"