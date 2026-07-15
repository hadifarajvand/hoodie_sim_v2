from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Iterable

from src.reference_model.models import TaskIdentity, TaskWorkload

@dataclass(frozen=True, slots=True)
class TraceRecord:
    task_identity: TaskIdentity
    workload: TaskWorkload
    decision_seed: int

@dataclass(frozen=True, slots=True)
class TraceRegistry:
    trace_id: str
    records: tuple[TraceRecord, ...]
    source_hash: str

    @classmethod
    def from_records(cls, trace_id: str, records: Iterable[TraceRecord], *, source_hash: str) -> "TraceRegistry":
        immutable = tuple(records)
        payload = {"trace_id": trace_id, "records": [asdict(record) for record in immutable], "source_hash": source_hash}
        trace_hash = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        return cls(trace_id=trace_hash, records=immutable, source_hash=source_hash)

    def canonical_payload(self) -> dict[str, object]:
        return {"trace_id": self.trace_id, "source_hash": self.source_hash, "records": [asdict(record) for record in self.records]}

    def hash(self) -> str:
        return self.trace_id
