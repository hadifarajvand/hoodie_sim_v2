from __future__ import annotations

import pytest

from src.hoodie.experiments.trace_registry import TraceRecord, TraceRegistry
from src.reference_model.models import TaskIdentity, TaskWorkload


def test_trace_registry_is_immutable_and_hash_stable() -> None:
    record = TraceRecord(TaskIdentity("task-1", "ea-1", "ea-2"), TaskWorkload(10, 5, 1), 7)
    registry = TraceRegistry.from_records("trace-a", [record], source_hash="src-hash")
    assert registry.hash() == registry.trace_id
    assert registry.records[0].task_identity.task_id == "task-1"
    with pytest.raises(AttributeError):
        registry.records += (record,)
