from __future__ import annotations

import pytest

from src.hoodie.experiments.aggregation import aggregate_records
from src.hoodie.experiments.schemas import TaskRecord


def test_dataset_schema_accepts_valid_records() -> None:
    record = TaskRecord("campaign", "figure_8a", "job-1", "run-1", "HOODIE", "hoodie_lstm", 7, "trace", "task-1", "src-1", 1, {"task_count": 1}, 10, 1, "local", "dest-1", 3, "completed", 0.0, 0.0, 1.0, 1.0, 1.0, "owner", "cfg", "src", "chk")
    aggregate = aggregate_records([record])
    assert aggregate.offered_tasks == 1
    assert aggregate.completed_tasks == 1


def test_dataset_schema_rejects_missing_provenance() -> None:
    with pytest.raises(TypeError):
        TaskRecord("campaign", "figure_8a", "job-1", "run-1", "HOODIE", "hoodie_lstm", 7, "trace", "task-1", "src-1", 1, {"task_count": 1}, 10, 1, "local", "dest-1", 3, "completed", 0.0, 0.0, 1.0, 1.0, 1.0, "owner", "cfg", "src")
