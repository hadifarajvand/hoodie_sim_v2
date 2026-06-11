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


def test_script_imports_without_running_validation():
    result = _run(["-c", "import scripts.check_hoodie_validation_runner_checkpoint_integration as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr
    assert "scripts.check_hoodie_validation_runner_checkpoint_integration" in result.stdout


def test_missing_allow_preflight_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/check_hoodie_validation_runner_checkpoint_integration.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--checkpoint-dir",
            str(tmp_path / "missing"),
            "--agent-count",
            "1",
        ]
    )
    assert result.returncode != 0


def test_agent_count_zero_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/check_hoodie_validation_runner_checkpoint_integration.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--checkpoint-dir",
            str(tmp_path / "missing"),
            "--agent-count",
            "0",
            "--allow-preflight",
        ]
    )
    assert result.returncode != 0


def test_output_inside_repo_is_refused_or_unsupported(tmp_path):
    repo_output = ROOT / "artifacts/paper-contract-audit/phase6_5/repo_output.json"
    if repo_output.exists():
        repo_output.unlink()
    result = _run(
        [
            "scripts/check_hoodie_validation_runner_checkpoint_integration.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--checkpoint-dir",
            str(tmp_path / "missing"),
            "--agent-count",
            "1",
            "--allow-preflight",
            "--output",
            "artifacts/paper-contract-audit/phase6_5/repo_output.json",
        ]
    )
    assert result.returncode != 0
    assert not repo_output.exists()


def test_tiny_checkpoint_preflight_report(tmp_path):
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    out = tmp_path / "validation_runner_preflight.json"
    result = _run(
        [
            "scripts/check_hoodie_validation_runner_checkpoint_integration.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--agent-count",
            "1",
            "--allow-preflight",
            "--allow-tiny-checkpoint-dir",
            "--output",
            str(out),
        ]
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text())
    assert report["validation_run"] is False
    assert report["simulation_rerun"] is False
    assert report["training_run"] is False
    assert report["checkpoint_created"] is False
    assert report["official_claim_allowed"] is False
    assert report["official_validation_ready"] is False
    assert report["figure10_static_contract"]["expected_policy_set_has_hoodie"] is True
    assert report["figure10_static_contract"]["official_policy_classes_has_hoodie"] is True
    assert report["figure10_static_contract"]["config_has_hoodie_checkpoint_dir"] is True
    assert len(report["checkpoint_agent_summaries"]) == 1
    agent = report["checkpoint_agent_summaries"][0]
    assert "torch_inspection" in agent
    assert "metadata_validation" in agent
    assert "runtime_compatible_for_preflight" in agent
    assert "blockers" in agent
    assert agent["runtime_compatible_for_preflight"] is True


def test_missing_sidecar_produces_blocker(tmp_path):
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    (checkpoint_dir / "agent_0.pth.meta.json").unlink()
    out = tmp_path / "validation_runner_preflight.json"
    result = _run(
        [
            "scripts/check_hoodie_validation_runner_checkpoint_integration.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--agent-count",
            "1",
            "--allow-preflight",
            "--allow-tiny-checkpoint-dir",
            "--output",
            str(out),
        ]
    )
    assert result.returncode != 0
    report = json.loads(out.read_text())
    agent = report["checkpoint_agent_summaries"][0]
    assert "missing_metadata_sidecar: agent_0" in agent["blockers"]
    assert "missing_metadata_sidecar: agent_0" in report["blockers"] or "missing_metadata_sidecar" in report["checkpoint_dir_assessment"].get("issues", [])
    assert agent["runtime_compatible_for_preflight"] is False


def test_tampered_metadata_official_claim_true_produces_blocker(tmp_path):
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    meta_path = checkpoint_dir / "agent_0.pth.meta.json"
    meta = json.loads(meta_path.read_text())
    meta["official_claim_allowed"] = True
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True))
    out = tmp_path / "validation_runner_preflight.json"
    result = _run(
        [
            "scripts/check_hoodie_validation_runner_checkpoint_integration.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--agent-count",
            "1",
            "--allow-preflight",
            "--allow-tiny-checkpoint-dir",
            "--output",
            str(out),
        ]
    )
    assert result.returncode != 0
    report = json.loads(out.read_text())
    agent = report["checkpoint_agent_summaries"][0]
    assert "metadata_official_claim_allowed_true" in report["blockers"]
    assert "metadata_official_claim_allowed_true" in agent["blockers"]
    assert agent["metadata_validation"]["official_claim_allowed"] is True
    assert agent["runtime_compatible_for_preflight"] is False


def test_trainer_json_checkpoint_is_not_accepted(tmp_path):
    checkpoint_dir = tmp_path / "trainer"
    checkpoint_dir.mkdir()
    (checkpoint_dir / "agent_0.pth").write_text(json.dumps({"policy_weights": [], "algorithm": "dqn"}))
    (checkpoint_dir / "agent_0.pth.meta.json").write_text(
        json.dumps(
            {
                "policy_name": "HOODIE",
                "checkpoint_format": "trainer_json_checkpoint",
                "official_claim_allowed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    out = tmp_path / "validation_runner_preflight.json"
    result = _run(
        [
            "scripts/check_hoodie_validation_runner_checkpoint_integration.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--agent-count",
            "1",
            "--allow-preflight",
            "--allow-tiny-checkpoint-dir",
            "--output",
            str(out),
        ]
    )
    assert result.returncode != 0
    report = json.loads(out.read_text())
    agent = report["checkpoint_agent_summaries"][0]
    assert (
        "trainer_json_checkpoint_not_accepted" in report["blockers"]
        or "metadata_checkpoint_format_invalid" in report["blockers"]
    )
    assert agent["runtime_compatible_for_preflight"] is False


def test_corrupt_pth_with_valid_metadata_is_not_runtime_compatible(tmp_path):
    checkpoint_dir = tmp_path / "corrupt"
    checkpoint_dir.mkdir()
    (checkpoint_dir / "agent_0.pth").write_text("not a torch checkpoint")
    (checkpoint_dir / "agent_0.pth.meta.json").write_text(
        json.dumps(
            {
                "policy_name": "HOODIE",
                "checkpoint_format": "pytorch_state_dict_file",
                "official_claim_allowed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    out = tmp_path / "validation_runner_preflight.json"
    result = _run(
        [
            "scripts/check_hoodie_validation_runner_checkpoint_integration.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--agent-count",
            "1",
            "--allow-preflight",
            "--allow-tiny-checkpoint-dir",
            "--output",
            str(out),
        ]
    )
    assert result.returncode != 0
    report = json.loads(out.read_text())
    agent = report["checkpoint_agent_summaries"][0]
    assert agent["runtime_compatible_for_preflight"] is False
    assert "checkpoint_not_loadable: agent_0" in agent["blockers"]
    assert "checkpoint_not_loadable: agent_0" in report["blockers"]


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
        "validation_runner_checkpoint_preflight_report.json",
    }
    before = {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    out = tmp_path / "validation_runner_preflight.json"
    result = _run(
        [
            "scripts/check_hoodie_validation_runner_checkpoint_integration.py",
            "--paper-contract",
            "config/paper_table4_contract.json",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--agent-count",
            "1",
            "--allow-preflight",
            "--allow-tiny-checkpoint-dir",
            "--output",
            str(out),
        ]
    )
    assert result.returncode == 0, result.stderr
    after = {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}
    assert before == after
