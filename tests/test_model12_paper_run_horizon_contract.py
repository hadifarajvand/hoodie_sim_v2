from __future__ import annotations

import csv
import json
from pathlib import Path

from environment.paper_horizon import (
    PAPER_ACTION_SLOTS,
    PAPER_DRAIN_SLOTS,
    PAPER_TOTAL_SLOTS,
    build_run_horizon_report,
    is_action_slot,
    is_drain_slot,
    slot_phase,
)
from training.orchestrate_model11 import preflight_runtime_trace


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_required_trace_files(trace_dir: Path) -> None:
    _write_csv(trace_dir / "task_lifecycle.csv", [{"task_id": 1, "arrival_time": 0, "final_status": "completed"}])
    _write_csv(trace_dir / "queue_trace.csv", [{"episode_id": 1, "time": 0, "node_id": 0, "queue_type": "private", "queue_length": 0, "arrivals": 0, "departures": 0, "drops": 0, "cpu_allocated": 1}])
    _write_csv(trace_dir / "action_trace.csv", [{"episode_id": 1, "time": 0, "agent_id": 0, "selected_action": 0, "reward_received": 0.0}])
    _write_csv(trace_dir / "episode_metrics.csv", [{"episode_id": 1, "total_tasks": 1, "completed_tasks": 1, "dropped_tasks": 0, "pending_tasks": 0, "average_latency": 1.0, "average_waiting_time": 0.0, "average_service_time": 1.0, "drop_ratio": 0.0, "average_queue_length": 0.0, "total_reward": 0.0, "mean_reward": 0.0}])


def _write_horizon_trace(trace_dir: Path) -> None:
    rows = []
    for time in range(PAPER_TOTAL_SLOTS):
        phase = slot_phase(time)
        rows.append(
            {
                "episode_id": 1,
                "time": time,
                "slot_phase": phase,
                "paper_action_slot": phase == "action",
                "paper_drain_slot": phase == "drain",
                "task_generation_allowed": phase == "action",
                "decision_allowed": phase == "action",
            }
        )
    _write_csv(trace_dir / "run_horizon_trace.csv", rows)


def test_horizon_constants_and_helpers() -> None:
    assert PAPER_ACTION_SLOTS == 100
    assert PAPER_DRAIN_SLOTS == 10
    assert PAPER_TOTAL_SLOTS == 110
    assert is_action_slot(0) is True
    assert is_action_slot(99) is True
    assert is_action_slot(100) is False
    assert is_drain_slot(100) is True
    assert is_drain_slot(109) is True
    assert is_drain_slot(110) is False
    assert slot_phase(-1) == "outside"
    assert slot_phase(0) == "action"
    assert slot_phase(99) == "action"
    assert slot_phase(100) == "drain"
    assert slot_phase(109) == "drain"
    assert slot_phase(110) == "outside"


