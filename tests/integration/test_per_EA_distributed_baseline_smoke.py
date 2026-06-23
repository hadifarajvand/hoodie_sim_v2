"""Integration tests: per-EA distributed baseline smoke artifacts (skip if absent)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.analysis.paper_faithful_simulation_production.metric_schema import PAPER_COMPATIBLE_METRIC_FIELDS

ROOT = Path("artifacts/production/true-per-EA-distributed-baseline")
pytestmark = pytest.mark.skipif(
    not (ROOT / "final-distributed-baseline-report.json").exists(),
    reason="distributed baseline artifacts not present; run --smoke first",
)


def _load(n):
    return json.loads((ROOT / n).read_text())


def test_required_artifacts_exist():
    for name in (
        "paper-distributed-agent-audit.json", "paper-distributed-agent-audit.md",
        "distributed-baseline-config.json", "distributed-smoke-run-manifest.json",
        "distributed-candidate-metrics.json", "shared-vs-distributed-summary.json",
        "per-agent-action-distribution.json", "per-agent-learning-health.json",
        "baseline-and-oracle-metrics.json", "reward-terminal-reconciliation-distributed.json",
        "claim-safety.json", "distributed-full-campaign-handoff.json",
        "distributed-full-campaign-command.txt", "final-distributed-baseline-report.json",
        "final-distributed-baseline-report.md", "commit-summary.md",
    ):
        assert (ROOT / name).exists(), name


def test_all_seven_figures_exist():
    for i in range(1, 8):
        assert list((ROOT / "figures").glob(f"figure_{i:02d}_*.png")), f"figure {i:02d} missing"


def test_paper_figures_8_to_11_and_subfigures_exist():
    figs = ROOT / "figures"
    # Combined paper figures
    for i in (8, 9, 10, 11):
        assert list(figs.glob(f"figure_{i:02d}_*.png")), f"paper figure {i:02d} missing"
    # Required sub-figures
    for sub in (
        "figure_08a_accumulated_reward.png", "figure_08b_reward_per_task.png",
        "figure_09a_action_distribution.png",
        "figure_09b_reward_by_task_arrival_probability.png",
        "figure_09c_reward_by_drl_agent_count.png",
        "figure_09d_reward_by_cpu_capacity.png",
        "figure_09e_reward_by_offloading_data_rate.png",
        "figure_10a_average_delay.png", "figure_10b_drop_ratio.png",
    ):
        assert (figs / sub).exists(), f"sub-figure {sub} missing"


def test_reconciliation_holds():
    rec = _load("reward-terminal-reconciliation-distributed.json")
    assert rec["reconciled_all"] is True
    assert abs(rec["raw_vs_canonical_delta_max"]) <= 1e-9


def test_metric_schema_consistent():
    for name in ("distributed-candidate-metrics.json", "baseline-and-oracle-metrics.json"):
        rows = _load(name)
        assert rows
        for r in rows:
            assert set(r) == set(PAPER_COMPATIBLE_METRIC_FIELDS)


def test_claim_safety_no_5000_no_proposed_method():
    cs = _load("claim-safety.json")
    assert cs["paper_reproduction_claim_made"] is False
    assert cs["performance_superiority_claim_made"] is False
    assert cs["baseline_superiority_claim_made"] is False
    assert cs["proposed_method_implemented"] is False


def test_per_agent_models_count():
    cfg = _load("distributed-baseline-config.json")
    assert cfg["num_agents"] == 20
    assert cfg["per_agent_replay"] is True
    assert cfg["per_agent_target_sync"] is True
