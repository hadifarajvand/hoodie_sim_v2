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


def test_final_report_documented_repair_and_next_step() -> None:
    report = _load("final-report.json")
    assert report["branch"] == "algorithm-fidelity-against-paper-repair"
    assert report["commit_sha"]
    assert report["verdict"] in {
        "algorithm_fidelity_repair_ready_for_extended_validation",
        "algorithm_fidelity_repair_blocked",
    }
    assert report["recommended_next_step"] in {
        "run_extended_validation",
        "prepare_full_campaign_config_only",
        "inspect_paper_exact_parameters",
        "inspect_multi_agent_training_gap",
        "blocked_due_to_algorithm_fidelity_gap",
    }
    assert report["reward_env_topology_changed"] is False
    assert report["algorithm_changed"] is True


def test_algorithm_audit_and_claim_safety_markers_exist() -> None:
    audit = _load("algorithm-fidelity-audit.json")
    assert audit["rows"]
    claim = _load("claim-safety.json")
    assert claim["paper_reproduction_claim_made"] is False
    assert claim["performance_superiority_claim_made"] is False
    assert claim["baseline_superiority_claim_made"] is False
    assert claim["training_5000_run"] is False
