from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)


def test_preflight_script_imports_without_training(tmp_path):
    result = subprocess.run(
        [str(PYTHON), "-c", "import scripts.check_hoodie_training_preflight as m; print(m.__name__)"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "scripts.check_hoodie_training_preflight" in result.stdout


def test_paper_contract_json_is_parsed(tmp_path):
    contract = json.loads((ROOT / "config/paper_table4_contract.json").read_text())
    assert contract["number_of_eas"] == 20
    assert contract["validation_episodes"] == 200
    assert contract["training_episodes"] == 5000


def test_expected_checkpoint_files_and_metadata_are_reported_for_20_agents(tmp_path):
    out = tmp_path / "preflight.json"
    result = subprocess.run(
        [
            str(PYTHON),
            "scripts/check_hoodie_training_preflight.py",
            "--paper-contract",
            str(ROOT / "config/paper_table4_contract.json"),
            "--agent-count",
            "20",
            "--output",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text())
    assert len(report["expected_checkpoint_files"]) == 20
    assert len(report["expected_metadata_files"]) == 20
    assert report["training_run"] is False
    assert report["checkpoint_created"] is False


def test_missing_paper_contract_produces_blocker(tmp_path):
    out = tmp_path / "preflight.json"
    result = subprocess.run(
        [
            str(PYTHON),
            "scripts/check_hoodie_training_preflight.py",
            "--paper-contract",
            str(tmp_path / "missing.json"),
            "--agent-count",
            "20",
            "--output",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text())
    assert report["paper_contract_loaded"] is False
    assert report["blockers"]


def test_no_forbidden_artifacts_created_outside_tmp_path(tmp_path):
    forbidden_suffixes = {".pth", ".pt", ".pkl", ".pickle"}
    forbidden_names = {"paper_state_trace.csv", "queue_trace.csv", "mleo_candidate_latency_trace.csv"}
    before = {
        p
        for p in ROOT.rglob("*")
        if p.suffix in forbidden_suffixes or p.name in forbidden_names
    }
    out = tmp_path / "preflight.json"
    subprocess.run(
        [
            str(PYTHON),
            "scripts/check_hoodie_training_preflight.py",
            "--paper-contract",
            str(ROOT / "config/paper_table4_contract.json"),
            "--agent-count",
            "20",
            "--output",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    after = {
        p
        for p in ROOT.rglob("*")
        if p.suffix in forbidden_suffixes or p.name in forbidden_names
    }
    assert before == after


def test_valid_contract_agent_count_zero_reports_invalid_agent_count(tmp_path):
    out = tmp_path / "preflight.json"
    result = subprocess.run(
        [
            str(PYTHON),
            "scripts/check_hoodie_training_preflight.py",
            "--paper-contract",
            str(ROOT / "config/paper_table4_contract.json"),
            "--agent-count",
            "0",
            "--output",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text())
    assert report["invalid_agent_count"] is True
    assert "invalid_agent_count" in report["blockers"]
    assert report["expected_checkpoint_files"] == []
    assert report["expected_metadata_files"] == []
    assert report["ready_for_tiny_smoke"] is False


def test_valid_contract_agent_count_negative_reports_invalid_agent_count(tmp_path):
    out = tmp_path / "preflight.json"
    result = subprocess.run(
        [
            str(PYTHON),
            "scripts/check_hoodie_training_preflight.py",
            "--paper-contract",
            str(ROOT / "config/paper_table4_contract.json"),
            "--agent-count",
            "-1",
            "--output",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text())
    assert report["invalid_agent_count"] is True
    assert "invalid_agent_count" in report["blockers"]
    assert report["expected_checkpoint_files"] == []
    assert report["expected_metadata_files"] == []
    assert report["ready_for_tiny_smoke"] is False


def test_missing_contract_agent_count_zero_reports_invalid_agent_count_and_contract_blocker(tmp_path):
    out = tmp_path / "preflight.json"
    result = subprocess.run(
        [
            str(PYTHON),
            "scripts/check_hoodie_training_preflight.py",
            "--paper-contract",
            str(tmp_path / "missing.json"),
            "--agent-count",
            "0",
            "--output",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text())
    assert report["paper_contract_loaded"] is False
    assert report["invalid_agent_count"] is True
    assert "invalid_agent_count" in report["blockers"]
    assert any(blocker.startswith("paper_contract_load_failed:") for blocker in report["blockers"])
    assert report["expected_checkpoint_files"] == []
    assert report["expected_metadata_files"] == []
    assert report["ready_for_tiny_smoke"] is False


def test_invalid_agent_count_preflight_creates_no_forbidden_artifacts_outside_tmp_path(tmp_path):
    forbidden_suffixes = {".pth", ".pt", ".pkl", ".pickle"}
    forbidden_names = {"paper_state_trace.csv", "queue_trace.csv", "mleo_candidate_latency_trace.csv"}
    before = {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}
    out = tmp_path / "preflight.json"
    result = subprocess.run(
        [
            str(PYTHON),
            "scripts/check_hoodie_training_preflight.py",
            "--paper-contract",
            str(ROOT / "config/paper_table4_contract.json"),
            "--agent-count",
            "0",
            "--output",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    after = {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}
    assert before == after
