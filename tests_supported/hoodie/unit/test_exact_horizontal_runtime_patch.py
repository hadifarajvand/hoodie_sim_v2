from __future__ import annotations

from types import SimpleNamespace

from src.environment.link_rate_config import LinkRateConfig
from src.environment.offload_trace_ledger import OffloadTraceLedger
from src.hoodie.experiments import exact_horizontal_runtime_patch as patch


def test_exact_horizontal_action_uses_horizontal_rate_and_lifecycle(monkeypatch) -> None:
    task = SimpleNamespace(
        task_id=11,
        selected_action="horizontal_6",
        size=2.0,
        metadata={
            "transmission_rate_source": "vertical_R_V",
            "transmission_data_rate_bps": 1.0,
        },
    )
    ledger = OffloadTraceLedger()
    environment = SimpleNamespace(
        link_rate_config=LinkRateConfig(
            horizontal_data_rate_mbps=30.0,
            vertical_data_rate_mbps=10.0,
            slot_duration_seconds=0.1,
        ),
        _trace_ledgers={11: ledger},
    )
    delegated: list[int] = []

    def admit(_environment, admitted_task) -> None:
        delegated.append(admitted_task.task_id)

    monkeypatch.setattr(patch, "_ORIGINAL_ADMIT", admit)
    patch.admit_with_exact_horizontal_runtime(environment, task)

    assert delegated == [11]
    assert task.metadata["transmission_rate_source"] == "horizontal_R_H"
    assert (
        task.metadata["transmission_data_rate_bps"]
        == environment.link_rate_config.horizontal_data_rate_bps
    )
    assert ledger.snapshot() == ("queued_public", "transmission_started")


def test_non_horizontal_action_is_unchanged(monkeypatch) -> None:
    task = SimpleNamespace(
        task_id=12,
        selected_action="cloud",
        size=2.0,
        metadata={"sentinel": True},
    )
    environment = SimpleNamespace(
        link_rate_config=LinkRateConfig(),
        _trace_ledgers={12: OffloadTraceLedger()},
    )
    monkeypatch.setattr(
        patch, "_ORIGINAL_ADMIT", lambda _environment, _task: None
    )
    patch.admit_with_exact_horizontal_runtime(environment, task)
    assert task.metadata == {"sentinel": True}
    assert environment._trace_ledgers[12].snapshot() == ()
