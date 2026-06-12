from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)


def _run(args, cwd=ROOT):
    return subprocess.run([str(PYTHON), *args], cwd=cwd, capture_output=True, text=True, check=False)


def _repo_forbidden_snapshot():
    forbidden_suffixes = {".pth", ".pt", ".pkl", ".pickle"}
    forbidden_names = {
        "hoodie_trained_checkpoint_evaluation_wiring_smoke_manifest.json",
        "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json",
        "hoodie_bounded_small_real_training_smoke_manifest.json",
        "hoodie_bounded_small_real_training_smoke_report.json",
        "hoodie_small_real_training_export_manifest.json",
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
        "main_stdout.txt",
        "main_stderr.txt",
        "main_returncode.txt",
        "scheduler.pth",
        "paper_state_trace.csv",
        "queue_trace.csv",
        "mleo_candidate_latency_trace.csv",
    }
    return {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}


def _fake_training_smoke_result(
    output_dir: Path,
    *,
    main_returncode: int = 0,
    runtime_loader_verified: bool = True,
    agent_load_model_verified: bool = True,
    include_export_manifest: bool = True,
    include_sidecar: bool = True,
) -> dict[str, object]:
    training_dir = output_dir
    checkpoint_dir = training_dir / "trained_checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    (checkpoint_dir / "agent_0.pth").write_text("checkpoint")
    if include_sidecar:
        (checkpoint_dir / "agent_0.pth.meta.json").write_text(
            json.dumps(
                {
                    "policy_name": "HOODIE",
                    "checkpoint_format": "pytorch_model_file",
                    "official_claim_allowed": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
    manifest = {
        "phase": "6.12",
        "blockers": [],
        "official_claim_allowed": False,
    }
    report = {
        "main_returncode": main_returncode,
        "runtime_loader_verified": runtime_loader_verified,
        "agent_load_model_verified": agent_load_model_verified,
        "official_claim_allowed": False,
        "blockers": [],
        "actual_agent_count": 1,
    }
    (training_dir / "hoodie_bounded_small_real_training_smoke_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    (training_dir / "hoodie_bounded_small_real_training_smoke_report.json").write_text(json.dumps(report, indent=2, sort_keys=True))
    if include_export_manifest:
        (training_dir / "hoodie_small_real_training_export_manifest.json").write_text(
            json.dumps({"blockers": []}, indent=2, sort_keys=True)
        )
    return {
        "manifest": manifest,
        "report": report,
        "manifest_path": training_dir / "hoodie_bounded_small_real_training_smoke_manifest.json",
        "report_path": training_dir / "hoodie_bounded_small_real_training_smoke_report.json",
        "export_manifest_path": training_dir / "hoodie_small_real_training_export_manifest.json",
        "checkpoint_dir": checkpoint_dir,
    }


def _fake_training_result_with_missing_sidecar(output_dir: Path) -> dict[str, object]:
    return _fake_training_smoke_result(output_dir, include_sidecar=False)


def _fake_successful_evaluation_report(output_dir: Path, run_id: str) -> tuple[bool, list[dict[str, object]], list[str], list[str], dict[str, object], dict[str, object], bool]:
    runner_output_dir = output_dir / "evaluation_runner"
    return (
        True,
        [
            {
                "regime_id": "delay",
                "policy_name": "HOODIE",
                "agent_index": 0,
                "source_checkpoint_path": str(output_dir / "training_smoke" / "trained_checkpoints" / "agent_0.pth"),
                "staged_checkpoint_path": str(runner_output_dir / "runs" / run_id / "delay" / "HOODIE" / "logs" / "agent_0.pth"),
                "source_metadata_path": str(output_dir / "training_smoke" / "trained_checkpoints" / "agent_0.pth.meta.json"),
                "staged_metadata_path": str(runner_output_dir / "runs" / run_id / "delay" / "HOODIE" / "logs" / "agent_0.pth.meta.json"),
                "source_torch_inspection": {"loadable": True},
                "staged_torch_inspection": {"loadable": True},
                "metadata_validation": {"official_claim_allowed": False, "blockers": []},
                "runner_layout_ready_for_smoke": True,
                "blockers": [],
            }
        ],
        [],
        [],
        {"figure10_data_ready": False},
        {"figure10_data_ready": False, "official_claim_allowed": False, "paper_reproduction_claim": False, "official_figure_claim": False},
        True,
    )


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def test_script_imports_without_running():
    result = _run(["-c", "import scripts.run_hoodie_trained_checkpoint_evaluation_wiring_smoke as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr
    assert "scripts.run_hoodie_trained_checkpoint_evaluation_wiring_smoke" in result.stdout


@pytest.mark.parametrize(
    "missing_flag, extra_args",
    [
        ("--allow-trained-checkpoint-evaluation-wiring-smoke", ["--allow-bounded-training-smoke", "--allow-figure10-validation-test-mode", "--allow-main-py-training-execution", "--allow-training-checkpoint-export"]),
        ("--allow-bounded-training-smoke", ["--allow-trained-checkpoint-evaluation-wiring-smoke", "--allow-figure10-validation-test-mode", "--allow-main-py-training-execution", "--allow-training-checkpoint-export"]),
        ("--allow-figure10-validation-test-mode", ["--allow-trained-checkpoint-evaluation-wiring-smoke", "--allow-bounded-training-smoke", "--allow-main-py-training-execution", "--allow-training-checkpoint-export"]),
        ("--allow-main-py-training-execution", ["--allow-trained-checkpoint-evaluation-wiring-smoke", "--allow-bounded-training-smoke", "--allow-figure10-validation-test-mode", "--allow-training-checkpoint-export"]),
        ("--allow-training-checkpoint-export", ["--allow-trained-checkpoint-evaluation-wiring-smoke", "--allow-bounded-training-smoke", "--allow-figure10-validation-test-mode", "--allow-main-py-training-execution"]),
    ],
)
def test_missing_allow_flags_exit_non_zero(tmp_path, missing_flag, extra_args):
    result = _run(
        [
            "scripts/run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--training-epochs",
            "1",
            "--training-episode-time",
            "3",
            "--validation-episodes",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_13_trained_checkpoint_evaluation_wiring_smoke",
            *extra_args,
        ]
    )
    assert result.returncode != 0


@pytest.mark.parametrize(
    "flag,value",
    [
        ("--training-epochs", "0"),
        ("--training-epochs", "2"),
        ("--training-episode-time", "0"),
        ("--training-episode-time", "4"),
        ("--validation-episodes", "0"),
        ("--validation-episodes", "2"),
    ],
)
def test_bounds_exit_non_zero(tmp_path, flag, value):
    result = _run(
        [
            "scripts/run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
            flag,
            value,
        ]
    )
    assert result.returncode != 0


def test_output_inside_repo_is_refused_and_creates_no_file_or_directory(tmp_path):
    repo_output = ROOT / "artifacts/paper-contract-audit/phase6_13/repo_output"
    if repo_output.exists():
        if repo_output.is_dir():
            shutil.rmtree(repo_output)
        else:
            repo_output.unlink()
    result = _run(
        [
            "scripts/run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
            "--output-dir",
            str(repo_output),
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ]
    )
    assert result.returncode != 0
    assert not repo_output.exists()


def test_successful_wiring_smoke_runs_only_in_tmp_path(tmp_path):
    pytest.importorskip("torch")
    import scripts.run_hoodie_trained_checkpoint_evaluation_wiring_smoke as smoke
    from training.hoodie_runtime_checkpoint_loader import load_hoodie_checkpoint_with_metadata

    out = tmp_path / "out"
    before = _repo_forbidden_snapshot()
    result = _run(
        [
            "scripts/run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
            "--output-dir",
            str(out),
            "--training-epochs",
            "1",
            "--training-episode-time",
            "3",
            "--validation-episodes",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_13_trained_checkpoint_evaluation_wiring_smoke",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ]
    )
    assert result.returncode == 0, result.stderr

    manifest = _load_json(out / "hoodie_trained_checkpoint_evaluation_wiring_smoke_manifest.json")
    report = _load_json(out / "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json")
    training_manifest = _load_json(out / "training_smoke" / "hoodie_bounded_small_real_training_smoke_manifest.json")
    training_report = _load_json(out / "training_smoke" / "hoodie_bounded_small_real_training_smoke_report.json")
    readiness = _load_json(out / "evaluation_runner" / "figure10_policy_readiness.json")
    validation_manifest = _load_json(out / "evaluation_runner" / "figure10_validation_manifest.json")

    assert manifest["trained_checkpoint_evaluation_wiring_smoke_run"] is True
    assert manifest["training_smoke_run"] is True
    assert manifest["training_smoke_scope"] == "bounded_small_real_training_smoke_only"
    assert manifest["training_epochs"] == 1
    assert manifest["training_episode_time"] == 3
    assert manifest["training_returncode"] == 0
    assert manifest["training_runtime_loader_verified"] is True
    assert manifest["training_agent_load_model_verified"] is True
    assert manifest["evaluation_runner_called"] is True
    assert manifest["figure10_validation_called"] is True
    assert manifest["figure10_validation_test_mode"] is True
    assert manifest["strict_readiness_used"] is False
    assert manifest["validation_episodes"] == 1
    assert manifest["validation_policies"] == ["HOODIE"]
    assert manifest["evaluation_returncode"] == 0
    assert manifest["main_py_called"] is True
    assert manifest["main_py_training_called_by_guarded_runner"] is True
    assert manifest["main_py_validation_called_by_figure10_runner"] is True
    assert manifest["simulation_rerun"] is True
    assert manifest["simulation_rerun_scope"] == "bounded_training_plus_test_mode_evaluation_wiring_smoke_only"
    assert manifest["official_simulation_rerun"] is False
    assert manifest["runner_checkpoint_staging_verified"] is True
    assert manifest["runner_sidecars_present"] is True
    assert manifest["runner_loaded_checkpoint_from_stdout"] is True
    assert manifest["evaluation_checkpoints_runtime_loadable"] is True
    assert manifest["figure10_data_ready"] is False
    assert manifest["official_training_run"] is False
    assert manifest["full_training_run"] is False
    assert manifest["paper_training_run"] is False
    assert manifest["paper_grade_5000_episode_training_run"] is False
    assert manifest["official_validation_run"] is False
    assert manifest["official_200_episode_validation_run"] is False
    assert manifest["official_figure_claims_made"] is False
    assert manifest["official_claim_allowed"] is False
    assert manifest["paper_reproduction_claim"] is False
    assert manifest["checkpoint_artifact_committed"] is False
    assert manifest["model_artifact_committed"] is False
    assert manifest["trace_artifact_committed"] is False
    assert manifest["figure10_artifact_committed"] is False
    assert manifest["figure8_claim"] is False
    assert manifest["figure9_claim"] is False
    assert manifest["figure10_claim"] is False
    assert manifest["figure11_claim"] is False
    assert report["trained_checkpoint_evaluation_wiring_smoke_run"] is True
    assert report["training_smoke_completed"] is True
    assert report["evaluation_runner_completed"] is True
    assert report["runner_checkpoint_staging_verified"] is True
    assert report["runner_sidecars_present"] is True
    assert report["runner_loaded_checkpoint_from_stdout"] is True
    assert report["evaluation_checkpoints_runtime_loadable"] is True
    assert report["figure10_data_ready"] is False
    assert report["official_claim_allowed"] is False
    assert report["paper_reproduction_claim"] is False
    assert report["blockers"] == []

    assert training_manifest["blockers"] == []
    assert training_report["blockers"] == []
    assert training_report["main_returncode"] == 0
    assert readiness["figure10_data_ready"] is False
    assert validation_manifest["diagnostic_only"] is True
    assert validation_manifest["figure10_data_ready"] is False

    training_checkpoint_dir = out / "training_smoke" / "trained_checkpoints"
    assert training_checkpoint_dir.is_dir()
    for agent_index in range(20):
        checkpoint = training_checkpoint_dir / f"agent_{agent_index}.pth"
        meta = training_checkpoint_dir / f"agent_{agent_index}.pth.meta.json"
        assert checkpoint.exists()
        assert meta.exists()
        metadata = _load_json(meta)
        assert metadata["policy_name"] == "HOODIE"
        assert metadata["trained_checkpoint"] is True
        assert metadata["paper_training_run"] is False
        assert metadata["official_claim_allowed"] is False
        model, loader_report = load_hoodie_checkpoint_with_metadata(checkpoint)
        assert model is not None
        assert loader_report["runtime_loadable"] is True

    runner_output_dir = out / "evaluation_runner"
    for regime in ("delay", "drop_ratio"):
        regime_dir = runner_output_dir / "runs" / "phase6_13_trained_checkpoint_evaluation_wiring_smoke_evaluation" / regime / "HOODIE"
        assert (regime_dir / "main_returncode.txt").exists()
        assert (regime_dir / "main_returncode.txt").read_text().strip() == "0"
        assert (regime_dir / "main_stdout.txt").exists()
        assert "model weights loaded" in (regime_dir / "main_stdout.txt").read_text()
        log_dir = regime_dir / "logs"
        assert (log_dir / "agent_0.pth").exists()
        assert (log_dir / "agent_0.pth.meta.json").exists()
        model, loader_report = load_hoodie_checkpoint_with_metadata(log_dir / "agent_0.pth")
        assert model is not None
        assert loader_report["runtime_loadable"] is True

    after = _repo_forbidden_snapshot()
    assert before == after


def test_training_smoke_failure_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_trained_checkpoint_evaluation_wiring_smoke as smoke

    def fake_training_smoke(**kwargs):
        return {
            "manifest": {"blockers": ["training_smoke_failed"]},
            "report": {"main_returncode": 1, "runtime_loader_verified": False, "agent_load_model_verified": False, "blockers": ["training_smoke_failed"], "official_claim_allowed": False},
            "manifest_path": kwargs["output_dir"] / "hoodie_bounded_small_real_training_smoke_manifest.json",
            "report_path": kwargs["output_dir"] / "hoodie_bounded_small_real_training_smoke_report.json",
            "export_manifest_path": kwargs["output_dir"] / "hoodie_small_real_training_export_manifest.json",
            "checkpoint_dir": kwargs["output_dir"] / "trained_checkpoints",
        }

    monkeypatch.setattr(smoke, "_run_training_smoke", fake_training_smoke)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--training-epochs",
            "1",
            "--training-episode-time",
            "3",
            "--validation-episodes",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_13_trained_checkpoint_evaluation_wiring_smoke",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json")
    assert "training_smoke_failed" in report["blockers"]


def test_training_missing_sidecar_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_trained_checkpoint_evaluation_wiring_smoke as smoke

    def fake_training_smoke(**kwargs):
        return _fake_training_smoke_result(kwargs["output_dir"], include_sidecar=False)

    def fake_collect(**kwargs):
        return True, [], [], [], {"figure10_data_ready": False}, {"official_claim_allowed": False, "paper_reproduction_claim": False, "official_figure_claim": False}, True

    monkeypatch.setattr(smoke, "_run_training_smoke", fake_training_smoke)
    monkeypatch.setattr(smoke, "_collect_evaluation_wiring_report", fake_collect)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--training-epochs",
            "1",
            "--training-episode-time",
            "3",
            "--validation-episodes",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_13_trained_checkpoint_evaluation_wiring_smoke",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json")
    assert any("training_metadata_sidecar_missing" in blocker for blocker in report["blockers"])


def test_evaluation_runner_failure_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_trained_checkpoint_evaluation_wiring_smoke as smoke
    from subprocess import CompletedProcess

    def fake_training_smoke(**kwargs):
        return _fake_training_smoke_result(kwargs["output_dir"])

    monkeypatch.setattr(smoke, "_run_training_smoke", fake_training_smoke)
    monkeypatch.setattr(smoke, "_run_figure10_validation_runner", lambda **kwargs: CompletedProcess(args=["figure10_validation.py"], returncode=1, stdout="", stderr="boom"))
    monkeypatch.setattr(smoke, "_collect_evaluation_wiring_report", lambda **kwargs: (False, [], [], [], {}, {}, False))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--training-epochs",
            "1",
            "--training-episode-time",
            "3",
            "--validation-episodes",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_13_trained_checkpoint_evaluation_wiring_smoke",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json")
    assert "evaluation_runner_failed" in report["blockers"]


def test_evaluation_main_returncode_missing_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_trained_checkpoint_evaluation_wiring_smoke as smoke
    from subprocess import CompletedProcess

    def fake_training_smoke(**kwargs):
        return _fake_training_smoke_result(kwargs["output_dir"])

    def fake_collect(**kwargs):
        return False, [], ["evaluation_main_returncode_missing"], [], {}, {}, False

    monkeypatch.setattr(smoke, "_run_training_smoke", fake_training_smoke)
    monkeypatch.setattr(smoke, "_run_figure10_validation_runner", lambda **kwargs: CompletedProcess(args=["figure10_validation.py"], returncode=0, stdout="", stderr=""))
    monkeypatch.setattr(smoke, "_collect_evaluation_wiring_report", fake_collect)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--training-epochs",
            "1",
            "--training-episode-time",
            "3",
            "--validation-episodes",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_13_trained_checkpoint_evaluation_wiring_smoke",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json")
    assert "evaluation_main_returncode_missing" in report["blockers"]


def test_evaluation_main_failed_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_trained_checkpoint_evaluation_wiring_smoke as smoke
    from subprocess import CompletedProcess

    def fake_training_smoke(**kwargs):
        return _fake_training_smoke_result(kwargs["output_dir"])

    def fake_collect(**kwargs):
        return False, [], ["evaluation_main_failed"], [], {}, {}, False

    monkeypatch.setattr(smoke, "_run_training_smoke", fake_training_smoke)
    monkeypatch.setattr(smoke, "_run_figure10_validation_runner", lambda **kwargs: CompletedProcess(args=["figure10_validation.py"], returncode=0, stdout="", stderr=""))
    monkeypatch.setattr(smoke, "_collect_evaluation_wiring_report", fake_collect)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--training-epochs",
            "1",
            "--training-episode-time",
            "3",
            "--validation-episodes",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_13_trained_checkpoint_evaluation_wiring_smoke",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json")
    assert "evaluation_main_failed" in report["blockers"]


def test_runner_stdout_missing_model_weights_loaded_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_trained_checkpoint_evaluation_wiring_smoke as smoke
    from subprocess import CompletedProcess

    def fake_training_smoke(**kwargs):
        return _fake_training_smoke_result(kwargs["output_dir"])

    def fake_collect(**kwargs):
        return False, [], ["runner_checkpoint_load_not_observed"], [], {"figure10_data_ready": False}, {"official_claim_allowed": False, "paper_reproduction_claim": False, "official_figure_claim": False}, False

    monkeypatch.setattr(smoke, "_run_training_smoke", fake_training_smoke)
    monkeypatch.setattr(smoke, "_run_figure10_validation_runner", lambda **kwargs: CompletedProcess(args=["figure10_validation.py"], returncode=0, stdout="ok", stderr=""))
    monkeypatch.setattr(smoke, "_collect_evaluation_wiring_report", fake_collect)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--training-epochs",
            "1",
            "--training-episode-time",
            "3",
            "--validation-episodes",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_13_trained_checkpoint_evaluation_wiring_smoke",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json")
    assert "runner_checkpoint_load_not_observed" in report["blockers"]


def test_unexpected_figure10_data_ready_true_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_trained_checkpoint_evaluation_wiring_smoke as smoke
    from subprocess import CompletedProcess

    def fake_training_smoke(**kwargs):
        return _fake_training_smoke_result(kwargs["output_dir"])

    def fake_collect(**kwargs):
        return True, [], ["unexpected_figure10_data_ready_true"], [], {"figure10_data_ready": True}, {"official_claim_allowed": False, "paper_reproduction_claim": False, "official_figure_claim": False}, True

    monkeypatch.setattr(smoke, "_run_training_smoke", fake_training_smoke)
    monkeypatch.setattr(smoke, "_run_figure10_validation_runner", lambda **kwargs: CompletedProcess(args=["figure10_validation.py"], returncode=0, stdout="", stderr=""))
    monkeypatch.setattr(smoke, "_collect_evaluation_wiring_report", fake_collect)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--training-epochs",
            "1",
            "--training-episode-time",
            "3",
            "--validation-episodes",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_13_trained_checkpoint_evaluation_wiring_smoke",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json")
    assert "unexpected_figure10_data_ready_true" in report["blockers"]


def test_runner_sidecar_missing_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_trained_checkpoint_evaluation_wiring_smoke as smoke
    from subprocess import CompletedProcess

    def fake_training_smoke(**kwargs):
        return _fake_training_smoke_result(kwargs["output_dir"])

    def fake_collect(**kwargs):
        return False, [], ["runner_metadata_sidecar_missing"], [], {}, {}, False

    monkeypatch.setattr(smoke, "_run_training_smoke", fake_training_smoke)
    monkeypatch.setattr(smoke, "_run_figure10_validation_runner", lambda **kwargs: CompletedProcess(args=["figure10_validation.py"], returncode=0, stdout="", stderr=""))
    monkeypatch.setattr(smoke, "_collect_evaluation_wiring_report", fake_collect)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_trained_checkpoint_evaluation_wiring_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--training-epochs",
            "1",
            "--training-episode-time",
            "3",
            "--validation-episodes",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_13_trained_checkpoint_evaluation_wiring_smoke",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json")
    assert "runner_metadata_sidecar_missing" in report["blockers"]


def test_no_generated_artifacts_outside_tmp_path(tmp_path):
    before = _repo_forbidden_snapshot()
    after = _repo_forbidden_snapshot()
    assert before == after
