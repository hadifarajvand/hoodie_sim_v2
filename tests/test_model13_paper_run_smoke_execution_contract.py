from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from environment.paper_horizon import build_run_horizon_report, validate_run_horizon_trace


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venvmac" / "bin" / "python"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _run_smoke(output_dir: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    cmd = [
        str(PYTHON),
        "-m",
        "simulation.run_paper_smoke",
        "--output-dir",
        str(output_dir),
        "--seed",
        "7",
        "--agents",
        "2",
        "--episodes",
        "1",
        "--trace-level",
        "full",
        *extra_args,
    ]
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)


def test_smoke_cli_creates_required_trace_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "smoke"
    result = _run_smoke(out_dir)
    assert result.returncode == 0, result.stderr
    trace_dir = out_dir / "trace"
    assert trace_dir.exists()
    for name in (
        "task_lifecycle.csv",
        "queue_trace.csv",
        "action_trace.csv",
        "episode_metrics.csv",
        "paper_state_trace.csv",
        "delayed_reward_event_trace.csv",
        "run_horizon_trace.csv",
        "run_horizon_report.json",
        "paper_smoke_execution_report.json",
    ):
        assert (trace_dir / name).exists() or (out_dir / name).exists()


def test_smoke_run_horizon_is_exactly_paper_contract(tmp_path: Path) -> None:
    out_dir = tmp_path / "smoke"
    result = _run_smoke(out_dir)
    assert result.returncode == 0, result.stderr
    report = json.loads((out_dir / "trace" / "run_horizon_report.json").read_text())
    assert report["paper_action_slots"] == 100
    assert report["paper_drain_slots"] == 10
    assert report["paper_total_slots"] == 110
    assert report["observed_action_slots"] == 100
    assert report["observed_drain_slots"] == 10
    assert report["observed_total_slots"] == 110
    assert report["task_generation_during_drain_count"] == 0
    assert report["decision_rows_during_drain_count"] == 0
    assert report["horizon_contract_passed"] is True
    assert report["paper_claims_made"] is False


def test_no_normal_selected_actions_during_drain(tmp_path: Path) -> None:
    out_dir = tmp_path / "smoke"
    result = _run_smoke(out_dir)
    assert result.returncode == 0, result.stderr
    action_rows = _read_csv(out_dir / "trace" / "action_trace.csv")
    assert all(not (100 <= int(row["time"]) <= 109 and row.get("selected_action") not in (None, "", "None")) for row in action_rows)


def test_run_horizon_trace_has_one_row_per_slot(tmp_path: Path) -> None:
    out_dir = tmp_path / "smoke"
    result = _run_smoke(out_dir)
    assert result.returncode == 0, result.stderr
    horizon_rows = _read_csv(out_dir / "trace" / "run_horizon_trace.csv")
    assert len(horizon_rows) == 110
    assert [row["slot_phase"] for row in horizon_rows[:100]] == ["action"] * 100
    assert [row["slot_phase"] for row in horizon_rows[100:]] == ["drain"] * 10


def test_smoke_report_is_honest(tmp_path: Path) -> None:
    out_dir = tmp_path / "smoke"
    result = _run_smoke(out_dir)
    assert result.returncode == 0, result.stderr
    report = json.loads((out_dir / "paper_smoke_execution_report.json").read_text())
    assert report["model"] == "Model 13 — Paper-Run Smoke Execution Contract"
    assert report["status"] == "passed"
    assert report["paper_claims_made"] is False
    assert report["official_reproduction_claimed"] is False
    assert report["simulation_scale"] == "tiny_smoke_only"
    assert report["full_pytest_executed"] is False
    assert report["large_artifacts_created"] is False
    assert report["cleanup_performed"] is False
    assert report["git_add_dot_used"] is False


def test_smoke_orchestration_path(tmp_path: Path) -> None:
    out_dir = tmp_path / "smoke"
    result = _run_smoke(out_dir, "--orchestrate")
    assert result.returncode == 0, result.stderr
    orchestration_dir = out_dir / "orchestration"
    assert (orchestration_dir / "model11_orchestration_manifest.json").exists()
    assert (orchestration_dir / "training" / "dataset_summary.json").exists()
    assert (orchestration_dir / "training" / "training_metrics.json").exists()
    assert (orchestration_dir / "training" / "phase3_training_report.json").exists()
    assert (orchestration_dir / "training" / "phase3_model.chkpt").exists()
    report = json.loads((out_dir / "paper_smoke_execution_report.json").read_text())
    assert report["orchestration_requested"] is True
    assert report["orchestration_status"] == "passed"
    assert report["paper_claims_made"] is False


def test_fail_fast_if_horizon_report_fails(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    trace_dir.mkdir()
    (trace_dir / "run_horizon_trace.csv").write_text("episode_id,time,slot_phase,paper_action_slot,paper_drain_slot,task_generation_allowed,decision_allowed\n1,0,action,True,False,True,True\n")
    (trace_dir / "run_horizon_report.json").write_text(json.dumps({"horizon_contract_passed": False}))
    try:
        validate_run_horizon_trace(trace_dir)
        assert False, "expected validation failure"
    except ValueError:
        pass

