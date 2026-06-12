from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)
os.environ.setdefault("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", "1")


def _run(args, cwd=ROOT):
    return subprocess.run([str(PYTHON), *args], cwd=cwd, capture_output=True, text=True, check=False)


def _repo_forbidden_snapshot():
    forbidden_suffixes = {".pth", ".pt", ".pkl", ".pickle"}
    forbidden_names = {
        "hoodie_small_real_training_smoke_preflight_report.json",
        "controlled_trained_checkpoint_loading_smoke_manifest.json",
        "controlled_trained_checkpoint_loading_smoke_report.json",
        "hoodie_checkpoint_format_report.json",
        "validation_runner_execution_smoke_manifest.json",
        "validation_runner_execution_smoke_report.json",
        "validation_runner_checkpoint_smoke_manifest.json",
        "validation_runner_checkpoint_smoke_report.json",
        "validation_runner_checkpoint_preflight_report.json",
        "figure10_policy_metrics_raw.csv",
        "figure10_policy_metrics_summary.json",
        "figure10_policy_readiness.json",
        "figure10_run_config_snapshot.json",
        "figure10_validation_manifest.json",
        "checkpointed_evaluation_manifest.json",
        "checkpointed_evaluation_report.json",
        "action_records.json",
        "hoodie_action_distribution.csv",
        "hoodie_action_distribution.json",
        "hoodie_action_distribution_metadata.json",
        "smoke_report.json",
        "manifest.json",
        "preflight_report.json",
    }
    return {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}


def test_script_imports_without_running():
    result = _run(["-c", "import scripts.check_hoodie_small_real_training_smoke_preflight as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr
    assert "scripts.check_hoodie_small_real_training_smoke_preflight" in result.stdout


def test_missing_allow_flag_exits_non_zero(tmp_path):
    result = _run(["scripts/check_hoodie_small_real_training_smoke_preflight.py", "--output", str(tmp_path / "report.json")])
    assert result.returncode != 0


def test_output_inside_repo_is_refused_and_creates_no_file(tmp_path):
    repo_output = ROOT / "artifacts/paper-contract-audit/phase6_10/repo_output.json"
    if repo_output.exists():
        repo_output.unlink()
    result = _run(
        [
            "scripts/check_hoodie_small_real_training_smoke_preflight.py",
            "--output",
            str(repo_output),
            "--allow-small-real-training-preflight",
        ]
    )
    assert result.returncode != 0
    assert not repo_output.exists()


@pytest.mark.parametrize("episodes", ["0", "3"])
def test_episodes_bounds_exit_non_zero(tmp_path, episodes):
    result = _run(
        [
            "scripts/check_hoodie_small_real_training_smoke_preflight.py",
            "--output",
            str(tmp_path / "report.json"),
            "--allow-small-real-training-preflight",
            "--episodes",
            episodes,
        ]
    )
    assert result.returncode != 0


@pytest.mark.parametrize("episode_time", ["0", "6"])
def test_episode_time_bounds_exit_non_zero(tmp_path, episode_time):
    result = _run(
        [
            "scripts/check_hoodie_small_real_training_smoke_preflight.py",
            "--output",
            str(tmp_path / "report.json"),
            "--allow-small-real-training-preflight",
            "--episode-time",
            episode_time,
        ]
    )
    assert result.returncode != 0


def test_expected_agent_count_zero_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/check_hoodie_small_real_training_smoke_preflight.py",
            "--output",
            str(tmp_path / "report.json"),
            "--allow-small-real-training-preflight",
            "--expected-agent-count",
            "0",
        ]
    )
    assert result.returncode != 0


