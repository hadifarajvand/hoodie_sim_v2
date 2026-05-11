from __future__ import annotations

from pathlib import Path

from .report import build_link_rate_contract_report, write_link_rate_contract_report


def run_link_rate_transmission_delay_contract() -> dict[str, Path]:
    report = build_link_rate_contract_report()
    json_path, md_path = write_link_rate_contract_report(report)
    return {"json": json_path, "markdown": md_path}

