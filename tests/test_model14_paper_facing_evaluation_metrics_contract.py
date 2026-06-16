from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

from evaluation.paper_metrics import (
    compute_paper_facing_metrics,
    validate_paper_facing_metrics_report,
    write_paper_facing_metrics_report,
)
from training.orchestrate_model11 import orchestrate


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venvmac" / "bin" / "python"


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_base_fixture(trace_dir: Path, include_optional: bool = True, include_horizon: bool = True) -> None:
    _write_csv(
        trace_dir / "task_lifecycle.csv",
        [
            {
                "task_id": 1,
                "episode_id": 1,
                "arrival_time": 0,
                "completion_time": 5,
                "latency": 5.0,
                "waiting_time": 2.0,
                "service_time": 3.0,
                "final_status": "completed",
                "drop_reason": "",
                "paper_m_pub": 0.0,
                "drop_penalty": 40.0,
            },
            {
                "task_id": 2,
                "episode_id": 1,
                "arrival_time": 1,
                "completion_time": "",
                "latency": "",
                "waiting_time": 0.0,
                "service_time": 0.0,
                "final_status": "dropped",
                "drop_reason": "timeout in public queue",
                "paper_m_pub": 7.0,
                "drop_penalty": 40.0,
            },
            {
                "task_id": 3,
                "episode_id": 1,
                "arrival_time": 2,
                "completion_time": "",
                "latency": "",
                "waiting_time": 0.0,
                "service_time": 0.0,
                "final_status": "pending",
                "drop_reason": "",
                "paper_m_pub": 0.0,
                "drop_penalty": 40.0,
            },
        ],
    )
    _write_csv(
        trace_dir / "action_trace.csv",
        [
            {
                "episode_id": 1,
                "time": 0,
                "agent_id": 0,
                "selected_action": 1,
                "first_stage_decision": "offload",
                "destination_type": "vertical_cloud",
                "destination_node_id": 1,
                "is_valid": True,
            },
        ],
    )
    _write_csv(
        trace_dir / "paper_state_trace.csv",
        [
            {
                "episode_id": 1,
                "time": 0,
                "agent_id": 0,
                "x_n_t": 1,
                "task_id": 1,
                "eta_n": 5.0,
                "w_priv_n": 0.0,
                "w_off_n": 0.0,
                "l_pub_n_prev_json": json.dumps([0.0, 1.0]),
                "active_load_vector_json": json.dumps([1.0, 0.0]),
                "L_t_json": json.dumps([[0.0, 0.0], [1.0, 0.0]]),
                "predicted_next_load_json": json.dumps([1.0, 0.0]),
                "predicted_next_load_method": "persistence_baseline",
                "paper_lstm_forecast": False,
                "unavailable_fields_json": json.dumps([]),
                "approximation_warnings_json": json.dumps(["persistence_baseline"]),
                "state_vector_json": json.dumps([5.0, 0.0, 0.0, 1.0]),
                "state_dim": 4,
            },
            {
                "episode_id": 1,
                "time": 1,
                "agent_id": 0,
                "x_n_t": 0,
                "task_id": 1,
                "eta_n": 0.0,
                "w_priv_n": 0.0,
                "w_off_n": 0.0,
                "l_pub_n_prev_json": json.dumps([0.0, 1.0]),
                "active_load_vector_json": json.dumps([0.0, 1.0]),
                "L_t_json": json.dumps([[1.0, 0.0], [0.0, 1.0]]),
                "predicted_next_load_json": json.dumps([0.0, 1.0]),
                "predicted_next_load_method": "persistence_baseline",
                "paper_lstm_forecast": False,
                "unavailable_fields_json": json.dumps([]),
                "approximation_warnings_json": json.dumps(["persistence_baseline"]),
                "state_vector_json": json.dumps([0.0, 0.0, 0.0, 0.0]),
                "state_dim": 4,
            },
        ],
    )
    _write_csv(
        trace_dir / "episode_metrics.csv",
        [
            {
                "episode_id": 1,
                "total_tasks": 3,
                "completed_tasks": 1,
                "dropped_tasks": 1,
                "pending_tasks": 1,
                "drop_ratio": 1 / 3,
                "average_latency": 5.0,
                "average_waiting_time": 2.0,
                "average_service_time": 3.0,
                "total_reward": -11.0,
                "mean_reward": -11.0,
            }
        ],
    )
    if include_optional:
        _write_csv(
            trace_dir / "delayed_reward_event_trace.csv",
            [
            {
                "task_id": 1,
                "episode_id": 1,
                "source_agent": 0,
                "decision_time": 0,
                "final_status": "completed",
                "completion_time": 5,
                "drop_time": "",
                "delay": 5,
                "reward": -5.0,
                "reward_reason": "completed",
                "paired_transition_found": True,
                "replay_pairing_status": "paired",
                    "reward_timing_convention": "completion_minus_arrival",
                },
                {
                    "task_id": 2,
                    "episode_id": 1,
                "source_agent": 0,
                "decision_time": 1,
                "final_status": "dropped",
                "drop_time": 110,
                "completion_time": "",
                "delay": "",
                "reward": -40.0,
                "reward_reason": "dropped",
                "paired_transition_found": True,
                "replay_pairing_status": "paired",
                    "reward_timing_convention": "completion_minus_arrival",
                },
            ],
        )
    if include_horizon:
        _write_csv(
        trace_dir / "queue_trace.csv",
        [
            {"episode_id": 1, "time": 0, "node_id": 0, "queue_type": "public:0", "queue_length": 1, "arrivals": 1, "departures": 0, "drops": 0, "cpu_allocated": 1, "paper_m_pub": 0.0},
            {"episode_id": 1, "time": 100, "node_id": 0, "queue_type": "public:0", "queue_length": 1, "arrivals": 0, "departures": 0, "drops": 0, "cpu_allocated": 1, "paper_m_pub": 2.0},
        ],
    )
        _write_csv(
            trace_dir / "run_horizon_trace.csv",
            [
                {
                    "episode_id": 1,
                    "time": t,
                    "slot_phase": "action" if t < 100 else "drain",
                    "paper_action_slot": t < 100,
                    "paper_drain_slot": t >= 100,
                    "task_generation_allowed": t < 100,
                    "decision_allowed": t < 100,
                }
                for t in range(110)
            ],
        )
        (trace_dir / "run_horizon_report.json").write_text(
            json.dumps(
                {
                    "paper_action_slots": 100,
                    "paper_drain_slots": 10,
                    "paper_total_slots": 110,
                    "observed_action_slots": 100,
                    "observed_drain_slots": 10,
                    "observed_total_slots": 110,
                    "task_generation_during_drain_count": 0,
                    "decision_rows_during_drain_count": 0,
                    "queue_rows_during_drain_count": 1,
                    "completions_during_drain_count": 1,
                    "drops_during_drain_count": 0,
                    "horizon_contract_passed": True,
                    "paper_claims_made": False,
                },
                indent=2,
                sort_keys=True,
            )
        )


