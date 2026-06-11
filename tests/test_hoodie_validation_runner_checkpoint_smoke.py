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


def test_script_imports_without_running_smoke():
    result = _run(["-c", "import scripts.run_hoodie_validation_runner_checkpoint_smoke as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr
    assert "scripts.run_hoodie_validation_runner_checkpoint_smoke" in result.stdout


def test_missing_allow_runner_checkpoint_smoke_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_checkpoint_smoke.py",
            "--checkpoint-dir",
            str(tmp_path / "missing"),
            "--output-dir",
            str(tmp_path / "out"),
            "--agent-count",
            "1",
        ]
    )
    assert result.returncode != 0


def test_agent_count_zero_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_checkpoint_smoke.py",
            "--checkpoint-dir",
            str(tmp_path / "missing"),
            "--output-dir",
            str(tmp_path / "out"),
            "--agent-count",
            "0",
            "--allow-runner-checkpoint-smoke",
        ]
    )
    assert result.returncode != 0


def test_output_inside_repo_is_refused_and_no_file_created(tmp_path):
    repo_output = ROOT / "artifacts/paper-contract-audit/phase6_6/repo_output.json"
    if repo_output.exists():
        repo_output.unlink()
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_checkpoint_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            str(repo_output),
            "--agent-count",
            "1",
            "--allow-runner-checkpoint-smoke",
        ]
    )
    assert result.returncode != 0
    assert not repo_output.exists()


def test_missing_checkpoint_dir_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_checkpoint_smoke.py",
            "--checkpoint-dir",
            str(tmp_path / "missing"),
            "--output-dir",
            str(tmp_path / "out"),
            "--agent-count",
            "1",
            "--allow-runner-checkpoint-smoke",
        ]
    )
    assert result.returncode != 0


def test_tiny_checkpoint_stages_to_runner_layout(tmp_path):
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    out = tmp_path / "runner"
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_checkpoint_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--run-id",
            "phase6_6_runner_smoke",
            "--allow-runner-checkpoint-smoke",
            "--allow-tiny-checkpoint-dir",
        ]
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads((out / "validation_runner_checkpoint_smoke_manifest.json").read_text())
    report = json.loads((out / "validation_runner_checkpoint_smoke_report.json").read_text())
    assert manifest["validation_run"] is False
    assert manifest["simulation_rerun"] is False
    assert manifest["training_run"] is False
    assert manifest["checkpoint_created"] is False
    assert manifest["official_claim_allowed"] is False
    assert manifest["figure10_claim"] is False
    assert manifest["main_py_called"] is False
    assert manifest["run_figure10_validation_called"] is False
    assert manifest["figure10_official_outputs_created"] is False
    assert report["validation_run"] is False
    assert report["simulation_rerun"] is False
    assert report["training_run"] is False
    assert report["checkpoint_created"] is False
    assert report["official_claim_allowed"] is False
    assert report["figure10_claim"] is False
    assert len(manifest["staged_checkpoint_summaries"]) == 2
    assert report["staged_checkpoint_count"] == 2
    assert report["staged_sidecar_count"] == 2
    assert report["all_staged_checkpoints_loadable"] is True
    delay_log = out / "runs" / "phase6_6_runner_smoke" / "delay" / "HOODIE" / "logs"
    drop_log = out / "runs" / "phase6_6_runner_smoke" / "drop_ratio" / "HOODIE" / "logs"
    for log_dir in [delay_log, drop_log]:
        assert (log_dir / "agent_0.pth").exists()
        assert (log_dir / "agent_0.pth.meta.json").exists()
        info = _run(
            [
                "-c",
                (
                    "from pathlib import Path; "
                    "from training.hoodie_checkpoint_interop import inspect_runtime_torch_checkpoint; "
                    "p=Path(r'%s'); "
                    "print(inspect_runtime_torch_checkpoint(p/'agent_0.pth')['loadable'])"
                )
                % str(log_dir),
            ]
        )
        assert info.returncode == 0, info.stderr
        assert "True" in info.stdout


def test_copy_hoodie_checkpoints_copies_sidecars(tmp_path):
    pytest.importorskip("torch")
    from figure10_validation import _copy_hoodie_checkpoints

    source = tmp_path / "source"
    log_dir = tmp_path / "logs"
    source.mkdir()
    p = source / "agent_0.pth"
    _create_tiny_checkpoint(tmp_path)
    # reuse the generated tiny checkpoint payload by copying it into the source dir
    tiny = tmp_path / "ckpt" / "agent_0.pth"
    tiny_meta = tmp_path / "ckpt" / "agent_0.pth.meta.json"
    p.write_bytes(tiny.read_bytes())
    (source / "agent_0.pth.meta.json").write_bytes(tiny_meta.read_bytes())
    ok, missing = _copy_hoodie_checkpoints(source, log_dir, 1)
    assert ok is True, missing
    assert (log_dir / "agent_0.pth").exists()
    assert (log_dir / "agent_0.pth.meta.json").exists()


def test_copy_hoodie_checkpoints_reports_missing_sidecar(tmp_path):
    pytest.importorskip("torch")
    from figure10_validation import _copy_hoodie_checkpoints

    source = tmp_path / "source"
    log_dir = tmp_path / "logs"
    source.mkdir()
    p = source / "agent_0.pth"
    p.write_text("not a checkpoint")
    ok, missing = _copy_hoodie_checkpoints(source, log_dir, 1)
    assert ok is False
    assert str(source / "agent_0.pth.meta.json") in missing


