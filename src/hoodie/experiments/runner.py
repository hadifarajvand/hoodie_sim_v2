from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .job_identity import compute_job_id
from .panel_registry import PANEL_REGISTRY
from .provenance import build_provenance_manifest, provenance_hash
from .resume import classify_job_state
from .storage import AtomicJobStorage
from .trace_registry import TraceRegistry

@dataclass(slots=True)
class CampaignRunner:
    campaign_id: str
    output_dir: Path

    def run_panel(self, panel_id: str, spec, trace: TraceRegistry, *, source_commit: str) -> Path:
        panel = PANEL_REGISTRY[panel_id]
        job_id = compute_job_id(spec, panel.spec, source_commit=source_commit, trace_hash=trace.hash()).value
        storage = AtomicJobStorage(self.output_dir / self.campaign_id / "jobs")
        job_dir = storage.write_job(job_id, {"spec": spec.canonical_payload(), "panel": panel_id, "trace_hash": trace.hash()})
        provenance = build_provenance_manifest(config_hash="config", source_hash=trace.source_hash, trace_hash=trace.hash(), checkpoint_hash="checkpoint")
        (job_dir / "provenance.json").write_text(json.dumps({"manifest": provenance.__dict__ if hasattr(provenance, "__dict__") else {"config_hash": provenance.config_hash, "source_hash": provenance.source_hash, "trace_hash": provenance.trace_hash, "checkpoint_hash": provenance.checkpoint_hash}, "hash": provenance_hash(provenance)}, sort_keys=True), encoding="utf-8")
        return job_dir
