from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any

_FORBIDDEN = {"config", "source", "checkpoint", "smoke-source", "unknown", "placeholder", "not_yet_implemented"}


@dataclass(frozen=True, slots=True)
class ProvenanceManifest:
    source_commit: str
    source_contract_hash: str
    panel_contract_hash: str
    job_spec_hash: str
    topology_hash: str
    physical_hash: str
    workload_hash: str
    training_hash: str
    evaluation_hash: str
    trace_hash: str
    checkpoint_hash: str
    dataset_hashes: tuple[str, ...] = ()
    render_hash: str | None = None

    @property
    def config_hash(self) -> str:
        return self.source_commit

    @property
    def source_hash(self) -> str:
        return self.source_contract_hash


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _check_payload(payload: object) -> None:
    text = _canonical_json(payload)
    for value in _FORBIDDEN:
        if f'"{value}"' in text or text == value:
            raise ValueError(f"forbidden placeholder provenance value: {value}")


def build_provenance_manifest(*, strict: bool = False, **payload: Any) -> ProvenanceManifest:
    manifest = ProvenanceManifest(
        source_commit=str(payload.get("source_commit", "")),
        source_contract_hash=str(payload.get("source_contract_hash", "")),
        panel_contract_hash=str(payload.get("panel_contract_hash", "")),
        job_spec_hash=str(payload.get("job_spec_hash", "")),
        topology_hash=str(payload.get("topology_hash", "")),
        physical_hash=str(payload.get("physical_hash", "")),
        workload_hash=str(payload.get("workload_hash", "")),
        training_hash=str(payload.get("training_hash", "")),
        evaluation_hash=str(payload.get("evaluation_hash", "")),
        trace_hash=str(payload.get("trace_hash", "")),
        checkpoint_hash=str(payload.get("checkpoint_hash", "")),
        dataset_hashes=tuple(str(item) for item in payload.get("dataset_hashes", ())),
        render_hash=str(payload["render_hash"]) if payload.get("render_hash") is not None else None,
    )
    if strict:
        _check_payload(asdict(manifest))
    return manifest


def provenance_hash(manifest: ProvenanceManifest) -> str:
    payload = json.dumps(asdict(manifest), sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()
