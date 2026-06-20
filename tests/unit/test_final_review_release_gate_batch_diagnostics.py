from __future__ import annotations

from src.analysis.final_review_release_gate_batch.runner import build_final_review_release_gate_batch_report


def test_gate_detects_static_reward_vertical_collapse_and_replay_cap() -> None:
    report = build_final_review_release_gate_batch_report().to_dict()

    assert report["final_verdict"] == "final_review_release_gate_blocked"
    assert report["diagnostic_findings"]["evaluation_reward_static_across_budget"] is True
    assert report["diagnostic_findings"]["vertical_action_collapse_detected"] is True
    assert report["diagnostic_findings"]["replay_size_cap_detected"] is True
    assert report["diagnostic_findings"]["evaluation_signal_sufficient_for_claims"] is False
    assert report["next_action_decision"]["recommended_next_action"] == "audit_reward_and_evaluation_design_before_more_training"

    means = report["reward_stability_review"]["evaluation_mean_rewards"]
    assert len(set(means.values())) == 1
    assert means["100"] == means["150"] == means["200"] == means["500"]
    assert report["action_collapse_review"]["vertical_share_by_budget"]["500"] == 1.0
    assert report["replay_buffer_review"]["observed_replay_size_by_checkpoint"]["100"] == 10000
    assert report["replay_buffer_review"]["observed_replay_size_by_checkpoint"]["500"] == 10000