def test_tampered_metadata_official_claim_true_fails_and_reports_blocker(tmp_path):
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    meta_path = checkpoint_dir / "agent_0.pth.meta.json"
    meta = json.loads(meta_path.read_text())
    meta["official_claim_allowed"] = True
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True))
    out = tmp_path / "runner"
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_checkpoint_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--allow-runner-checkpoint-smoke",
            "--allow-tiny-checkpoint-dir",
        ]
    )
    assert result.returncode != 0
    manifest = json.loads((out / "validation_runner_checkpoint_smoke_manifest.json").read_text())
    report = json.loads((out / "validation_runner_checkpoint_smoke_report.json").read_text())
    assert any(
        "metadata_official_claim_allowed_true" in summary["blockers"]
        for summary in manifest["staged_checkpoint_summaries"]
    )
    assert "metadata_official_claim_allowed_true" in manifest["blockers"]
    assert "metadata_official_claim_allowed_true" in report["blockers"]
    assert not any(
        summary["runner_layout_ready_for_smoke"] for summary in manifest["staged_checkpoint_summaries"]
    )
    assert manifest["figure10_claim"] is False
    assert report["figure10_claim"] is False


def test_corrupt_checkpoint_exits_non_zero_and_not_layout_ready(tmp_path):
    checkpoint_dir = tmp_path / "corrupt"
    checkpoint_dir.mkdir()
    (checkpoint_dir / "agent_0.pth").write_text("not a checkpoint")
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
    out = tmp_path / "runner"
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_checkpoint_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--allow-runner-checkpoint-smoke",
            "--allow-tiny-checkpoint-dir",
        ]
    )
    assert result.returncode != 0
    manifest = json.loads((out / "validation_runner_checkpoint_smoke_manifest.json").read_text())
    report = json.loads((out / "validation_runner_checkpoint_smoke_report.json").read_text())
    assert manifest["staged_checkpoint_summaries"][0]["runner_layout_ready_for_smoke"] is False
    assert "source_checkpoint_not_loadable: agent_0" in manifest["staged_checkpoint_summaries"][0]["blockers"]
    assert "source_checkpoint_not_loadable: agent_0" in manifest["blockers"]
    assert "source_checkpoint_not_loadable: agent_0" in report["blockers"]
    assert report["all_staged_checkpoints_loadable"] is False


def test_trainer_json_checkpoint_is_refused(tmp_path):
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
    out = tmp_path / "runner"
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_checkpoint_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--allow-runner-checkpoint-smoke",
            "--allow-tiny-checkpoint-dir",
        ]
    )
    assert result.returncode != 0
    manifest = json.loads((out / "validation_runner_checkpoint_smoke_manifest.json").read_text())
    report = json.loads((out / "validation_runner_checkpoint_smoke_report.json").read_text())
    assert manifest["staged_checkpoint_summaries"][0]["runner_layout_ready_for_smoke"] is False
    assert any(
        blocker in manifest["staged_checkpoint_summaries"][0]["blockers"]
        for blocker in {"trainer_json_checkpoint_not_accepted", "metadata_checkpoint_format_invalid", "source_checkpoint_not_loadable: agent_0"}
    )
    assert any(
        blocker in manifest["blockers"]
        for blocker in {"trainer_json_checkpoint_not_accepted", "metadata_checkpoint_format_invalid", "source_checkpoint_not_loadable: agent_0"}
    )
    assert report["all_staged_checkpoints_loadable"] is False


def test_staged_checkpoint_not_loadable_is_reported(tmp_path):
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    out = tmp_path / "runner"

    import scripts.run_hoodie_validation_runner_checkpoint_smoke as smoke

    original_copy = smoke._copy_sidecars

    def corrupt_stage_sidecars(source_checkpoint_dir, staged_log_dir, agent_count):
        copied = original_copy(source_checkpoint_dir, staged_log_dir, agent_count)
        staged_file = staged_log_dir / "agent_0.pth"
        staged_file.write_text("not a checkpoint after copy")
        return copied

    smoke._copy_sidecars = corrupt_stage_sidecars
    try:
        result = smoke._stage_run_layout(out, "phase6_6_runner_smoke", checkpoint_dir, 1)
    finally:
        smoke._copy_sidecars = original_copy
    assert result["report"]["all_staged_checkpoints_loadable"] is False
    manifest = result["manifest"]
    report = result["report"]
    assert "staged_checkpoint_not_loadable: agent_0" in manifest["staged_checkpoint_summaries"][0]["blockers"]
    assert "staged_checkpoint_not_loadable: agent_0" in manifest["blockers"]
    assert "staged_checkpoint_not_loadable: agent_0" in report["blockers"]
    assert report["all_staged_checkpoints_loadable"] is False


def test_no_forbidden_artifacts_created_outside_tmp_path(tmp_path):
    forbidden_suffixes = {".pth", ".pt", ".pkl", ".pickle"}
    forbidden_names = {
        "paper_state_trace.csv",
        "queue_trace.csv",
        "mleo_candidate_latency_trace.csv",
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
    }
    before = {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}
    checkpoint_dir = _create_tiny_checkpoint(tmp_path)
    out = tmp_path / "runner"
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_checkpoint_smoke.py",
            "--checkpoint-dir",
            str(checkpoint_dir),
            "--output-dir",
            str(out),
            "--agent-count",
            "1",
            "--allow-runner-checkpoint-smoke",
            "--allow-tiny-checkpoint-dir",
        ]
    )
    assert result.returncode == 0, result.stderr
    after = {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}
    assert before == after
