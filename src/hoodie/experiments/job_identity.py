from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from .specification import ExperimentSpec, PanelSpec

@dataclass(frozen=True, slots=True)
class ContentAddress:
    value: str


def _digest(payload: object) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def compute_experiment_id(spec: ExperimentSpec, *, source_commit: str) -> ContentAddress:
    payload = {"source_commit": source_commit, "spec": spec.canonical_payload()}
    return ContentAddress(_digest(payload))


def compute_job_id(spec: ExperimentSpec, panel: PanelSpec, *, source_commit: str, trace_hash: str) -> ContentAddress:
    payload = {"source_commit": source_commit, "spec": spec.canonical_payload(), "panel": asdict(panel), "trace_hash": trace_hash}
    return ContentAddress(_digest(payload))
