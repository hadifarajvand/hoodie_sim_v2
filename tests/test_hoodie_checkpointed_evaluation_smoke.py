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


def _create_tiny_checkpoint(tmp_path):
    pytest.importorskip("torch")
    out = tmp_path / "ckpt"
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
    return out


def test_script_imports_without_running_evaluation():
    result = _run(["-c", "import scripts.run_hoodie_checkpointed_evaluation_smoke as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr
    assert "scripts.run_hoodie_checkpointed_evaluation_smoke" in result.stdout


def test_missing_checkpoint_dir_fails_safely(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_checkpointed_evaluation_smoke.py",
            "--checkpoint-dir",
            str(tmp_path / "missing"),
            "--output-dir",
            str(tmp_path / "out"),
            "--agent-count",
            "1",
            "--evaluation-steps",
            "3",
            "--seed",
            "42",
            "--allow-evaluation-smoke",
        ]
    )
    assert result.returncode != 0


def test_invalid_agent_count_zero_fails_safely(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_checkpointed_evaluation_smoke.py",
            "--checkpoint-dir",
            str(tmp_path / "missing"),
            "--output-dir",
            str(tmp_path / "out"),
            "--agent-count",
            "0",
            "--evaluation-steps",
            "3",
            "--seed",
            "42",
            "--allow-evaluation-smoke",
        ]
    )
    assert result.returncode != 0


def test_output_inside_repo_is_refused_without_flag(tmp_path):
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    result = _run(
        [
            "scripts/run_hoodie_checkpointed_evaluation_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            "artifacts/paper-contract-audit/phase6_4/repo_output",
            "--agent-count",
            "1",
            "--evaluation-steps",
            "3",
            "--seed",
            "42",
            "--allow-evaluation-smoke",
        ]
    )
    assert result.returncode != 0


def test_checkpointed_evaluation_smoke_creates_expected_outputs(tmp_path):
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    out = tmp_path / "eval"
    result = _run(
        [
            "scripts/run_hoodie_checkpointed_evaluation_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--evaluation-steps",
            "3",
            "--seed",
            "42",
            "--allow-evaluation-smoke",
        ]
    )
    assert result.returncode == 0, result.stderr
    for name in [
        "checkpointed_evaluation_manifest.json",
        "checkpointed_evaluation_report.json",
        "action_records.json",
        "hoodie_action_distribution.csv",
        "hoodie_action_distribution.json",
        "hoodie_action_distribution_metadata.json",
    ]:
        assert (out / name).exists(), name


def test_action_records_have_expected_count_and_string_actions(tmp_path):
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    out = tmp_path / "eval"
    result = _run(
        [
            "scripts/run_hoodie_checkpointed_evaluation_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--evaluation-steps",
            "3",
            "--seed",
            "42",
            "--allow-evaluation-smoke",
        ]
    )
    assert result.returncode == 0, result.stderr
    records = json.loads((out / "action_records.json").read_text())
    assert len(records) == 3
    assert all(isinstance(record["selected_action"], str) for record in records)
    assert all(record["policy_name"] == "HOODIE" for record in records)


def test_action_distribution_outputs_are_non_official(tmp_path):
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    out = tmp_path / "eval"
    result = _run(
        [
            "scripts/run_hoodie_checkpointed_evaluation_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--evaluation-steps",
            "3",
            "--seed",
            "42",
            "--allow-evaluation-smoke",
        ]
    )
    assert result.returncode == 0, result.stderr
    dist = json.loads((out / "hoodie_action_distribution.json").read_text())
    meta = json.loads((out / "hoodie_action_distribution_metadata.json").read_text())
    manifest = json.loads((out / "checkpointed_evaluation_manifest.json").read_text())
    report = json.loads((out / "checkpointed_evaluation_report.json").read_text())
    assert dist["policy_name"] == "HOODIE"
    assert dist["total_actions"] == 3
    assert meta["official_figure_claim"] is False
    assert meta["simulation_rerun"] is False
    assert meta["training_run"] is False
    assert manifest["official_figure_claim"] is False
    assert report["official_claim_allowed"] is False


def test_runtime_inspection_summary_agents_are_normalized(tmp_path):
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    out = tmp_path / "eval"
    result = _run(
        [
            "scripts/run_hoodie_checkpointed_evaluation_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--evaluation-steps",
            "3",
            "--seed",
            "42",
            "--allow-evaluation-smoke",
        ]
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads((out / "checkpointed_evaluation_manifest.json").read_text())
    agents = manifest["runtime_inspection_summary"]["agents"]
    assert len(agents) == 1
    agent = agents[0]
    assert "torch_inspection" in agent
    assert "model_reconstruction" in agent
    assert "metadata_validation" in agent
    assert "blockers" in agent
    assert agent["agent_index"] == 0


def test_missing_sidecar_detected_as_blocker(tmp_path):
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    (checkpoint_dir / "agent_0.pth.meta.json").unlink()
    result = _run(
        [
            "scripts/run_hoodie_checkpointed_evaluation_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            str(tmp_path / "eval"),
            "--agent-count",
            "1",
            "--evaluation-steps",
            "3",
            "--seed",
            "42",
            "--allow-evaluation-smoke",
        ]
    )
    assert result.returncode != 0


def test_tampered_metadata_official_claim_is_detected(tmp_path):
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    meta_path = checkpoint_dir / "agent_0.pth.meta.json"
    meta = json.loads(meta_path.read_text())
    meta["official_claim_allowed"] = True
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True))
    out = tmp_path / "eval"
    result = _run(
        [
            "scripts/run_hoodie_checkpointed_evaluation_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--evaluation-steps",
            "3",
            "--seed",
            "42",
            "--allow-evaluation-smoke",
        ]
    )
    assert result.returncode != 0
    manifest = json.loads((out / "checkpointed_evaluation_manifest.json").read_text())
    agents = manifest["runtime_inspection_summary"]["agents"]
    assert len(agents) == 1
    assert "metadata_official_claim_allowed_true" in agents[0]["blockers"]
    assert "metadata_official_claim_allowed_true" in manifest["blockers"]


def test_no_forbidden_artifacts_created_outside_tmp_path(tmp_path):
    forbidden_suffixes = {".pth", ".pt", ".pkl", ".pickle"}
    forbidden_names = {
        "paper_state_trace.csv",
        "queue_trace.csv",
        "mleo_candidate_latency_trace.csv",
        "checkpointed_evaluation_manifest.json",
        "checkpointed_evaluation_report.json",
        "action_records.json",
        "hoodie_action_distribution.csv",
        "hoodie_action_distribution.json",
        "hoodie_action_distribution_metadata.json",
    }
    before = {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    result = _run(
        [
            "scripts/run_hoodie_checkpointed_evaluation_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            str(tmp_path / "eval"),
            "--agent-count",
            "1",
            "--evaluation-steps",
            "3",
            "--seed",
            "42",
            "--allow-evaluation-smoke",
        ]
    )
    assert result.returncode == 0, result.stderr
    after = {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}
    assert before == after
