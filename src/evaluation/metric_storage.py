from __future__ import annotations

import json
from pathlib import Path

from .metrics import TraceMetrics


def persist_metrics(output_dir: Path, metrics: TraceMetrics) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{metrics.trace_id}_{metrics.policy_name}_{metrics.seed}.json"
    path.write_text(json.dumps(metrics.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path
