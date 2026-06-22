from __future__ import annotations

from types import SimpleNamespace

from src.analysis.algorithm_fidelity_against_paper_repair.runner import (
    ALGO_EXPLORATION_KWARGS,
    _build_learning_health,
    _build_paper_algorithm_1_mapping,
    _build_paper_audits,
    _configure_episode_target_sync,
    build_algorithm_fidelity_markdown,
    build_final_report_markdown,
)


def test_algorithm_fidelity_against_paper_repair_paper_audit_covers_algorithm_1_and_repair_notes() -> None:
    audits = _build_paper_audits()
    statuses = {row["status"] for row in audits["rows"]}
    assert "matched" in statuses
    assert "matched_with_repair" in statuses
    assert "approximated" in statuses
    mapping = _build_paper_algorithm_1_mapping()
    assert len(mapping) >= 4
    assert any(item["paper_step"].startswith("epsilon-greedy") for item in mapping)
    markdown = build_algorithm_fidelity_markdown(audits)
    assert "# Algorithm fidelity against paper audit" in markdown
    assert "Summary status" in markdown
    assert "matched_with_repair" in markdown


def test_algorithm_fidelity_against_paper_repair_episode_target_sync_hook_sets_episode_contract() -> None:
    session = SimpleNamespace(
        campaign_config=SimpleNamespace(target_update_contract=None),
        trainer=SimpleNamespace(config=SimpleNamespace(target_update_contract=None)),
    )
    _configure_episode_target_sync(session)
    contract = session.campaign_config.target_update_contract
    assert contract.target_update_unit == "episode"
    assert contract.update_frequency == 2000
    assert contract.approval_status.endswith("approved")
    assert session.trainer.config.target_update_contract.target_update_unit == "episode"


def test_algorithm_fidelity_against_paper_repair_learning_health_uses_oracle_gap_and_q_ranking_fields() -> None:
    before_rows = [
        {
            "training_budget": 100,
            "action_local_count": 10,
            "action_horizontal_count": 0,
            "action_vertical_count": 0,
            "reward_per_task": -5.0,
            "completion_ratio": 0.1,
            "drop_ratio": 0.8,
            "reward_reconciled": True,
            "terminal_reconciled": True,
            "raw_vs_canonical_reward_delta": 0.0,
        }
    ]
    rows = [
        {
            "training_budget": 100,
            "action_local_count": 4,
            "action_horizontal_count": 3,
            "action_vertical_count": 3,
            "reward_per_task": -4.0,
            "completion_ratio": 0.2,
            "drop_ratio": 0.7,
            "reward_reconciled": True,
            "terminal_reconciled": True,
            "raw_vs_canonical_reward_delta": 0.0,
            "q_value_diagnostics": {"q_local_mean": 1.0, "q_horizontal_mean": 2.0, "q_vertical_mean": 3.0},
        }
    ]
    oracle_report = {
        "policy_results": {
            "capacity_proportional_split": {
                "completion_ratio": 0.15,
                "reward_per_task": -4.5,
            }
        }
    }
    health = _build_learning_health(rows=rows, before_rows=before_rows, oracle_report=oracle_report)
    assert health["candidate_uses_more_than_one_action_in_greedy_eval"] is True
    assert health["candidate_reward_task_improves_vs_before"] is True
    assert health["candidate_completion_improves_vs_before"] is True
    assert health["candidate_vs_capacity_split_gap"]["completion_ratio_gap"] == 0.05000000000000002
    assert health["q_value_ranking"]["q_local_mean"] == 1.0


def test_algorithm_fidelity_against_paper_repair_final_report_markdown_includes_claim_safety_section() -> None:
    report = {
        "verdict": "algorithm_fidelity_repair_blocked",
        "recommended_next_step": "inspect_paper_exact_parameters",
        "algorithm_1_audited": True,
        "ddqn_audited": True,
        "dueling_audited": True,
        "lstm_audited": True,
        "target_update_audited": True,
        "multi_agent_audited": True,
        "replay_update_timing_audited": True,
        "pipeline_gates": {"reward_reconciliation_passed": True},
        "candidate_before": {"final_budget": {"completion_ratio": 0.1, "reward_per_task": -5.0}},
        "candidate_after": {"completion_ratio": 0.2, "reward_per_task": -4.0},
        "claim_safety": {"paper_reproduction_claim_made": False},
    }
    markdown = build_final_report_markdown(report)
    assert "Claim safety" in markdown
    assert "No paper-reproduction or superiority claims are made." in markdown
