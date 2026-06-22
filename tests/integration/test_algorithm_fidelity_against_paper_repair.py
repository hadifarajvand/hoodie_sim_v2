"""Integration tests for algorithm-fidelity repair artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path("artifacts/production/algorithm-fidelity-against-paper-repair")
pytestmark = pytest.mark.skipif(
    not (ROOT / "final-report.json").exists(),
    reason="algorithm-fidelity artifacts not present; run the repair smoke first",
)


def _load(name: str):
    return json.loads((ROOT / name).read_text())


def test_required_artifacts_exist() -> None:
    for name in (
        "algorithm-fidelity-audit.json",
        "algorithm-fidelity-audit.md",
        "paper-algorithm-1-mapping.json",
        "ddqn-target-calculation-audit.json",
        "dueling-network-audit.json",
        "lstm-state-window-audit.json",
        "target-network-update-audit.json",
        "multi-agent-implementation-audit.json",
        "state-action-policy-wiring-audit.json",
        "replay-update-timing-audit.json",
        "optimizer-loss-learning-rate-audit.json",
        "algorithm-repair-implementation-summary.json",
        "candidate-metrics-after-algorithm-repair.json",
        "baseline-and-oracle-metrics.json",
        "learning-health-after-algorithm-repair.json",
        "reward-terminal-reconciliation-after-algorithm-repair.json",
        "claim-safety.json",
        "final-report.json",
        "final-report.md",
        "commit-summary.md",
        "figure-manifest.json",
    ):
        assert (ROOT / name).exists(), name


def test_required_figures_exist() -> None:
    for name in (
        "figure_01_algorithm_fidelity_status.png",
        "figure_02_q_target_before_after.png",
        "figure_03_action_distribution_before_after_algorithm_repair.png",
        "figure_04_candidate_vs_capacity_split.png",
        "figure_05_q_value_state_action_ranking.png",
        "figure_06_learning_health_after_algorithm_repair.png",
    ):
        assert (ROOT / "figures" / name).exists(), name


def test_pipeline_gates_and_training_bounds() -> None:
    report = _load("final-report.json")
    gates = report["pipeline_gates"]
    assert gates["reward_reconciliation_passed"] is True
    assert gates["terminal_reconciliation_passed"] is True
    assert gates["raw_vs_canonical_delta_zero"] is True
    assert gates["terminal_coverage_one"] is True
    assert gates["metric_schema_valid"] is True
    assert gates["completion_nonzero"] is True
    assert report["training_5000_run"] is False
    assert report["max_training_budget"] == 1000
    assert report["training_budgets"] == [50, 100, 200, 300, 500, 750, 1000]


def test_candidate_and_oracle_comparison_present() -> None:
    report = _load("final-report.json")
    assert report["capacity_split_oracle"] is not None
    assert report["candidate_after"] is not None
    assert report["learning_health"] is not None
    assert report["claim_safety"]["paper_reproduction_claim_made"] is False
