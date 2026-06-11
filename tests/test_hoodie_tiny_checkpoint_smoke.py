from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)


def _run(args, cwd=ROOT):
    return subprocess.run([str(PYTHON), *args], cwd=cwd, capture_output=True, text=True, check=False)


def test_script_imports_without_running_training():
    result = _run(["-c", "import scripts.run_hoodie_tiny_checkpoint_smoke as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr
    assert "scripts.run_hoodie_tiny_checkpoint_smoke" in result.stdout


def test_invalid_agent_count_zero_fails_safely():
    result = _run(
        [
            "scripts/run_hoodie_tiny_checkpoint_smoke.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--output-dir",
            "/tmp/hoodie_phase6_3_smoke_zero",
            "--agent-count",
            "0",
            "--episodes",
            "1",
            "--steps-per-episode",
            "2",
            "--seed",
            "42",
            "--allow-create-checkpoint",
        ]
    )
    assert result.returncode != 0


def test_invalid_agent_count_negative_fails_safely():
    result = _run(
        [
            "scripts/run_hoodie_tiny_checkpoint_smoke.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--output-dir",
            "/tmp/hoodie_phase6_3_smoke_negative",
            "--agent-count",
            "-1",
            "--episodes",
            "1",
            "--steps-per-episode",
            "2",
            "--seed",
            "42",
            "--allow-create-checkpoint",
        ]
    )
    assert result.returncode != 0


def test_tiny_smoke_creates_checkpoint_and_reports(tmp_path):
    pytest.importorskip("torch")
    out = tmp_path / "smoke"
    result = _run(
        [
            "scripts/run_hoodie_tiny_checkpoint_smoke.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--episodes",
            "1",
            "--steps-per-episode",
            "2",
            "--seed",
            "42",
            "--allow-create-checkpoint",
        ]
    )
    assert result.returncode == 0, result.stderr
    for name in ["manifest.json", "smoke_report.json", "agent_0.pth", "agent_0.pth.meta.json"]:
        assert (out / name).exists(), name

    meta = json.loads((out / "agent_0.pth.meta.json").read_text())
    assert meta["policy_name"] == "HOODIE"
    assert meta["checkpoint_format"] == "pytorch_state_dict_file"
    assert meta["official_claim_allowed"] is False


def test_generated_checkpoint_can_be_inspected(tmp_path):
    pytest.importorskip("torch")
    out = tmp_path / "smoke"
    result = _run(
        [
            "scripts/run_hoodie_tiny_checkpoint_smoke.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--episodes",
            "1",
            "--steps-per-episode",
            "2",
            "--seed",
            "42",
            "--allow-create-checkpoint",
        ]
    )
    assert result.returncode == 0, result.stderr
    inspect_result = _run(
        [
            "-c",
            (
                "from pathlib import Path; "
                "from training.hoodie_checkpoint_interop import inspect_runtime_torch_checkpoint, assess_hoodie_checkpoint_dir; "
                "p=Path(r'%s'); "
                "info=inspect_runtime_torch_checkpoint(p/'agent_0.pth'); "
                "assess=assess_hoodie_checkpoint_dir(p, expected_agent_count=1); "
                "print(info['loadable'], assess['suitable_for_official_validation'])"
            )
            % str(out),
        ]
    )
    assert inspect_result.returncode == 0, inspect_result.stderr
    assert "True" in inspect_result.stdout


def test_output_inside_repo_is_refused_without_flag(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_tiny_checkpoint_smoke.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--output-dir",
            "artifacts/paper-contract-audit/phase6_3/repo_output",
            "--agent-count",
            "1",
            "--episodes",
            "1",
            "--steps-per-episode",
            "2",
            "--seed",
            "42",
            "--allow-create-checkpoint",
        ]
    )
    assert result.returncode != 0


def test_no_forbidden_artifacts_created_outside_tmp_path(tmp_path):
    forbidden_suffixes = {".pth", ".pt", ".pkl", ".pickle"}
    forbidden_names = {"paper_state_trace.csv", "queue_trace.csv", "mleo_candidate_latency_trace.csv"}
    before = {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}
    out = tmp_path / "smoke"
    result = _run(
        [
            "scripts/run_hoodie_tiny_checkpoint_smoke.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--episodes",
            "1",
            "--steps-per-episode",
            "2",
            "--seed",
            "42",
            "--allow-create-checkpoint",
        ]
    )
    assert result.returncode == 0, result.stderr
    after = {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}
    assert before == after


def test_manifest_and_report_do_not_claim_official_readiness(tmp_path):
    pytest.importorskip("torch")
    out = tmp_path / "smoke"
    result = _run(
        [
            "scripts/run_hoodie_tiny_checkpoint_smoke.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--episodes",
            "1",
            "--steps-per-episode",
            "2",
            "--seed",
            "42",
            "--allow-create-checkpoint",
        ]
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads((out / "manifest.json").read_text())
    report = json.loads((out / "smoke_report.json").read_text())
    assert manifest["official_claim_allowed"] is False
    assert manifest["paper_reproduction_claim"] is False
    assert report["official_claim_allowed"] is False
    assert report["official_training_run"] is False
