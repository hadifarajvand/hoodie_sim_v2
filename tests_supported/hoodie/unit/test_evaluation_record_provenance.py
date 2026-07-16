from __future__ import annotations

from src.hoodie.experiments import evaluation_record_patch as patch
from src.hoodie.experiments import production_patch


def _evidence() -> dict[str, object]:
    return {
        "task_id": 11,
        "source_agent_id": 3,
        "decision_slot": 7,
        "selected_action": "horizontal_8",
        "resolved_destination": "8",
        "legal_action_mask": {
            "local": True,
            "horizontal": True,
            "vertical": True,
        },
        "decision_observation": {
            "size": 2.5,
            "processing_density": 0.297,
            "absolute_deadline_slot": 25,
            "topology": ("8", "13"),
            "queue_load": 4.0,
            "history_length": 10,
            "hoodie_q_value_summary": {
                "local": -2.0,
                "horizontal_8": 4.0,
                "horizontal_13": 1.0,
                "cloud": 0.0,
            },
        },
    }


def test_task_and_decision_outputs_are_joined_to_real_decision_evidence() -> None:
    patch.install_evaluation_record_patch()
    key = "trace-a:11"
    patch._RECORDS.clear()
    patch._RECORDS[key] = _evidence()

    task = production_patch.TaskRecord(
        campaign_id="campaign-a",
        panel_id="figure_10a",
        job_id="job-a",
        run_id="trace-a",
        policy="HOODIE",
        variant="hoodie_lstm",
        seed=7,
        trace_hash="trace-hash",
        task_id="11",
        source_agent="recorded-in-trace",
        arrival_slot=5,
        workload={"task_sizes": (2.0, 3.0)},
        deadline=24,
        decision_slot=5,
        selected_action="horizontal_8",
        destination="8",
        completion_or_drop_slot=9,
        outcome="completed",
        queue_delay=None,
        transmission_delay=None,
        service_delay=None,
        end_to_end_delay=5.0,
        reward=-5.0,
        learner_owner="HOODIE",
        config_hash="config-hash",
        source_hash="source-hash",
        checkpoint_hash="checkpoint-hash",
    )
    assert task.source_agent == "3"
    assert task.learner_owner == "EA-3"
    assert task.decision_slot == 7
    assert task.deadline == 25
    assert task.workload["task_size_mbits"] == 2.5
    assert task.workload["processing_density_gcycles_per_mbit"] == 0.297
    assert key in patch._RECORDS

    decision = production_patch.DecisionRecord(
        observation_ref=key,
        legal_action_mask={},
        selected_action="horizontal_8",
        exploration=False,
        forecast_fields={"use_lstm": True},
        q_value_summary={},
        policy_metadata={"policy": "HOODIE"},
    )
    assert decision.legal_action_mask["local"] is True
    assert decision.legal_action_mask["horizontal_8"] is True
    assert decision.legal_action_mask["horizontal_13"] is True
    assert decision.legal_action_mask["cloud"] is True
    assert decision.q_value_summary["horizontal_8"] == 4.0
    assert decision.forecast_fields["source_agent_id"] == 3
    assert decision.forecast_fields["decision_slot"] == 7
    assert decision.policy_metadata["resolved_destination"] == "8"
    assert key not in patch._RECORDS


def test_registry_is_cleared_before_each_evaluation_run(monkeypatch) -> None:
    patch._RECORDS["stale:1"] = _evidence()

    def fake_run(_runner, *_args, **_kwargs):
        return {
            "per_trace": [
                {
                    "trace_id": "trace-b",
                    "raw_records": [
                        {
                            **_evidence(),
                            "task_id": 12,
                        }
                    ],
                }
            ]
        }

    monkeypatch.setattr(patch, "_ORIGINAL_RUN", fake_run)
    result = patch._run_with_record_registry(object())
    assert result["per_trace"]
    assert "stale:1" not in patch._RECORDS
    assert "trace-b:12" in patch._RECORDS
