from __future__ import annotations

import json

from .config import REPORT_JSON, REPORT_MD
from .model import FullHOODIEMechanismFidelityBatchReport


def write_full_hoodie_mechanism_fidelity_batch_report(report: FullHOODIEMechanismFidelityBatchReport) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("# Full HOODIE Mechanism Fidelity Batch\n\n" + json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

