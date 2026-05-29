from __future__ import annotations

import json
from pathlib import Path

from .config import REPORT_JSON, REPORT_MD
from .model import DistributedMultiAgentHOODIETrainingBatchReport


def write_distributed_multi_agent_hoodie_training_batch_report(report: DistributedMultiAgentHOODIETrainingBatchReport) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("# Distributed Multi-Agent HOODIE Training Batch\n\n" + json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