def test_metrics_pass_on_complete_tiny_fixture(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_base_fixture(trace_dir)
    report = write_paper_facing_metrics_report(trace_dir)
    assert report["status"] == "passed"
    assert report["counts"]["total_tasks"] == 3
    assert report["counts"]["completed_tasks"] == 1
    assert report["counts"]["dropped_tasks"] == 1
    assert report["counts"]["pending_tasks"] == 1
    assert pytest.approx(report["ratios"]["drop_ratio"], rel=1e-9) == 1 / 3
    assert pytest.approx(report["public_queue_throw"]["throw_ratio_proxy"], rel=1e-9) == report["ratios"]["drop_ratio"]
    assert report["public_queue_throw"]["timeout_drop_count"] == 1
    assert report["latency_delay"]["average_latency"] == 5.0
    assert report["latency_delay"]["delay_source"] == "delayed_reward_event_trace"
    assert report["reward"]["reward_count"] == 2
    assert report["horizon"]["horizon_contract_passed"] is True
    assert report["paper_claims_made"] is False
    assert report["official_reproduction_claimed"] is False
    assert report["validation_errors"] == []


def test_missing_optional_files_produces_degraded_status_not_failure(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_base_fixture(trace_dir, include_optional=False, include_horizon=False)
    report = write_paper_facing_metrics_report(trace_dir)
    assert report["status"] == "degraded"
    assert any("delayed_reward_event_trace" in warning for warning in report["warnings"])
    assert any("horizon" in warning for warning in report["warnings"])
    assert report["latency_delay"]["delay_source"] == "task_lifecycle_latency_fallback"
    assert report["validation_errors"] == []


def test_required_missing_file_fails(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    trace_dir.mkdir()
    _write_csv(
        trace_dir / "action_trace.csv",
        [{"episode_id": 1, "time": 0, "agent_id": 0, "selected_action": 1, "first_stage_decision": "offload", "destination_type": "vertical_cloud", "destination_node_id": 1, "is_valid": True}],
    )
    _write_csv(trace_dir / "episode_metrics.csv", [{"episode_id": 1, "total_tasks": 0, "completed_tasks": 0, "dropped_tasks": 0, "pending_tasks": 0, "drop_ratio": 0.0}])
    with pytest.raises(ValueError):
        compute_paper_facing_metrics(trace_dir)


def test_action_during_drain_is_validation_error(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_base_fixture(trace_dir)
    (trace_dir / "action_trace.csv").write_text(
        "episode_id,time,agent_id,selected_action,first_stage_decision,destination_type,destination_node_id,is_valid\n"
        "1,0,0,1,offload,vertical_cloud,1,True\n"
        "1,100,0,1,offload,vertical_cloud,1,True\n"
    )
    report = compute_paper_facing_metrics(trace_dir)
    assert report["actions"]["normal_selected_actions_during_drain_count"] == 1
    errors = validate_paper_facing_metrics_report(report)
    assert any("normal_selected_actions_during_drain_count" in error for error in errors)


def test_episode_metrics_cross_check_mismatch_is_detected(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_base_fixture(trace_dir)
    _write_csv(
        trace_dir / "episode_metrics.csv",
        [
            {
                "episode_id": 1,
                "total_tasks": 2,
                "completed_tasks": 1,
                "dropped_tasks": 1,
                "pending_tasks": 0,
                "drop_ratio": 0.5,
                "average_latency": 5.0,
                "average_waiting_time": 2.0,
                "average_service_time": 3.0,
            }
        ],
    )
    report = compute_paper_facing_metrics(trace_dir)
    assert report["episode_metrics_cross_check"]["cross_check_passed"] is False
    assert "total_tasks" in report["episode_metrics_cross_check"]["differences"]
    assert report["status"] in {"degraded", "failed"}


def test_public_queue_throw_metrics(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_base_fixture(trace_dir)
    report = compute_paper_facing_metrics(trace_dir)
    assert report["public_queue_throw"]["public_queue_throw_bits"] == 7.0
    assert report["public_queue_throw"]["public_queue_throw_events"] == 1


def test_model11_orchestration_writes_metrics_report(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_base_fixture(trace_dir)
    out_dir = tmp_path / "out"
    result = orchestrate(
        trace_dir=trace_dir,
        output_dir=out_dir,
        algorithm="dqn",
        epochs=1,
        batch_size=1,
        checkpoint_every=1,
        seed=7,
    )
    report_path = out_dir / "paper_facing_metrics_report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text())
    manifest = json.loads((out_dir / "model11_orchestration_manifest.json").read_text())
    assert result["manifest"]["paper_claims_made"] is False
    assert report["paper_claims_made"] is False
    assert manifest["paper_facing_metrics_report_path"] == str(report_path)
    assert manifest["paper_facing_metrics_status"] in {"passed", "degraded"}
    assert manifest["paper_facing_metrics_validation_errors_count"] == len(report["validation_errors"])


def test_model13_smoke_writes_metrics_report(tmp_path: Path) -> None:
    out_dir = tmp_path / "smoke"
    result = subprocess.run(
        [
            str(PYTHON),
            "-m",
            "simulation.run_paper_smoke",
            "--output-dir",
            str(out_dir),
            "--seed",
            "7",
            "--agents",
            "2",
            "--episodes",
            "1",
            "--trace-level",
            "full",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    report_path = out_dir / "trace" / "paper_facing_metrics_report.json"
    smoke_report_path = out_dir / "paper_smoke_execution_report.json"
    assert report_path.exists()
    smoke_report = json.loads(smoke_report_path.read_text())
    report = json.loads(report_path.read_text())
    assert smoke_report["paper_facing_metrics_report_path"] == str(report_path)
    assert smoke_report["paper_facing_metrics_status"] in {"passed", "degraded"}
    assert smoke_report["paper_facing_metrics_validation_errors_count"] == len(report["validation_errors"])
    assert report["paper_claims_made"] is False
    assert report["official_reproduction_claimed"] is False