def test_horizon_trace_generation(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_horizon_trace(trace_dir)
    rows = list(csv.DictReader((trace_dir / "run_horizon_trace.csv").open()))
    assert len(rows) == 110
    assert sum(1 for row in rows if row["slot_phase"] == "action") == 100
    assert sum(1 for row in rows if row["slot_phase"] == "drain") == 10
    assert all(row["task_generation_allowed"] == "True" for row in rows if row["slot_phase"] == "action")
    assert all(row["decision_allowed"] == "True" for row in rows if row["slot_phase"] == "action")
    assert all(row["task_generation_allowed"] == "False" for row in rows if row["slot_phase"] == "drain")
    assert all(row["decision_allowed"] == "False" for row in rows if row["slot_phase"] == "drain")


def test_build_run_horizon_report_passes_valid_paper_fixture(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_horizon_trace(trace_dir)
    _write_required_trace_files(trace_dir)
    _write_csv(
        trace_dir / "task_lifecycle.csv",
        [
            {"task_id": 1, "arrival_time": 0, "final_status": "completed"},
            {"task_id": 2, "arrival_time": 99, "final_status": "completed"},
        ],
    )
    _write_csv(
        trace_dir / "action_trace.csv",
        [{"episode_id": 1, "time": time, "agent_id": 0, "selected_action": 1, "reward_received": 0.0} for time in range(100)],
    )
    _write_csv(
        trace_dir / "queue_trace.csv",
        [{"episode_id": 1, "time": time, "node_id": 0, "queue_type": "private", "queue_length": 0, "arrivals": 0, "departures": 0, "drops": 0, "cpu_allocated": 1} for time in range(110)],
    )
    _write_csv(
        trace_dir / "delayed_reward_event_trace.csv",
        [{"task_id": 1, "episode_id": 1, "source_agent": 0, "decision_time": 0, "final_status": "completed", "completion_time": 105, "drop_time": "", "delay": 105, "reward": -105.0, "drop_penalty": 40.0, "reward_reason": "completed", "paired_transition_found": True, "replay_inserted": True, "replay_pairing_status": "paired", "reward_timing_convention": "completion_minus_arrival"}],
    )
    report = build_run_horizon_report(trace_dir)
    assert report["paper_action_slots"] == 100
    assert report["paper_drain_slots"] == 10
    assert report["observed_total_slots"] == 110
    assert report["task_generation_during_drain_count"] == 0
    assert report["decision_rows_during_drain_count"] == 0
    assert report["queue_rows_during_drain_count"] > 0
    assert report["completions_during_drain_count"] >= 1
    assert report["horizon_contract_passed"] is True
    assert report["paper_claims_made"] is False


def test_build_run_horizon_report_fails_if_task_arrives_during_drain(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_horizon_trace(trace_dir)
    _write_required_trace_files(trace_dir)
    _write_csv(trace_dir / "task_lifecycle.csv", [{"task_id": 1, "arrival_time": 100, "final_status": "completed"}])
    report = build_run_horizon_report(trace_dir)
    assert report["task_generation_during_drain_count"] == 1
    assert report["horizon_contract_passed"] is False


def test_build_run_horizon_report_fails_if_decision_occurs_during_drain(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_horizon_trace(trace_dir)
    _write_required_trace_files(trace_dir)
    _write_csv(trace_dir / "action_trace.csv", [{"episode_id": 1, "time": 100, "agent_id": 0, "selected_action": 1, "reward_received": 0.0, "decision_allowed": False}])
    report = build_run_horizon_report(trace_dir)
    assert report["decision_rows_during_drain_count"] == 1
    assert report["horizon_contract_passed"] is False


def test_model11_preflight_warns_when_horizon_report_missing(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_required_trace_files(trace_dir)
    out_dir = tmp_path / "out"
    report = preflight_runtime_trace(trace_dir, out_dir)
    assert report["preflight_status"] == "passed"
    assert any("run_horizon_report.json missing" in warning for warning in report["warnings"])
    assert report["paper_claims_made"] is False
    assert report["simulation_executed"] is False


def test_model11_preflight_fails_if_horizon_report_failed(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_required_trace_files(trace_dir)
    (trace_dir / "run_horizon_report.json").write_text(json.dumps({"horizon_contract_passed": False, "paper_action_slots": 100, "paper_drain_slots": 10, "paper_total_slots": 110}))
    out_dir = tmp_path / "out"
    try:
        preflight_runtime_trace(trace_dir, out_dir)
        assert False, "expected failure"
    except ValueError as exc:
        assert "paper horizon contract failed" in str(exc)
    report = json.loads((out_dir / "preflight_runtime_trace_report.json").read_text())
    assert report["horizon_contract_passed"] is False


def test_model11_preflight_accepts_valid_horizon_report(tmp_path: Path) -> None:
    trace_dir = tmp_path / "trace"
    _write_required_trace_files(trace_dir)
    (trace_dir / "run_horizon_report.json").write_text(json.dumps({"horizon_contract_passed": True, "paper_action_slots": 100, "paper_drain_slots": 10, "paper_total_slots": 110}))
    out_dir = tmp_path / "out"
    report = preflight_runtime_trace(trace_dir, out_dir)
    assert report["preflight_status"] == "passed"
    assert report["paper_action_slots"] == 100
    assert report["paper_drain_slots"] == 10
    assert report["paper_total_slots"] == 110
    assert report["horizon_contract_passed"] is True
