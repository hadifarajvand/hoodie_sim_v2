from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json

@dataclass(frozen=True, slots=True)
class ProvenanceManifest:
    config_hash: str
    source_hash: str
    trace_hash: str
    checkpoint_hash: str


def build_provenance_manifest(*, config_hash: str, source_hash: str, trace_hash: str, checkpoint_hash: str) -> ProvenanceManifest:
    return ProvenanceManifest(config_hash, source_hash, trace_hash, checkpoint_hash)


def provenance_hash(manifest: ProvenanceManifest) -> str:
    payload = json.dumps(asdict(manifest), sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()