def test_successful_preflight_writes_report(tmp_path):
    out = tmp_path / "preflight.json"
    before = _repo_forbidden_snapshot()
    result = _run(
        [
            "scripts/check_hoodie_small_real_training_smoke_preflight.py",
            "--output",
            str(out),
            "--episodes",
            "1",
            "--episode-time",
            "3",
            "--seed",
            "42",
            "--expected-agent-count",
            "20",
            "--allow-small-real-training-preflight",
        ]
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text())
    assert report["preflight_run"] is True
    assert report["training_execution_run"] is False
    assert report["simulation_rerun"] is False
    assert report["main_py_called"] is False
    assert report["figure10_validation_called"] is False
    assert report["checkpoint_created"] is False
    assert report["model_artifact_created"] is False
    assert report["official_claim_allowed"] is False
    assert report["official_200_episode_validation_run"] is False
    assert report["official_figure_claims_made"] is False
    assert report["main_py_cli_detected"] is True
    assert report["main_py_training_path_detected"] is True
    assert report["agent_store_model_detected"] is True
    assert report["agent_unified_loader_detected"] is True
    assert report["export_module_detected"] is True
    assert report["export_metadata_detected"] is True
    assert report["runtime_loader_ready"] is True
    assert report["safe_output_routing_ready"] is True
    assert report["bounded_training_config_ready"] is True
    assert report["checkpoint_export_ready"] is True
    assert report["metadata_sidecar_ready"] is True
    assert report["small_real_training_execution_ready"] is True
    assert "training_checkpoint_export_missing" not in report["blockers"]
    assert "training_checkpoint_metadata_sidecar_missing" not in report["blockers"]
    assert any(item in report["warnings"] for item in ["preflight_only_no_training_executed", "figure10_remains_blocked"])
    assert report["proposed_next_phase_command_preview"]
    after = _repo_forbidden_snapshot()
    assert before == after


def test_readiness_helper_requires_export_and_metadata():
    import scripts.check_hoodie_small_real_training_smoke_preflight as preflight

    ready_result = preflight.compute_small_real_training_readiness(
        main_info={
            "cli_flags": {flag: True for flag in ["--config", "--log_folder", "--hyperparameters_file", "--epochs", "--validate", "--trace_output_dir", "--seed", "--trace_level"]},
            "training_path_detected": True,
            "checkpoint_export_detected": True,
        },
        agent_info={
            "store_model_detected": True,
            "unified_loader_detected": True,
        },
        loader_info={
            "full_model_supported": True,
            "state_dict_payload_supported": True,
            "trainer_json_rejected": True,
        },
        export_info={
            "module_exists": True,
            "build_training_checkpoint_metadata_detected": True,
            "export_agent_runtime_checkpoint_detected": True,
            "export_training_checkpoints_detected": True,
            "meta_json_detected": True,
            "official_claim_allowed_detected": True,
        },
    )
    missing_metadata_result = preflight.compute_small_real_training_readiness(
        main_info={
            "cli_flags": {flag: True for flag in ["--config", "--log_folder", "--hyperparameters_file", "--epochs", "--validate", "--trace_output_dir", "--seed", "--trace_level"]},
            "training_path_detected": True,
            "checkpoint_export_detected": True,
        },
        agent_info={
            "store_model_detected": True,
            "unified_loader_detected": True,
        },
        loader_info={
            "full_model_supported": True,
            "state_dict_payload_supported": True,
            "trainer_json_rejected": True,
        },
        export_info={
            "module_exists": True,
            "build_training_checkpoint_metadata_detected": True,
            "export_agent_runtime_checkpoint_detected": True,
            "export_training_checkpoints_detected": True,
            "meta_json_detected": False,
            "official_claim_allowed_detected": False,
        },
    )
    assert ready_result["small_real_training_execution_ready"] is True
    assert ready_result["checkpoint_export_ready"] is True
    assert ready_result["metadata_sidecar_ready"] is True
    assert "training_checkpoint_metadata_sidecar_missing" not in ready_result["blockers"]
    assert missing_metadata_result["small_real_training_execution_ready"] is False
    assert missing_metadata_result["metadata_sidecar_ready"] is False
    assert "training_checkpoint_metadata_sidecar_missing" in missing_metadata_result["blockers"]


def test_no_generated_artifacts_outside_tmp_path(tmp_path):
    before = _repo_forbidden_snapshot()
    out = tmp_path / "preflight.json"
    result = _run(
        [
            "scripts/check_hoodie_small_real_training_smoke_preflight.py",
            "--output",
            str(out),
            "--allow-small-real-training-preflight",
        ]
    )
    assert result.returncode == 0, result.stderr
    after = _repo_forbidden_snapshot()
    assert before == after
